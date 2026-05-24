import io, csv, datetime, hashlib, uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo, BeneficiariuEvaluation
from benefisiariu.forms import    BenefisiariuForm, AddressTLForm, AddressOriginForm, PhotoUploadForm, BeneficiariuEvaluationForm
from kni.models import Business, LocBussiness, Program, Employee, Finance, BusinessBaseline, BusinessMonitoring
from kni.forms import BusinessKNIForm, LocBusinessKNIForm, ProgramKNIForm, EmployeeKNIForm, FinanceKNIForm, BusinessMonitoringForm, BusinessBaselineForm
from custom.models import TIpu_Programa, Status, Year
from config.decorators import allowed_users



@login_required
@allowed_users(allowed_roles=['KS'])
def ks_avaliasaun(request):
    group = request.user.groups.all()[0].name
    context ={
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'dash-ks', 'link_text': 'Painel Kreditu Suave'},
            {'link_name': 'geral-ks', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'ks-ava', 'link_text':'Avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun_ks/option.html', context)    

@login_required
@allowed_users(allowed_roles=['KS'])
def avalia_list_ks(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").all()
    context ={
        'benefs': benefs,
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'dash-ks', 'link_text': 'Painel Kreditu Suave'},
            {'link_name': 'geral-ks', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun_ks/list.html', context)

@login_required
@allowed_users(allowed_roles=['KS'])
def avalia_list2_ks(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.objects.prefetch_related('negosiu', 'Pnegosiu','negosiu__monitorings','negosiu__baseline',).all()
    context ={
        'benefs': benefs,
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'dash-ks', 'link_text': 'Painel Kreditu Suave'},
            {'link_name': 'geral-ks', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun_ks/listm.html', context)

@login_required
@allowed_users(allowed_roles=['KS'])
def benef_evaluation_list_ks(request):
    filter_status = request.GET.get('status')
    benefs = Benefisiariu.objects.select_related('status').prefetch_related('evaluations').all()
    if filter_status:
        benefs = benefs.filter(evaluations__status=filter_status).distinct()
    total_ativu = BeneficiariuEvaluation.objects.filter(status='Ativu').count()
    total_laativu = BeneficiariuEvaluation.objects.filter(status='La_ativu').count()
    total_suspendu = BeneficiariuEvaluation.objects.filter(status='Suspendu').count()
    total_pending = BeneficiariuEvaluation.objects.filter(status='Pending').count()
    context = {
        'benefs': benefs,
        'filter_status': filter_status,
        'total_ativu': total_ativu,
        'total_laativu': total_laativu,
        'total_suspendu': total_suspendu,
        'total_pending': total_pending,
        'title': 'Lista Avaliasaun',
        'legend': 'Lista Avaliasaun Benefisiariu',
        'link_antes': [
            {
                'link_name': 'dash-ks',
                'link_text': 'Painel Kreditu Suave'
            },
        ],
    }
    return render(request, 'avaliasaun_ks/list2.html', context)

@login_required
@allowed_users(allowed_roles=['KS'])
@transaction.atomic
def evaluate_benef_ks(request, hashid):
    benef = get_object_or_404(Benefisiariu, hashed=hashid)
    if request.method == 'POST':
        form = BeneficiariuEvaluationForm(request.POST)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.benefisiariu = benef
            evaluation.save()
            status_obj = Status.objects.filter(name=evaluation.status).first()
            if status_obj:
                benef.status = status_obj
                benef.save()
            else:
                messages.error(request, f"Status '{evaluation.status}' la Ejiste iha tabela Status.")
                return redirect('ava-fh')
            messages.success(request, "Avalia ona ho susesu.")
            return redirect('ava-fh')

    else:
        form = BeneficiariuEvaluationForm()

    context = {
        'benef': benef,
        'form': form,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'dash-ks', 'link_text': 'Painel Kreditu Suave'},
            {'link_name': 'geral-ks', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text': 'Lista avaliasaun Benefisiariu'}
        ],
    }

    return render(request, 'avaliasaun_ks/forms.html', context)


@login_required
@allowed_users(allowed_roles=['Employee', 'KNI','KS'])
@transaction.atomic
def monitoring_create_ks(request, hashid):
    business = get_object_or_404(Business, hashed=hashid)
    if not hasattr(business, 'baseline'):
        messages.warning(request, "Presiza halo baseline antes monitoring.")
        return redirect('baseline-list')
    tinan = Year.active_objects.filter(is_active=True).first()
    if request.method == 'POST':
        form = BusinessMonitoringForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.business = business
            obj.verification_status = 'Pending'
            obj.uploaded_by = request.user
            obj.year = tinan
            obj.save()
            messages.success(request, "Monitoring hato'o ho status Pending.")
            return redirect('monitoring-list')
    else:
        form = BusinessMonitoringForm()
    context = {
        'form': form,
        'business': business,
        'title': 'Input Monitoring',
        'legend': 'Depois Apoiu Monitoring'
    }

    return render(request, 'avaliasaun_ks/forms.html', context)

@login_required
@allowed_users(allowed_roles=['KS','KNI'])
@transaction.atomic
def baseline_create(request, hashid):
    business = get_object_or_404(Business, hashed=hashid)
    if hasattr(business, 'baseline'):
        messages.warning(
            request,
            "Baseline ba negósiu ida ne'e iha ona.")
        return redirect('baseline-list')
    if request.method == 'POST':
        form = BusinessBaselineForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.business = business
            obj.created_by = request.user
            obj.save()
            messages.success(request, "Baseline rai ho sukses.")
            return redirect('baseline-list')

    else:
        form = BusinessBaselineForm()
    context = {
        'form': form,
        'business': business,
        'title': 'Input Baseline',
        'legend': 'Baseline Antes Apoiu',
    }
    return render(request, 'avaliasaun_ks/forms.html', context)

@login_required
@allowed_users(allowed_roles=['KS'])
def baseline_list(request):

    baselines = BusinessBaseline.objects.select_related(
        'business',
        'business__benefisiariu'
    )

    context = {
        'baselines': baselines,
        'title': 'Lista Baseline',
        'legend': 'Dadus Antes Apoiu',
    }

    return render(
        request,
        'avaliasaun_ks/baseline_list.html',
        context
    )

@login_required
@allowed_users(allowed_roles=['KS'])
def monitoring_list(request):
    group = request.user.groups.all()[0].name
    monitorings = BusinessMonitoring.objects.select_related('business', 'business__benefisiariu')
    pending = monitorings.filter(verification_status='Pending').count()
    verified = monitorings.filter(verification_status='Verified').count()
    critical = monitorings.filter(monitoring_status='Critical').count()
    risk = monitorings.filter(monitoring_status='Risk').count()
    normal = monitorings.filter(monitoring_status='Normal').count()
    context = {
        'monitorings': monitorings,
        'pending': pending,
        'verified': verified,
        'critical': critical,
        'risk': risk,
        'normal': normal,
        'group':group,
        'title': 'Lista Monitoring',
        'legend': 'Dadus Monitoring',
    }

    return render(request, 'avaliasaun_ks/monitoring_list.html', context)