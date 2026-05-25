import datetime, hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo
from kni.models import Business, Program, Finance, LocBussiness
from manufatureira.models import Manufatur, Lokalizasaun, Membro, Aktividade
from benefisiariu.forms import BenefisiariuForm, AddressTLForm, AddressOriginForm, PhotoUploadForm
from manufatureira.forms import ManufaturForm, LokalizasaunForm, MembroForm, AktividadeForm, BusinessDNIMForm, \
                                LocBusinessDNIMForm, ProgramDNIMForm, EmployeeDNIMForm, FinanceDNIMForm
from custom.models import Status,Tipu_Apoio, TIpu_Programa
from config.decorators import allowed_users
from django.conf import settings


# ═══════════════════════════════════════════════════════
# 1. ADD MANUFATUR (START FROM BENEFISIARIU)
# ═══════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['dnim'])
@transaction.atomic
def add_benef_dnim(request):
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
            obj1 = Manufatur.objects.get_or_create(
                benefisiariu = obj,
                leader_name = obj,
                status = Status.objects.get(name="Ativu"),
                created_by = request.user)
            obj2 = Program.objects.get_or_create(
                benefisiariu = obj,
                program_type = TIpu_Programa.objects.get(pk=3),
                status = Status.objects.get(pk=1),
                created_by = request.user
                )
            obj3 = Business.objects.get_or_create(
                benefisiariu = obj
                )
            messages.success(request, "Dadus Benefisiariu rai ho susesu.")
            return redirect('manuf-detail-dnim', hashid=obj.hashed)
    else:
        form = BenefisiariuForm()
        
    context = {
        'group': group,
        'form': form,
        'title': 'Registo Dados',
        'legend': 'Registo Dados Benefisiariu Manufatureira ',
        'link_antes': [
            {'link_name': 'dash-man', 'link_text': 'Painel Manufatureira'},
            {'link_name': 'geral_man', 'link_text': 'Lista Benefisiariu'},
        ],
    }
    return render(request, 'DNIM/form.html', context)


@login_required
@allowed_users(allowed_roles=['dnim'])
@transaction.atomic
def edit_benef_dnim(request, hashid):
    group = request.user.groups.all()[0].name if request.user.groups.exists() else None
    obj = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = BenefisiariuForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            benef = form.save(commit=False)
            benef.updated_by = request.user
            benef.updated_at = datetime.datetime.now()
            benef.save()
            messages.success(request,"Dadus Benefisiariu atualiza ho susesu.")
            return redirect('manuf-detail-dnim', hashid=benef.hashed)
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

    return render(request, 'DNIM/form.html', context)

# ══════════════════════════════════════════════════════════════
#  2. ALTERA ENDERESU TL
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['dnim'])
def AddressTLUpdate_dnim(request, hashid):
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
            return redirect('manuf-detail-dnim', hashid=hashid)
    else:
        form = AddressTLForm(instance=objects)
        
    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Altera Enderesu',
        'legend': 'Altera Enderesu',
    }

    return render(request, 'DNIM/form_addressBnf.html', context)

# ══════════════════════════════════════════════════════════════
#  3. ALTERA ENDERESU ORIGIN
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['dnim'])
def AddressOriginUpdate_dnim(request, hashid):
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
            return redirect('manuf-detail-dnim', hashid=hashid)
    else:
        form = AddressOriginForm(instance=objects)

    context = {
        'hashid': hashid,
        'form':   form,
        'emp':    emp,
        'title':  'Altera Enderesu Origin',
        'legend': 'Altera Enderesu Origin',
    }
    return render(request, 'DNIM/form_origin.html', context)

