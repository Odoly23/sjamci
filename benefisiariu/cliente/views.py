import csv, datetime, io
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
from monitoring.models import BusinessImpactMonitoring,  FundUsage, BusinessAsset, CashFlow, FinancialBook
from monitoring.forms import FundUsageForm, BusinessAssetForm, FinancialBookForm, CashFlowForm
from notif.utils import send_notification
from django.contrib.auth.models import User, Group
# ══════════════════════════════════════════════════════════════
#  HELPER
# ══════════════════════════════════════════════════════════════
def _get_my_benef(request):
    try:
        return request.user.benefisiariuuser.benefisiariu
    except Exception:
        return None

def _check_ownership(benef, my_benef):
    return benef == my_benef

def _sync_fund_used(monitoring):
    total_out = monitoring.cashflows.filter(transaction_type='OUT').aggregate(total=Sum('amount'))['total'] or 0
    monitoring.fund_used    = total_out
    monitoring.fund_balance = (monitoring.fund_received or 0) - total_out
    monitoring.save(update_fields=['fund_used', 'fund_balance'])

def sync_monitoring_fund(monitoring):
    total_used = monitoring.cashflows.filter(transaction_type='OUT').aggregate(total=Sum('amount'))['total'] or 0
    monitoring.fund_used = total_used
    monitoring.fund_balance = (monitoring.fund_received - total_used)
    monitoring.save(update_fields=['fund_used', 'fund_balance'])


kni_users =  User.objects.filter(groups__name='KNI').distinct()
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
    
    pedidus = Pedidu.objects.filter(benefisiariu=benef)
    monitorings_data = []
    for business in businesses:
        monitorings = BusinessImpactMonitoring.objects.filter(business=business)
        for monitoring in monitorings:
            monitorings_data.append({
                'monitoring': monitoring,
                'business': business,
                'fund_usages': monitoring.fund_usages.all(),
                'assets': monitoring.assets.all(),
                'cashflows': monitoring.cashflows.all(),
                'financial_books': monitoring.financial_books.all(),
            })
    # ============================================================

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
        'pedidus':        pedidus,
        'monitorings_data': monitorings_data,  # <-- TAMBAHAN
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
            pedidu = Pedidu.objects.create(
                benefisiariu = benef,
                tipo         = tipo,
                assuntu      = assuntu,
                deskrisaun   = deskrisaun,
                status       = 'pending',)
            for user in kni_users:
                send_notification(
                    sender=request.user, receiver=user, title='Pedido Foun', message=f'{benef.name} submete Pedido.', notif_type='PEDIDU', link=f'KNI-Home/pedidu/{pedidu.hashed}/')
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


# ============================================================
# CLIENTE - INPUT FUND USAGE (VERSI BARU)
# ============================================================

@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_fund_usage_add(request, business_id):
    benef = _get_my_benef(request)
    if not benef:
        messages.error(request, 'Konta la iha dadus.')
        return redirect('home')
    business = get_object_or_404(Business, id=business_id, benefisiariu=benef)
    monitoring = BusinessImpactMonitoring.objects.filter(business=business).first()
    
    if not monitoring:
        messages.warning(request, 'La iha monitorizasaun impaktu. Kontaktu staff KNI atu rejistu uluk.')
        return redirect('cliente-dashboard')
    
    if request.method == 'POST':
        form = FundUsageForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Utilizasaun fundus rai ho susesu!")
            return redirect('cliente-dashboard')
    else:
        form = FundUsageForm()
    context = {
        'form': form,
        'monitoring': monitoring,
        'business': business,
        'benef': benef,
        'title': 'Adiciona Utilizasaun Fundus',
        'legend': f"Gastu sira ba negosiu {business.name if business.name else business.idea}",

    }
    return render(request, 'clinte/form_fund_usage.html', context)


@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_asset_add(request, business_id):
    """Cliente adiciona asset ba business id"""
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
    
    business = get_object_or_404(Business, id=business_id, benefisiariu=benef)
    monitoring = BusinessImpactMonitoring.objects.filter(business=business).first()
    
    if not monitoring:
        messages.warning(request, 'La iha monitorizasaun impaktu. Kontaktu staff KNI atu rejistu uluk.')
        return redirect('cliente-dashboard')
    
    if request.method == 'POST':
        form = BusinessAssetForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Asset rai ho susesu!")
            return redirect('cliente-dashboard')
    else:
        form = BusinessAssetForm()
    
    return render(request, 'clinte/form_fund_usage.html', {
        'form': form,
        'monitoring': monitoring,
        'business': business,
        'benef': benef,
        'title': 'Adiciona Asset',
        'legend': f"Gastu sira ba negosiu {business.name if business.name else business.idea}",
    })


