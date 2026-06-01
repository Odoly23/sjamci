from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Sum

from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo, Pedidu, BenefisiariuUser
from benefisiariu.forms import BenefisiariuForm, AddressTLForm, AddressOriginForm, PhotoUploadForm
from kni.models import Business, Program, Finance, LocBussiness, Employee
from mpms.models import mpmsEmpresa, mpmsLokalizasaun, mpmsLisensamentu, mpmsKapital, mpmsEmpregador, mpmsMateriaPrima, mpmsAtividade
from config.decorators import allowed_users
import base64
from django.core.files.base import ContentFile


# ══════════════════════════════════════════════════════════════
#  HELPER — ambil benefisiariu dari user yang login
#  + validasi keamanan: pastikan data milik dia sendiri
# ══════════════════════════════════════════════════════════════

def _get_my_benef(request):
    """
    Ambil Benefisiariu milik user yang sedang login.
    Return None kalau user bukan cliente atau belum terhubung.
    """
    try:
        return request.user.benefisiariuuser.benefisiariu
    except Exception:
        return None


def _check_ownership(benef, my_benef):
    """Pastikan data yang diakses milik user sendiri."""
    return benef == my_benef


# ══════════════════════════════════════════════════════════════
#  1. DASHBOARD CLIENTE — lihat semua data milik sendiri
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_dashboard(request):
    group = request.user.groups.all()[0].name
    benef = _get_my_benef(request)
    if not benef:
        messages.error(request, 'Konta kliente la iha dadus. Kontaktu administrador.')
        return redirect('home')

    businesses     = Business.objects.filter(benefisiariu=benef)
    programs       = Program.objects.filter(benefisiariu=benef)
    finances       = Finance.objects.filter(business__in=businesses)
    employees      = Employee.objects.filter(business__in=businesses)
    addtl          = getattr(benef, 'addresstl', None)
    address_origin = getattr(benef, 'addressorigin', None)
    photo          = getattr(benef, 'photo', None)
    location       = LocBussiness.objects.filter(benefisiariu=benef).first()
    total_program  = programs.aggregate(total=Sum('amount'))['total'] or 0

    # Data MPMS jika ada
    empresa      = mpmsEmpresa.objects.filter(benefisiariu=benef).first()
    lokal        = getattr(empresa, 'lokalizasaun', None) if empresa else None
    lisensamentu = getattr(empresa, 'lisensamentu', None) if empresa else None
    kapital      = getattr(empresa, 'kapital', None) if empresa else None
    empregador   = getattr(empresa, 'empregador', None) if empresa else None
    materia      = getattr(empresa, 'materia_prima', None) if empresa else None
    atividades   = empresa.atividades.all() if empresa else []
    pedidus = Pedidu.objects.filter(benefisiariu=benef)


    context = {
        'group': group,
        'benef':          benef,
        'photo':          photo,
        'addtl':          addtl,
        'address_origin': address_origin,
        'location':       location,
        'businesses':     businesses,
        'programs':       programs,
        'finances':       finances,
        'employees':      employees,
        'total_program':  total_program,
        'empresa':        empresa,
        'lokal':          lokal,
        'lisensamentu':   lisensamentu,
        'kapital':        kapital,
        'empregador':     empregador,
        'materia':        materia,
        'pedidus':        pedidus,
        'atividades':     atividades,
        'title':          'Minha Dashboard',
        'legend':         'Dadus Hau Nian',
    }
    return render(request, 'clinte/dash.html', context)


# ══════════════════════════════════════════════════════════════
#  2. UPDATE PERFIL PRIBADI
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_perfil_update(request):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')

    if request.method == 'POST':
        # Hanya izinkan field tertentu yang bisa diupdate cliente
        form = BenefisiariuForm(request.POST, request.FILES, instance=benef)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualiza ho susesu.')
            return redirect('cliente-dashboard')
    else:
        form = BenefisiariuForm(instance=benef)

    # Batasi field yang bisa diedit cliente — hapus field sensitif
    for field in ['status', 'file']:
        if field in form.fields:
            form.fields.pop(field)

    return render(request, 'clinte/form.html', {
        'form':   form,
        'benef':  benef,
        'title':  'Atualiza Perfil',
        'legend': 'Atualiza Dadus Pesoal',
    })


