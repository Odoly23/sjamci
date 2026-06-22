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
@allowed_users(allowed_roles=['mpms'])
def avaliasaun_mpms(request):
    group = request.user.groups.all()[0].name
    context ={
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral MPMS',
        'link_antes': [
            {'link_name': 'dash-mpms', 'link_text': 'Painel MPMS'},
            {'link_name': 'mpms-list', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'ava-mpms', 'link_text':'Avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'Avaliasaun_mpms/option.html', context)    

@login_required
@allowed_users(allowed_roles=['mpms'])
def avalia_list_mpms(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS").all()
    context ={
        'benefs': benefs,
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral MPMS',
        'link_antes': [
            {'link_name': 'dash-mpms', 'link_text': 'Painel MPMS'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'Avaliasaun_mpms/list.html', context)

@login_required
@allowed_users(allowed_roles=['mpms'])
def avalia_list2_mpms(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.objects.filter(Pnegosiu__program_type__name="MPMS").prefetch_related('negosiu', 'Pnegosiu','negosiu__monitorings','negosiu__baseline',).all()
    context ={
        'benefs': benefs,
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral MPMS',
        'link_antes': [
            {'link_name': 'dash-mpms', 'link_text': 'Painel MPMS'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'Avaliasaun_mpms/listm.html', context)

@login_required
@allowed_users(allowed_roles=['mpms'])
def benef_evaluation_list(request):
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
                'link_name': 'dash-mpms',
                'link_text': 'Painel KNI'
            },
        ],
    }
    return render(request, 'Avaliasaun_mpms/list2.html', context)

@login_required
@allowed_users(allowed_roles=['Employee', 'mpms'])
@transaction.atomic
def monitoring_create_mpms(request, hashid):
    group = request.user.groups.all()[0].name
    business = get_object_or_404(Business, hashed=hashid)
    if not BusinessBaseline.objects.filter(business=business).exists():
        messages.warning(request, "Presiza halo Avaliasaun Antes.")
        return redirect('avalia-list2-mpms')
    tinan = Year.active_objects.filter(is_active=True).first()
    if not tinan:
        messages.error(request, "Tinan ativu la ejiste! Favor ativa tinan ida iha admin antes.")
        return redirect('avalia-list2-mpms')
    if request.method == 'POST':
        form = BusinessMonitoringForm(request.POST, request.FILES)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.business = business
            obj.verification_status = 'Pending'
            if hasattr(obj, 'uploaded_by'):
                obj.uploaded_by = request.user
            obj.year = tinan
            obj.save()            
            messages.success(request, "Avaliasaun Depois Susesu Hein Konfirmasaun")
            return redirect('avalia-list2-mpms')
    else:
        form = BusinessMonitoringForm()
        
    context = {
        'form': form,
        'business': business,
        'group':group,
        'title': 'Input Monitoring',
        'legend': 'Depois Apoiu Monitoring',
        'link_antes': [
            {'link_name': 'dash-mpms', 'link_text': 'Painel MPMS'},
            {'link_name': 'mpms-list', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'ava-mpms', 'link_text':'Avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'Avaliasaun_mpms/forms.html', context)


@login_required
@allowed_users(allowed_roles=['mpms'])
@transaction.atomic
def baseline_create_mpms(request, hashid):
    group = request.user.groups.all()[0].name
    business = get_object_or_404(Business, hashed=hashid)
    if BusinessBaseline.objects.filter(business=business).exists():
        messages.warning(request, "Baseline ba negósiu ida ne'e iha ona.")
        return redirect('avalia-list2-mpms')        
    if request.method == 'POST':
        form = BusinessBaselineForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.business = business
            if hasattr(obj, 'created_by'):
                obj.created_by = request.user
            obj.save()            
            messages.success(request, "Avaliasaun Antes Susesu.")
            return redirect('avalia-list2-mpms')
    else:
        form = BusinessBaselineForm()
    context = {
        'form': form,
        'group':group,
        'business': business,
        'title': 'Input Baseline',
        'legend': 'Baseline Antes Apoiu',
        'link_antes': [
            {'link_name': 'dash-mpms', 'link_text': 'Painel MPMS'},
            {'link_name': 'mpms-list', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'ava-mpms', 'link_text':'Avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'Avaliasaun_mpms/forms.html', context)

@login_required
@allowed_users(allowed_roles=['mpms'])
def baseline_list_mpms(request):
    group = request.user.groups.all()[0].name
    baselines = BusinessBaseline.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="MPMS").select_related('business', 'business__benefisiariu').distinct()
    context = {
        'baselines': baselines,
        'title': 'Lista Baseline',
        'legend': 'Dadus Antes Apoiu',
        'group':group,
        'link_antes': [
            {'link_name': 'dash-mpms', 'link_text': 'Painel MPMS'},
            {'link_name': 'mpms-list', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'ava-mpms', 'link_text':'Avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'Avaliasaun_mpms/baseline_list.html', context)

@login_required
@allowed_users(allowed_roles=['mpms'])
def monitoring_list_mpms(request):
    group = request.user.groups.all()[0].name
    monitorings = BusinessMonitoring.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="MPMS").select_related('business', 'business__benefisiariu').distinct()
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
        'title': 'Lista Monitoring',
        'legend': 'Dadus Monitoring',
        'group':group,
        'link_antes': [
            {'link_name': 'dash-mpms', 'link_text': 'Painel MPMS'},
            {'link_name': 'mpms-list', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'ava-mpms', 'link_text':'Avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'Avaliasaun_mpms/monitoring_list.html', context)
