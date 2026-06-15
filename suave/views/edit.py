import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
 
from benefisiariu.models import Benefisiariu
from kni.models import Business, Employee, Finance
from suave.models import (
    EkipaMember, ProductService, MainCustomer,
    Competitor, MarketAssessment, FinancialAssessment,
    FixedAsset, CreditInfo,
)
from suave.forms import (
    EkipaMemberForm, ProductServiceForm, MainCustomerForm,
    CompetitorForm, MarketAssessmentForm, FinancialAssessmentForm,
    FixedAssetForm, CreditInfoForm, EmployeeKSForm, FinanceKSForm,
)
from config.decorators import allowed_users
 
 
def _back(hashid):
    """Shortcut redirect ke halaman detail."""
    return redirect('benef-detail-ks', hashid=hashid)
 
 
def _ctx(hashid, benef, form, title, legend):
    return {
        'hashid': hashid,
        'emp':    benef,
        'form':   form,
        'title':  title,
        'legend': legend,
        'link_antes': [
            {
                'link_name': 'benef-detail-ks', 
                'link_text': 'Fila Fali Detail', 
                'link_param': hashid,  
            },
        ],
    }
 
 
# ══════════════════════════════════════════════════════════════
#  EMPLOYEE  — Edit
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Employee_Edit_ks(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(Employee, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        form = EmployeeKSForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Trabalhadores atualiza ho sukses.")
            return _back(hashid)
    else:
        form = EmployeeKSForm(instance=obj)
        form.fields['business'].queryset = businesses
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Trabalhadores', f'Edit Trabalhadores — {obj.business.name}'))
 
 
# ══════════════════════════════════════════════════════════════
#  FINANCE  — Edit
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Finance_Edit_ks(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(Finance, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        form = FinanceKSForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Finansiamento atualiza ho sukses.")
            return _back(hashid)
    else:
        form = FinanceKSForm(instance=obj)
        form.fields['business'].queryset = businesses
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Finansiamento', f'Edit Finansiamento — {obj.business.name}'))
 
 
# ══════════════════════════════════════════════════════════════
#  EKIPA MEMBER  — Edit / Delete
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def EkipaMember_Edit(request, hashid, pk):
    benef = get_object_or_404(Benefisiariu, hashed=hashid)
    obj   = get_object_or_404(EkipaMember, pk=pk, benefisiariu=benef)
 
    if request.method == 'POST':
        form = EkipaMemberForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Ekipa Membru atualiza ho sukses.")
            return _back(hashid)
    else:
        form = EkipaMemberForm(instance=obj)
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Ekipa Membru', f'Edit Ekipa Membru — {obj.name}'))
 
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def EkipaMember_Delete(request, hashid, pk):
    benef = get_object_or_404(Benefisiariu, hashed=hashid)
    obj   = get_object_or_404(EkipaMember, pk=pk, benefisiariu=benef)
 
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f"Ekipa Membru '{name}' hamoos ho sukses.")
        return _back(hashid)
 
    return render(request, 'Dash/Forms/confirm_delete.html', {
        'obj': obj, 'emp': benef, 'hashid': hashid,
        'title': 'Hamoos Ekipa Membru',
        'legend': f'Konfirma Hamoos: {obj.name}',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  PRODUTO / SERVISU  — Edit / Delete
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def ProductService_Edit(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(ProductService, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        form = ProductServiceForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Produto/Servisu atualiza ho sukses.")
            return _back(hashid)
    else:
        form = ProductServiceForm(instance=obj)
        form.fields['business'].queryset = businesses
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Produto/Servisu', f'Edit Produto — {obj.name}'))
 
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def ProductService_Delete(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(ProductService, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f"Produto '{name}' hamoos ho sukses.")
        return _back(hashid)
 
    return render(request, 'Dash/Forms/confirm_delete.html', {
        'obj': obj, 'emp': benef, 'hashid': hashid,
        'title': 'Hamoos Produto/Servisu',
        'legend': f'Konfirma Hamoos: {obj.name}',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  KLIENTE PRINSIPAL  — Edit / Delete
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def MainCustomer_Edit(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(MainCustomer, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        form = MainCustomerForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Kliente Prinsipal atualiza ho sukses.")
            return _back(hashid)
    else:
        form = MainCustomerForm(instance=obj)
        form.fields['business'].queryset = businesses
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Kliente Prinsipal', f'Edit Kliente — {obj.name}'))
 
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def MainCustomer_Delete(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(MainCustomer, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f"Kliente '{name}' hamoos ho sukses.")
        return _back(hashid)
 
    return render(request, 'Dash/Forms/confirm_delete.html', {
        'obj': obj, 'emp': benef, 'hashid': hashid,
        'title': 'Hamoos Kliente Prinsipal',
        'legend': f'Konfirma Hamoos: {obj.name}',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  KOMPETITOR  — Edit / Delete
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Competitor_Edit(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(Competitor, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        form = CompetitorForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Kompetitor atualiza ho sukses.")
            return _back(hashid)
    else:
        form = CompetitorForm(instance=obj)
        form.fields['business'].queryset = businesses
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Kompetitor', f'Edit Kompetitor — {obj.name}'))
 
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def Competitor_Delete(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(Competitor, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f"Kompetitor '{name}' hamoos ho sukses.")
        return _back(hashid)
 
    return render(request, 'Dash/Forms/confirm_delete.html', {
        'obj': obj, 'emp': benef, 'hashid': hashid,
        'title': 'Hamoos Kompetitor',
        'legend': f'Konfirma Hamoos: {obj.name}',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  AVALIASAUN MERKADU  — Edit (OneToOne)
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def MarketAssessment_Edit(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(MarketAssessment, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        form = MarketAssessmentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Avaliasaun Merkadu atualiza ho sukses.")
            return _back(hashid)
    else:
        form = MarketAssessmentForm(instance=obj)
        form.fields['business'].queryset = businesses
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Avaliasaun Merkadu', f'Edit Avaliasaun Merkadu — {obj.business}'))
 
 
# ══════════════════════════════════════════════════════════════
#  AVALIASAUN FINANSEIRU  — Edit (OneToOne)
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def FinancialAssessment_Edit(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(FinancialAssessment, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        form = FinancialAssessmentForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Avaliasaun Finanseiru atualiza ho sukses.")
            return _back(hashid)
    else:
        form = FinancialAssessmentForm(instance=obj)
        form.fields['business'].queryset = businesses
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Avaliasaun Finanseiru', f'Edit Avaliasaun Finanseiru — {obj.business}'))
 
 
# ══════════════════════════════════════════════════════════════
#  ASSET FIXU  — Edit / Delete
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def FixedAsset_Edit(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    financials = FinancialAssessment.objects.filter(business__in=businesses)
    obj        = get_object_or_404(FixedAsset, pk=pk, financial__in=financials)
 
    if request.method == 'POST':
        form = FixedAssetForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Asset Fixu atualiza ho sukses.")
            return _back(hashid)
    else:
        form = FixedAssetForm(instance=obj)
        form.fields['financial'].queryset = financials
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Asset Fixu', f'Edit Asset Fixu — {obj.name}'))
 
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def FixedAsset_Delete(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    financials = FinancialAssessment.objects.filter(business__in=businesses)
    obj        = get_object_or_404(FixedAsset, pk=pk, financial__in=financials)
 
    if request.method == 'POST':
        name = obj.name
        obj.delete()
        messages.success(request, f"Asset Fixu '{name}' hamoos ho sukses.")
        return _back(hashid)
 
    return render(request, 'Dash/Forms/confirm_delete.html', {
        'obj': obj, 'emp': benef, 'hashid': hashid,
        'title': 'Hamoos Asset Fixu',
        'legend': f'Konfirma Hamoos: {obj.name}',
    })
 
 
# ══════════════════════════════════════════════════════════════
#  INFORMASAUN KREDITU  — Edit (OneToOne)
# ══════════════════════════════════════════════════════════════
 
@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def CreditInfo_Edit(request, hashid, pk):
    benef      = get_object_or_404(Benefisiariu, hashed=hashid)
    businesses = Business.objects.filter(benefisiariu=benef)
    obj        = get_object_or_404(CreditInfo, pk=pk, business__in=businesses)
 
    if request.method == 'POST':
        form = CreditInfoForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, "Informasaun Kreditu atualiza ho sukses.")
            return _back(hashid)
    else:
        form = CreditInfoForm(instance=obj)
        form.fields['business'].queryset = businesses
 
    return render(request, 'Dash/Forms/form.html',
        _ctx(hashid, benef, form, 'Edit Informasaun Kreditu', f'Edit Kreditu — {obj.business}'))
 
 