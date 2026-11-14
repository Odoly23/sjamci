from . import i18n
from .lang import current_lang


def ui_language(request):
    """Fó lian atuál no lista bandeira ba template hotu (navbar, admin)."""
    return {'ui_lang': current_lang(request), 'ui_languages': i18n.LANGUAGES}
