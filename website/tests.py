"""Teste ba pajina públiku: lian, estatístika agregadu, privasidade."""
from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse

from benefisiariu.models import Benefisiariu
from custom.models import Municipality, TIpu_Programa, Year
from kni.models import LocBussiness, Program
from website import i18n, stats
from website.models import Announcement


class LandingPageTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        dili = Municipality.objects.create(name='Dili')
        oecusse = Municipality.objects.create(name='Regiao Administrativa Especial Oe-Cusse Ambeno')
        kni = TIpu_Programa.objects.create(name='KNI')
        y2023 = Year.objects.create(year=2023, is_active=True)
        y2024 = Year.objects.create(year=2024, is_active=True)
        people = [('Ana Segredu', 'Feto', dili, y2023), ('Beto Segredu', 'M', dili, y2023),
                  ('Carla Segredu', 'feto', oecusse, y2024), ('Dino Segredu', 'Mane', None, y2024)]
        for name, sex, municipality, year in people:
            benef = Benefisiariu.objects.create(name=name, sex=sex, phone='+67077000000')
            if municipality:
                LocBussiness.objects.create(benefisiariu=benef, municipality=municipality)
            Program.objects.create(benefisiariu=benef, program_type=kni, year=year, amount=100)

    def setUp(self):
        cache.clear()

    def test_every_text_is_translated_in_four_languages(self):
        self.assertEqual(i18n.all_keys_complete(), [])
        self.assertEqual(len(i18n.LANGUAGES), 4)

    def test_landing_is_public_and_has_required_sections(self):
        response = self.client.get(reverse('landing'))
        self.assertEqual(response.status_code, 200)
        for marker in ('class="topbar"', 'class="flags"', 'id="menu"', 'class="slider"', 'class="kpis',
                       'id="map"', 'id="chart-year"', 'id="informasaun"', 'id="kontaktu"'):
            self.assertContains(response, marker)
        self.assertEqual(response.content.decode().count('class="flag'), 5)   # konteiner + bandeira 4

    def test_signed_in_users_go_to_dashboard(self):
        self.client.force_login(User.objects.create_user('u1', password='x-User1-pass!'))
        self.assertRedirects(self.client.get(reverse('landing')), reverse('home'), fetch_redirect_response=False)

    def test_flag_click_switches_language(self):
        expected = {'tet': 'Estatístika benefisiáriu', 'pt': 'Estatísticas de beneficiários',
                    'en': 'Beneficiary statistics', 'id': 'Statistik penerima manfaat'}
        for code, heading in expected.items():
            response = self.client.get(reverse('set-lang', args=[code]), {'next': '/'})
            self.assertRedirects(response, '/', fetch_redirect_response=False)
            page = self.client.get(reverse('landing'))
            self.assertContains(page, f'<html lang="{code}">')
            self.assertContains(page, heading)

    def test_language_switch_rejects_unknown_code_and_external_redirect(self):
        self.client.get(reverse('set-lang', args=['en']), {'next': '/'})
        response = self.client.get(reverse('set-lang', args=['xx']), {'next': 'https://evil.example/'})
        self.assertRedirects(response, '/', fetch_redirect_response=False)
        self.assertContains(self.client.get(reverse('landing')), '<html lang="en">')

    def test_statistics_per_municipality_and_year(self):
        data = self.client.get(reverse('public-stats')).json()
        self.assertEqual(data['totals']['beneficiaries'], 4)
        counts = {m['iso']: m['count'] for m in data['municipalities']}
        self.assertEqual(counts, {'TL-DI': 2, 'TL-OE': 1})
        self.assertEqual(data['unlocated'], 1)
        self.assertEqual(data['by_sex'], {'male': 2, 'female': 2, 'unknown': 0})
        self.assertEqual(data['by_year'], [{'year': 2023, 'count': 2}, {'year': 2024, 'count': 2}])

        only_2023 = self.client.get(reverse('public-stats'), {'year': 2023}).json()
        self.assertEqual(only_2023['totals']['beneficiaries'], 2)
        self.assertEqual([m['iso'] for m in only_2023['municipalities']], ['TL-DI'])
        self.assertEqual(self.client.get(reverse('public-stats'), {'year': 'abc'}).json()['year'], None)

    def test_public_endpoints_never_expose_personal_data(self):
        for url in (reverse('landing'), reverse('public-stats'), reverse('public-stats-csv')):
            body = self.client.get(url).content.decode()
            self.assertNotIn('Segredu', body, url)
            self.assertNotIn('77000000', body, url)

    def test_csv_download(self):
        response = self.client.get(reverse('public-stats-csv'), {'year': 2023})
        self.assertEqual(response['Content-Type'], 'text/csv; charset=utf-8')
        lines = response.content.decode('utf-8-sig').strip().splitlines()
        self.assertEqual(lines[1], 'Dili,2023,2')
        self.assertTrue(lines[-1].endswith(',2023,2'))

    def test_every_database_municipality_name_maps_to_the_map(self):
        names = ['Aileu', 'Ainaro', 'Baucau', 'Bobonaro', 'Covalima', 'Dili', 'Ermera', 'Lautem', 'Liquiçá',
                 'Manatuto', 'Manufahi', 'Regiao Administrativa Especial Oe-Cusse Ambeno', 'Viqueque']
        self.assertEqual(len({stats.municipality_iso(n) for n in names}), 13)
        self.assertNotIn(None, [stats.municipality_iso(n) for n in names])

    def test_announcements_use_translation_with_tetun_fallback(self):
        Announcement.objects.create(title='Avizu Tetun', body='Konteúdu', title_en='English notice', level='important')
        Announcement.objects.create(title='La publika', body='x', is_published=False)
        self.assertContains(self.client.get(reverse('landing')), 'Avizu Tetun')
        self.client.get(reverse('set-lang', args=['en']))
        page = self.client.get(reverse('landing'))
        self.assertContains(page, 'English notice')
        self.assertNotContains(page, 'La publika')
        self.client.get(reverse('set-lang', args=['pt']))
        self.assertContains(self.client.get(reverse('landing')), 'Avizu Tetun')


