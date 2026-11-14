"""Jerasaun password temporáriu ne'ebé seguru.

Sistema la uza ona password default fixu (ezemplu password hanesan ba
utilizador hotu): kada konta foun ka reset simu password aleatóriu ida
ne'ebé hatudu dala ida de'it ba operadór atu entrega ba na'in konta.
"""
import secrets
import string

_SYMBOLS = '@#$%&*+-_!?'
_ALPHABET = string.ascii_letters + string.digits + _SYMBOLS


def temporary_password(length=14):
    """Fó fali password aleatóriu ho letra boot, ki'ik, númeru no símbolu."""
    while True:
        pwd = ''.join(secrets.choice(_ALPHABET) for _ in range(length))
        if (any(c.islower() for c in pwd) and any(c.isupper() for c in pwd)
                and any(c.isdigit() for c in pwd) and any(c in _SYMBOLS for c in pwd)):
            return pwd
