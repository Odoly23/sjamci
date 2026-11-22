"""Importa dadus grupu benefisiáriu DNIM husi Excel (sheet ida kada munisípiu).

    python manage.py import_dnim_excel Dadus_Geral_DNIM.xlsx            # teste de'it
    python manage.py import_dnim_excel Dadus_Geral_DNIM.xlsx --commit   # rai
"""
import re

import openpyxl
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from config.import_utils import Places, Report, integer, key, money, non_empty_rows, phone, text, year
from custom.models import IndustryType, Status, Tipu_Apoio, Year
from manufatureira.models import Aktividade, Lokalizasaun, Manufatur, Membro
from seguransa.signals import audit_paused

HEADERS = {
    'name': ('narangrupu',), 'leader': ('naranchefe',), 'phone': ('nokontaktu',), 'place': ('municpio', 'municipio'),
    'industry': ('tipuindustria',), 'support': ('tipuapoio',), 'year': ('tinan',), 'amount': ('valor',),
    'members': ('menbro', 'membro'), 'male': ('mane',), 'female': ('feto',), 'status': ('obs',),
}
INDUSTRY_ALIASES = {'karpintaria': 'Carpintaria', 'carpintaria': 'Carpintaria', 'paderia': 'Padaria',
                    'alfaiate': 'Alfaiate', 'sorutais': 'Soru Tais', 'oficina': 'Oficina'}
SUPPORT_ALIASES = {'subvensoenspublico': 'Subvenções Publicas', 'subvencoespublicas': 'Subvenções Publicas',
                   'subvencoes': 'Subvenções', 'formsaun': 'Formasaun', 'formasaun': 'Formasaun',
                   'kopersaununtlmci': 'Kopersaun UNTL/MCI'}
STATUS_ALIASES = {'ativo': 'Ativu', 'ativu': 'Ativu', 'lao': 'Ativu', 'parado': 'Parado', 'paradu': 'Parado'}


def _columns(header_row):
    found = {}
    for index, cell in enumerate(header_row):
        label = key(cell)
        for field, prefixes in HEADERS.items():
            if field not in found and any(label.startswith(p) for p in prefixes):
                found[field] = index
    return found