@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_cashflow_add(request, business_id):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
    business = get_object_or_404(Business, id=business_id,   benefisiariu=benef)
    monitoring = BusinessImpactMonitoring.objects.filter(business=business).first()
    if not monitoring:
        messages.warning(
            request,
            'La iha monitorizasaun impaktu. Kontaktu staff KNI atu rejistu uluk.'
        )
        return redirect('cliente-dashboard')
    if monitoring.fund_balance <= 0:
        messages.warning(request,  'Deskulpa, osan uza hotu ona.')
        return redirect('cliente-dashboard')

    if request.method == 'POST':
        form = CashFlowForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            if (
                form.cleaned_data['transaction_type'] == 'OUT'
                and amount > monitoring.fund_balance
            ):
                messages.error(request,f'Osan disponivel deit ${monitoring.fund_balance}')
                return render(request,'clinte/form_cashflow.html',
                    {
                        'form': form,
                        'monitoring': monitoring,
                        'business': business,
                        'benef': benef,
                    }
                )

            obj = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            if obj.transaction_type == 'OUT':
                FundUsage.objects.create(
                    monitoring=monitoring,
                    item_name=obj.description,
                    amount=obj.amount,
                    description=f"Auto husi CashFlow {obj.transaction_date}",
                    created_by=request.user
                )
            sync_monitoring_fund(monitoring)
            for user in kni_users:
                send_notification(
                    sender=request.user, receiver=user, title='Utilizasaun Fundus', message=f'{benef.name} submete Utilizasaun.', notif_type='CASHFLOW', link=f'KNI-Home/cashflow/{obj.id}/')
            messages.success(request, 'Fluxu osan rai ho susesu!')
            return redirect('cliente-dashboard')

    else:
        form = CashFlowForm(
            initial={
                'transaction_date': datetime.date.today()
            }
        )
    context = {
        'form': form,
        'monitoring': monitoring,
        'business': business,
        'benef': benef,
        'title': 'Adiciona Fluxu Osan',
        'legend': f'Gastu sira ba negosiu {business.name or business.idea}',
    }

    return render(request, 'clinte/form_cashflow.html', context)


@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_financial_book_add(request, business_id):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
    
    business = get_object_or_404(Business, id=business_id, benefisiariu=benef)
    monitoring = BusinessImpactMonitoring.objects.filter(business=business).first()
    
    if not monitoring:
        messages.warning(request, 'La iha monitorizasaun impaktu. Kontaktu staff KNI atu rejistu ulok.')
        return redirect('cliente-dashboard')
    
    if request.method == 'POST':
        form = FinancialBookForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            for user in kni_users:
                send_notification(
                    sender=request.user, receiver=user, title='Livru Kontabilidade Foun', message=f'{benef.name} submete Livru.',  notif_type='BOOK',  link=f'KNI-Home/financial-book/{book.id}/')
            messages.success(request, "Livru kontabilidade rai ho susesu!")
            return redirect('cliente-dashboard')
    else:
        form = FinancialBookForm()
    
    return render(request, 'clinte/form_financial_book.html', {
        'form': form,
        'monitoring': monitoring,
        'business': business,
        'benef': benef,
        'title': 'Adiciona Livru Kontabilidade',
        'legend': f"Gastu sira ba negosiu {business.name if business.name else business.idea}",
    })


# ============================================================
# CLIENTE - EDIT & DELETE (menggunakan pk)
# ============================================================