class SystemLanguageSwitchTests(TestCase):
    """Bandeira 4 iha pajina sistema no painel admin."""

    @classmethod
    def setUpTestData(cls):
        from django.contrib.auth.models import Group
        Group.objects.create(name='admin')
        cls.admin = User.objects.create_superuser('xefe', password='x-Xefe-pass-2026!')
        cls.admin.groups.add(Group.objects.get(name='admin'))

    def test_system_pages_show_four_flags_and_translate_menu(self):
        self.client.force_login(self.admin)
        page = self.client.get(reverse('home'))
        self.assertContains(page, 'class="lang-switch"')
        for code in ('tet', 'pt', 'en', 'id'):
            self.assertContains(page, reverse('set-lang', args=[code]))
        self.assertContains(page, 'Relatoriu')

        expected = {'pt': ('Relatórios', 'Sair'), 'en': ('Reports', 'Sign out'), 'id': ('Laporan', 'Keluar')}
        for code, words in expected.items():
            response = self.client.get(reverse('set-lang', args=[code]), {'next': reverse('home')})
            self.assertRedirects(response, reverse('home'), fetch_redirect_response=False)
            page = self.client.get(reverse('home'))
            self.assertContains(page, f'<html lang="{code}">')
            for word in words:
                self.assertContains(page, word)

    def test_switch_returns_to_the_same_page(self):
        self.client.force_login(self.admin)
        target = reverse('activity-log') + '?action=update'
        response = self.client.get(reverse('set-lang', args=['en']), {'next': target})
        self.assertRedirects(response, target, fetch_redirect_response=False)

    def test_django_admin_has_switch_and_follows_language(self):
        self.client.force_login(self.admin)
        index = reverse('admin:index')
        self.assertContains(self.client.get(index), 'class="lang-switch"')
        self.client.get(reverse('set-lang', args=['id']))
        self.assertContains(self.client.get(index), 'Selamat datang')
        self.client.get(reverse('set-lang', args=['en']))
        self.assertContains(self.client.get(index), 'Welcome')

    def test_menu_dictionary_covers_three_target_languages(self):
        from website.ui_strings import UI
        self.assertEqual([k for k, v in UI.items() if set(v) != {'pt', 'en', 'id'}], [])
