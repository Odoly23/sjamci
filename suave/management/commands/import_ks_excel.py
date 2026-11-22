"""Importa lista benefisiáriu Kreditu Suave husi Excel.

    python manage.py import_ks_excel Dados_Kreditu_suave.xlsx            # teste de'it
    python manage.py import_ks_excel Dados_Kreditu_suave.xlsx --commit   # rai

Lee sheet "Dados Kredit Suave" (lista aprovadu) no kompleta ho sheet
"Informasaun FGKS 2021 2022 2023" (tinan, trabalhadór, rendimentu, kolaterál),
liga tuir naran empreza. Sheet "Monitorin ..." (kestionáriu detalladu) seidauk importa.
"""
import openpyxl
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from benefisiariu.models import Benefisiariu
from config.import_utils import Places, Report, integer, key, money, non_empty_rows, phone, text, year
from custom.models import Bussines_size, Category_Emp, Faze, Sector, Status, TIpu_Programa, Year
from kni.models import Business, Employee, Finance, LocBussiness, Program
from seguransa.signals import audit_paused
from suave.models import CreditInfo, FinancialAssessment

MASTER_SHEET = 'dadoskreditsuave'
INFO_SHEET = 'informasaunfgks202120222023'
MASTER = {'entrepreneur': 'naranempreza', 'enterprise': 'naranempresariu', 'size': 'businesssize', 'sex': 'jeneru',
          'activity': 'atividadenegosiu', 'category': 'kategoriaempreza', 'status': 'statusatividade',
          'phone': 'nukontakto', 'municipality': 'municipio', 'post': 'postoadministrativo', 'village': 'suco',
          'aldeia': 'aldeia', 'amount': 'amount', 'repayment': 'implicasaun', 'recommendation': 'rekomendasaun',
          'notes': 'obs'}
INFO = {'enterprise': 'enterprisename', 'approved': 'amountapproved', 'collateral': 'amountofcollateral',
        'bank': 'approvedbybnctl', 'female': 'female', 'male': 'male', 'employees': 'employees',
        'revenue': 'annualrevenue', 'assets': 'totalassets', 'repay_problem': 'anyproblemwithrepay',
        'year': 'observation'}
SECTORS = {'industria': 'Industria', 'industry': 'Industria', 'agricultura': 'Agrikultura', 'agrikultura': 'Agrikultura',
           'turismo': 'Turismu', 'turismu': 'Turismu', 'comercio': 'Komersiu', 'komersiu': 'Komersiu'}


def _table(sheet, wanted, anchor='no'):
    """Fó fali lista dicionáriu {kampu: valór} tuir títulu koluna."""
    rows = non_empty_rows(sheet)
    header_index = next((i for i, row in enumerate(rows) if any(key(c) == anchor for c in row[:3])), None)
    if header_index is None:
        return []
    columns = {}
    for index, cell in enumerate(rows[header_index]):
        label = key(cell)
        for field, prefix in wanted.items():
            if label.startswith(prefix) and field not in columns:
                columns[field] = index
    return [{field: (row[index] if index < len(row) else None) for field, index in columns.items()}
            for row in rows[header_index + 1:]]


def _repayment(raw):
    """Tradús nota pagamentu ba opsaun formuláriu (OnTime/Late/Stuck/Done/Failed)."""
    value = key(raw)
    if not value:
        return None
    for needle, code in (('macet', 'Stuck'), ('seluhotu', 'Done'), ('falla', 'Failed'), ('tarde', 'Late'),
                         ('seludiak', 'OnTime'), ('laonormal', 'OnTime'), ('selunormal', 'OnTime')):
        if needle in value:
            return code
    return 'Other'


