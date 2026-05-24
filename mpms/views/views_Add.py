# views/mpms.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction

from config.decorators import allowed_users

from mpms.models import (
    mpmsEmpresa,
    mpmsLokalizasaun,
    mpmsLisensamentu,
    mpmsKapital,
    mpmsEmpregador,
    mpmsMateriaPrima,
    mpmsAtividade,
)

from mpms.forms import (
    MpmsEmpresaForm,
    MpmsLokalizasaunForm,
    MpmsLisensamentuForm,
    MpmsKapitalForm,
    MpmsEmpregadorForm,
    MpmsMateriaPrimaForm,
    MpmsAtividadeForm,
)

from benefisiariu.models import Benefisiariu


# =========================================================
# 1. LIST EMPRESA
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
def mpms_empresa_list(request):

    empresas = mpmsEmpresa.objects.select_related(
        'benefisiariu',
        'tipo_atividade'
    ).all()

    context = {
        'empresas': empresas,
        'title': 'Lista Empresa MPMS',
        'legend': 'Lista Empresa MPMS',
    }

    return render(request, 'mpms/list.html', context)


# =========================================================
# 2. CREATE EMPRESA
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
@transaction.atomic
def mpms_empresa_create(request, benef_hash):

    benef = get_object_or_404(
        Benefisiariu,
        hashed=benef_hash
    )

    if request.method == 'POST':

        form = MpmsEmpresaForm(request.POST)

        if form.is_valid():

            obj = form.save(commit=False)
            obj.benefisiariu = benef
            obj.save()

            messages.success(
                request,
                'Empresa MPMS konsege rai ho sukses.'
            )

            return redirect(
                'mpms-detail',
                obj.hashed
            )

    else:
        form = MpmsEmpresaForm()

    context = {
        'form': form,
        'benef': benef,
        'title': 'Registu Empresa',
        'legend': 'Registu Empresa MPMS',
    }

    return render(request, 'mpms/forms.html', context)


# =========================================================
# 3. DETAIL PAGE
#    INPUT STEP BY STEP
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
def mpms_detail(request, hashid):

    empresa = get_object_or_404(
        mpmsEmpresa,
        hashed=hashid
    )

    context = {
        'empresa': empresa,
        'title': 'Detail Empresa MPMS',
        'legend': 'Detail Empresa',
    }

    return render(request, 'mpms/detail.html', context)


# =========================================================
# 4. LOKALIZASAUN
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
@transaction.atomic
def mpms_lokalizasaun_create(request, hashid):

    empresa = get_object_or_404(
        mpmsEmpresa,
        hashed=hashid
    )

    try:
        instance = empresa.lokalizasaun
    except:
        instance = None

    if request.method == 'POST':

        form = MpmsLokalizasaunForm(
            request.POST,
            instance=instance
        )

        if form.is_valid():

            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()

            messages.success(
                request,
                'Lokalizasaun konsege rai.'
            )

            return redirect(
                'mpms-detail',
                empresa.hashed
            )

    else:

        form = MpmsLokalizasaunForm(
            instance=instance
        )

    context = {
        'form': form,
        'empresa': empresa,
        'title': 'Lokalizasaun Empresa',
        'legend': 'Input Lokalizasaun',
    }

    return render(request, 'mpms/forms.html', context)


# =========================================================
# 5. LISENSAMENTU
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
@transaction.atomic
def mpms_lisensamentu_create(request, hashid):

    empresa = get_object_or_404(
        mpmsEmpresa,
        hashed=hashid
    )

    try:
        instance = empresa.lisensamentu
    except:
        instance = None

    if request.method == 'POST':

        form = MpmsLisensamentuForm(
            request.POST,
            instance=instance
        )

        if form.is_valid():

            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()

            messages.success(
                request,
                'Lisensamentu konsege rai.'
            )

            return redirect(
                'mpms-detail',
                empresa.hashed
            )

    else:

        form = MpmsLisensamentuForm(
            instance=instance
        )

    context = {
        'form': form,
        'empresa': empresa,
        'title': 'Lisensamentu',
        'legend': 'Input Lisensamentu',
    }

    return render(request, 'mpms/forms.html', context)


# =========================================================
# 6. KAPITAL
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
@transaction.atomic
def mpms_kapital_create(request, hashid):

    empresa = get_object_or_404(
        mpmsEmpresa,
        hashed=hashid
    )

    try:
        instance = empresa.kapital
    except:
        instance = None

    if request.method == 'POST':

        form = MpmsKapitalForm(
            request.POST,
            instance=instance
        )

        if form.is_valid():

            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()

            messages.success(
                request,
                'Kapital konsege rai.'
            )

            return redirect(
                'mpms-detail',
                empresa.hashed
            )

    else:

        form = MpmsKapitalForm(
            instance=instance
        )

    context = {
        'form': form,
        'empresa': empresa,
        'title': 'Kapital',
        'legend': 'Input Kapital',
    }

    return render(request, 'mpms/forms.html', context)


# =========================================================
# 7. EMPREGADOR
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
@transaction.atomic
def mpms_empregador_create(request, hashid):

    empresa = get_object_or_404(
        mpmsEmpresa,
        hashed=hashid
    )

    try:
        instance = empresa.empregador
    except:
        instance = None

    if request.method == 'POST':

        form = MpmsEmpregadorForm(
            request.POST,
            instance=instance
        )

        if form.is_valid():

            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()

            messages.success(
                request,
                'Dadus empregador konsege rai.'
            )

            return redirect(
                'mpms-detail',
                empresa.hashed
            )

    else:

        form = MpmsEmpregadorForm(
            instance=instance
        )

    context = {
        'form': form,
        'empresa': empresa,
        'title': 'Empregador',
        'legend': 'Input Empregador',
    }

    return render(request, 'mpms/forms.html', context)


# =========================================================
# 8. MATERIA PRIMA
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
@transaction.atomic
def mpms_materia_create(request, hashid):

    empresa = get_object_or_404(
        mpmsEmpresa,
        hashed=hashid
    )

    try:
        instance = empresa.materia_prima
    except:
        instance = None

    if request.method == 'POST':

        form = MpmsMateriaPrimaForm(
            request.POST,
            instance=instance
        )

        if form.is_valid():

            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()

            messages.success(
                request,
                'Materia prima konsege rai.'
            )

            return redirect(
                'mpms-detail',
                empresa.hashed
            )

    else:

        form = MpmsMateriaPrimaForm(
            instance=instance
        )

    context = {
        'form': form,
        'empresa': empresa,
        'title': 'Materia Prima',
        'legend': 'Input Materia Prima',
    }

    return render(request, 'mpms/forms.html', context)


# =========================================================
# 9. ATIVIDADE
# =========================================================

@login_required
@allowed_users(allowed_roles=['KNI', 'Employee'])
@transaction.atomic
def mpms_atividade_create(request, hashid):

    empresa = get_object_or_404(
        mpmsEmpresa,
        hashed=hashid
    )

    if request.method == 'POST':

        form = MpmsAtividadeForm(request.POST)

        if form.is_valid():

            obj = form.save(commit=False)
            obj.empresa = empresa
            obj.save()

            messages.success(
                request,
                'Atividade konsege rai.'
            )

            return redirect(
                'mpms-detail',
                empresa.hashed
            )

    else:

        form = MpmsAtividadeForm()

    context = {
        'form': form,
        'empresa': empresa,
        'title': 'Atividade',
        'legend': 'Input Atividade',
    }

    return render(request, 'mpms/forms.html', context)