class Command(BaseCommand):
    help = 'Importa grupu benefisiáriu DNIM (Manufatureira) husi ficheiru Excel.'

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

        self.report = Report()
        self.places = Places()
        self.user = user
        self.existing = {(key(m.name), getattr(getattr(m, 'lokalidade', None), 'municipality_id', None))
                         for m in Manufatur.objects.select_related('lokalidade')}
        self.created = {}
        self.industries = {key(i.name): i for i in IndustryType.objects.all()}
        self.supports = {key(s.name): s for s in Tipu_Apoio.objects.all()}
        self.statuses = {s.name: s for s in Status.objects.all()}

        with transaction.atomic(), audit_paused():
            for sheet in workbook.worksheets:
                self._sheet(sheet)
            if not options['commit']:
                transaction.set_rollback(True)

        for line in self.report.lines():
            self.stdout.write(line)
        if options['commit']:
            self.stdout.write(self.style.SUCCESS('Dadus rai ona iha baze-dadus.'))
        else:
            self.stdout.write(self.style.WARNING('TESTE DE\'IT — la rai buat ida. Uza --commit atu rai.'))

    def _sheet(self, sheet):
        title = sheet.title.strip()
        rows = non_empty_rows(sheet)
        header_index = next((i for i, row in enumerate(rows) if key(row[0]) == 'no'), None)
        if header_index is None:
            self.report.warn('Sheet la iha liña títulu "NO"', title)
            return
        columns = _columns(rows[header_index])
        if 'name' not in columns:
            self.report.warn('Sheet la iha koluna "Naran Grupu"', title)
            return
        municipality = self.places.municipality(title)
        prefix = ''
        if municipality is None and key(title) == 'atauro':
            municipality = self.places.municipality('Dili')
            prefix = 'Atauro'
            self.report.warn('Munisípiu Atauro la iha iha sistema — rai iha Dili ho nota "Atauro"', title)
        if municipality is None:
            self.report.warn('Munisípiu la hatene (sheet salta)', title)
            return

        def cell(row, field):
            index = columns.get(field)
            return row[index] if index is not None and index < len(row) else None

        for number, row in enumerate(rows[header_index + 1:], start=1):
            name = text(cell(row, 'name'))
            if not name:
                continue
            where = f'{title} #{number}'
            self.report.count('Liña lee')
            identity = (key(name), municipality.id)
            if identity in self.created:
                # Grupu hanesan mosu dala rua iha ficheiru = apoiu tan ba grupu ne'e
                self._activity(self.created[identity], row, cell, where, STATUS_ALIASES.get(key(cell(row, 'status'))))
                self.report.count('Liña repete (aumenta hanesan apoiu ba grupu hanesan)')
                continue
            if identity in self.existing:
                self.report.count('Iha ona iha sistema (salta)')
                continue

            status_raw = key(cell(row, 'status'))
            status_name = STATUS_ALIASES.get(status_raw)
            if status_raw and not status_name:
                self.report.warn('Estadu la koñese', f'{where}: {text(cell(row, "status"))[:20]}')
            manufatur = Manufatur.objects.create(
                name=name[:200], leader_name=text(cell(row, 'leader'))[:200] or '-',
                phone=phone(cell(row, 'phone')) or None, status=status_name or None, created_by=self.user)
            self.created[identity] = manufatur
            self.report.count('Grupu kria')
            if not text(cell(row, 'leader')):
                self.report.warn('La iha naran xefe grupu', where)

            # "Munisípiu, Postu, Suku, Aldeia" — separadór bele "," ka "/"
            parts = [text(p) for p in re.split(r'[,/]', text(cell(row, 'place'))) if text(p)]
            if parts and self.places.municipality(parts[0]) is not None or (parts and key(parts[0]) == key(title)):
                parts = parts[1:]
            post = self.places.post(municipality, parts[0]) if parts else None
            village = self.places.village(post, parts[1]) if len(parts) > 1 else None
            rest = parts[2:] if village else (parts[1:] if post else parts)
            if parts and post is None:
                self.report.warn('Postu administrativu la hetan iha sistema', f'{where}: {parts[0][:25]}')
            elif len(parts) > 1 and village is None:
                self.report.warn('Suku la hetan iha sistema', f'{where}: {parts[1][:25]}')
            aldeia = ' / '.join(filter(None, [prefix] + rest))[:50]
            Lokalizasaun.objects.create(manufatur=manufatur, municipality=municipality, administrativepost=post,
                                        village=village, aldeia=aldeia or None, created_by=self.user)

            male, female, total = integer(cell(row, 'male')), integer(cell(row, 'female')), integer(cell(row, 'members'))
            if male is not None or female is not None or total is not None:
                if total is not None and (male or female) and total != (male or 0) + (female or 0):
                    self.report.warn('Totál membru la hanesan mane + feto (uza mane + feto)', where)
                Membro.objects.create(manufatur=manufatur, male=male or 0, female=female or 0, members=total)
            else:
                self.report.warn('La iha númeru membru', where)

            self._activity(manufatur, row, cell, where, status_name)

    def _lookup(self, cache, model, aliases, raw, label, where):
        if not text(raw):
            return None
        wanted = aliases.get(key(raw), text(raw))[:100]
        found = cache.get(key(wanted))
        if found is None:
            found = model.objects.create(name=wanted)
            cache[key(wanted)] = found
            self.report.count(f'{label} foun kria')
        return found

    def _activity(self, manufatur, row, cell, where, status_name):
        support_raw, industry_raw = cell(row, 'support'), cell(row, 'industry')
        year_number = year(cell(row, 'year'))
        amount = money(cell(row, 'amount'))
        if not (text(support_raw) or text(industry_raw) or year_number or amount):
            return
        if text(cell(row, 'year')) and year_number is None:
            self.report.warn('Tinan la válidu', f'{where}: {text(cell(row, "year"))[:12]}')
        if text(cell(row, 'amount')) and amount is None:
            self.report.warn('Montante la bele lee', f'{where}: {text(cell(row, "amount"))[:16]}')
        if year_number is None:
            self.report.warn('Apoiu la iha tinan', where)
        if amount is None:
            self.report.warn('Apoiu la iha montante', where)
        year_obj = Year.objects.get_or_create(year=year_number)[0] if year_number else None
        Aktividade.objects.create(
            manufatur=manufatur,
            industry_type=self._lookup(self.industries, IndustryType, INDUSTRY_ALIASES, industry_raw, 'Tipu indústria', where),
            support_type=self._lookup(self.supports, Tipu_Apoio, SUPPORT_ALIASES, support_raw, 'Tipu apoiu', where),
            year=year_obj, amount=float(amount) if amount is not None else None,
            status=self.statuses.get(status_name) if status_name else None, created_by=self.user)
        self.report.count('Atividade/apoiu kria')