# ══════════════════════════════════════════════════════════════
#  3. UPDATE FOTO
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_photo_update(request):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')

    photo, _ = Photo.objects.get_or_create(benefisiariu=benef)

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Foto atualiza ho susesu.')
            return redirect('cliente-dashboard')
    else:
        form = PhotoUploadForm(instance=photo)

    return render(request, 'clinte/form.html', {
        'form':   form,
        'benef':  benef,
        'title':  'Atualiza Foto',
        'legend': 'Upload Foto Foun',
    })


# ══════════════════════════════════════════════════════════════
#  4. UPDATE ENDERESU TL
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_address_update(request):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')

    obj = AddressTL.objects.filter(benefisiariu=benef).first()

    if request.method == 'POST':
        form = AddressTLForm(request.POST, instance=obj)
        if form.is_valid():
            instance              = form.save(commit=False)
            instance.benefisiariu = benef
            instance.save()
            messages.success(request, 'Enderesu atualiza ho susesu.')
            return redirect('cliente-dashboard')
    else:
        form = AddressTLForm(instance=obj)

    return render(request, 'clinte/form_address.html', {
        'form':   form,
        'benef':  benef,
        'title':  'Atualiza Enderesu',
        'legend': 'Atualiza Enderesu Moris',
    })


# ══════════════════════════════════════════════════════════════
#  5. MINHA PROGRAMA — lihat program milik sendiri
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_programa(request):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')

    programs      = Program.objects.filter(benefisiariu=benef).order_by('-id')
    total_program = programs.aggregate(total=Sum('amount'))['total'] or 0

    return render(request, 'clinte/programa.html', {
        'benef':         benef,
        'programs':      programs,
        'total_program': total_program,
        'title':         'Minha Programa',
        'legend':        'Lista Programa Hau Nian',
    })


# ══════════════════════════════════════════════════════════════
#  6. PEDIDU / KELUHAN — kliente bisa submit permintaan
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_pedidu(request):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')

    TIPO_CHOICES = [
        ('Partisipa Treinamentu', 'Partisipa Treinamentu'),
        ('Pedidu Informasaun',    'Pedidu Informasaun'),
        ('Reclamasaun',           'Reclamasaun'),
        ('seluk',                 'Seluk'),
    ]
    if request.method == 'POST':
        tipo       = request.POST.get('tipo', '').strip()
        assuntu    = request.POST.get('assuntu', '').strip()
        deskrisaun = request.POST.get('deskrisaun', '').strip()

        if not tipo or not assuntu or not deskrisaun:
            messages.warning(request, 'Favor prenxe kampu hotu.')
        else:
            Pedidu.objects.create(
                benefisiariu = benef,
                tipo         = tipo,
                assuntu      = assuntu,
                deskrisaun   = deskrisaun,
                status       = 'pending',
            )
            messages.success(request, 'Pedidu haruka ho susesu. Ekipa sei kontaktu ita.')
            return redirect('cliente-dashboard')
    context = {
        'benef':        benef,
        'tipo_choices': TIPO_CHOICES,
        'title':        'Pedidu / Keluhan',
        'legend':       'Haruka Pedidu Ka Keluhan',
    }
    return render(request, 'clinte/pedido.html', context)


@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_photo_update(request):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')

    photo, _ = Photo.objects.get_or_create(benefisiariu=benef)

    if request.method == 'POST':
        cropped = request.POST.get('cropped_image', '')
        if cropped and cropped.startswith('data:image'):
            # Decode base64 dari cropper.js
            fmt, imgstr = cropped.split(';base64,')
            ext         = fmt.split('/')[-1]  # jpeg
            img_data    = ContentFile(
                base64.b64decode(imgstr),
                name=f'foto_{benef.id}.{ext}'
            )
            photo.image = img_data
            photo.save()
            messages.success(request, 'Foto atualiza ho susesu.')
            return redirect('cliente-dashboard')
        else:
            messages.warning(request, 'Favor crop foto uluk molok rai.')

    return render(request, 'clinte/foto.html', {
        'photo': photo,
        'benef': benef,
        'title': 'Atualiza Foto',
    })