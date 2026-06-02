import csv, io, datetime, hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from config.decorators import allowed_users
from django.db.models import Count, Max, Q, Prefetch, Exists, OuterRef, Sum
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from monitoring.models import BusinessImpactMonitoring, FundUsage, BusinessAsset, CashFlow, FinancialBook
from kni.models import    Business, LocBussiness, Program, Employee, Finance
from monitoring.forms import BusinessImpactMonitoringForm, FundUsageForm, FinancialBookForm, CashFlowForm, BusinessAssetForm

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def impact_monitoring_add(request, business_hashid):
    business = get_object_or_404(Business, hashed=business_hashid)
    tottal = Employee.objects.filter(business=business).first()
    group = request.user.groups.all()[0].name if request.user.groups.exists() else None
    if request.method == 'POST':
        form = BusinessImpactMonitoringForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.business = business
            obj.monitoring_date = datetime.datetime.now()
            obj.status_id = 1
            obj.total_employee = tottal.total
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Monitorizasaun impaktu rai ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=obj.id)
    else:
        form = BusinessImpactMonitoringForm(initial={'monitoring_date': datetime.date.today()})
    
    context = {
        'group': group,
        'form': form,
        'business': business,
        'title': 'Monitorizasaun Impaktu Foun',
        'legend': f"Rejistu Monitorizasaun ba {business.name or business.idea}",
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
        ],
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def impact_monitoring_edit(request, business_hashid, pk):
    """Edita monitorizasaun impaktu"""
    business = get_object_or_404(Business, hashed=business_hashid)
    obj = get_object_or_404(BusinessImpactMonitoring, id=pk, business=business)
    group = request.user.groups.all()[0].name if request.user.groups.exists() else None
    
    if request.method == 'POST':
        form = BusinessImpactMonitoringForm(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = request.user
            instance.updated_at = datetime.datetime.now()
            instance.save()
            messages.success(request, "Monitorizasaun impaktu atualiza ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=obj.id)
    else:
        form = BusinessImpactMonitoringForm(instance=obj)
    
    context = {
        'group': group,
        'form': form,
        'obj': obj,
        'business': business,
        'title': 'Edita Monitorizasaun Impaktu',
        'legend': f"Atualiza dadus monitorizasaun ba {business.name or business.idea}",
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'benef-detail-kni', 'link_text': 'Benefisiariu', 'params': {'hashid': business.benefisiariu.hashed}},
            {'link_name': 'business_impact_list', 'link_text': 'Lista Monitorizasaun', 'params': {'business_hashid': business.hashed}},
        ],
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def impact_monitoring_delete(request, business_hashid, pk):
    """Apaga monitorizasaun impaktu"""
    business = get_object_or_404(Business, hashed=business_hashid)
    obj = get_object_or_404(BusinessImpactMonitoring, id=pk, business=business)
    
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Monitorizasaun impaktu hamoos ho susesu!")
        return redirect('business_impact_list', business_hashid=business.hashed)
    
    context = {
        'obj': obj,
        'business': business,
        'title': 'Hamoos Monitorizasaun',
        'message': f"Boot hakarak hamoos monitorizasaun loron {obj.monitoring_date} ba negosiu {business.name or business.idea}?",
    }
    return render(request, 'Dash/confirm_delete.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def impact_monitoring_detail(request, business_hashid, pk):
    """Detallu monitorizasaun impaktu"""
    business = get_object_or_404(Business, hashed=business_hashid)
    obj = get_object_or_404(BusinessImpactMonitoring, id=pk, business=business)
    group = request.user.groups.all()[0].name if request.user.groups.exists() else None
    
    # Relacionados
    fund_usages = obj.fund_usages.all()
    assets = obj.assets.all()
    cashflows = obj.cashflows.all()
    financial_books = obj.financial_books.all()
    
    context = {
        'group': group,
        'obj': obj,
        'business': business,
        'fund_usages': fund_usages,
        'assets': assets,
        'cashflows': cashflows,
        'financial_books': financial_books,
        'title': 'Detallu Monitorizasaun Impaktu',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'benef-detail-kni', 'link_text': 'Benefisiariu', 'params': {'hashid': business.benefisiariu.hashed}},
            {'link_name': 'business_impact_list', 'link_text': 'Lista Monitorizasaun', 'params': {'business_hashid': business.hashed}},
        ],
    }
    return render(request, 'Dash/impact_monitoring_detail.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def impact_monitoring_list(request, business_hashid):
    """Lista hotu monitorizasaun impaktu ba negosiu ida"""
    business = get_object_or_404(Business, hashed=business_hashid)
    group = request.user.groups.all()[0].name if request.user.groups.exists() else None
    monitorings = BusinessImpactMonitoring.objects.filter(business=business)
    
    context = {
        'group': group,
        'business': business,
        'monitorings': monitorings,
        'title': 'Lista Monitorizasaun Impaktu',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'benef-detail-kni', 'link_text': 'Benefisiariu', 'params': {'hashid': business.benefisiariu.hashed}},
        ],
    }
    return render(request, 'Dash/impact_monitoring_list.html', context)