# ══════════════════════════════════════════════════════════════
#  4. LOKASAUN NEGOSIU
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['dnim'])
def Localidade_Add_dnim(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = LocBussiness.objects.filter(benefisiariu=emp).first()
    if request.method == 'POST':
        form = LocBusinessDNIMForm(request.POST, instance=objects)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.benefisiariu = emp
            instance.created_by = request.user
            instance.save()
            obj = Lokalizasaun.objects.get_or_create(
                municipality = instance.municipality,
                administrativepost = instance.administrativepost,
                village = instance.village,
                latitude = instance.latitude,
                longitude = instance.longitude,
                area_polygon = instance.area_polygon,
                created_by = request.user)
            messages.success(request, "Lokasaun negosiu atualiza ona.")
            return redirect('manuf-detail-dnim', hashid=hashid)
    else:
        form = LocBusinessDNIMForm(instance=objects)
    context = {
        'hashid':       hashid,
        'form':         form,
        'emp':          emp,
        'MAPBOX_TOKEN': settings.MAPBOX_TOKEN,
        'title':        'Lokasaun Negosiu',
        'legend':       'Lokasaun Negosiu',
    }
    return render(request, 'DNIM/form_address.html', context)

# ══════════════════════════════════════════════════════════════
#  5. REJISTU NEGOSIU No Edit
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['dnim'])
@transaction.atomic
def Business_Add_dnim(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = BusinessDNIMForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.benefisiariu = emp
            obj.save()
            messages.success(request, "Negosiu rai ho susesu.")
            return redirect('manuf-detail-dnim', hashid=hashid)
    else:
        form = BusinessDNIMForm()

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Rejistu Negosiu',
        'legend':     'Rejistu Negosiu KNI',
    }
    return render(request, 'DNIM/form.html', context)

@login_required
@allowed_users(allowed_roles=['dnim'])
@transaction.atomic
def Business_Edit_dnim(request, hashid):
    emp = get_object_or_404(Business, hashed=hashid)
    if request.method == 'POST':
        form = BusinessDNIMForm(request.POST, instance=emp)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.save()
            obj1 = Manufatur.objects.get(benefisiariu = obj.benefisiariu, name = obj.name)
            obj.save
            messages.success(request, "Negosiu rai ho susesu.")
            return redirect('manuf-detail-dnim', hashid=hashid)
    else:
        form = BusinessDNIMForm(instance=emp)

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Altera Negosiu',
        'legend':     'Altera Negosiu Manufatureira',
    }
    return render(request, 'DNIM/form.html', context)

# ══════════════════════════════════════════════════════════════
#  6. REJISTU PROGRAMA KNI
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['dnim'])
@transaction.atomic
def Program_Add_dnim(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = ProgramDNIMForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.benefisiariu = emp
            obj.program_type = TIpu_Programa.objects.get(name='dnim')
            obj.status_id = 1
            obj.save()
            total_budget = Program.objects.filter(benefisiariu=emp, program_type__name='dnim').aggregate(total=Sum('amount'))['total'] or 0
            for b in Business.objects.filter(benefisiariu=emp):
                Finance.objects.update_or_create(business=b, defaults={'budget': total_budget})
            messages.success(request, "Programa KNI rai ho susesu.")
            return redirect('manuf-detail-dnim', hashid=hashid)
    else:
        form = ProgramDNIMForm()

    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Programa KNI',
        'legend': 'Programa KNI Foun',
    }
    return render(request, 'DNIM/form.html', context)


# ══════════════════════════════════════════════════════════════
#  7. TRABALHADORES
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['dnim'])
@transaction.atomic
def Employee_Add_dnim(request, hashid):
    emp        = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)
    if request.method == 'POST':
        form = EmployeeDNIMForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Trabalhadores rai ho susesu.")
            return redirect('manuf-detail-dnim', hashid=hashid)
    else:
        form = EmployeeDNIMForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Rejistu Trabalhadores',
        'legend':     'Trabalhadores Foun',
    }
    return render(request, 'DNIM/form.html', context)


