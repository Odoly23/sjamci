"""Teste ba importasaun Excel (DNIM, MPMS, Kreditu Suave) ho ficheiru sintétiku."""
import tempfile
from decimal import Decimal
from io import StringIO

import openpyxl
from django.core.management import call_command
from django.test import TestCase

from benefisiariu.models import Benefisiariu
from config.import_utils import key, money, year
from custom.models import AdministrativePost, Faze, Municipality, Sector, Status, TIpu_Programa, Village
from kni.models import Business, Employee, LocBussiness, Program
from manufatureira.models import Aktividade, Manufatur
from mpms.models import mpmsEmpresa
from seguransa.models import ActivityLog
from suave.models import CreditInfo, FinancialAssessment


def _workbook(sheets):
    workbook = openpyxl.Workbook()
    workbook.remove(workbook.active)
    for title, rows in sheets.items():
        sheet = workbook.create_sheet(title)
        for row in rows:
            sheet.append(row)
    handle = tempfile.NamedTemporaryFile(suffix='.xlsx', delete=False)
    workbook.save(handle.name)
    return handle.name


def _run(command, path, *args):
    out = StringIO()
    call_command(command, path, *args, stdout=out)
    return out.getvalue()


class ParsingTests(TestCase):
    def test_money_formats_seen_in_ministry_files(self):
        cases = {'$          2,000,00': '2000.00', '$ . 2, 000.00': '2000.00', '$ 1.500,00': '1500.00',
                 '$.1, 500.00': '1500.00', '21.000.00': '21000.00', '2,500': '2500.00', '3.5': '3.50',
                 1500: '1500.00', 24985.29: '24985.29'}
        for raw, expected in cases.items():
            self.assertEqual(money(raw), Decimal(expected), raw)
        self.assertIsNone(money('abc'))
        self.assertIsNone(money(None))

    def test_year_and_key(self):
        self.assertEqual(year('2014'), 2014)
        self.assertEqual(year(2014.0), 2014)
        self.assertIsNone(year('Novembro'))
        self.assertEqual(key(' Liquiçá-Vila '), 'liquicavila')


class ImportBase(TestCase):
    @classmethod
    def setUpTestData(cls):
        Status.objects.create(pk=1, name='Ativu')
        Status.objects.create(pk=2, name='Parado')
        cls.baucau = Municipality.objects.create(name='Baucau')
        cls.liquica = Municipality.objects.create(name='Liquiçá')
        Municipality.objects.create(name='Dili')
        cls.post = AdministrativePost.objects.create(name='Baucau', municipality=cls.baucau)
        cls.village = Village.objects.create(name='Tirilolo', administrativepost=cls.post)


