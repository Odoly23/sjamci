"""Teste ba rejistu offline (PWA): sinkronizasaun, duplikadu, permisaun."""
import uuid

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from benefisiariu.models import Benefisiariu, BenefisiariuUser
from custom.models import Faze, Municipality, Status, TIpu_Programa, Year
from kni.models import Business, LocBussiness, Program
from offline.models import OfflineSubmission


class OfflineSyncTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        for name in ['KNI', 'KS', 'Cliente']:
            Group.objects.create(name=name)
        cls.officer = User.objects.create_user('ofisial', password='x-0fisial-pass!')
        cls.officer.groups.add(Group.objects.get(name='KNI'))
        cls.other = User.objects.create_user('seluk', password='x-Seluk-pass!')
        cls.other.groups.add(Group.objects.get(name='KS'))
        Status.objects.create(pk=1, name='Ativu')
        TIpu_Programa.objects.create(name='KNI')
        cls.year = Year.objects.create(year=2026, is_active=True)
        cls.faze = Faze.objects.create(name='I')
        cls.municipality = Municipality.objects.create(name='Dili')

    def _payload(self, **overrides):
        data = {
            'uuid': str(uuid.uuid4()),
            'module': 'kni',
            'filled_at': '2026-11-01T08:30:00Z',
            'benef.name': 'Maria Offline',
            'benef.phone': '+67077001122',
            'business.name': 'Kios Maria',
            'business.idea': 'Kios',
            'location.municipality': str(self.municipality.pk),
            'location.latitude': '-8.556',
            'location.longitude': '125.560',
            'program.faze': str(self.faze.pk),
            'program.year': str(self.year.pk),
            'program.amount': '1200',
        }
        data.update(overrides)
        return {k: v for k, v in data.items() if v is not None}

    def _sync(self, payload):
        return self.client.post(reverse('offline-sync'), payload)

    def test_full_registration_is_saved_like_online(self):
        self.client.force_login(self.officer)
        response = self._sync(self._payload())
        self.assertEqual(response.status_code, 200, response.content)
        body = response.json()
        benef = Benefisiariu.objects.get(name='Maria Offline')
        self.assertEqual(body['url'], reverse('benef-detail-kni', args=[benef.hashed]))
        self.assertTrue(Business.objects.filter(benefisiariu=benef, name='Kios Maria').exists())
        self.assertEqual(LocBussiness.objects.get(benefisiariu=benef).latitude, '-8.556')
        program = Program.objects.get(benefisiariu=benef)
        self.assertEqual((program.program_type.name, program.amount), ('KNI', 1200))
        # regra online nian mós aplika: konta kliente kria ho password temporáriu
        self.assertTrue(BenefisiariuUser.objects.filter(benefisiariu=benef).exists())
        self.assertTrue(any('Password temporáriu' in m for m in body['messages']))
        # mensajen la hela ba pajina tuir mai
        self.assertNotContains(self.client.get(reverse('offline-hub')), 'Password temporáriu')

    def test_resending_same_record_does_not_duplicate(self):
        self.client.force_login(self.officer)
        payload = self._payload()
        self.assertEqual(self._sync(payload).status_code, 200)
        again = self._sync(payload)
        self.assertEqual(again.status_code, 200)
        self.assertTrue(again.json()['duplicate'])
        self.assertEqual(Benefisiariu.objects.filter(name='Maria Offline').count(), 1)
        self.assertEqual(OfflineSubmission.objects.count(), 1)

    def test_location_is_optional(self):
        self.client.force_login(self.officer)
        payload = self._payload(**{'location.municipality': None, 'location.latitude': None,
                                   'location.longitude': None})
        self.assertEqual(self._sync(payload).status_code, 200)
        self.assertFalse(LocBussiness.objects.exists())

    def test_invalid_fields_are_reported_and_nothing_saved(self):
        self.client.force_login(self.officer)
        response = self._sync(self._payload(**{'benef.name': '', 'program.amount': 'abc'}))
        self.assertEqual(response.status_code, 422)
        errors = response.json()['errors']
        self.assertIn('name', errors['benef'])
        self.assertIn('amount', errors['program'])
        self.assertFalse(Benefisiariu.objects.exists())

    def test_existing_beneficiary_is_rejected(self):
        Benefisiariu.objects.create(name='Maria Offline')
        self.client.force_login(self.officer)
        response = self._sync(self._payload())
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()['status'], 'rejected')
        self.assertEqual(Benefisiariu.objects.count(), 1)
        self.assertFalse(OfflineSubmission.objects.exists())

    def test_failure_in_later_step_rolls_back_everything(self):
        TIpu_Programa.objects.all().delete()      # pasu programa sei falla
        self.client.force_login(self.officer)
        users_before = User.objects.count()
        response = self._sync(self._payload())
        self.assertEqual(response.status_code, 500)
        self.assertFalse(Benefisiariu.objects.exists())
        self.assertFalse(Business.objects.exists())
        self.assertEqual(User.objects.count(), users_before)

    def test_requires_login_and_matching_role(self):
        self.assertEqual(self._sync(self._payload()).status_code, 401)
        self.client.force_login(self.other)
        self.assertEqual(self._sync(self._payload()).status_code, 403)
        self.assertEqual(self.client.get(reverse('offline-form', args=['kni'])).status_code, 403)
        self.assertEqual(self.client.get(reverse('offline-form', args=['ks'])).status_code, 200)
        self.assertFalse(Benefisiariu.objects.exists())

    def test_record_of_another_user_cannot_be_probed(self):
        self.client.force_login(self.officer)
        payload = self._payload()
        self._sync(payload)
        second = User.objects.create_user('ofisial2', password='x-0fisial2-pass!')
        second.groups.add(Group.objects.get(name='KNI'))
        self.client.force_login(second)
        self.assertEqual(self._sync(payload).status_code, 403)

    def test_pwa_files_are_served(self):
        manifest = self.client.get(reverse('pwa-manifest'))
        self.assertEqual(manifest.json()['start_url'], reverse('offline-hub'))
        worker = self.client.get(reverse('pwa-sw'))
        self.assertEqual(worker['Service-Worker-Allowed'], '/')
        self.assertIn(reverse('offline-form', args=['mpms']), worker.content.decode())

    def test_form_page_contains_all_steps_and_geo_data(self):
        self.client.force_login(self.officer)
        response = self.client.get(reverse('offline-form', args=['kni']))
        for step in ('benef', 'business', 'location', 'program'):
            self.assertContains(response, f'data-step="{step}"')
        self.assertContains(response, 'id="geo-data"')
