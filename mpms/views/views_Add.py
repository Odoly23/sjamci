import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.conf import settings

from config.decorators import allowed_users

from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin
from benefisiariu.forms import BenefisiariuForm, AddressTLForm, AddressOriginForm

from kni.models import Business, Program, Finance, LocBussiness, Employee
from kni.forms import BusinessKNIForm, ProgramKNIForm, FinanceKNIForm, LocBusinessKNIForm, EmployeeKNIForm

from mpms.models import (
    mpmsEmpresa, mpmsLokalizasaun, mpmsLisensamentu,
    mpmsKapital, mpmsEmpregador, mpmsMateriaPrima, mpmsAtividade
)
from mpms.forms import (
    MpmsEmpresaForm, MpmsLokalizasaunForm, MpmsLisensamentuForm, BusinessMPMSForm,
    MpmsKapitalForm, MpmsEmpregadorForm, MpmsMateriaPrimaForm, MpmsAtividadeForm, ProgramMPMSForm
)

from custom.models import Status, TIpu_Programa


# ══════════════════════════════════════════════════════════════
#  1. ADD BENEFISIARIU
# ══════════════════════════════════════════════════════════════
def _get_empresa_and_benef(hashid):
    empresa = get_object_or_404(mpmsEmpresa, hashed=hashid)
    return empresa, empresa.benefisiariu

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def add_benef_mpms(request):
    group = request.user.groups.all()[0].name

    if request.method == 'POST':
        form = BenefisiariuForm(request.POST, request.FILES)
        if form.is_valid():
            name  = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')

            if phone and Benefisiariu.objects.filter(phone=phone).exists():
                messages.warning(request, "Benefisiariu ho telefone hanesan iha ona.")
                return redirect('add-benef-mpms')

            obj            = form.save(commit=False)
            obj.created_by = request.user
            obj.status     = Status.objects.get(pk=1)
            obj.save()

            messages.success(request, "Dadus Benefisiariu rai ho susesu.")
            return redirect('mpms-business-add', hashid=obj.hashed)
    else:
        form = BenefisiariuForm()

    context = {
        'group':  group,
        'form':   form,
        'title':  'Registo Dados',
        'legend': 'Registo Dados Benefisiariu MPMS',
    }
    return render(request, 'MPMS/form.html', context)


# ══════════════════════════════════════════════════════════════
#  2. EDIT BENEFISIARIU
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def edit_benef_mpms(request, hashid):
    group = request.user.groups.all()[0].name if request.user.groups.exists() else None
    obj   = get_object_or_404(Benefisiariu, hashed=hashid)

    if request.method == 'POST':
        form = BenefisiariuForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            benef            = form.save(commit=False)
            benef.updated_by = request.user
            benef.updated_at = datetime.datetime.now()
            benef.save()
            messages.success(request, "Dadus Benefisiariu atualiza ho susesu.")
            return redirect('mpms-detail', hashid=benef.hashed)
    else:
        form = BenefisiariuForm(instance=obj)

    context = {
        'group':  group,
        'form':   form,
        'obj':    obj,
        'title':  'Edit Dados Benefisiariu',
        'legend': 'Atualiza Dados Benefisiariu MPMS',
    }
    return render(request, 'MPMS/form.html', context)


# ══════════════════════════════════════════════════════════════
#  3. ALTERA ENDERESU TL
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
def AddressTLUpdate_mpms(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = AddressTL.objects.filter(benefisiariu=emp).first()

    if request.method == 'POST':
        form = AddressTLForm(request.POST, instance=objects)
        if form.is_valid():
            instance              = form.save(commit=False)
            instance.benefisiariu = emp
            instance.save()
            messages.success(request, "Enderesu atualiza ona.")
            return redirect('mpms-detail', hashid=hashid)
    else:
        form = AddressTLForm(instance=objects)

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Altera Enderesu',
        'legend': 'Altera Enderesu',
    }
    return render(request, 'MPMS/form_addressBnf.html', context)


# ══════════════════════════════════════════════════════════════
#  4. ALTERA ENDERESU ORIGIN
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
def AddressOriginUpdate_mpms(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = AddressOrigin.objects.filter(benefisiariu=emp).first()

    if request.method == 'POST':
        form = AddressOriginForm(request.POST, instance=objects)
        if form.is_valid():
            instance              = form.save(commit=False)
            instance.benefisiariu = emp
            instance.save()
            messages.success(request, "Enderesu origin atualiza ona.")
            return redirect('mpms-detail', hashid=hashid)
    else:
        form = AddressOriginForm(instance=objects)

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Altera Enderesu Origin',
        'legend': 'Altera Enderesu Origin',
    }
    return render(request, 'MPMS/form_origin.html', context)


