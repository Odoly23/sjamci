"""Lian interfase: cookie ida de'it ba pajina públiku, sistema no painel admin."""
from django.conf import settings

from . import i18n


def current_lang(request):
    lang = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    return lang if lang in i18n.CODES else i18n.DEFAULT
