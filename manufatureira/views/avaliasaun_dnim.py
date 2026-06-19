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
@allowed_users(allowed_roles=['dnim'])
def avaliasaun_dnim(request):
    group = request.user.groups.all()[0].name
    context ={
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral Manufatureira',
        'link_antes': [
            {'link_name': 'dash-man', 'link_text': 'Painel Manufatureira'},
            {'link_name': 'geral_man', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'av-dash', 'link_text':'Avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun_dnim/option.html', context)    

@login_required
@allowed_users(allowed_roles=['dnim'])
def dnimvalia_list(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.objects.filter(Pnegosiu__program_type__name="MANUFATUREIRA").all()
    context ={
        'benefs': benefs,
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'dash-man', 'link_text': 'Painel Manufatureira'},
            {'link_name': 'geral_man', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun_dnim/list.html', context)

@login_required
@allowed_users(allowed_roles=['dnim'])
def avalia_list2(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.objects.prefetch_related('negosiu', 'Pnegosiu','negosiu__monitorings','negosiu__baseline',).all()
    context ={
        'benefs': benefs,
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'dash-man', 'link_text': 'Painel Manufatureira'},
            {'link_name': 'geral_man', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun_dnim/listm.html', context)

@login_required
@allowed_users(allowed_roles=['dnim'])
def dnim_evaluation_list(request):
    group = request.user.groups.all()[0].name
    filter_status = request.GET.get('status')
    benefs = Benefisiariu.objects.select_related('status').prefetch_related('evaluations').filter(Pnegosiu__program_type__name="MANUFATUREIRA").all()
    if filter_status:
        benefs = benefs.filter(evaluations__status=filter_status).distinct()
    total_ativu = BeneficiariuEvaluation.objects.filter(status='Ativu').count()
    total_laativu = BeneficiariuEvaluation.objects.filter(status='La_ativu').count()
    total_suspendu = BeneficiariuEvaluation.objects.filter(status='Suspendu').count()
    total_pending = BeneficiariuEvaluation.objects.filter(status='Pending').count()
    context = {
        'group':group,  
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
                'link_name': 'dash-man',
                'link_text': 'Painel Manufatureira'
            },
        ],
    }
    return render(request, 'avaliasaun_dnim/list2.html', context)

@login_required
@allowed_users(allowed_roles=['dnim'])
@transaction.atomic
def evaluate_benef(request, hashid):
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
                return redirect('benef-evaluation-list')
            messages.success(request, "Avaliasaun sukses.")
            return redirect('benef-evaluation-list')
    else:
        form = BeneficiariuEvaluationForm()
    context = {
        'benef': benef,
        'form': form,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'dash-man', 'link_text': 'Painel Manufatureira'},
            {'link_name': 'geral_man', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun_dnim/forms.html', context)



@login_required
@allowed_users(allowed_roles=['Employee', 'dnim'])
@transaction.atomic
def monitoring_create(request, hashid):
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

    return render(request, 'avaliasaun_dnim/forms.html', context)

@login_required
@allowed_users(allowed_roles=['dnim'])
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
    return render(request, 'avaliasaun_dnim/forms.html', context)

@login_required
@allowed_users(allowed_roles=['dnim'])
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
        'avaliasaun_dnim/baseline_list.html',
        context
    )

@login_required
@allowed_users(allowed_roles=['dnim'])
def monitoring_list(request):
    monitorings = BusinessMonitoring.objects.select_related('business', 'business__benefisiariu')
    pending = monitorings.filter(verification_status='Pending').count()
    verified = monitorings.filter(verification_status='Verified'
    ).count()

    critical = monitorings.filter(
        monitoring_status='Critical'
    ).count()

    risk = monitorings.filter(
        monitoring_status='Risk'
    ).count()

    normal = monitorings.filter(
        monitoring_status='Normal'
    ).count()

    context = {
        'monitorings': monitorings,

        'pending': pending,
        'verified': verified,

        'critical': critical,
        'risk': risk,
        'normal': normal,

        'title': 'Lista Monitoring',
        'legend': 'Dadus Monitoring',
    }

    return render(
        request,
        'avaliasaun_dnim/monitoring_list.html',
        context
    )