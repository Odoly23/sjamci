from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from django.http import JsonResponse
from kni.models import Business, LocBussiness, Program, Employee, Finance
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin
from suave.models import EkipaMember, ProductService, MainCustomer, Competitor, MarketAssessment, FinancialAssessment, FixedAsset, CreditInfo
from benefisiariu.forms import BenefisiariuForm, AddressTLForm, AddressOriginForm
from suave.forms import BusinessKSForm, LocBusinessKSForm, ProgramKSForm, EmployeeKSForm, FinanceKSForm,  EkipaMemberForm,  ProductServiceForm,\
    MainCustomerForm,  CompetitorForm, MarketAssessmentForm, FinancialAssessmentForm, FixedAssetForm, CreditInfoForm
from custom.models import Status
from config.decorators import allowed_users

# ══════════════════════════════════════════════════════════════
#  1. MAPA KREDITU SUAVE
# ══════════════════════════════════════════════════════════════
@login_required
def APIGISKS(request):
    businesses = Business.objects.filter(benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE").select_related("benefisiariu", "sector")
    obj = []
    for business in businesses:
        lokasi = LocBussiness.objects.filter(benefisiariu=business.benefisiariu).select_related("municipality", "administrativepost", "village").first()
        if not lokasi:
            continue
        if not lokasi.latitude or not lokasi.longitude:
            continue
        try:
            latitude = float(lokasi.latitude)
            longitude = float(lokasi.longitude)
        except:
            continue
        obj.append({
            "name": business.name,
            "owner": business.benefisiariu.name,
            "sector": business.sector.name if business.sector else "",
            "municipality": (lokasi.municipality.name if lokasi.municipality else ""),
            "administrativepost": (lokasi.administrativepost.name if lokasi.administrativepost else ""),
            "village": (lokasi.village.name if lokasi.village else ""),
            "latitude": latitude,
            "longitude": longitude,
        })
    return JsonResponse({"obj": obj})

# ══════════════════════════════════════════════════════════════
#  2. ADD BENEFISIARIU
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def add_benef_ks(request):
    group = request.user.groups.all()[0].name
    if request.method == 'POST':
        form = BenefisiariuForm(request.POST, request.FILES)
        if form.is_valid():
            name  = form.cleaned_data.get('name')
            phone = form.cleaned_data.get('phone')
            if Benefisiariu.objects.filter(Q(name=name) | Q(phone=phone)).exists():
                messages.warning(request, "Benefisiariu ho naran ka telefone hanesan iha ona.")
                return redirect('add-benef-ks')
            obj              = form.save(commit=False)
            obj.created_user = request.user
            obj.status       = Status.objects.get(pk=1)
            obj.save()
            messages.success(request, "Dadus Benefisiariu rai ho sukses.")
            return redirect('benef-detail-ks', hashid=obj.hashed)
    else:
        form = BenefisiariuForm()
    context = {
        'group':  group,
        'form':   form,
        'title':  'Registo Dados',
        'legend': 'Registo Dados Benefisiariu Kreditu Suave',
        'link_antes': [
            {'link_name': 'dash-ks',  'link_text': 'Painel Kreditu Suave'},
            {'link_name': 'geral-ks', 'link_text': 'Lista Benefisiariu'},
        ],
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  2. EDIT BENEFISIARIU
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def edit_benef_ks(request, hashid):
    group = request.user.groups.all()[0].name
    obj   = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = BenefisiariuForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            benef              = form.save(commit=False)
            benef.updated_user = request.user
            benef.save()
            messages.success(request, "Dadus Benefisiariu atualiza ho sukses.")
            return redirect('benef-detail-ks', hashid=benef.hashed)
    else:
        form = BenefisiariuForm(instance=obj)
    context = {
        'group':  group,
        'form':   form,
        'obj':    obj,
        'title':  'Edit Dados Benefisiariu',
        'legend': 'Atualiza Dados Benefisiariu KS',
        'link_antes': [
            {'link_name': 'dash-ks',  'link_text': 'Painel Kreditu Suave'},
            {'link_name': 'geral-ks', 'link_text': 'Lista Benefisiariu'},
        ],
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  3. ENDERESU TL
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KS']) 
def AddressTLUpdate_ks(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = AddressTL.objects.filter(benefisiariu=emp).first()
    if request.method == 'POST':            
        form = AddressTLForm(request.POST, instance=objects)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.benefisiariu = emp
            if hasattr(instance, 'user'):
                instance.user = request.user
            instance.save()
            messages.success(request, "Enderesu atualiza ona.")
            return redirect('benef-detail-ks', hashid=hashid)
    else:
        form = AddressTLForm(instance=objects)

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Altera Enderesu',
        'legend':     'Altera Enderesu',
    }
    return render(request, 'Dash/Forms/form_addressBnf.html', context)
# ══════════════════════════════════════════════════════════════
#  4. ENDERESU ORIGIN
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
def AddressOriginUpdate_ks(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = AddressOrigin.objects.filter(benefisiariu=emp).first()
    if request.method == 'POST':
        form = AddressOriginForm(request.POST, instance=objects)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.benefisiariu = emp
            instance.save()
            messages.success(request, "Enderesu origin atualiza ona.")
            return redirect('benef-detail-ks', hashid=hashid)
    else:
        form = AddressOriginForm(instance=objects)

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Altera Enderesu Origin',
        'legend':     'Altera Enderesu Origin',
    }
    return render(request, 'Dash/Forms/form_origin.html', context)


# ══════════════════════════════════════════════════════════════
#  5. LOKASAUN NEGOSIU
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
def Localidade_Add_ks(request, hashid):
    emp     = get_object_or_404(Benefisiariu, hashed=hashid)
    objects = LocBussiness.objects.filter(benefisiariu=emp).first()
    if request.method == 'POST':
        form = LocBusinessKSForm(request.POST, instance=objects)
        if form.is_valid():
            instance              = form.save(commit=False)
            instance.benefisiariu = emp
            instance.save()
            messages.success(request, "Lokasaun negosiu atualiza ona.")
            return redirect('benef-detail-ks', hashid=hashid)
    else:
        form = LocBusinessKSForm(instance=objects)

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Lokasaun Negosiu',
        'legend':     'Lokasaun Negosiu',
    }
    return render(request, 'Dash/Forms/form_address.html', context)


# ══════════════════════════════════════════════════════════════
#  6. NEGOSIU
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Business_Add_ks(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = BusinessKSForm(request.POST)
        if form.is_valid():
            obj= form.save(commit=False)
            obj.benefisiariu = emp
            obj.save()
            messages.success(request, "Negosiu rai ho sukses.")
            return redirect('benef-detail-ks', hashid=hashid)
    else:
        form = BusinessKSForm()

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Rejistu Negosiu',
        'legend':     'Rejistu Negosiu Kreditu Suave',
    }
    return render(request, 'Dash/Forms/form.html', context)
# ══════════════════════════════════════════════════════════════
#  7. PROGRAMA KS
#     Otomatis sinkron total amount ke Finance setelah save
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Program_Add_ks(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = ProgramKSForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.benefisiariu = emp
            obj.status = Status.objects.get(pk=1)
            obj.save()
            total = Program.objects.filter(benefisiariu=emp, program_type__name='KREDITU SUAVE').aggregate(total=Sum('amount'))['total'] or 0
            businesses = Business.objects.filter(benefisiariu=emp)
            for business in businesses:
                finance, created = Finance.objects.get_or_create(business=business)
                finance.budget = total
                finance.save()
            messages.success(request, "Programa Kreditu Suave rai ho Susesu.")
            return redirect('benef-detail-ks',   hashid=hashid)
    else:
        form = ProgramKSForm()
    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Programa KS',
        'legend': 'Programa Kreditu Suave Foun',
    }

    return render(request,  'Dash/Forms/form.html',    context)


# ══════════════════════════════════════════════════════════════
#  8. TRABALHADORES
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Employee_Add_ks(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = EmployeeKSForm(request.POST)
        form.fields['business'].queryset = businesses

        if form.is_valid():
            obj = form.save(commit=False)

            if obj.business not in businesses:
                messages.error(request, "Business la validu.")
                return redirect('benef-detail-ks', hashid=hashid)

            obj.save()

            messages.success(request, "Trabalhadores rai ho susesu.")
            return redirect('benef-detail-ks', hashid=hashid)

    else:
        form = EmployeeKSForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Trabalhadores',
        'legend': 'Trabalhadores Foun',
    }

    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  9. FINANSIAMENTO
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Finance_Add_ks(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = FinanceKSForm(request.POST)
        form.fields['business'].queryset = businesses

        if form.is_valid():
            obj = form.save(commit=False)

            if obj.business not in businesses:
                messages.error(request, "Business la validu.")
                return redirect('benef-detail-ks', hashid=hashid)

            obj.save()

            messages.success(request, "Finansiamento rai ho susesu.")
            return redirect('benef-detail-ks', hashid=hashid)

    else:
        form = FinanceKSForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Finansiamento',
        'legend': 'Finansiamento Foun',
    }

    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  11. EKIPA MEMBRU
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def EkipaMember_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = EkipaMemberForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.benefisiariu = emp
            obj.save()
            messages.success(request, "Ekipa Membru rai ho sukses.")
            return redirect('benef-detail-ks', hashid=hashid)
    else:
        form = EkipaMemberForm()

    context = {
        'hashid':     hashid,
        'form':       form,
        'emp':        emp,
        'title':      'Rejistu Ekipa Membru',
        'legend':     'Ekipa Membru Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  12. PRODUTO / SERVISU
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def ProductService_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = ProductServiceForm(request.POST)
        form.fields['business'].queryset = businesses

        if form.is_valid():
            obj = form.save(commit=False)

            if obj.business not in businesses:
                messages.error(request, "Business la validu.")
                return redirect('benef-detail-ks', hashid=hashid)

            obj.save()

            messages.success(request, "Produto/Servisu rai ho sukses.")
            return redirect('benef-detail-ks', hashid=hashid)

    else:
        form = ProductServiceForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Produto/Servisu',
        'legend': 'Produto/Servisu Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  13. KLIENTE PRINSIPAL
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def MainCustomer_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = MainCustomerForm(request.POST)
        form.fields['business'].queryset = businesses

        if form.is_valid():
            obj = form.save(commit=False)

            if obj.business not in businesses:
                messages.error(request, "Business la validu.")
                return redirect('benef-detail-ks', hashid=hashid)

            obj.save()

            messages.success(request, "Kliente Prinsipal rai ho sukses.")
            return redirect('benef-detail-ks', hashid=hashid)

    else:
        form = MainCustomerForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Kliente Prinsipal',
        'legend': 'Kliente Prinsipal Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  14. KOMPETITOR
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Competitor_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = CompetitorForm(request.POST)
        form.fields['business'].queryset = businesses

        if form.is_valid():
            obj = form.save(commit=False)

            if obj.business not in businesses:
                messages.error(request, "Business la validu.")
                return redirect('benef-detail-ks', hashid=hashid)

            obj.save()

            messages.success(request, "Kompetitor rai ho sukses.")
            return redirect('benef-detail-ks', hashid=hashid)

    else:
        form = CompetitorForm()
        form.fields['business'].queryset = businesses

    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Kompetitor',
        'legend': 'Kompetitor Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  15. AVALIASAUN MERKADU  (OneToOne per Business)
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def MarketAssessment_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = MarketAssessmentForm(request.POST)
        form.fields['business'].queryset = businesses

        if form.is_valid():
            obj = form.save(commit=False)

            if MarketAssessment.objects.filter(
                business=obj.business
            ).exists():
                messages.warning(
                    request,
                    "Avaliasaun Merkadu ba negosiu ida ne'e iha ona."
                )
                return redirect('benef-detail-ks', hashid=hashid)

            obj.save()

            messages.success(
                request,
                "Avaliasaun Merkadu rai ho sukses."
            )
            return redirect('benef-detail-ks', hashid=hashid)

    else:
        form = MarketAssessmentForm()
        form.fields['business'].queryset = businesses
    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Avaliasaun Merkadu',
        'legend': 'Avaliasaun Merkadu Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)


# ══════════════════════════════════════════════════════════════
#  16. AVALIASAUN FINANSEIRU  (OneToOne per Business)
# ══════════════════════════════════════════════════════════════
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def FinancialAssessment_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = FinancialAssessmentForm(request.POST)
        form.fields['business'].queryset = businesses

        if form.is_valid():
            obj = form.save(commit=False)

            if FinancialAssessment.objects.filter(
                business=obj.business
            ).exists():
                messages.warning(
                    request,
                    "Avaliasaun Finanseiru ba negosiu ida ne'e iha ona."
                )
                return redirect('benef-detail-ks', hashid=hashid)

            obj.save()

            messages.success(
                request,
                "Avaliasaun Finanseiru rai ho sukses."
            )
            return redirect('benef-detail-ks', hashid=hashid)

    else:
        form = FinancialAssessmentForm()
        form.fields['business'].queryset = businesses
    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Avaliasaun Finanseiru',
        'legend': 'Avaliasaun Finanseiru Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)

# ══════════════════════════════════════════════════════════════
#  17. ASSET FIXU
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def FixedAsset_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)

    businesses = Business.objects.filter(
        benefisiariu=emp
    )

    financials = FinancialAssessment.objects.filter(
        business__in=businesses
    )

    if request.method == 'POST':
        form = FixedAssetForm(request.POST)
        form.fields['financial'].queryset = financials

        if form.is_valid():
            obj = form.save(commit=False)

            if obj.financial not in financials:
                messages.error(
                    request,
                    "Financial Assessment la validu."
                )
                return redirect(
                    'benef-detail-ks',
                    hashid=hashid
                )

            obj.save()

            messages.success(
                request,
                "Asset Fixu rai ho susesu."
            )

            return redirect(
                'benef-detail-ks',
                hashid=hashid
            )

    else:
        form = FixedAssetForm()
        form.fields['financial'].queryset = financials

    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Rejistu Asset Fixu',
        'legend': 'Asset Fixu Foun',
    }

    return render(request,  'Dash/Forms/form.html',   context)


# ══════════════════════════════════════════════════════════════
#  18. INFORMASAUN KREDITU  (OneToOne per Business)
# ══════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def CreditInfo_Add(request, hashid):
    emp = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=emp)

    if request.method == 'POST':
        form = CreditInfoForm(request.POST)
        form.fields['business'].queryset = businesses

        if form.is_valid():
            obj = form.save(commit=False)

            if CreditInfo.objects.filter(
                business=obj.business
            ).exists():
                messages.warning(
                    request,
                    "Informasaun Kreditu ba negosiu ida ne'e iha ona."
                )
                return redirect('benef-detail-ks', hashid=hashid)

            obj.save()

            messages.success(
                request,
                "Informasaun Kreditu rai ho sukses."
            )
            return redirect('benef-detail-ks', hashid=hashid)

    else:
        form = CreditInfoForm()
        form.fields['business'].queryset = businesses
    context = {
        'hashid': hashid,
        'form': form,
        'emp': emp,
        'title': 'Informasaun Kreditu',
        'legend': 'Informasaun Kreditu Foun',
    }
    return render(request, 'Dash/Forms/form.html', context)