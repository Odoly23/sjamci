import io, csv, datetime, hashlib, uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo
from benefisiariu.forms import    BenefisiariuForm, AddressTLForm, AddressOriginForm, PhotoUploadForm
from kni.models import Business, LocBussiness, Program, Employee, Finance
from kni.forms import BusinessKNIForm, LocBusinessKNIForm, ProgramKNIForm, EmployeeKNIForm, FinanceKNIForm
from custom.models import TIpu_Programa, Status
from config.decorators import allowed_users
from django.conf import settings
from django.views.decorators.cache import never_cache


@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def add_benef_kni(request):
    group = request.user.groups.all()[0].name
    
    if request.method == 'POST':
        form = BenefisiariuForm(request.POST, request.FILES)
        if form.is_valid():
            name  = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')
            if Benefisiariu.objects.filter(Q(name=name) | Q(phone=phone)).exists():
                messages.warning(request, "Benefisiariu ho naran ka telefone hanesan iha ona.")
                return redirect('add-benef-kni')
                
            obj = form.save(commit=False)
            obj.created_by = request.user
            obj.status = Status.objects.get(pk=1)
            obj.save()
            
            messages.success(request, "Dadus Benefisiariu rai ho sukses.")
            return redirect('benef-detail-kni', hashid=obj.hashed)
    else:
        form = BenefisiariuForm()
        
    context = {
        'group': group,
        'form': form,
        'title': 'Registo Dados',
        'legend': 'Registo Dados Benefisiariu KNI',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
        ],
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def edit_benef_kni(request, hashid):
    group = request.user.groups.all()[0].name if request.user.groups.exists() else None
    obj = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = BenefisiariuForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            benef = form.save(commit=False)
            benef.updated_by = request.user
            benef.updated_at = datetime.datetime.now()
            benef.save()
            messages.success(request,"Dadus Benefisiariu atualiza ho sukses.")
            return redirect('benef-detail-kni', hashid=benef.hashed)
    else:
        form = BenefisiariuForm(instance=obj)
    context = {
        'group': group,
        'form': form,
        'obj': obj,
        'title': 'Edit Dados Benefisiariu',
        'legend': 'Atualiza Dados Benefisiariu KNI',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
        ],
    }

    return render(request, 'Dash/Forms/form.html', context)

# ══════════════════════════════════════════════════════════════
#  2. ALTERA ENDERESU TL
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KNI'])
def AddressTLUpdate_kni(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = AddressTL.objects.filter(benefisiariu=emp).first()
    
    if request.method == 'POST':
        form = AddressTLForm(request.POST, instance=objects)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.benefisiariu = emp
            if hasattr(instance, 'user'):
                instance.created_by = request.user
            instance.save()
            messages.success(request, "Enderesu atualiza ona.")
            return redirect('benef-detail-kni', hashid=hashid)
    else:
        form = AddressTLForm(instance=objects)
        
    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Altera Enderesu',
        'legend': 'Altera Enderesu',
    }

    return render(request, 'Dash/Forms/form_addressBnf.html', context)

# ══════════════════════════════════════════════════════════════
#  3. ALTERA ENDERESU ORIGIN
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KNI'])
def AddressOriginUpdate_kni(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = AddressOrigin.objects.filter(benefisiariu=emp).first()

    if request.method == 'POST':
        form = AddressOriginForm(request.POST, instance=objects)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.benefisiariu = emp
            instance.created_by         = request.user
            instance.save()
            messages.success(request, "Enderesu origin atualiza ona.")
            return redirect('kni-addtl-update', hashid=hashid)
    else:
        form = AddressOriginForm(instance=objects)

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Altera Enderesu Origin',
        'legend': 'Altera Enderesu Origin',
    }
    return render(request, 'Dash/Forms/form_origin.html', context)

# ══════════════════════════════════════════════════════════════
#  4. LOKASAUN NEGOSIU
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KNI'])
def Localidade_Add(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = LocBussiness.objects.filter(benefisiariu=emp).first()

    if request.method == 'POST':
        form = LocBusinessKNIForm(request.POST, instance=objects)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.benefisiariu = emp
            instance.created_by = request.user
            instance.save()
            messages.success(request, "Lokasaun negosiu atualiza ona.")
            return redirect('benef-detail-kni', hashid=hashid)
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
    return render(request, 'Dash/Forms/form_address.html', context)

# ══════════════════════════════════════════════════════════════
#  5. REJISTU NEGOSIU
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def Business_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = BusinessKNIForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.benefisiariu = emp
            obj.save()
            messages.success(request, "Negosiu rai ho sukses.")
            return redirect('benef-detail-kni', hashid=hashid)
    else:
        form = BusinessKNIForm()

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Rejistu Negosiu',
        'legend':     'Rejistu Negosiu KNI',
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  6. REJISTU PROGRAMA KNI
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def Program_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = ProgramKNIForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.benefisiariu = emp
            obj.program_type = TIpu_Programa.objects.get(name='KNI')
            obj.status_id = 1
            obj.save()
            total_budget = Program.objects.filter(benefisiariu=emp, program_type__name='KNI').aggregate(total=Sum('amount'))['total'] or 0
            for b in Business.objects.filter(benefisiariu=emp):
                Finance.objects.update_or_create(business=b, defaults={'budget': total_budget})
            messages.success(request, "Programa KNI rai ho susesu.")
            return redirect('benef-detail-kni', hashid=hashid)
    else:
        form = ProgramKNIForm()

    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Programa KNI',
        'legend': 'Programa KNI Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  7. TRABALHADORES
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def Employee_Add(request, hashid):
    emp        = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)
    if request.method == 'POST':
        form = EmployeeKNIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Trabalhadores rai ho sukses.")
            return redirect('benef-detail-kni', hashid=hashid)
    else:
        form = EmployeeKNIForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Rejistu Trabalhadores',
        'legend':     'Trabalhadores Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  8. FINANSIAMENTO
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def Finance_Add(request, hashid):
    emp        = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)
    if request.method == 'POST':
        form = FinanceKNIForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Finansiamento rai ho sukses.")
            return redirect('benef-detail-kni', hashid=hashid)
    else:
        form = FinanceKNIForm()
        form.fields['business'].queryset = businesses
    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Rejistu Finansiamento',
        'legend':     'Finansiamento Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)