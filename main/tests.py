"""Teste automátiku ba integridade no seguransa sistema SJAMCI.

Halo: python manage.py test
"""
import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth.models import Group, User
from django.template import TemplateDoesNotExist
from django.template.loader import get_template
from django.test import TestCase, override_settings
from django.urls import URLPattern, URLResolver, get_resolver, reverse

from benefisiariu.models import Benefisiariu, BenefisiariuUser
from users.passwords import temporary_password

BASE_DIR = Path(settings.BASE_DIR)
LOCAL_APPS = ['main', 'custom', 'benefisiariu', 'kni', 'suave', 'manufatureira',
              'notif', 'report', 'users', 'mpms', 'monitoring', 'config']


def _source_files(*suffixes):
    for app in LOCAL_APPS:
        for path in (BASE_DIR / app).rglob('*'):
            if (path.suffix in suffixes and 'static' not in path.parts
                    and 'migrations' not in path.parts and path.name != 'tests.py'):
                yield path


def _url_names():
    return {k for k in get_resolver().reverse_dict.keys() if isinstance(k, str)}


def _walk(patterns, prefix=''):
    for p in patterns:
        if isinstance(p, URLResolver):
            if p.app_name == 'admin':
                continue
            yield from _walk(p.url_patterns, prefix + str(p.pattern))
        elif isinstance(p, URLPattern):
            yield prefix + str(p.pattern), p


class ProjectIntegrityTests(TestCase):
    """Garante katak la iha template, naran URL ka rota ne'ebé kotu/duplikadu."""

    def test_all_templates_compile(self):
        errors = []
        for path in _source_files('.html'):
            if 'templates' not in path.parts:
                continue
            rel = path.relative_to(path.parents[len(path.parts) - path.parts.index('templates') - 2]).as_posix()
            try:
                get_template(rel)
            except Exception as exc:  # noqa: BLE001
                errors.append(f'{rel}: {exc}')
        self.assertEqual(errors, [])

    def test_referenced_templates_exist(self):
        pattern = re.compile(
            r"""(?:render\(\s*request\s*,\s*|include\s+|extends\s+|template_name\s*=\s*)['"]([^'"]+\.(?:html|txt))['"]""")
        missing = []
        for path in _source_files('.py', '.html'):
            for name in pattern.findall(path.read_text(encoding='utf-8')):
                try:
                    get_template(name)
                except TemplateDoesNotExist:
                    missing.append(f'{path.relative_to(BASE_DIR)}: {name}')
        self.assertEqual(missing, [])

    def test_referenced_url_names_exist(self):
        names = _url_names()
        in_template = re.compile(r"""\{%\s*url\s+['"]([^'":]+)['"]""")
        in_python = re.compile(r"""(?:redirect|reverse)\(\s*['"]([a-zA-Z_][\w-]*)['"]""")
        missing = []
        for path in _source_files('.py', '.html'):
            text = path.read_text(encoding='utf-8')
            found = in_template.findall(text)
            if path.suffix == '.py':
                found += in_python.findall(text)
            missing += [f'{path.relative_to(BASE_DIR)}: {n}' for n in found if n not in names]
        self.assertEqual(missing, [])

    def test_no_duplicate_routes_or_names(self):
        seen_paths, seen_names, dups = {}, {}, []
        for route, pattern in _walk(get_resolver().url_patterns):
            if route in seen_paths:
                dups.append(f'path duplikadu: {route}')
            seen_paths[route] = True
            if pattern.name:
                if pattern.name in seen_names:
                    dups.append(f'naran duplikadu: {pattern.name}')
                seen_names[pattern.name] = True
        self.assertEqual(dups, [])


