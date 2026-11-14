import re

from django import template
from django.utils.safestring import mark_safe

from website.ui_strings import UI

register = template.Library()

_TEXT_NODE = re.compile(r'>([^<>]+)<')
_DYNAMIC = re.compile(r'\s+')


def _lookup(text, lang):
    entry = UI.get(text)
    return entry.get(lang) if entry else None


class UITranslateNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        html = self.nodelist.render(context)
        lang = context.get('ui_lang')
        if not lang or lang == 'tet':
            return html

        def swap(match):
            raw = match.group(1)
            core = raw.strip()
            if not core:
                return match.group(0)
            translated = _lookup(_DYNAMIC.sub(' ', core), lang)
            if translated is None:
                # Testu ho parte dinámiku iha klaran (ezemplu "© 2026 - Versaun : 1.0")
                stripped = _DYNAMIC.sub(' ', re.sub(r'\d{4}', '', core))
                translated = _lookup(stripped, lang)
                if translated is None:
                    return match.group(0)
                year = re.search(r'\d{4}', core)
                if year:
                    translated = translated.replace('&copy; -', f'&copy; {year.group(0)} -')
            lead = raw[:len(raw) - len(raw.lstrip())]
            tail = raw[len(raw.rstrip()):]
            return f'>{lead}{translated}{tail}<'

        return mark_safe(_TEXT_NODE.sub(swap, html))


@register.tag
def uitranslate(parser, token):
    """Tradús testu menu/elementu komún iha blok ne'e tuir lian utilizador nian."""
    nodelist = parser.parse(('enduitranslate',))
    parser.delete_first_token()
    return UITranslateNode(nodelist)
