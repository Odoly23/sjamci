"""Importa rejistu empreza MPMS (DNPE) husi Excel (sheet ida kada munisípiu).

    python manage.py import_mpms_excel Dados_MPMS.xlsx             # teste de'it
    python manage.py import_mpms_excel Dados_MPMS.xlsx --commit    # rai

Ficheiru orijinál iha problema ne'ebé komandu ne'e trata:
  * koluna "Naran Diretor" no "Naran Kompania" troka fatin iha sheet balun
    → deteta kada sheet (bele obriga ho --company-first / --director-first);
  * liña balun muda koluna ida ba loos/karuk → aliña fali tuir valór válidu;
  * valór la tuir opsaun formuláriu → rai mamuk no hatudu iha avizu.
"""
import re

import openpyxl
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from benefisiariu.models import Benefisiariu
from config.import_utils import Places, Report, integer, key, money, non_empty_rows, phone, text, year
from custom.models import Bussines_size, Category_Emp, Status, TIPO_ATIVIDADE
from kni.models import Business
from mpms.models import (KAPITAL_RANGE_CHOICES, LISENSAMENTU_CHOICES, LISENSAMENTU_STATUS_CHOICES,
                         MATERIA_ORIGEM_CHOICES, TIPO_RAI_CHOICES, TIPU_FUNDUS_CHOICES, TOTAL_FUNDUS_CHOICES,
                         mpmsEmpregador, mpmsEmpresa, mpmsKapital, mpmsLisensamentu, mpmsLokalizasaun,
                         mpmsMateriaPrima)
from seguransa.signals import audit_paused

HEADERS = [
    ('activity', 'tipoatividade'), ('director', 'narandiretor'), ('director', 'narandireitor'),
    ('company', 'narankompania'), ('company', 'narankomp'), ('sex', 'sexo'), ('education', 'niveledukasaun'),
    ('contact', 'nooffice'), ('municipality', 'munisipio'), ('post', 'postoadm'), ('village', 'suco'),
    ('aldeia', 'aldeia'), ('street', 'ruaavenida'), ('founded', 'tinanhari'),
    ('license_status', 'lisensamentoaktividadeiha'), ('license', 'lisensamentoaktividade'),
    ('land', 'tipopropriodade'), ('capital', 'kapitalinvestimento'), ('fund_type', 'tipufundus'),
    ('fund_total', 'totalfundus'), ('gross', 'totallukru'), ('net', 'lukru'), ('staff', 'totalempregador'),
    ('material_cost', 'kustu'), ('material_origin', 'materiaprima'),
]
CHOICES = {
    'license': {c for c, _ in LISENSAMENTU_CHOICES},
    'license_status': {c for c, _ in LISENSAMENTU_STATUS_CHOICES},
    'land': {c for c, _ in TIPO_RAI_CHOICES},
    'capital': {c for c, _ in KAPITAL_RANGE_CHOICES},
    'fund_type': {c for c, _ in TIPU_FUNDUS_CHOICES},
    'fund_total': {c for c, _ in TOTAL_FUNDUS_CHOICES},
}
ALIASES = {
    'fund_type': {'media': 'medias', 'mediu': 'medias', 'pequena': 'pequenas', 'grande': 'grandes',
                  'homeindustria': 'home_industria__caseiras'},
    'fund_total': {'1___4': '1___5', '1___6': '1___5', '5___19': '6___20', '6___21': '6___20'},
}
SHIFTABLE = ['license', 'license_status', 'land', 'capital', 'fund_type', 'fund_total']
EDUCATION = {'primaria': 'primaria', 'presecundaria': 'pre_secundaria', 'secundaria': 'secundaria',
             'liseneiatura': 'lisensiatura', 'lisensiatura': 'lisensiatura', 'licenciatura': 'lisensiatura',
             'master': 'mestrado', 'mestrado': 'mestrado', 'doutoramento': 'doutoramento'}
