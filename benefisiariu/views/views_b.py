import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo
from .forms import AddressTLForm, AddressOriginForm, PhotoUploadForm
from .decorators import allowed_users


# ── Helper anti-duplikasi ─────────────────────────────────────

def _generate_token(request, session_key):
    """Buat token baru dan simpan ke session (dipanggil saat GET)."""
    token = str(uuid.uuid4())
    request.session[session_key] = token
    return token

def _is_duplicate(request, session_key, posted_token):
    """
    Kembalikan True jika request adalah duplikasi (Back + Submit lagi).
    Jika valid: hapus token dari session agar tidak bisa dipakai lagi.
    """
    saved_token = request.session.get(session_key)
    if not saved_token or saved_token != posted_token:
        return True   # token tidak ada / tidak cocok → duplikasi
    del request.session[session_key]
    return False


# ══════════════════════════════════════════════════════════════
#  ADDRESS TL
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['admin', 'staff', 'KS', 'KNI'])
def AddressTLUpdate(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = AddressTL.objects.filter(benefisiariu=emp).first()

    if request.method == 'POST':
        # ── Cek duplikasi ────────────────────────────────────
        posted_token = request.POST.get('_form_token', '')
        if _is_duplicate(request, 'token_addtl', posted_token):
            messages.warning(request, "Dadus ne'e hotu submete ona.")
            return redirect('dtl-benef', hashid=hashid)

        form = AddressTLForm(request.POST, instance=objects)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.benefisiariu = emp
            instance.user         = request.user
            instance.save()
            messages.success(request, 'Enderesu altera ona.')
            return redirect('dtl-benef', hashid=hashid)
    else:
        form = AddressTLForm(instance=objects)

    context = {
        'hashid':      hashid,
        'form':        form,
        'emp':         emp,
        'form_token':  _generate_token(request, 'token_addtl'),
        'title':       'Altera Enderesu',
        'legend':      'Altera Enderesu',
    }
    return render(request, 'Dash/form_address.html', context)


# ══════════════════════════════════════════════════════════════
#  ADDRESS ORIGIN
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['admin', 'staff', 'KS', 'KNI'])
def AddressOriginUpdate(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = AddressOrigin.objects.filter(benefisiariu=emp).first()

    if request.method == 'POST':
        posted_token = request.POST.get('_form_token', '')
        if _is_duplicate(request, 'token_addori', posted_token):
            messages.warning(request, "Dadus ne'e hotu submete ona.")
            return redirect('dtl-benef', hashid=hashid)

        form = AddressOriginForm(request.POST, instance=objects)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.benefisiariu = emp
            instance.user         = request.user
            instance.save()
            messages.success(request, 'Enderesu origin altera ona.')
            return redirect('dtl-benef', hashid=hashid)
    else:
        form = AddressOriginForm(instance=objects)

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'form_token': _generate_token(request, 'token_addori'),
        'title':      'Altera Enderesu Origin',
        'legend':     'Altera Enderesu Origin',
    }
    return render(request, 'Dash/form.html', context)


# ══════════════════════════════════════════════════════════════
#  PHOTO
# ══════════════════════════════════════════════════════════════

@login_required
def PhotoUpdate(request, hashid):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    obj, _     = Photo.objects.get_or_create(benefisiariu=benef)

    if request.method == 'POST':
        posted_token = request.POST.get('_form_token', '')
        if _is_duplicate(request, 'token_photo', posted_token):
            messages.warning(request, "Foto hotu submete ona.")
            return redirect('dtl-benef', hashid=hashid)

        form = PhotoUploadForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            instance      = form.save(commit=False)
            instance.user = request.user
            instance.save()
            messages.success(request, 'Foto atualiza ona.')
            return redirect('dtl-benef', hashid=hashid)
    else:
        form = PhotoUploadForm(instance=obj)

    context = {
        'form':       form,
        'hashid':     hashid,
        'img':        obj,
        'form_token': _generate_token(request, 'token_photo'),
        'legend':     'Update Photo',
    }
    return render(request, 'Dash/employee_photo.html', context)