class AccessControlTests(TestCase):
    """Garante katak dadus la bele asesu se la iha login/permisaun."""

    @classmethod
    def setUpTestData(cls):
        for name in ['admin', 'KNI', 'KS', 'dnim', 'mpms', 'Cliente', 'staff']:
            Group.objects.create(name=name)
        cls.admin = User.objects.create_user('admin1', password='x-Adm1n-pass!')
        cls.admin.groups.add(Group.objects.get(name='admin'))
        cls.cliente = User.objects.create_user('cliente1', password='x-Cl1ente-pass!')
        cls.cliente.groups.add(Group.objects.get(name='Cliente'))
        cls.nogroup = User.objects.create_user('nogroup', password='x-N0group-pass!')
        benef = Benefisiariu.objects.create(name='Teste Benef')
        cls.benef_user = BenefisiariuUser.objects.create(benefisiariu=benef, user=cls.cliente)

    def _routes_without_args(self):
        for route, pattern in _walk(get_resolver().url_patterns):
            if '<' not in route and '(' not in route and not route.startswith(('static/', 'media/')):
                yield '/' + route

    def test_anonymous_never_gets_data(self):
        public = {reverse('login'), reverse('password_reset'), reverse('password_reset_done'),
                  reverse('password_reset_complete')}
        leaked = []
        for url in self._routes_without_args():
            if url in public:
                continue
            status = self.client.get(url).status_code
            if status == 200:
                leaked.append(url)
        self.assertEqual(leaked, [])

    def test_report_api_requires_login(self):
        for url in self._routes_without_args():
            if url.startswith('/Api/sumario/'):
                self.assertIn(self.client.get(url).status_code, (401, 403), url)

    def test_report_api_works_for_staff(self):
        self.client.force_login(self.admin)
        for url in self._routes_without_args():
            if url.startswith('/Api/sumario/'):
                self.assertEqual(self.client.get(url).status_code, 200, url)

    def test_wrong_role_gets_403(self):
        self.client.force_login(self.cliente)
        for name in ['kni-dash', 'u-list', 'audit-login-list', 'benefisiariu-user-list', 'dash-mpms']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 403, name)

    def test_user_without_group_does_not_crash(self):
        self.client.force_login(self.nogroup)
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.assertEqual(self.client.get(reverse('kni-dash')).status_code, 403)

    def test_password_reset_needs_post_and_role(self):
        url = reverse('benefisiariu-user-reset-password', args=[self.benef_user.pk])
        old_hash = self.cliente.password
        self.client.force_login(self.cliente)
        self.assertEqual(self.client.post(url).status_code, 403)
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(url).status_code, 405)
        self.cliente.refresh_from_db()
        self.assertEqual(self.cliente.password, old_hash)
        self.assertEqual(self.client.post(url).status_code, 302)
        self.cliente.refresh_from_db()
        self.assertNotEqual(self.cliente.password, old_hash)

    def test_delete_account_needs_post(self):
        url = reverse('benefisiariu-user-delete', args=[self.benef_user.pk])
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(BenefisiariuUser.objects.filter(pk=self.benef_user.pk).exists())


class LoginSecurityTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('maria', password='Loos-Password-2026!')

    @override_settings(AXES_FAILURE_LIMIT=3)
    def test_account_locks_after_repeated_failures(self):
        url = reverse('login')
        for i in range(3):
            self.client.post(url, {'username': 'maria', 'password': f'sala-{i}'})
        response = self.client.post(url, {'username': 'maria', 'password': 'Loos-Password-2026!'})
        self.assertEqual(response.status_code, 429)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {'username': 'maria', 'password': 'Loos-Password-2026!'})
        self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)

    def test_temporary_passwords_are_random_and_strong(self):
        generated = {temporary_password() for _ in range(50)}
        self.assertEqual(len(generated), 50)
        for pwd in generated:
            self.assertGreaterEqual(len(pwd), 14)
            self.assertTrue(any(c.isdigit() for c in pwd) and any(c.isupper() for c in pwd))

    def test_no_hardcoded_default_passwords(self):
        offenders = [str(p.relative_to(BASE_DIR)) for p in _source_files('.py')
                     if re.search(r"MCI@#2026|Password_123", p.read_text(encoding='utf-8'))]
        self.assertEqual(offenders, [])
