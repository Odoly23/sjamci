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
from seguransa import totp
from seguransa.models import ActivityLog, UserSecurity
from seguransa.utils import require_password_change
from users.passwords import temporary_password

BASE_DIR = Path(settings.BASE_DIR)
LOCAL_APPS = ['main', 'custom', 'benefisiariu', 'kni', 'suave', 'manufatureira',
              'notif', 'report', 'users', 'mpms', 'monitoring', 'config', 'seguransa']


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
        public = {reverse('login'), reverse('healthz'), reverse('password_reset'), reverse('password_reset_done'),
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


class AccountSecurityFeatureTests(TestCase):
    """Troka password obrigatóriu, verifikasaun pasu-2 no rejistu auditoria."""

    PASSWORD = 'Loos-Password-2026!'

    @classmethod
    def setUpTestData(cls):
        Group.objects.create(name='admin')
        cls.user = User.objects.create_user('joao', password=cls.PASSWORD)
        cls.user.groups.add(Group.objects.get(name='admin'))

    def _login(self, password=None):
        return self.client.post(reverse('login'), {'username': 'joao', 'password': password or self.PASSWORD})

    def test_temporary_password_must_be_changed_before_using_system(self):
        require_password_change(self.user)
        self._login()
        self.assertRedirects(self.client.get(reverse('home')), reverse('password-change'))
        response = self.client.post(reverse('password-change'), {
            'old_password': self.PASSWORD,
            'new_password1': 'Foun-Password-2027!', 'new_password2': 'Foun-Password-2027!'})
        self.assertRedirects(response, reverse('home'))
        self.assertEqual(self.client.get(reverse('home')).status_code, 200)
        self.assertFalse(UserSecurity.objects.get(user=self.user).must_change_password)

    def test_weak_new_password_rejected(self):
        self._login()
        self.client.post(reverse('password-change'), {
            'old_password': self.PASSWORD, 'new_password1': '12345', 'new_password2': '12345'})
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(self.PASSWORD))

    def _enable_two_factor(self):
        self._login()
        self.client.get(reverse('two-factor'))
        security = UserSecurity.objects.get(user=self.user)
        code = totp._code(security.totp_secret, totp.current_step())
        self.client.post(reverse('two-factor'), {'code': code})
        security.refresh_from_db()
        self.assertTrue(security.totp_enabled)
        self.client.post(reverse('logout'))
        self.client.get(reverse('logout'))
        return security

    def test_two_factor_login_requires_valid_code(self):
        security = self._enable_two_factor()
        self.assertRedirects(self._login(), reverse('two-factor-verify'))
        # password de'it la to'o
        self.assertEqual(self.client.get(reverse('home')).status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)
        self.client.post(reverse('two-factor-verify'), {'code': '000000'})
        self.assertNotIn('_auth_user_id', self.client.session)
        # kódigu ne'ebé uza tiha ona iha ativasaun la bele uza fali
        used = totp._code(security.totp_secret, security.totp_last_step)
        self.client.post(reverse('two-factor-verify'), {'code': used})
        self.assertNotIn('_auth_user_id', self.client.session)
        # kódigu foun válidu → login kompletu
        UserSecurity.objects.filter(pk=security.pk).update(totp_last_step=0)
        fresh = totp._code(security.totp_secret, totp.current_step())
        # (ho espasu, hanesan aplikasaun balu hatudu: "123 456")
        spaced = f'{fresh[:3]} {fresh[3:]}'
        self.assertRedirects(self.client.post(reverse('two-factor-verify'), {'code': spaced}), reverse('home'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_two_factor_locks_after_too_many_wrong_codes(self):
        self._enable_two_factor()
        self._login()
        for i in range(5):
            response = self.client.post(reverse('two-factor-verify'), {'code': f'00000{i}'})
        self.assertRedirects(response, reverse('login'))
        self.assertNotIn('pending_2fa', self.client.session)

    def test_totp_matches_rfc6238_vector(self):
        secret = 'GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ'   # "12345678901234567890"
        self.assertEqual(totp._code(secret, 59 // 30), '287082')
        self.assertEqual(totp._code(secret, 1111111109 // 30), '081804')

    def test_data_changes_are_audited(self):
        self.client.force_login(self.user)
        self.client.get(reverse('home'))
        benef = Benefisiariu.objects.create(name='Ana Teste')
        benef.name = 'Ana Teste Foun'
        benef.save()
        benef.delete()
        logs = ActivityLog.objects.filter(model='Benefisiariu').order_by('id')
        actions = list(logs.values_list('action', flat=True))
        self.assertEqual((actions[0], actions[-1]), ('create', 'delete'))
        renamed = [log for log in logs if 'name' in log.changes]
        self.assertEqual(len(renamed), 1)
        self.assertEqual(renamed[0].changes['name'], ['Ana Teste', 'Ana Teste Foun'])

    def test_security_events_record_who_did_it(self):
        self._login()
        self.client.post(reverse('password-change'), {
            'old_password': self.PASSWORD,
            'new_password1': 'Foun-Password-2027!', 'new_password2': 'Foun-Password-2027!'})
        event = ActivityLog.objects.get(action='security')
        self.assertEqual((event.username, event.ip_address), ('joao', '127.0.0.1'))

    def test_passwords_never_written_to_audit_log(self):
        self.user.set_password('Seluk-Password-2028!')
        self.user.save()
        for log in ActivityLog.objects.filter(model='User'):
            self.assertNotIn('password', log.changes)

    def test_activity_log_admin_only(self):
        self.assertEqual(self.client.get(reverse('activity-log')).status_code, 302)
        other = User.objects.create_user('seluk', password=self.PASSWORD)
        self.client.force_login(other)
        self.assertEqual(self.client.get(reverse('activity-log')).status_code, 403)
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('activity-log')).status_code, 200)
        self.assertEqual(self.client.get(reverse('activity-log-export')).status_code, 200)

    def test_health_check(self):
        response = self.client.get(reverse('healthz'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['database'], 'ok')
