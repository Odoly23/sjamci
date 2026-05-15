import io, csv, datetime, hashlib, uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo, BeneficiariuEvaluation
from benefisiariu.forms import    BenefisiariuForm, AddressTLForm, AddressOriginForm, PhotoUploadForm, BeneficiariuEvaluationForm
from kni.models import Business, LocBussiness, Program, Employee, Finance
from kni.forms import BusinessKNIForm, LocBusinessKNIForm, ProgramKNIForm, EmployeeKNIForm, FinanceKNIForm
from custom.models import TIpu_Programa, Status
from config.decorators import allowed_users


@login_required
@allowed_users(allowed_roles=['KNI'])
def avalia_list(request):
    group = request.user.groups.all()[0].name
    benefs = Benefisiariu.objects.all()
    context ={
        'benefs': benefs,
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
            try:
                benef.status = Status.objects.get(pk=1) 
                benef.save()
            except Status.DoesNotExist:
                pass
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