# ══════════════════════════════════════════════════════════════
#  5. LOKASAUN NEGOSIU
#     Simpan LocBussiness → sync ke mpmsLokalizasaun otomatis
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def Localidade_Add_mpms(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = LocBussiness.objects.filter(benefisiariu=emp).first()

    if request.method == 'POST':
        form = LocBusinessKNIForm(request.POST, instance=objects)
        if form.is_valid():
            instance              = form.save(commit=False)
            instance.benefisiariu = emp
            instance.save()

            # ── Sync ke mpmsLokalizasaun semua Empresa ────────
            empresas = mpmsEmpresa.objects.filter(benefisiariu=emp)
            for empresa in empresas:
                mpmsLokalizasaun.objects.update_or_create(
                    empresa=empresa,
                    defaults={
                        'municipality':       instance.municipality,
                        'administrativepost': instance.administrativepost,
                        'village':            instance.village,
                        'aldeia':             instance.aldeia,
                        'latitude':           instance.latitude,
                        'longitude':          instance.longitude,
                        'area_polygon':       instance.area_polygon,
                    }
                )

            messages.success(request, "Lokasaun negosiu atualiza ona.")
            return redirect('mpms-detail', hashid=hashid)
    else:
        form = LocBusinessKNIForm(instance=objects)

    context = {
        'hashid':       hashid,
        'form':         form,
        'emp':          emp,
        'MAPBOX_TOKEN': settings.MAPBOX_TOKEN,
        'title':        'Lokasaun Negosiu',
        'legend':       'Lokasaun Negosiu',
    }
    return render(request, 'mpms/forms_address.html', context)


# ══════════════════════════════════════════════════════════════
#  6. REJISTU NEGOSIU
#     Simpan Business → otomatis buat mpmsEmpresa
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def Business_Add_mpms(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)

    if request.method == 'POST':
        form = BusinessMPMSForm(request.POST)
        if form.is_valid():
            business              = form.save(commit=False)
            business.benefisiariu = emp
            business.save()

            # ── Otomatis buat mpmsEmpresa ─────────────────────
            mpmsEmpresa.objects.get_or_create(
                benefisiariu=emp,
                business=business,
                defaults={
                    'company_name': business.name or emp.name,
                }
            )

            messages.success(request, "Negosiu no Empresa MPMS rai ho susesu.")
            return redirect('mpms-program-add', hashid=hashid)
    else:
        form = BusinessMPMSForm()

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Rejistu Negosiu',
        'legend': 'Rejistu Negosiu MPMS',
    }
    return render(request, 'MPMS/form.html', context)


# ══════════════════════════════════════════════════════════════
#  EDIT NEGOSIU
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def Business_Edit_mpms(request, hashid):
    business = get_object_or_404(Business, hashed=hashid)
    if request.method == 'POST':
        form = BusinessKNIForm(request.POST, instance=business)
        if form.is_valid():
            old_name = business.name
            obj      = form.save()
            if old_name != obj.name:
                mpmsEmpresa.objects.filter(business=obj).update(company_name=obj.name)
            messages.success(request, "Negosiu atualiza ho susesu.")
            return redirect('mpms-detail', hashid=obj.benefisiariu.hashed)
    else:
        form = BusinessKNIForm(instance=business)

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    business,
        'title':  'Altera Negosiu',
        'legend': 'Altera Negosiu MPMS',
    }
    return render(request, 'MPMS/form.html', context)


