import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.views.decorators.http import require_POST
from django.db import transaction
from config.decorators import allowed_users
from users.models import Emp, EmpPosition, EmpDivision, EmpUser, EmpPhoto
from users.forms import EmpForm, EmpPositionForm, EmpDivisionForm
from users.utils import criar_ou_atualiza_user

@login_required
@allowed_users(allowed_roles=['admin'])
def PList(request):
    group = request.user.groups.first().name if request.user.groups.exists() else None
    objects = EmpUser.objects.select_related('emp', 'user').prefetch_related('user__groups').all()
    context = {
        'group': group,
        'objects': objects,
        'title': 'Lista Utilizador',
        'legend': 'Lista Utilizador',
        'link_antes': [{'link_name': "u-list", 'link_text': "Lista Utilizador"}],
    }
    return render(request, 'users/list.html', context)

@login_required
def emp_detail(request, pk):
    emp = get_object_or_404(Emp.objects.select_related('created_by'),pk=pk)
    position = emp.positions.filter(is_active=True).first()
    division = emp.divisions.filter(is_active=True).first()
    photo = getattr(emp, 'photo', None)
    empuser = getattr(emp, 'account', None)
    contact = {
        'phone': emp.phone,
        'email': empuser.user.email if empuser and empuser.user else None
    }
    context = {
        'legend': 'Detallu Funcionariu',
        'title': 'Detallu Funcionariu',
        'obj': emp,
        'position': position,
        'division': division,
        'photo': photo,
        'membrouser': empuser,
        'contact': contact,
    }
    return render(request, 'users/detail.html', context)

@login_required
@allowed_users(allowed_roles=['admin'])
def EmpAdd(request):
    group = request.user.groups.first().name if request.user.groups.exists() else None
    if request.method == 'POST':
        form = EmpForm(request.POST)
        if form.is_valid():
            instance = form.save(commit=False)
            instance.created_by = request.user
            instance.save()
            messages.success(request, f'Funcionariu {instance.name} aumenta ona. Favor kompleta Pozisaun ho Divizaun.')
            return redirect('emp-detail', pk=instance.pk)
    else:
        form = EmpForm()
    context = {
        'form': form,
        'group': group,
        'title': 'Aumenta Funcionariu',
        'legend': 'Aumenta Funcionariu'
    }
    return render(request, 'users/form.html', context)

@login_required
@allowed_users(allowed_roles=['admin'])
def emp_update(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    form = EmpForm(request.POST or None, instance=emp)
    if form.is_valid():
        form.save()
        messages.success(request, 'Dadus Funcionariu atualiza ho susesu!')
        return redirect('emp-detail', pk=emp.pk)
    context = {
        'legend': 'Atualiza Dadus Funcionariu',
        'title': 'Atualiza Dadus Funcionariu',
        'form': form,
        'emp': emp,
    }
    return render(request, 'users/form.html', context)

@login_required
@allowed_users(allowed_roles=['admin'])
def emp_delete(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    if request.method == 'POST':
        emp.delete()
        messages.success(request, 'Funcionariu halakon ho susesu!')
        return redirect('u-list')
    context = {
        'legend': 'Halakon Funcionariu',
        'emp': emp,
    }
    return render(request, 'users/emp_confirm_delete.html', context)


@login_required
@allowed_users(allowed_roles=['admin'])
@transaction.atomic
def empposition_update(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    instance, created = EmpPosition.objects.get_or_create(employee=emp)
    form = EmpPositionForm(request.POST or None, instance=instance)
    if form.is_valid():
        position_obj = form.save(commit=False)
        position_obj.employee = emp
        position_obj.save()
        user, group_name = criar_ou_atualiza_user(emp)
        messages.success(request, f"Pozisaun atualiza. User: {user.username} Group: {group_name}")
        return redirect('emp-detail', pk=emp.pk)
    else:
        form = EmpPositionForm(instance=instance)
    context = {
        'legend': 'Atualiza Pojisaun',
        'title': 'Atualiza Pojisaun',
        'form': form,
        'emp': emp,
    }
    return render(request, 'users/form.html', context)

@login_required
@allowed_users(allowed_roles=['admin'])
def empdivision_update(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    instance, created = EmpDivision.objects.get_or_create(employee=emp)
    form = EmpDivisionForm(request.POST or None, instance=instance)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.employee = emp
        obj.save()
        user, group_name = criar_ou_atualiza_user(emp)
        messages.success(request,  f"Divizaun atualiza. Group: {group_name}")
        messages.success(request, 'Divizaun atualiza ho susesu!')
        return redirect('emp-detail', pk=emp.pk)
    context = {
        'legend': 'Atualiza Divizaun',
        'title': 'Atualiza Divizaun',
        'form': form,
        'emp': emp,
    }
    return render(request, 'users/form.html', context)

@login_required
@require_POST
def upload_photo(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    photo, created = EmpPhoto.objects.get_or_create(emp=emp)
    if 'image' in request.FILES:
        photo.image = request.FILES['image']
        photo.save()
        messages.success(request, 'Foto atualiza ho susesu!')
    else:
        messages.error(request, 'Favor hili foto uluk.')
    return redirect('emp-detail', pk=pk)

@login_required
@allowed_users(allowed_roles=['admin'])
def audit_login_list(request):
    from.models import AuditLogin
    logs = AuditLogin.objects.select_related('user').all().order_by('-login_time')
    context = {
        'legend': 'Audit Login',
        'title': 'Audit Login',
        'logs': logs,
    }
    return render(request, 'users/audit_login_list.html', context)