# ============================================================
# FUND USAGE - VIEWS
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def fund_usage_add(request, business_hashid, monitoring_pk):
    """Adiciona utilizasaun fundus"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    
    if request.method == 'POST':
        form = FundUsageForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Utilizasaun fundus rai ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    else:
        form = FundUsageForm()
    
    context = {
        'form': form,
        'monitoring': monitoring,
        'business': business,
        'title': 'Utilizasaun Fundus Foun',
        'legend': f"Gastu sira ba monitorizasaun loron {monitoring.monitoring_date}",
        'back_url': f'/kni/business/{business.hashed}/impact/{monitoring.id}/detail/',
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def fund_usage_edit(request, business_hashid, monitoring_pk, pk):
    """Edita utilizasaun fundus"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj = get_object_or_404(FundUsage, id=pk, monitoring=monitoring)
    
    if request.method == 'POST':
        form = FundUsageForm(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = request.user
            instance.updated_at = datetime.datetime.now()
            instance.save()
            messages.success(request, "Utilizasaun fundus atualiza ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    else:
        form = FundUsageForm(instance=obj)
    
    context = {
        'form': form,
        'obj': obj,
        'monitoring': monitoring,
        'business': business,
        'title': 'Edita Utilizasaun Fundus',
        'legend': f"Atualiza gastu {obj.item_name}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def fund_usage_delete(request, business_hashid, monitoring_pk, pk):
    """Apaga utilizasaun fundus"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj = get_object_or_404(FundUsage, id=pk, monitoring=monitoring)
    
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Utilizasaun fundus hamoos ho susesu!")
        return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    
    context = {
        'obj': obj,
        'title': 'Hamoos Utilizasaun Fundus',
        'message': f"Boot hakarak hamoos gastu {obj.item_name} ($ {obj.amount})?",
    }
    return render(request, 'Dash/confirm_delete.html', context)


# ============================================================
# BUSINESS ASSET - VIEWS
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def business_asset_add(request, business_hashid, monitoring_pk):
    """Adiciona asset ba negosiu"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    
    if request.method == 'POST':
        form = BusinessAssetForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Asset rai ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    else:
        form = BusinessAssetForm()
    
    context = {
        'form': form,
        'monitoring': monitoring,
        'business': business,
        'title': 'Asset Foun',
        'legend': f"Rejistu asset foun ba monitorizasaun loron {monitoring.monitoring_date}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def business_asset_edit(request, business_hashid, monitoring_pk, pk):
    """Edita asset"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj = get_object_or_404(BusinessAsset, id=pk, monitoring=monitoring)
    
    if request.method == 'POST':
        form = BusinessAssetForm(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = request.user
            instance.updated_at = datetime.datetime.now()
            instance.save()
            messages.success(request, "Asset atualiza ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    else:
        form = BusinessAssetForm(instance=obj)
    
    context = {
        'form': form,
        'obj': obj,
        'monitoring': monitoring,
        'business': business,
        'title': 'Edita Asset',
        'legend': f"Atualiza asset {obj.asset_name}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def business_asset_delete(request, business_hashid, monitoring_pk, pk):
    """Apaga asset"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj = get_object_or_404(BusinessAsset, id=pk, monitoring=monitoring)
    
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Asset hamoos ho susesu!")
        return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    
    context = {
        'obj': obj,
        'title': 'Hamoos Asset',
        'message': f"Boot hakarak hamoos asset {obj.asset_name}?",
    }
    return render(request, 'Dash/confirm_delete.html', context)


# ============================================================
# CASH FLOW - VIEWS
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def cashflow_add(request, business_hashid, monitoring_pk):
    """Adiciona fluxu osan"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    
    if request.method == 'POST':
        form = CashFlowForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Fluxu osan rai ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    else:
        form = CashFlowForm(initial={'transaction_date': datetime.date.today()})
    
    context = {
        'form': form,
        'monitoring': monitoring,
        'business': business,
        'title': 'Fluxu Osan Foun',
        'legend': f"Rejistu transasaun ba monitorizasaun loron {monitoring.monitoring_date}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def cashflow_edit(request, business_hashid, monitoring_pk, pk):
    """Edita fluxu osan"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj = get_object_or_404(CashFlow, id=pk, monitoring=monitoring)
    
    if request.method == 'POST':
        form = CashFlowForm(request.POST, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = request.user
            instance.updated_at = datetime.datetime.now()
            instance.save()
            messages.success(request, "Fluxu osan atualiza ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    else:
        form = CashFlowForm(instance=obj)
    
    context = {
        'form': form,
        'obj': obj,
        'monitoring': monitoring,
        'business': business,
        'title': 'Edita Fluxu Osan',
        'legend': f"Atualiza transasaun {obj.description}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def cashflow_delete(request, business_hashid, monitoring_pk, pk):
    """Apaga fluxu osan"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj = get_object_or_404(CashFlow, id=pk, monitoring=monitoring)
    
    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Fluxu osan hamoos ho susesu!")
        return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    
    context = {
        'obj': obj,
        'title': 'Hamoos Fluxu Osan',
        'message': f"Boot hakarak hamoos transasaun {obj.description} ($ {obj.amount})?",
    }
    return render(request, 'Dash/confirm_delete.html', context)


# ============================================================
# FINANCIAL BOOK - VIEWS
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def financial_book_add(request, business_hashid, monitoring_pk):
    """Adiciona livru kontabilidade"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    
    if request.method == 'POST':
        form = FinancialBookForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Livru kontabilidade rai ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    else:
        form = FinancialBookForm()
    
    context = {
        'form': form,
        'monitoring': monitoring,
        'business': business,
        'title': 'Livru Kontabilidade Foun',
        'legend': f"Anexa dokumentu ba monitorizasaun loron {monitoring.monitoring_date}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def financial_book_edit(request, business_hashid, monitoring_pk, pk):
    """Edita livru kontabilidade"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj = get_object_or_404(FinancialBook, id=pk, monitoring=monitoring)
    
    if request.method == 'POST':
        form = FinancialBookForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.updated_by = request.user
            instance.updated_at = datetime.datetime.now()
            instance.save()
            messages.success(request, "Livru kontabilidade atualiza ho susesu!")
            return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    else:
        form = FinancialBookForm(instance=obj)
    
    context = {
        'form': form,
        'obj': obj,
        'monitoring': monitoring,
        'business': business,
        'title': 'Edita Livru Kontabilidade',
        'legend': f"Atualiza dokumentu {obj.title}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def financial_book_delete(request, business_hashid, monitoring_pk, pk):
    """Apaga livru kontabilidade"""
    business = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj = get_object_or_404(FinancialBook, id=pk, monitoring=monitoring)
    
    if request.method == 'POST':
        # Apaga file physically
        if obj.file:
            obj.file.delete()
        obj.delete()
        messages.success(request, "Livru kontabilidade hamoos ho susesu!")
        return redirect('business_impact_detail', business_hashid=business.hashed, pk=monitoring.id)
    
    context = {
        'obj': obj,
        'title': 'Hamoos Livru Kontabilidade',
        'message': f"Boot hakarak hamoos dokumentu {obj.title}?",
    }
    return render(request, 'Dash/confirm_delete.html', context)