class DnimImportTests(ImportBase):
    HEADER = ['NO', 'Naran Grupu', 'Naran Chefe do Grupo', 'No Kontaktu', 'Municpio/ Posto/ Suco / Aldeia',
              'Tipu Industria', 'Tipu Apoio', 'Tinan', 'Valor osan', 'Membro', 'Mane', 'Feto', 'OBS']

    def _file(self):
        return _workbook({
            'Baucau': [['DADUS GRUPU'], ['BAUCAU'], self.HEADER,
                       [1, 'Grupu Tais', 'Maria Teste', 77000001, 'Baucau, Baucau Vila, Tirilolo, Aldeia A',
                        'Soru Tais', 'Subvensoens publico', 2014, '$. 1,500.00', 8, 3, 5, 'Ativo'],
                       [2, 'Grupu Karpintaria', 'Joao Teste', None, 'Baucau / Laran La Iha', 'karpintaria',
                        'Formsaun', None, None, None, None, None, 'Parado'],
                       [3, 'Grupu Tais', 'Maria Teste', 77000001, 'Baucau, Baucau Vila', 'Soru Tais',
                        'Subvenções Publicas', 2016, 2000, None, None, None, 'Ativo']],
            'Atauro': [['x'], self.HEADER, [1, 'Grupu Boneka', 'Ana Teste', None, 'Vila', 'Boneka', 'Formasaun', 2012, '$ 2.000,00', 4, None, None, 'ativo']],
            'Nowhere': [self.HEADER, [1, 'X', 'Y']],
        })

    def test_dry_run_saves_nothing(self):
        output = _run('import_dnim_excel', self._file())
        self.assertIn('TESTE DE\'IT', output)
        self.assertFalse(Manufatur.objects.exists())

    def test_commit_creates_groups_with_location_members_and_support(self):
        path = self._file()
        output = _run('import_dnim_excel', path, '--commit')
        self.assertEqual(Manufatur.objects.count(), 3)
        tais = Manufatur.objects.get(name='Grupu Tais')
        self.assertEqual((tais.leader_name, tais.phone, tais.status), ('Maria Teste', '77000001', 'Ativu'))
        self.assertEqual((tais.lokalidade.municipality, tais.lokalidade.administrativepost, tais.lokalidade.village),
                         (self.baucau, self.post, self.village))
        self.assertEqual((tais.members_data.male, tais.members_data.female, tais.members_data.members), (3, 5, 8))
        # liña repete = apoiu daruak ba grupu hanesan
        self.assertEqual(sorted(tais.atividades.values_list('year__year', 'amount')), [(2014, 1500.0), (2016, 2000.0)])
        self.assertEqual(tais.atividades.first().support_type.name, 'Subvenções Publicas')
        # totál membru mantein maski la iha mane/feto
        self.assertEqual(Manufatur.objects.get(name='Grupu Boneka').members_data.members, 4)
        self.assertEqual(Manufatur.objects.get(name='Grupu Boneka').lokalidade.municipality.name, 'Dili')
        self.assertIn('Munisípiu la hatene', output)
        self.assertIn('Atauro', output)

        again = _run('import_dnim_excel', path, '--commit')
        self.assertEqual(Manufatur.objects.count(), 3)
        self.assertEqual(Aktividade.objects.count(), 4)
        self.assertIn('Iha ona iha sistema (salta): 4', again)

    def test_bulk_import_does_not_flood_audit_log(self):
        before = ActivityLog.objects.count()
        _run('import_dnim_excel', self._file(), '--commit')
        self.assertEqual(ActivityLog.objects.count(), before)
        # rejistu normál fila fali hafoin importasaun
        Manufatur.objects.create(name='Hafoin', leader_name='x')
        self.assertEqual(ActivityLog.objects.count(), before + 1)


NAMES = ['Ida', 'Rua', 'Tolu', 'Haat', 'Lima']


