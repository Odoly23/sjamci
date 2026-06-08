import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib import messages
from config.decorators import allowed_users
from monitoring.models import BusinessImpactMonitoring, FundUsage, BusinessAsset, CashFlow, FinancialBook
from monitoring.forms import BusinessImpactMonitoringForm, FundUsageForm, FinancialBookForm, CashFlowForm, BusinessAssetForm
from kni.models import Business, Employee


# ── helper ────────────────────────────────────────────────────────────────────

def _benef_redirect(business):
    """Redirect balik ke halaman detail benefisiariu."""
    return redirect('benef-detail-kni', hashid=business.benefisiariu.hashed)

def _get_group(user):
    return user.groups.first().name if user.groups.exists() else None


# ============================================================
# IMPACT MONITORING
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def impact_monitoring_add(request, business_hashid):
    business  = get_object_or_404(Business, hashed=business_hashid)
    employee  = Employee.objects.filter(business=business).first()

    if request.method == 'POST':
        form = BusinessImpactMonitoringForm(request.POST)
        if form.is_valid():
            obj                  = form.save(commit=False)
            obj.business         = business
            obj.monitoring_date  = datetime.date.today()
            obj.status_id        = 1
            obj.total_employee   = employee.total if employee else 0
            obj.created_by       = request.user
            obj.save()
            messages.success(request, "Monitorizasaun impaktu rai ho susesu!")
            return _benef_redirect(business)
    else:
        form = BusinessImpactMonitoringForm()

    context = {
        'group'      : _get_group(request.user),
        'form'       : form,
        'business'   : business,
        'title'      : 'Monitorizasaun Impaktu Foun',
        'legend'     : f"Rejistu Monitorizasaun ba {business.name or business.idea}",
        'link_antes' : [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
        ],
    }
    return render(request, 'moni/forms.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def impact_monitoring_edit(request, business_hashid, pk):
    business = get_object_or_404(Business, hashed=business_hashid)
    obj      = get_object_or_404(BusinessImpactMonitoring, id=pk, business=business)

    if request.method == 'POST':
        form = BusinessImpactMonitoringForm(request.POST, instance=obj)
        if form.is_valid():
            instance            = form.save(commit=False)
            instance.updated_by = request.user
            instance.save()
            messages.success(request, "Monitorizasaun impaktu atualiza ho susesu!")
            return _benef_redirect(business)
    else:
        form = BusinessImpactMonitoringForm(instance=obj)

    context = {
        'group'      : _get_group(request.user),
        'form'       : form,
        'obj'        : obj,
        'business'   : business,
        'title'      : 'Edita Monitorizasaun Impaktu',
        'legend'     : f"Atualiza dadus monitorizasaun ba {business.name or business.idea}",
        'link_antes' : [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
        ],
    }
    return render(request, 'moni/forms.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def impact_monitoring_delete(request, business_hashid, pk):
    business = get_object_or_404(Business, hashed=business_hashid)
    obj      = get_object_or_404(BusinessImpactMonitoring, id=pk, business=business)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Monitorizasaun impaktu hamoos ho susesu!")
        return _benef_redirect(business)

    context = {
        'obj'     : obj,
        'business': business,
        'title'   : 'Hamoos Monitorizasaun',
        'message' : f"Boot hakarak hamoos monitorizasaun loron {obj.monitoring_date} ba negosiu {business.name or business.idea}?",
    }
    return render(request, 'Dash/confirm_delete.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def impact_monitoring_detail(request, business_hashid, pk):
    business = get_object_or_404(Business, hashed=business_hashid)
    obj      = get_object_or_404(BusinessImpactMonitoring, id=pk, business=business)

    context = {
        'group'          : _get_group(request.user),
        'obj'            : obj,
        'business'       : business,
        'fund_usages'    : obj.fund_usages.all(),
        'assets'         : obj.assets.all(),
        'cashflows'      : obj.cashflows.all(),
        'financial_books': obj.financial_books.all(),
        'title'          : 'Detallu Monitorizasaun Impaktu',
        'link_antes'     : [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'benef-detail-kni', 'link_text': 'Benefisiariu', 'params': {'hashid': business.benefisiariu.hashed}},
        ],
    }
    return render(request, 'Dash/impact_monitoring_detail.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def impact_monitoring_list(request, business_hashid):
    business    = get_object_or_404(Business, hashed=business_hashid)
    monitorings = BusinessImpactMonitoring.objects.filter(business=business)

    context = {
        'group'      : _get_group(request.user),
        'business'   : business,
        'monitorings': monitorings,
        'title'      : 'Lista Monitorizasaun Impaktu',
        'link_antes' : [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'benef-detail-kni', 'link_text': 'Benefisiariu', 'params': {'hashid': business.benefisiariu.hashed}},
        ],
    }
    return render(request, 'Dash/impact_monitoring_list.html', context)


# ============================================================
# FUND USAGE
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def fund_usage_add(request, business_hashid, monitoring_pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)

    if request.method == 'POST':
        form = FundUsageForm(request.POST)
        if form.is_valid():
            obj            = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Utilizasaun fundus rai ho susesu!")
            return _benef_redirect(business)
    else:
        form = FundUsageForm()

    context = {
        'form'      : form,
        'monitoring': monitoring,
        'business'  : business,
        'title'     : 'Utilizasaun Fundus Foun',
        'legend'    : f"Gastu sira ba monitorizasaun loron {monitoring.monitoring_date}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def fund_usage_edit(request, business_hashid, monitoring_pk, pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj        = get_object_or_404(FundUsage, id=pk, monitoring=monitoring)

    if request.method == 'POST':
        form = FundUsageForm(request.POST, instance=obj)
        if form.is_valid():
            instance            = form.save(commit=False)
            instance.updated_by = request.user
            instance.save()
            messages.success(request, "Utilizasaun fundus atualiza ho susesu!")
            return _benef_redirect(business)
    else:
        form = FundUsageForm(instance=obj)

    context = {
        'form'      : form,
        'obj'       : obj,
        'monitoring': monitoring,
        'business'  : business,
        'title'     : 'Edita Utilizasaun Fundus',
        'legend'    : f"Atualiza gastu {obj.item_name}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def fund_usage_delete(request, business_hashid, monitoring_pk, pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj        = get_object_or_404(FundUsage, id=pk, monitoring=monitoring)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Utilizasaun fundus hamoos ho susesu!")
        return _benef_redirect(business)

    context = {
        'obj'    : obj,
        'title'  : 'Hamoos Utilizasaun Fundus',
        'message': f"Boot hakarak hamoos gastu {obj.item_name} ($ {obj.amount})?",
    }
    return render(request, 'Dash/confirm_delete.html', context)


# ============================================================
# BUSINESS ASSET
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def business_asset_add(request, business_hashid, monitoring_pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)

    if request.method == 'POST':
        form = BusinessAssetForm(request.POST)
        if form.is_valid():
            obj            = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Asset rai ho susesu!")
            return _benef_redirect(business)
    else:
        form = BusinessAssetForm()

    context = {
        'form'      : form,
        'monitoring': monitoring,
        'business'  : business,
        'title'     : 'Asset Foun',
        'legend'    : f"Rejistu asset foun ba monitorizasaun loron {monitoring.monitoring_date}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def business_asset_edit(request, business_hashid, monitoring_pk, pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj        = get_object_or_404(BusinessAsset, id=pk, monitoring=monitoring)

    if request.method == 'POST':
        form = BusinessAssetForm(request.POST, instance=obj)
        if form.is_valid():
            instance            = form.save(commit=False)
            instance.updated_by = request.user
            instance.save()
            messages.success(request, "Asset atualiza ho susesu!")
            return _benef_redirect(business)
    else:
        form = BusinessAssetForm(instance=obj)

    context = {
        'form'      : form,
        'obj'       : obj,
        'monitoring': monitoring,
        'business'  : business,
        'title'     : 'Edita Asset',
        'legend'    : f"Atualiza asset {obj.asset_name}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def business_asset_delete(request, business_hashid, monitoring_pk, pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj        = get_object_or_404(BusinessAsset, id=pk, monitoring=monitoring)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Asset hamoos ho susesu!")
        return _benef_redirect(business)

    context = {
        'obj'    : obj,
        'title'  : 'Hamoos Asset',
        'message': f"Boot hakarak hamoos asset {obj.asset_name}?",
    }
    return render(request, 'Dash/confirm_delete.html', context)


# ============================================================
# CASH FLOW
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def cashflow_add(request, business_hashid, monitoring_pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)

    if request.method == 'POST':
        form = CashFlowForm(request.POST)
        if form.is_valid():
            obj            = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Fluxu osan rai ho susesu!")
            return _benef_redirect(business)
    else:
        form = CashFlowForm(initial={'transaction_date': datetime.date.today()})

    context = {
        'form'      : form,
        'monitoring': monitoring,
        'business'  : business,
        'title'     : 'Fluxu Osan Foun',
        'legend'    : f"Rejistu transasaun ba monitorizasaun loron {monitoring.monitoring_date}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def cashflow_edit(request, business_hashid, monitoring_pk, pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj        = get_object_or_404(CashFlow, id=pk, monitoring=monitoring)

    if request.method == 'POST':
        form = CashFlowForm(request.POST, instance=obj)
        if form.is_valid():
            instance            = form.save(commit=False)
            instance.updated_by = request.user
            instance.save()
            messages.success(request, "Fluxu osan atualiza ho susesu!")
            return _benef_redirect(business)
    else:
        form = CashFlowForm(instance=obj)

    context = {
        'form'      : form,
        'obj'       : obj,
        'monitoring': monitoring,
        'business'  : business,
        'title'     : 'Edita Fluxu Osan',
        'legend'    : f"Atualiza transasaun {obj.description}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def cashflow_delete(request, business_hashid, monitoring_pk, pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj        = get_object_or_404(CashFlow, id=pk, monitoring=monitoring)

    if request.method == 'POST':
        obj.delete()
        messages.success(request, "Fluxu osan hamoos ho susesu!")
        return _benef_redirect(business)

    context = {
        'obj'    : obj,
        'title'  : 'Hamoos Fluxu Osan',
        'message': f"Boot hakarak hamoos transasaun {obj.description} ($ {obj.amount})?",
    }
    return render(request, 'Dash/confirm_delete.html', context)


# ============================================================
# FINANCIAL BOOK
# ============================================================

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def financial_book_add(request, business_hashid, monitoring_pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)

    if request.method == 'POST':
        form = FinancialBookForm(request.POST, request.FILES)
        if form.is_valid():
            obj            = form.save(commit=False)
            obj.monitoring = monitoring
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Livru kontabilidade rai ho susesu!")
            return _benef_redirect(business)
    else:
        form = FinancialBookForm()

    context = {
        'form'      : form,
        'monitoring': monitoring,
        'business'  : business,
        'title'     : 'Livru Kontabilidade Foun',
        'legend'    : f"Anexa dokumentu ba monitorizasaun loron {monitoring.monitoring_date}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def financial_book_edit(request, business_hashid, monitoring_pk, pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj        = get_object_or_404(FinancialBook, id=pk, monitoring=monitoring)

    if request.method == 'POST':
        form = FinancialBookForm(request.POST, request.FILES, instance=obj)
        if form.is_valid():
            instance            = form.save(commit=False)
            instance.updated_by = request.user
            instance.save()
            messages.success(request, "Livru kontabilidade atualiza ho susesu!")
            return _benef_redirect(business)
    else:
        form = FinancialBookForm(instance=obj)

    context = {
        'form'      : form,
        'obj'       : obj,
        'monitoring': monitoring,
        'business'  : business,
        'title'     : 'Edita Livru Kontabilidade',
        'legend'    : f"Atualiza dokumentu {obj.title}",
    }
    return render(request, 'Dash/Forms/form.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def financial_book_delete(request, business_hashid, monitoring_pk, pk):
    business   = get_object_or_404(Business, hashed=business_hashid)
    monitoring = get_object_or_404(BusinessImpactMonitoring, id=monitoring_pk, business=business)
    obj        = get_object_or_404(FinancialBook, id=pk, monitoring=monitoring)

    if request.method == 'POST':
        if obj.file:
            obj.file.delete()
        obj.delete()
        messages.success(request, "Livru kontabilidade hamoos ho susesu!")
        return _benef_redirect(business)

    context = {
        'obj'    : obj,
        'title'  : 'Hamoos Livru Kontabilidade',
        'message': f"Boot hakarak hamoos dokumentu {obj.title}?",
    }
    return render(request, 'Dash/confirm_delete.html', context)