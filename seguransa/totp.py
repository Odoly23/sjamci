"""TOTP (RFC 6238) — kódigu dijitu 6 kompativel ho Google/Microsoft Authenticator."""
import base64
import hashlib
import hmac
import secrets
import struct
import time
from urllib.parse import quote

STEP = 30
DIGITS = 6


def new_secret():
    return base64.b32encode(secrets.token_bytes(20)).decode('ascii')


def _code(secret, step):
    key = base64.b32decode(secret, casefold=True)
    digest = hmac.new(key, struct.pack('>Q', step), hashlib.sha1).digest()
    offset = digest[-1] & 0x0F
    number = struct.unpack('>I', digest[offset:offset + 4])[0] & 0x7FFFFFFF
    return str(number % 10 ** DIGITS).zfill(DIGITS)


def current_step(now=None):
    return int((now if now is not None else time.time()) // STEP)


def matching_step(secret, code, last_step=0, window=1, now=None):
    """Fó fali 'step' ne'ebé kódigu ne'e válidu ba, ka None.

    Simu diferensa relójiu ±30 segundu no rekuza kódigu ne'ebé uza tiha ona.
    """
    code = (code or '').strip().replace(' ', '')
    if not secret or len(code) != DIGITS or not code.isdigit():
        return None
    step = current_step(now)
    for candidate in range(step - window, step + window + 1):
        if candidate > last_step and hmac.compare_digest(_code(secret, candidate), code):
            return candidate
    return None


def provisioning_uri(secret, username, issuer='SJAMCI'):
    label = quote(f'{issuer}:{username}')
    return f'otpauth://totp/{label}?secret={secret}&issuer={quote(issuer)}&digits={DIGITS}&period={STEP}'