class MpmsImportTests(ImportBase):
    HEADER = ['Tipo Atividade', 'Naran Diretor Empresas', 'Naran Kompania', 'Sexo', 'Nivel Edukasaun',
              'No Office/Hp/WA/Email/Website', 'Munisipio', 'Posto Adm.', 'Suco', 'Aldeia', 'Rua Avenida',
              'Tinan Hari Kompania', 'Lisensamento Aktividade', 'Lisensamento Aktividade iha',
              'Tipo Propriodade/Rai halao Aktividade', 'Kapital Investimento', 'Tipu Fundus Kapital',
              'Total Fundus $?', 'Total lukru $ Brutu (Kotor)/Mes/Ano', 'Lukru $ Likidu (Bersih)/Mes/Ano',
              'Total Empregador', None, None, None, 'Kustu ($) ba Materia Prima', "Materia Prima mai husi ne'ebe"]

    def _rows(self):
        # Títulu dehan diretór uluk, maibé dadus tau kompania uluk (hanesan ficheiru orijinál)
        rows = [['oficina_motor', f'Oficina Motor {NAMES[i]} Lda', f'Diretor {NAMES[i]}', 'mane', 'secundaria', f'7700010{i}',
                 'baucau', 'baucau', 'Tirilolo', 'Aldeia', '0', 2015 + i, 'iha', 'valido', 'rai_privado',
                 '0___5000', 'mikro', '1___5', 900, 600, 2, 1, 0, 0, 50, None] for i in range(5)]
        # liña ida muda koluna ida ba loos (hahú husi lisensa)
        shifted = ['salon_barberia fase_kareta', 'Salon Furak Enin', 'Rosa Teste', 'feto', 'liseneiatura', 'rosa@example.tl',
                   'baucau', 'baucau', 'Suku La Iha', 'Aldeia B', 'Rua 1', 2020, None, 'laiha', None, 'rai_aluguer',
                   '5000___30_000', 'Pequena', '6___21', 3000, 2000, 1, 4, 0, 0, None, None]
        bad = ['padeiria', 'Padaria Kios', 'Tomas Teste', 'M', 'tekbok', '0', '0', 'baucau', '', '', '', 'X',
               'talvez', '', 'rai_estado', '3', 'mikro', '1___5', 'abc', 10, 0, 0, 0, 0, None, None]
        return [self.HEADER, [None] * 20 + ['Nasional', None, 'Internasional'], [None] * 20 + ['Mane', 'Feto', 'Mane', 'Feto'],
                *rows, shifted, bad, ['kios', '?', None]]

    def _file(self):
        return _workbook({'Geral': [['Rekapitulasaun']], 'baucau': self._rows()})

    def test_dry_run_saves_nothing(self):
        _run('import_mpms_excel', self._file())
        self.assertFalse(mpmsEmpresa.objects.exists())
        self.assertFalse(Benefisiariu.objects.exists())

    def test_commit_detects_swapped_name_columns_and_maps_fields(self):
        path = self._file()
        output = _run('import_mpms_excel', path, '--commit')
        self.assertIn('DIFERENTE husi títulu', output)
        self.assertEqual(mpmsEmpresa.objects.count(), 7)
        empresa = mpmsEmpresa.objects.get(company_name='Oficina Motor Rua Lda')
        self.assertEqual(empresa.benefisiariu.name, 'Diretor Rua')
        self.assertEqual((empresa.benefisiariu.sex, empresa.benefisiariu.nivel_edukasaun), ('Mane', 'secundaria'))
        self.assertEqual((empresa.tipo_atividade.name, empresa.tinan_hari), ('Oficina Motor', '2016'))
        self.assertEqual((empresa.lokalizasaun.municipality, empresa.lokalizasaun.village), (self.baucau, self.village))
        self.assertEqual((empresa.lisensamentu.lisensamentu, empresa.lisensamentu.lisensamentu_status,
                          empresa.lisensamentu.tipo_rai), ('iha', 'valido', 'rai_privado'))
        self.assertEqual((empresa.kapital.kapital_investimento, empresa.kapital.tipu_fundus, empresa.kapital.total_fundus,
                          empresa.kapital.lukru_brutu_mes), ('0___5000', 'mikro', '1___5', Decimal('900.00')))
        self.assertEqual((empresa.empregador.nasional_mane, empresa.empregador.nasional_feto), (2, 1))
        self.assertEqual(empresa.materia_prima.kustu, Decimal('50.00'))
        self.assertEqual(empresa.business.name, 'Oficina Motor Rua Lda')

    def test_shifted_row_is_realigned_and_aliases_applied(self):
        output = _run('import_mpms_excel', self._file(), '--commit')
        empresa = mpmsEmpresa.objects.get(company_name='Salon Furak Enin')
        self.assertIn('Liña muda koluna', output)
        self.assertEqual((empresa.lisensamentu.lisensamentu, empresa.lisensamentu.tipo_rai), ('laiha', 'rai_aluguer'))
        self.assertEqual((empresa.kapital.kapital_investimento, empresa.kapital.tipu_fundus, empresa.kapital.total_fundus),
                         ('5000___30_000', 'pequenas', '6___20'))
        self.assertEqual(empresa.empregador.nasional_feto, 4)
        self.assertEqual(empresa.benefisiariu.nivel_edukasaun, 'lisensiatura')
        self.assertEqual(empresa.benefisiariu.email_website, 'rosa@example.tl')
        self.assertEqual(empresa.business.idea, 'Salon Barberia, Fase Kareta')
        self.assertIn('Suku La Iha', empresa.lokalizasaun.aldeia)

    def test_invalid_values_are_blanked_and_reported_not_fatal(self):
        output = _run('import_mpms_excel', self._file(), '--commit')
        empresa = mpmsEmpresa.objects.get(company_name='Padaria Kios')
        self.assertIsNone(empresa.kapital.kapital_investimento)
        self.assertIsNone(empresa.lisensamentu.lisensamentu)
        self.assertIsNone(empresa.tinan_hari)
        self.assertEqual(empresa.benefisiariu.nivel_edukasaun, 'seluk')
        for expected in ('Kapitál investimentu: valór la tuir opsaun', 'Tinan hari la válidu', 'La iha naran kompania no diretór'):
            self.assertIn(expected, output)

    def test_rerun_creates_no_duplicates_and_orientation_can_be_forced(self):
        path = self._file()
        _run('import_mpms_excel', path, '--commit')
        again = _run('import_mpms_excel', path, '--commit')
        self.assertEqual(mpmsEmpresa.objects.count(), 7)
        self.assertIn('Iha ona (salta): 7', again)
        mpmsEmpresa.objects.all().delete()
        Benefisiariu.objects.all().delete()
        _run('import_mpms_excel', path, '--commit', '--director-first', 'baucau')
        self.assertTrue(mpmsEmpresa.objects.filter(company_name='Diretor Rua').exists())


