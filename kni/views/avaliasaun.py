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
from django.utils import timezone


@login_required
@allowed_users(allowed_roles=['KNI'])
def avaliasaun(request):
    group = request.user.groups.all()[0].name
    context ={
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'av-dash', 'link_text':'Avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun/option.html', context)    

@login_required
@allowed_users(allowed_roles=['KNI'])
def avalia_list(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.objects.prefetch_related('negosiu', 'Pnegosiu').all()
    context ={
        'benefs': benefs,
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun/list.html', context)

@login_required
@allowed_users(allowed_roles=['KNI'])
def avalia_list2(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.objects.prefetch_related('negosiu', 'Pnegosiu','negosiu__monitorings','negosiu__baseline',).all()
    context ={
        'benefs': benefs,
        'group':group,
        'title': 'Avaliasaun Benefisiariu Geral',
        'legend': 'Avaliasaun Geral KNI',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun/listm.html', context)

@login_required
@allowed_users(allowed_roles=['KNI'])
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
                'link_name': 'kni-dash',
                'link_text': 'Painel KNI'
            },
        ],
    }
    return render(request, 'avaliasaun/list2.html', context)

@login_required
@allowed_users(allowed_roles=['KNI'])
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
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text':'Lista avaliasaun Benefisiariu'}
        ],
    }
    return render(request, 'avaliasaun/forms.html', context)



@login_required
@allowed_users(allowed_roles=['Employee', 'KNI'])
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
        'legend': 'Depois Apoiu Monitoring',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'benef-evaluation-list', 'link_text': 'Lista Avaliasaun Benefisiariu'},
            {'link_name': 'baseline-list', 'link_text': 'Lista Baseline'},
            {'link_name': 'add-monits', 'link_text': f'Monitorizasaun: {business.name}', 'link_param': business.hashed}
        ],
    }

    return render(request, 'avaliasaun/forms.html', context)

@login_required
@allowed_users(allowed_roles=['KNI'])
@transaction.atomic
def baseline_create(request, hashid):
    business = get_object_or_404(Business, hashed=hashid)
    if hasattr(business, 'baseline'):
        messages.warning(request, f"Baseline ba negósiu '{business.name}' iha ona.")
        return redirect('baseline-list')
    if not business.benefisiariu:
        messages.error(request, "Benefisiariu la iha dadus kompletu. Favor kompleta dadus benefisiariu uluk.")
        return redirect('benefisiariu-update', hashed=business.benefisiariu.hashed)
    if request.method == 'POST':
        form = BusinessBaselineForm(request.POST)
        if form.is_valid():
            obj = form.save(commit=False)
            obj.business = business
            obj.created_by = request.user
            obj.created_at = timezone.now()
            obj.save()
            
            messages.success(request, f"Baseline ba '{business.name}' rai ho sukses.")
            return redirect('baseline-list')
        else:
            messages.error(request, "Formulariu la validu. Favor verifika dadus.")
    else:
        initial_data = {}
        if business.benefisiariu:
            initial_data = {
                'note': f"Baseline ba {business.name} - {business.benefisiariu.name}"
            }
        form = BusinessBaselineForm(initial=initial_data)
    
    context = {
        'form': form,
        'business': business,
        'title': f'Input Baseline - {business.name}',
        'legend': 'Baseline Antes Apoiu',
        'button_text': 'Rai Baseline',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text': 'Lista Avaliasaun Benefisiariu'},
            {'link_name': 'baseline-list', 'link_text': 'Lista Baseline'},
            {'link_name': 'add-baseline', 'link_text': f'Baseline: {business.name}', 'link_param': business.hashed}
        ],
    }
    return render(request, 'avaliasaun/forms.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def baseline_list(request):
    group = request.user.groups.all()[0].name
    baselines = BusinessBaseline.objects.select_related('business', 'business__benefisiariu')
    context = {
        'group':group,
        'baselines': baselines,
        'title': 'Lista Baseline',
        'legend': 'Dadus Antes Apoiu',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text': 'Lista Avaliasaun Benefisiariu'},
            {'link_name': 'baseline-list', 'link_text': 'Lista Avaliasaun Antes Apoiu'}
        ],
    }
    return render(request, 'avaliasaun/baseline_list.html', context)

@login_required
@allowed_users(allowed_roles=['KNI'])
def monitoring_list(request):
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
        'title': 'Lista Monitoring',
        'legend': 'Dadus Monitoring',
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
            {'link_name': 'geral-kni', 'link_text': 'Lista Benefisiariu'},
            {'link_name': 'list-ava', 'link_text': 'Lista Avaliasaun Benefisiariu'},
            {'link_name': 'monitoring-list', 'link_text': 'Lista Avaliasaun Depois Apoiu'},
        ],
    }

    return render(request, 'avaliasaun/monitoring_list.html', context)