@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_fund_usage_edit(request, pk):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
    
    obj = get_object_or_404(FundUsage, id=pk, monitoring__business__benefisiariu=benef)
    
    if request.method == 'POST':
        form = FundUsageForm(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = request.user
            instance.save()
            messages.success(request, "Utilizasaun fundus atualiza ho susesu!")
            return redirect('cliente-dashboard')
    else:
        form = FundUsageForm(instance=obj)
    
    return render(request, 'clinte/form_fund_usage.html', {
        'form': form,
        'obj': obj,
        'benef': benef,
        'title': 'Edita Utilizasaun Fundus',
        'legend': f"Atualiza gastu {obj.item_name}",
    })


@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_fund_usage_delete(request, pk):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
    
    obj = get_object_or_404(FundUsage, id=pk, monitoring__business__benefisiariu=benef)
    
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Utilizasaun fundus hamoos ho susesu!")
        return redirect('cliente-dashboard')
    
    return render(request, 'clinte/confirm_delete.html', {
        'obj': obj,
        'title': 'Hamoos Utilizasaun Fundus',
        'message': f"Boot hakarak hamoos gastu {obj.item_name} ($ {obj.amount})?",
    })


@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_asset_edit(request, pk):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
    
    obj = get_object_or_404(BusinessAsset, id=pk, monitoring__business__benefisiariu=benef)
    
    if request.method == 'POST':
        form = BusinessAssetForm(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = request.user
            instance.save()
            messages.success(request, "Asset atualiza ho susesu!")
            return redirect('cliente-dashboard')
    else:
        form = BusinessAssetForm(instance=obj)
    
    return render(request, 'clinte/form_fund_usage.html', {
        'form': form,
        'obj': obj,
        'benef': benef,
        'title': 'Edita Asset',
        'legend': f"Atualiza asset {obj.asset_name}",
    })


@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_asset_delete(request, pk):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
    
    obj = get_object_or_404(BusinessAsset, id=pk, monitoring__business__benefisiariu=benef)
    
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Asset hamoos ho susesu!")
        return redirect('cliente-dashboard')
    
    return render(request, 'clinte/confirm_delete.html', {
        'obj': obj,
        'title': 'Hamoos Asset',
        'message': f"Boot hakarak hamoos asset {obj.asset_name}?",
    })


@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_cashflow_edit(request, business_id, pk):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
 
    business   = get_object_or_404(Business, id=business_id, benefisiariu=benef)
    monitoring = BusinessImpactMonitoring.objects.filter(business=business).first()
 
    if not monitoring:
        messages.warning(request, 'La iha monitorizasaun impaktu. Kontaktu staff KNI atu rejistu uluk.')
        return redirect('cliente-dashboard')
 
    obj = get_object_or_404(CashFlow, id=pk, monitoring=monitoring)
 
    if request.method == 'POST':
        form = CashFlowForm(request.POST, instance=obj)
        if form.is_valid():
            instance            = form.save(commit=False)
            instance.updated_by = request.user
            instance.save()
            _sync_fund_used(monitoring)  # ← sync setelah edit
            messages.success(request, "Fluxu osan atualiza ho susesu!")
            return redirect('cliente-dashboard')
    else:
        form = CashFlowForm(instance=obj)
 
    return render(request, 'clinte/form_cashflow.html', {
        'form'      : form,
        'obj'       : obj,
        'monitoring': monitoring,
        'business'  : business,
        'benef'     : benef,
        'title'     : 'Edita Fluxu Osan',
        'legend'    : f"Atualiza transasaun {obj.description}",
    })

@login_required
@allowed_users(allowed_roles=['Cliente'])
@transaction.atomic
def cliente_cashflow_delete(request, business_id, pk):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
 
    business   = get_object_or_404(Business, id=business_id, benefisiariu=benef)
    monitoring = BusinessImpactMonitoring.objects.filter(business=business).first()
 
    if not monitoring:
        return redirect('cliente-dashboard')
 
    obj = get_object_or_404(CashFlow, id=pk, monitoring=monitoring)
 
    if request.method == 'POST':
        obj.delete()
        _sync_fund_used(monitoring)  # ← sync setelah delete
        messages.success(request, "Fluxu osan hamoos ho susesu!")
        return redirect('cliente-dashboard')
 
    return render(request, 'Dash/confirm_delete.html', {
        'obj'    : obj,
        'title'  : 'Hamoos Fluxu Osan',
        'message': f"Boot hakarak hamoos transasaun {obj.description} ($ {obj.amount})?",
    })


@login_required
@allowed_users(allowed_roles=['Cliente'])
def cliente_financial_book_delete(request, pk):
    benef = _get_my_benef(request)
    if not benef:
        return redirect('home')
    
    obj = get_object_or_404(FinancialBook, id=pk, monitoring__business__benefisiariu=benef)
    
    if request.method == 'POST':
        if obj.file:
            obj.file.delete()
        obj.delete()
        messages.success(request, "Livru kontabilidade hamoos ho susesu!")
        return redirect('cliente-dashboard')
    
    return render(request, 'clinte/confirm_delete.html', {
        'obj': obj,
        'title': 'Hamoos Livru Kontabilidade',
        'message': f"Boot hakarak hamoos dokumentu {obj.title}?",
    })