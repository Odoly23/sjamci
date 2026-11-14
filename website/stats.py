"""Estatístika agregadu ba pajina públiku — la inklui dadus pesoál."""
import unicodedata

from django.core.cache import cache
from django.db.models import Count
from django.utils import timezone

from benefisiariu.models import Benefisiariu
from kni.models import Business, Program

CACHE_SECONDS = 600

# Naran munisípiu iha baze-dadus → kódigu ISO iha mapa
_ISO = {
    'aileu': 'TL-AL', 'ainaro': 'TL-AN', 'baucau': 'TL-BA', 'bobonaro': 'TL-BO', 'covalima': 'TL-CO',
    'dili': 'TL-DI', 'atauro': 'TL-DI', 'ermera': 'TL-ER', 'lautem': 'TL-LA', 'liquica': 'TL-LI',
    'manatuto': 'TL-MT', 'manufahi': 'TL-MF', 'viqueque': 'TL-VI',
}
_SEX = {'mane': 'male', 'm': 'male', 'feto': 'female', 'f': 'female'}


def _plain(text):
    text = unicodedata.normalize('NFKD', text or '').encode('ascii', 'ignore').decode().lower()
    return ''.join(ch for ch in text if ch.isalpha())


def municipality_iso(name):
    key = _plain(name)
    if 'cusse' in key or 'oecus' in key or 'ambeno' in key:
        return 'TL-OE'
    return _ISO.get(key)


def available_years():
    years = Program.objects.exclude(year=None).values_list('year__year', flat=True).distinct()
    return sorted({y for y in years if y}, reverse=True)


def compute(year=None):
    programs = Program.objects.exclude(benefisiariu=None)
    benefs = Benefisiariu.objects.all()
    if year:
        programs = programs.filter(year__year=year)
        benefs = benefs.filter(Pnegosiu__year__year=year)
    benefs = benefs.distinct()
    benef_ids = benefs.values('id')

    # Benefisiáriu ida konta dala ida de'it kada munisípiu
    by_mun = {}
    unlocated = 0
    rows = benefs.values('locnegosiu__municipality__name').annotate(n=Count('id', distinct=True))
    for row in rows:
        name = row['locnegosiu__municipality__name']
        if not name:
            unlocated += row['n']
            continue
        iso = municipality_iso(name)
        entry = by_mun.setdefault(iso or name, {'iso': iso, 'name': name, 'count': 0})
        entry['count'] += row['n']
        if _plain(name) == 'atauro':
            entry['name'] = 'Dili'
        if iso == 'TL-OE':
            entry['name'] = 'Oe-Cusse Ambeno'
    municipalities = sorted(by_mun.values(), key=lambda item: (-item['count'], item['name']))

    by_program = [
        {'name': row['program_type__name'] or '—', 'count': row['n']}
        for row in programs.values('program_type__name').annotate(n=Count('benefisiariu', distinct=True)).order_by('-n')
    ]

    sex = {'male': 0, 'female': 0, 'unknown': 0}
    for row in benefs.values('sex').annotate(n=Count('id', distinct=True)):
        sex[_SEX.get((row['sex'] or '').strip().lower(), 'unknown')] += row['n']

    # Tendénsia tinan-tinan la depende ba filtru tinan
    by_year = [
        {'year': row['year__year'], 'count': row['n']}
        for row in Program.objects.exclude(year=None).exclude(benefisiariu=None)
        .values('year__year').annotate(n=Count('benefisiariu', distinct=True)).order_by('year__year')
    ]

    return {
        'year': year,
        'totals': {
            'beneficiaries': benefs.count(),
            'businesses': Business.objects.filter(benefisiariu__in=benef_ids).count(),
            'municipalities': len([m for m in municipalities if m['count']]),
            'programs': programs.count(),
        },
        'municipalities': municipalities,
        'unlocated': unlocated,
        'by_program': by_program,
        'by_sex': sex,
        'by_year': by_year,
        'generated_at': timezone.localtime().strftime('%d/%m/%Y %H:%M'),
    }


def get(year=None):
    key = f'website-stats-{year or "all"}'
    data = cache.get(key)
    if data is None:
        data = compute(year)
        cache.set(key, data, CACHE_SECONDS)
    return data