# ══════════════════════════════════════════════════════════════
#  8. FINANSIAMENTO
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['dnim'])
@transaction.atomic
def Finance_Add_dnim(request, hashid):
    emp        = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)
    if request.method == 'POST':
        form = FinanceDNIMForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Finansiamento rai ho susesu.")
            return redirect('manuf-detail-dnim', hashid=hashid)
    else:
        form = FinanceDNIMForm()
        form.fields['business'].queryset = businesses
    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Rejistu Finansiamento',
        'legend':     'Finansiamento Foun',
    }
    return render(request, 'DNIM/form.html', context)
@login_required
@allowed_users(allowed_roles=['admin', 'dnim'])
@transaction.atomic
def Manufatur_Add_dnim(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)

    if request.method == 'POST':
        form = ManufaturForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.benefisiariu = emp
            obj.save()

            messages.success(request, "Manufatur rai ho susesu.")
            return redirect('benef-detail', hashid=hashid)
    else:
        form = ManufaturForm()

    context = {
        'form': form,
        'emp': emp,
        'title': 'Rejistu Manufatur',
        'legend': 'Rejistu Manufatur Foun',
    }
    return render(request, 'DNIM/form.html', context)


# ═══════════════════════════════════════════════════════
# 2. LOKALIZASAUN
# ═══════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['admin', 'dnim'])
def Lokalizasaun_Add_dnim(request, manuf_id):
    manuf = get_object_or_404(Manufatur, id=manuf_id)
    obj = Lokalizasaun.objects.filter(manufatur=manuf).first()

    if request.method == 'POST':
        form = LokalizasaunForm(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.manufatur = manuf
            instance.created_by = request.user
            instance.save()

            messages.success(request, "Lokalizasaun rai ho susesu.")
            return redirect('manuf-detail', id=manuf_id)
    else:
        form = LokalizasaunForm(instance=obj)

    context = {
        'form': form,
        'manuf': manuf,
        'title': 'Lokalizasaun Manufatur',
        'legend': 'Input Lokalizasaun',
    }
    return render(request, 'DNIM/form_address.html', context)


# ═══════════════════════════════════════════════════════
# 3. MEMBRO
# ═══════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['admin', 'dnim'])
def Membro_Add_dnim(request, manuf_id):
    manuf = get_object_or_404(Manufatur, id=manuf_id)
    obj = Membro.objects.filter(manufatur=manuf).first()

    if request.method == 'POST':
        form = MembroForm(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.manufatur = manuf
            instance.save()

            messages.success(request, "Dados membro rai ho susesu.")
            return redirect('manuf-detail', id=manuf_id)
    else:
        form = MembroForm(instance=obj)

    context = {
        'form': form,
        'manuf': manuf,
        'title': 'Dados Membro',
        'legend': 'Input Membro',
    }
    return render(request, 'DNIM/form.html', context)


# ═══════════════════════════════════════════════════════
# 4. AKTIVIDADE (PROGRAM + STATUS + YEAR)
# ═══════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['admin', 'dnim'])
@transaction.atomic
def Aktividade_Add_dnim(request, manuf_id):
    manuf = get_object_or_404(Manufatur, id=manuf_id)

    if request.method == 'POST':
        form = AktividadeForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)

            obj.manufatur = manuf

            # STATUS default
            obj.status = Status.objects.get(pk=1)

            obj.save()

            # optional: update Program finance
            total = Aktividade.objects.filter(manufatur=manuf).aggregate(
                total=Sum('amount')
            )['total'] or 0

            for p in Program.objects.filter(benefisiariu=manuf.benefisiariu):
                Finance.objects.update_or_create(
                    business=p.benefisiariu.business_set.first(),
                    defaults={'budget': total}
                )

            messages.success(request, "Aktividade rai ho susesu.")
            return redirect('manuf-detail', id=manuf_id)

    else:
        form = AktividadeForm()

    context = {
        'form': form,
        'manuf': manuf,
        'title': 'Rejistu Aktividade',
        'legend': 'Aktividade Manufatur',
    }
    return render(request, 'DNIM/form.html', context)