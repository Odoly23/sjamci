"""Ferramenta komún ba importasaun dadus husi Excel.

Ficheiru husi diresaun sira dala barak la konsistente (kolunaa muda fatin,
montante hakerek hanesan testu, naran munisípiu ho ortografia oioin), entaun
funsaun sira ne'e tolera variasaun no rejista avizu duké para importasaun.
"""
import difflib
import re
import unicodedata
from collections import Counter, defaultdict
from decimal import Decimal, InvalidOperation


def text(value):
    """Valór sélula hanesan testu moos ('' se mamuk)."""
    if value is None:
        return ''
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    return re.sub(r'\s+', ' ', str(value)).strip()


def key(value):
    """Xave komparasaun: la iha asentu, espasu ka pontuasaun."""
    plain = unicodedata.normalize('NFKD', text(value)).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', plain)


def integer(value):
    raw = text(value)
    if not raw:
        return None
    try:
        return int(float(raw.replace(',', '.')))
    except ValueError:
        return None


def money(value):
    """Lee montante maski hakerek '$. 1,500.00', '$ 1.500,00' ka '2,000,00'."""
    if value is None or value == '':
        return None
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return Decimal(str(value)).quantize(Decimal('0.01'))
    digits = re.sub(r'[^0-9.,]', '', str(value)).strip('.,')
    if not digits:
        return None
    # Separadór ikus ho dijitu 1–2 mak desimál; seluk mak separadór millar
    cents = '00'
    match = re.search(r'[.,](\d{1,2})$', digits)
    if match:
        cents = match.group(1).ljust(2, '0')
        digits = digits[:match.start()]
    whole = re.sub(r'[.,]', '', digits)
    try:
        return Decimal(f'{whole or "0"}.{cents}')
    except InvalidOperation:
        return None


def year(value):
    number = integer(value)
    return number if number and 1975 <= number <= 2100 else None


def phone(value):
    raw = text(value)
    return '' if raw in ('0', '-') else raw[:20]


# ── Lokalizasaun ──────────────────────────────────────────────
_MUNICIPALITY_ALIASES = {
    'oecusse': 'oecusse', 'oecuse': 'oecusse', 'oequse': 'oecusse', 'oecussi': 'oecusse', 'raeoa': 'oecusse',
    'oecusseambeno': 'oecusse', 'regiaoadministrativaespecialoecusseambeno': 'oecusse',
    'liquisa': 'liquica', 'likisa': 'liquica', 'manututo': 'manatuto', 'covalima': 'covalima',
    'kovalima': 'covalima', 'suai': 'covalima', 'lospalos': 'lautem', 'same': 'manufahi',
}


def _municipality_key(name):
    plain = key(name)
    return _MUNICIPALITY_ALIASES.get(plain, plain)


class Places:
    """Buka munisípiu / postu / suku iha baze-dadus tuir naran aproximadu."""

    def __init__(self):
        from custom.models import AdministrativePost, Municipality, Village
        self.municipalities = {_municipality_key(m.name): m for m in Municipality.objects.all()}
        self.posts = defaultdict(dict)
        for post in AdministrativePost.objects.exclude(municipality=None):
            self.posts[post.municipality_id][key(post.name)] = post
        self.villages = defaultdict(dict)
        for village in Village.objects.exclude(administrativepost=None):
            self.villages[village.administrativepost_id][key(village.name)] = village

    def municipality(self, name):
        return self.municipalities.get(_municipality_key(name))

    @staticmethod
    def _closest(options, name):
        """Naran hanesan → hanesan la ho "Vila" → besik liu (erru ortografia ki'ik)."""
        wanted = key(name)
        if not wanted or not options:
            return None
        if wanted in options:
            return options[wanted]
        trimmed = re.sub(r'(vila|villa)$', '', wanted)
        if trimmed and trimmed in options:
            return options[trimmed]
        close = difflib.get_close_matches(trimmed or wanted, list(options), n=1, cutoff=0.84)
        return options[close[0]] if close else None

    def post(self, municipality, name):
        if municipality is None:
            return None
        return self._closest(self.posts[municipality.id], name)

    def village(self, post, name):
        if post is None:
            return None
        return self._closest(self.villages[post.id], name)


class Report:
    """Rezumu importasaun: kontajen no avizu agrupa tuir tipu."""

    def __init__(self):
        self.counts = Counter()
        self.warnings = defaultdict(list)

    def count(self, name, amount=1):
        self.counts[name] += amount

    def warn(self, kind, where):
        self.warnings[kind].append(where)

    def lines(self, examples=5):
        yield 'REZUMU'
        for name, total in self.counts.items():
            yield f'  {name}: {total}'
        if self.warnings:
            yield 'AVIZU (dadus ne\'ebé presiza verifika)'
            for kind, places in sorted(self.warnings.items(), key=lambda item: -len(item[1])):
                sample = '; '.join(places[:examples])
                more = f' … (+{len(places) - examples})' if len(places) > examples else ''
                yield f'  [{len(places)}] {kind}: {sample}{more}'


def non_empty_rows(sheet):
    return [row for row in sheet.iter_rows(values_only=True) if any(cell not in (None, '') for cell in row)]