class KsImportTests(ImportBase):
    def _file(self):
        return _workbook({
            'Dados Kredit Suave': [
                [None, 'LISTA APROVADU'],
                [None, 'No', 'Naran Empreza', 'Naran Empresariu', 'Business Size', 'Jeneru', 'Atividade Negosiu',
                 'Kategoria Empreza', 'Status Atividade', 'Nu. Kontakto', 'Municipio', 'Posto Administrativo',
                 'Suco', 'Aldeia', 'Amount', 'Implicasaun renebus', 'Rekomendasaun', 'Obs'],
                [None, 1, 'Abel Teste', 'Abel Karpintaria, Enin', 'Micro', 'Mane', 'Fabrika Karpintaria', 'Industria',
                 'Ativa', 77000009, 'Baucau', 'Baucau', 'Tirilolo', 'Aldeia C', 25000, 'Banku lao normal', 'Kontinua', None],
                [None, 2, 'Berta Teste', 'Berta Agro Lda', 'Small', 'Feto', 'Hakiak manu', 'Agricultura',
                 'Parado 2024', None, 'Liquica', 'La Iha', None, None, None, 'Banku macet', None, 'Nota'],
            ],
            'Informasaun FGKS 2021 2022 2023': [
                [None, 'No', "Entrepreneur's Name", 'Gender', 'Enterprise Name', 'Sectors', 'Business Activities',
                 'Municipality', 'Approved by BNCTL', 'Amount Approved', 'Amount of Collateral', 'Employees', 'Female',
                 'Male', 'Annual Revenue', 'Total Assets', 'Business Size', 'Bookeeping', 'Business Challenges',
                 'Financial Challenges', 'Reason for getting loan', 'Any problem with repayment',
                 'Programs to be Continued', 'Access Again', 'Observation'],
                [None, 1, 'Abel Teste', 'M', 'Abel Karpintaria, Enin', 'Industry', 'x', 'Baucau', 'Approve', 24985.29,
                 18738.97, 4, 1, 3, 8640, 25000, 'Micro', 'Approve', None, None, None, 'Selu diak hela', None, None, 2022],
            ],
            'Monitorin Kredit Suave 2025': [['x']],
        })

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        Sector.objects.create(name='Industria')
        Sector.objects.create(name='Agrikultura')
        Faze.objects.create(name='KREDITU')
        TIpu_Programa.objects.create(name='KREDITU SUAVE')

    def test_dry_run_saves_nothing(self):
        _run('import_ks_excel', self._file())
        self.assertFalse(Program.objects.exists())

    def test_commit_merges_master_list_with_information_sheet(self):
        path = self._file()
        output = _run('import_ks_excel', path, '--commit')
        self.assertIn('SEIDAUK IMPORTA: Monitorin Kredit Suave 2025', output)
        # títulu koluna troka: "Naran Empreza" mak naran emprezáriu
        abel = Benefisiariu.objects.get(name='Abel Teste')
        business = Business.objects.get(benefisiariu=abel)
        self.assertEqual((business.name, business.sector.name), ('Abel Karpintaria, Enin', 'Industria'))
        program = Program.objects.get(benefisiariu=abel)
        self.assertEqual((program.program_type.name, program.year.year, program.amount), ('KREDITU SUAVE', 2022, Decimal('24985.29')))
        self.assertEqual(LocBussiness.objects.get(benefisiariu=abel).village, self.village)
        employee = Employee.objects.get(business=business)
        self.assertEqual((employee.male, employee.female, employee.total), (3, 1, 4))
        self.assertEqual(FinancialAssessment.objects.get(business=business).annual_revenue, Decimal('8640.00'))
        credit = CreditInfo.objects.get(business=business)
        self.assertEqual((credit.repayment_status, credit.approved_by_bank, credit.collateral_amount),
                         ('OnTime', 'BNCTL', Decimal('18738.97')))

        berta = Benefisiariu.objects.get(name='Berta Teste')
        self.assertEqual(berta.status.name, 'Parado')
        self.assertEqual(CreditInfo.objects.get(business__benefisiariu=berta).repayment_status, 'Stuck')
        self.assertEqual(LocBussiness.objects.get(benefisiariu=berta).municipality, self.liquica)
        self.assertIn('La iha montante kréditu', output)

        again = _run('import_ks_excel', path, '--commit')
        self.assertEqual(Program.objects.count(), 2)
        self.assertIn('Iha ona (salta): 2', again)