class Command(BaseCommand):
    help = 'Importa lista benefisiáriu Kreditu Suave husi ficheiru Excel.'

    def add_arguments(self, parser):
        parser.add_argument('file')
        parser.add_argument('--commit', action='store_true', help='Rai iha baze-dadus (se la iha, teste de\'it)')
        parser.add_argument('--user', help='Username ne\'ebé rejista hanesan kriadór')

    def handle(self, *args, **options):
        try:
            workbook = openpyxl.load_workbook(options['file'], read_only=True, data_only=True)
        except Exception as exc:  # noqa: BLE001
            raise CommandError(f'La konsege loke ficheiru: {exc}')
        user = None
        if options['user']:
            user = get_user_model().objects.filter(username=options['user']).first()
            if user is None:
                raise CommandError('Utilizador la eziste.')
        sheets = {key(s.title): s for s in workbook.worksheets}
        if MASTER_SHEET not in sheets:
            raise CommandError('Sheet "Dados Kredit Suave" la iha iha ficheiru.')
        # Iha sheet ne'e títulu "Naran Empreza" iha leten koluna naran emprezáriu (no vice-versa)
        master = [r for r in _table(sheets[MASTER_SHEET], MASTER) if text(r.get('entrepreneur')) and text(r.get('enterprise'))]
        info = {key(r.get('enterprise')): r for r in _table(sheets[INFO_SHEET], INFO)} if INFO_SHEET in sheets else {}

        report = Report()
        places = Places()
        statuses = {s.name: s for s in Status.objects.all()}
        sectors = {s.name: s for s in Sector.objects.all()}
        sizes = {key(s.name): s for s in Bussines_size.objects.all()}
        categories = {key(c.name): c for c in Category_Emp.objects.all()}
        existing = {(key(b.name), key(b.benefisiariu.name)) for b in
                    Business.objects.filter(benefisiariu__Pnegosiu__program_type__name='KREDITU SUAVE')
                    .select_related('benefisiariu')}

        with transaction.atomic(), audit_paused():
            program_type, _ = TIpu_Programa.objects.get_or_create(name='KREDITU SUAVE')
            faze = Faze.objects.filter(name='KREDITU').first()
            for number, row in enumerate(master, start=1):
                where = f'#{number}'
                report.count('Liña lee')
                person_name, company = text(row['entrepreneur']), text(row['enterprise'])
                if (key(company), key(person_name)) in existing:
                    report.count('Iha ona (salta)')
                    continue
                existing.add((key(company), key(person_name)))
                extra = info.get(key(company), {})
                if not extra:
                    report.warn('La hetan iha sheet "Informasaun FGKS" (la iha tinan/trabalhadór)', where)

                status_raw = key(row.get('status'))
                status = statuses.get('Parado') if status_raw.startswith('parad') else statuses.get('Ativu')
                sex = {'mane': 'Mane', 'm': 'Mane', 'feto': 'Feto', 'f': 'Feto'}.get(key(row.get('sex')))
                person = Benefisiariu.objects.create(name=person_name[:100], sex=sex, phone=phone(row.get('phone')) or None,
                                                     status=status, created_by=user)
                sector = sectors.get(SECTORS.get(key(row.get('category')), ''))
                if text(row.get('category')) and sector is None:
                    report.warn('Setór la koñese', f'{where}: {text(row.get("category"))[:20]}')
                business = Business.objects.create(
                    benefisiariu=person, name=company[:100], idea=text(row.get('activity'))[:100], sector=sector,
                    size=sizes.get(key(row.get('size'))),
                    category=next((c for k, c in categories.items() if k and k in key(company)), None))
                report.count('Benefisiáriu no negósiu kria')

                municipality = places.municipality(row.get('municipality'))
                atauro = key(row.get('municipality')) == 'atauro' and municipality is None
                if atauro:
                    municipality = places.municipality('Dili')
                    report.warn('Munisípiu Atauro la iha iha sistema — rai iha Dili ho nota "Atauro"', where)
                if municipality is None:
                    report.warn('Munisípiu la hetan (lokalizasaun la rai)', f'{where}: {text(row.get("municipality"))[:20]}')
                else:
                    post = places.post(municipality, row.get('post'))
                    village = places.village(post, row.get('village'))
                    aldeia = ' / '.join(filter(None, ['Atauro' if atauro else '', text(row.get('aldeia'))]))
                    if text(row.get('post')) and post is None:
                        report.warn('Postu administrativu la hetan iha sistema', f'{where}: {text(row.get("post"))[:22]}')
                    elif text(row.get('village')) and village is None:
                        report.warn('Suku la hetan iha sistema (rai iha aldeia)', f'{where}: {text(row.get("village"))[:22]}')
                        aldeia = ' / '.join(filter(None, [text(row.get('village')), aldeia]))
                    LocBussiness.objects.create(benefisiariu=person, municipality=municipality, administrativepost=post,
                                                village=village, aldeia=aldeia[:50] or None, created_by=user)

                amount = money(extra.get('approved')) or money(row.get('amount'))
                year_number = year(extra.get('year'))
                if amount is None:
                    report.warn('La iha montante kréditu', where)
                if year_number is None:
                    report.warn('La iha tinan kréditu', where)
                Program.objects.create(
                    benefisiariu=person, program_type=program_type, faze=faze,
                    year=Year.objects.get_or_create(year=year_number)[0] if year_number else None,
                    approved_amount=amount, amount=amount, status=status)
                report.count('Programa Kreditu Suave kria')
                if amount is not None:
                    Finance.objects.create(business=business, budget=float(amount))

                male, female, total = integer(extra.get('male')), integer(extra.get('female')), integer(extra.get('employees'))
                if male is not None or female is not None or total is not None:
                    Employee.objects.create(business=business, male=male or 0, female=female or 0,
                                            total=total if total is not None else (male or 0) + (female or 0))
                revenue, assets = money(extra.get('revenue')), money(extra.get('assets'))
                if revenue is not None or assets is not None:
                    FinancialAssessment.objects.create(business=business, annual_revenue=revenue, total_assets=assets)

                notes = ' | '.join(filter(None, [text(row.get('repayment')), text(extra.get('repay_problem')), text(row.get('notes'))]))
                bank = text(extra.get('bank'))
                CreditInfo.objects.create(
                    business=business, amount=amount, repayment_notes=notes or None,
                    repayment_status=_repayment(extra.get('repay_problem')) or _repayment(row.get('repayment')),
                    recommendation=text(row.get('recommendation')) or None,
                    collateral_amount=money(extra.get('collateral')),
                    approved_by_bank='BNCTL' if key(bank).startswith('approv') else (bank[:200] or None))
            if not options['commit']:
                transaction.set_rollback(True)

        skipped = [s.title for s in workbook.worksheets if key(s.title).startswith('monitorin')]
        if skipped:
            self.stdout.write('SEIDAUK IMPORTA: ' + ', '.join(skipped) + ' (kestionáriu detalladu)')
        for line in report.lines():
            self.stdout.write(line)
        if options['commit']:
            self.stdout.write(self.style.SUCCESS('Dadus rai ona iha baze-dadus.'))
        else:
            self.stdout.write(self.style.WARNING('TESTE DE\'IT — la rai buat ida. Uza --commit atu rai.'))