# ══════════════════════════════════════════════════════════════
#  7. REJISTU PROGRAMA
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def Program_Add_mpms(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)

    if request.method == 'POST':
        form = ProgramMPMSForm(request.POST)
        if form.is_valid():
            obj              = form.save(commit=False)
            obj.benefisiariu = emp
            obj.program_type = TIpu_Programa.objects.get(name='MPMS')
            obj.status_id    = 1
            obj.save()

            # ── Update Finance budget ─────────────────────────
            total_budget = Program.objects.filter(
                benefisiariu=emp,
                program_type__name='MPMS'
            ).aggregate(total=Sum('amount'))['total'] or 0

            for b in Business.objects.filter(benefisiariu=emp):
                Finance.objects.update_or_create(
                    business=b,
                    defaults={'budget': total_budget}
                )

            # ── Sync ke mpmsAtividade ─────────────────────────
            empresas = mpmsEmpresa.objects.filter(benefisiariu=emp)
            for empresa in empresas:
                mpmsAtividade.objects.get_or_create(
                    empresa=empresa,
                    year=obj.year,
                    defaults={
                        'tipu_apoio':  obj.t_apoiu.name if obj.t_apoiu else None,
                        'amount':      obj.amount,
                        'status':      obj.status,
                    }
                )

            messages.success(request, "Dados Guardado Ho Suseso.")
            return redirect('mpms-detail', hashid=hashid)
    else:
        form = ProgramMPMSForm()

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Rejistu Programa MPMS',
        'legend': 'Programa MPMS Foun',
    }
    return render(request, 'MPMS/form.html', context)


# ══════════════════════════════════════════════════════════════
#  8. TRABALHADORES
#     Simpan Employee → sync ke mpmsEmpregador otomatis
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def Employee_Add_mpms(request, hashid):
    emp        = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = EmployeeKNIForm(request.POST)
        if form.is_valid():
            employee = form.save()

            # ── Sync ke mpmsEmpregador ────────────────────────
            empresa = mpmsEmpresa.objects.filter(
                business=employee.business
            ).first()

            if empresa:
                mpmsEmpregador.objects.update_or_create(
                    empresa=empresa,
                    defaults={
                        'nasional_mane': employee.male   or 0,
                        'nasional_feto': employee.female or 0,
                    }
                )

            messages.success(request, "Trabalhadores no Empregador rai ho susesu.")
            return redirect('mpms-detail', hashid=hashid)
    else:
        form = EmployeeKNIForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Rejistu Trabalhadores',
        'legend': 'Trabalhadores Foun',
    }
    return render(request, 'MPMS/form.html', context)


# ══════════════════════════════════════════════════════════════
#  9. FINANSIAMENTO
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def Finance_Add_mpms(request, hashid):
    emp        = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = FinanceKNIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Finansiamento rai ho susesu.")
            return redirect('mpms-detail', hashid=hashid)
    else:
        form = FinanceKNIForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Rejistu Finansiamento',
        'legend': 'Finansiamento Foun',
    }
    return render(request, 'MPMS/form.html', context)


# ══════════════════════════════════════════════════════════════
#  10. DETAIL PAGE
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['mpms'])
def mpms_detail(request, hashid):
    # Coba via Benefisiariu dulu (dari add_benef_mpms)
    benef   = Benefisiariu.objects.filter(hashed=hashid).first()
    empresa = None

    if benef:
        empresa = mpmsEmpresa.objects.filter(benefisiariu=benef).first()
    else:
        empresa = mpmsEmpresa.objects.filter(hashed=hashid).first()

    if not empresa:
        messages.warning(request, "Empresa seidauk hari, rai Negosiu uluk.")
        return redirect('add-benef-mpms')

    context = {
        'empresa': empresa,
        'title':   'Detail Empresa MPMS',
        'legend':  'Detail Empresa',
    }
    return render(request, 'mpms/detail.html', context)