SIZE = {'mikro': 'Micro', 'home_industria__caseiras': 'Micro', 'pequenas': 'Small', 'medias': 'Medium'}
COMPANY_WORDS = re.compile(
    r'\b(lda|unip\w*|enin|oficina|ofisina|bengkel|salon|salaun|barber\w*|motor|kios|loja|toko|foto\s?cop\w*|'
    r'print\w*|rental|karpintaria|carpintaria|mobil\w*|bata[ck]o|alfa[iy]ate|tais|grupu|grupo|ko+perativa|'
    r'cooperativa|pad[ae]ria|restaurante|servi\w*|store|shop|studio|electr\w*|comp\w*|unipessoal|uni)\b|\d', re.I)


def _choice(field, raw):
    value = text(raw).lower()
    if not value:
        return ''
    if value in CHOICES[field]:
        return value
    alias = ALIASES.get(field, {}).get(value) or ALIASES.get(field, {}).get(key(value))
    return alias if alias in CHOICES[field] else None


def _pretty(slug):
    return re.sub(r'[_\s]+', ' ', slug).strip().title()


class Command(BaseCommand):
    help = 'Importa rejistu empreza MPMS husi ficheiru Excel DNPE.'

    def add_arguments(self, parser):
        parser.add_argument('file')
        parser.add_argument('--commit', action='store_true', help='Rai iha baze-dadus (se la iha, teste de\'it)')
        parser.add_argument('--user', help='Username ne\'ebé rejista hanesan kriadór')
        parser.add_argument('--company-first', default='', help='Sheet (separa ho vírgula) ne\'ebé koluna dahuluk mak naran kompania')
        parser.add_argument('--director-first', default='', help='Sheet ne\'ebé koluna dahuluk mak naran diretór')

    def handle(self, *args, **options):
        try:
            workbook = openpyxl.load_workbook(options['file'], read_only=True, data_only=True)
        except Exception as exc:  # noqa: BLE001
            raise CommandError(f'La konsege loke ficheiru: {exc}')
        self.user = None
        if options['user']:
            self.user = get_user_model().objects.filter(username=options['user']).first()
            if self.user is None:
                raise CommandError('Utilizador la eziste.')
        self.force = {key(n): True for n in options['company_first'].split(',') if n.strip()}
        self.force.update({key(n): False for n in options['director_first'].split(',') if n.strip()})

        self.report = Report()
        self.places = Places()
        self.status = Status.objects.filter(pk=1).first()
        self.activities = {key(a.name): a for a in TIPO_ATIVIDADE.objects.all()}
        self.categories = {key(c.name): c for c in Category_Emp.objects.all()}
        self.sizes = {s.name: s for s in Bussines_size.objects.all()}
        self.people = {}
        self.existing = {
            (key(e.company_name), key(e.benefisiariu.name), getattr(getattr(e, 'lokalizasaun', None), 'municipality_id', None))
            for e in mpmsEmpresa.objects.select_related('benefisiariu', 'lokalizasaun')}
        self.orientation = []

        with transaction.atomic(), audit_paused():
            for sheet in workbook.worksheets:
                if key(sheet.title) != 'geral':
                    self._sheet(sheet)
            if not options['commit']:
                transaction.set_rollback(True)

        self.stdout.write('ORDEN NARAN KADA SHEET (verifika ezemplu)')
        for line in self.orientation:
            self.stdout.write('  ' + line)
        for line in self.report.lines():
            self.stdout.write(line)
        if options['commit']:
            self.stdout.write(self.style.SUCCESS('Dadus rai ona iha baze-dadus.'))
        else:
            self.stdout.write(self.style.WARNING('TESTE DE\'IT — la rai buat ida. Uza --commit atu rai.'))

    # ── Lee sheet ─────────────────────────────────────────────
    def _columns(self, rows):
        header_index = next((i for i, row in enumerate(rows) if any(key(c) == 'tipoatividade' for c in row)), None)
        if header_index is None:
            return None, None
        columns = {}
        for index, cell in enumerate(rows[header_index]):
            label = key(cell)
            if not label:
                continue
            for field, prefix in HEADERS:
                if label.startswith(prefix) and field not in columns:
                    columns[field] = index
                    break
        # "Total Empregador" kobre koluna 4: nasionál mane/feto, internasionál mane/feto
        if 'staff' not in columns and 'material_cost' in columns:
            columns['staff'] = columns['material_cost'] - 4
        return header_index, columns

    def _sheet(self, sheet):
        title = sheet.title.strip()
        rows = non_empty_rows(sheet)
        header_index, columns = self._columns(rows)
        if columns is None or 'director' not in columns or 'company' not in columns:
            self.report.warn('Sheet la iha títulu ne\'ebé koñese (salta)', title)
            return
        municipality = self.places.municipality(title)
        if municipality is None:
            self.report.warn('Munisípiu la hatene (sheet salta)', title)
            return
        first, second = sorted((columns['director'], columns['company']))
        data = [row for row in rows[header_index + 1:]
                if text(row[columns['activity']] if columns['activity'] < len(row) else '')
                and key(row[columns['activity']]) not in ('nasional', 'mane', 'internasional')]

        # Koluna ida-ne'ebé mak naran kompania? (títulu la fiar iha sheet balun)
        def score(index):
            return sum(1 for row in data if index < len(row) and COMPANY_WORDS.search(text(row[index])))
        header_says_company_first = columns['company'] == first
        company_first = header_says_company_first
        a, b = score(first), score(second)
        if abs(a - b) >= max(3, len(data) * 0.08):
            company_first = a > b
        if key(title) in self.force:
            company_first = self.force[key(title)]
        company_col, director_col = (first, second) if company_first else (second, first)
        note = '' if company_first == header_says_company_first else '  ← DIFERENTE husi títulu'
        sample = next((row for row in data if text(row[company_col]) and text(row[director_col])), None)
        example = f' | ez.: kompania="{text(sample[company_col])[:22]}", diretór="{text(sample[director_col])[:22]}"' if sample else ''
        self.orientation.append(f'{title}: koluna dahuluk = {"kompania" if company_first else "diretór"}{note}{example}')

        for number, row in enumerate(data, start=1):
            self._row(title, number, row, columns, municipality, company_col, director_col)

    # ── Liña ida ──────────────────────────────────────────────
    def _row(self, title, number, row, columns, municipality, company_col, director_col):
        where = f'{title} #{number}'
        report = self.report
        report.count('Liña lee')

        def cell(field, shift=0):
            index = columns.get(field)
            if index is None:
                return None
            index += shift
            return row[index] if 0 <= index < len(row) else None

        company = text(row[company_col] if company_col < len(row) else '')
        director = text(row[director_col] if director_col < len(row) else '')
        if company in ('', '?', '0', '-'):
            company = ''
        if director in ('', '?', '0', '-'):
            director = ''
        if not company and not director:
            report.warn('La iha naran kompania no diretór (salta)', where)
            return
        if not director:
            report.warn('La iha naran diretór (uza naran kompania)', where)
            director = company
        if not company:
            report.warn('La iha naran kompania (uza naran diretór)', where)
            company = director

        identity = (key(company), key(director), municipality.id)
        if identity in self.existing:
            report.count('Iha ona (salta)')
            return
        self.existing.add(identity)

        # Aliña fali blok lisensa→fundus se liña muda koluna ida
        def valid(shift):
            return sum(1 for f in SHIFTABLE if _choice(f, cell(f, shift)))
        shift = max((0, -1, 1), key=valid)
        if shift and valid(shift) > valid(0):
            report.warn('Liña muda koluna (aliña fali automátiku)', where)
        else:
            shift = 0

        def choice(field, label):
            raw = cell(field, shift)
            value = _choice(field, raw)
            if value is None:
                report.warn(f'{label}: valór la tuir opsaun (rai mamuk)', f'{where}: {text(raw)[:22]}')
            return value or None

        sex = {'mane': 'Mane', 'feto': 'Feto'}.get(key(cell('sex')))
        if not sex:
            report.warn('Sexu la rejista', where)
        education_raw = key(cell('education'))
        education = EDUCATION.get(education_raw, 'seluk' if education_raw else None)
        contact = text(cell('contact'))
        contact = '' if contact in ('0', '-') else contact
        email = contact if '@' in contact else ''

        person_key = (key(director), key(phone(contact)))
        person = self.people.get(person_key)
        if person is None:
            person = Benefisiariu.objects.filter(name__iexact=director, phone=phone(contact)).first() if contact else None
        if person is None:
            person = Benefisiariu.objects.create(
                name=director[:100], sex=sex, nivel_edukasaun=education, phone=phone(contact) or None,
                email_website=email[:200] or None, status=self.status, created_by=self.user)
            report.count('Benefisiáriu (diretór) kria')
        self.people[person_key] = person

        slugs = text(cell('activity')).split()
        activity_name = _pretty(slugs[0])[:100]
        activity = self.activities.get(key(activity_name))
        if activity is None:
            activity = TIPO_ATIVIDADE.objects.create(name=activity_name)
            self.activities[key(activity_name)] = activity
            report.count('Tipu atividade foun kria')

        fund_type = choice('fund_type', 'Tipu fundus')
        category = next((c for k, c in self.categories.items() if k and k in key(company)), None)
        business = Business.objects.create(
            benefisiariu=person, name=company[:100], idea=', '.join(_pretty(s) for s in slugs)[:100],
            category=category, size=self.sizes.get(SIZE.get(fund_type or '')))
        founded = year(cell('founded'))
        if text(cell('founded')) and founded is None:
            report.warn('Tinan hari la válidu', f'{where}: {text(cell("founded"))[:12]}')
        empresa = mpmsEmpresa.objects.create(
            benefisiariu=person, business=business, company_name=company[:200], tipo_atividade=activity,
            tinan_hari=str(founded) if founded else None, created_by=self.user)
        report.count('Empreza kria')

        post = self.places.post(municipality, cell('post'))
        village = self.places.village(post, cell('village'))
        aldeia = text(cell('aldeia'))
        aldeia = '' if aldeia == '0' else aldeia
        if text(cell('post')) not in ('', '0') and post is None:
            report.warn('Postu administrativu la hetan iha sistema', f'{where}: {text(cell("post"))[:22]}')
        elif text(cell('village')) not in ('', '0') and village is None:
            report.count('Suku la hetan iha sistema (rai hanesan testu iha aldeia)')
            aldeia = ' / '.join(filter(None, [text(cell('village')), aldeia]))
        street = text(cell('street'))
        mpmsLokalizasaun.objects.create(
            empresa=empresa, municipality=municipality, administrativepost=post, village=village,
            aldeia=aldeia[:100] or None, rua_avenida=None if street in ('', '0') else street[:200])

        mpmsLisensamentu.objects.create(
            empresa=empresa, lisensamentu=choice('license', 'Lisensamentu'),
            lisensamentu_status=choice('license_status', 'Estadu lisensa'), tipo_rai=choice('land', 'Tipu rai'))

        def amount(field, label):
            raw = cell(field, shift)
            value = money(raw)
            if text(raw) and value is None:
                report.warn(f'{label}: montante la bele lee', f'{where}: {text(raw)[:16]}')
            return value
        mpmsKapital.objects.create(
            empresa=empresa, kapital_investimento=choice('capital', 'Kapitál investimentu'), tipu_fundus=fund_type,
            total_fundus=choice('fund_total', 'Totál fundus'),
            lukru_brutu_mes=amount('gross', 'Lukru brutu'), lukru_likidu_mes=amount('net', 'Lukru líkidu'))

        staff = columns.get('staff')
        numbers = [integer(row[staff + shift + i]) if staff is not None and 0 <= staff + shift + i < len(row) else None
                   for i in range(4)]
        numbers = [n if n is not None and 0 <= n < 5000 else 0 for n in numbers]
        mpmsEmpregador.objects.create(
            empresa=empresa, nasional_mane=numbers[0], nasional_feto=numbers[1],
            internasional_mane=numbers[2], internasional_feto=numbers[3])

        cost = amount('material_cost', 'Kustu matéria-prima')
        origin = text(cell('material_origin', shift)).lower()
        origin = origin if origin in {c for c, _ in MATERIA_ORIGEM_CHOICES} else None
        if cost is not None or origin:
            mpmsMateriaPrima.objects.create(empresa=empresa, kustu=cost, origem=origin)