# ══════════════════════════════════════════════════════════════
#  11. MPMS LOKALIZASAUN (input langsung)
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def mpms_lokalizasaun_create(request, hashid):
    empresa, benef = _get_empresa_and_benef(hashid)
    instance       = getattr(empresa, 'lokalizasaun', None)
 
    if request.method == 'POST':
        form = MpmsLokalizasaunForm(request.POST, instance=instance)
        if form.is_valid():
            obj         = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, 'Lokalizasaun konsege rai.')
            return redirect('mpms-detail', hashid=benef.hashed)
    else:
        form = MpmsLokalizasaunForm(instance=instance)
 
    return render(request, 'mpms/forms_address.html', {
        'form':    form,
        'empresa': empresa,
        'benef':   benef,
        'title':   'Lokalizasaun Empresa',
        'legend':  'Input Lokalizasaun',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  LISENSAMENTU
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def mpms_lisensamentu_create(request, hashid):
    empresa, benef = _get_empresa_and_benef(hashid)
    instance       = getattr(empresa, 'lisensamentu', None)
 
    if request.method == 'POST':
        form = MpmsLisensamentuForm(request.POST, instance=instance)
        if form.is_valid():
            obj         = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, 'Lisensamentu konsege rai.')
            return redirect('mpms-detail', hashid=benef.hashed)
    else:
        form = MpmsLisensamentuForm(instance=instance)
 
    return render(request, 'mpms/forms.html', {
        'form':    form,
        'empresa': empresa,
        'benef':   benef,
        'title':   'Lisensamentu',
        'legend':  'Input Lisensamentu',
    })

@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def mpms_empresa_edit(request, hashid):
    group = request.user.groups.all()[0].name
    empresa, benef = _get_empresa_and_benef(hashid)
    if request.method == 'POST':
        form = MpmsEmpresaForm(request.POST, instance=empresa)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.benefisiariu = benef
            if not obj.business:
                obj.business = empresa.business
            obj.save()
            messages.success(request, 'Dadus Empresa atualiza ho susesu.')
            return redirect('mpms-detail', hashid=benef.hashed)
    else:
        form = MpmsEmpresaForm(instance=empresa)
    context = {
        'group':group,
        'form': form,
        'empresa': empresa,
        'benef': benef,
        'title': 'Empresa MPMS',
        'legend': 'Atualiza Dadus Empresa',
    }
    return render(request, 'mpms/forms.html', context)
 
 
# ══════════════════════════════════════════════════════════════
#  KAPITAL
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def mpms_kapital_create(request, hashid):
    empresa, benef = _get_empresa_and_benef(hashid)
    instance       = getattr(empresa, 'kapital', None)
 
    if request.method == 'POST':
        form = MpmsKapitalForm(request.POST, instance=instance)
        if form.is_valid():
            obj         = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, 'Kapital konsege rai.')
            return redirect('mpms-detail', hashid=benef.hashed)
    else:
        form = MpmsKapitalForm(instance=instance)
 
    return render(request, 'mpms/forms.html', {
        'form':    form,
        'empresa': empresa,
        'benef':   benef,
        'title':   'Kapital',
        'legend':  'Input Kapital',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  EMPREGADOR
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def mpms_empregador_create(request, hashid):
    empresa, benef = _get_empresa_and_benef(hashid)
    instance       = getattr(empresa, 'empregador', None)
 
    if request.method == 'POST':
        form = MpmsEmpregadorForm(request.POST, instance=instance)
        if form.is_valid():
            obj         = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, 'Dadus empregador konsege rai.')
            return redirect('mpms-detail', hashid=benef.hashed)
    else:
        form = MpmsEmpregadorForm(instance=instance)
 
    return render(request, 'mpms/forms.html', {
        'form':    form,
        'empresa': empresa,
        'benef':   benef,
        'title':   'Empregador',
        'legend':  'Input Empregador',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  MATERIA PRIMA
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def mpms_materia_create(request, hashid):
    empresa, benef = _get_empresa_and_benef(hashid)
    instance       = getattr(empresa, 'materia_prima', None)
 
    if request.method == 'POST':
        form = MpmsMateriaPrimaForm(request.POST, instance=instance)
        if form.is_valid():
            obj         = form.save(commit=False)
            obj.empresa = empresa
            obj.save()
            messages.success(request, 'Materia prima konsege rai.')
            return redirect('mpms-detail', hashid=benef.hashed)
    else:
        form = MpmsMateriaPrimaForm(instance=instance)
 
    return render(request, 'mpms/forms.html', {
        'form':    form,
        'empresa': empresa,
        'benef':   benef,
        'title':   'Materia Prima',
        'legend':  'Input Materia Prima',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  ATIVIDADE
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def mpms_atividade_create(request, hashid):
    group = request.user.groups.all()[0].name
    empresa, benef = _get_empresa_and_benef(hashid)
    if request.method == 'POST':
        form = MpmsAtividadeForm(request.POST, benef=benef)
        if form.is_valid():
            obj         = form.save(commit=False)
            obj.empresa = empresa
            obj.status_id = 1
            obj.save()
            messages.success(request, 'Atividade konsege rai.')
            return redirect('mpms-detail', hashid=benef.hashed)
    else:
        form = MpmsAtividadeForm(benef=benef)
 
    context = {
        'group':group,
        'form':    form,
        'empresa': empresa,
        'benef':   benef,
        'title':   'Atividade',
        'legend':  'Input Atividade',
    }
    return render(request, 'mpms/forms.html', context)
