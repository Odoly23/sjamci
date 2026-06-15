import csv, io, datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from config.decorators import allowed_users
from users.models import Emp, EmpPosition, EmpDivision, EmpUser, EmpPhoto
from users.forms import EmpForm, EmpPositionForm, EmpDivisionForm, UserForm
from django.http import JsonResponse
from django.views.decorators.http import require_POST
import json


@login_required
@allowed_users(allowed_roles=['admin'])
def PList(request):
	group = request.user.groups.all()[0].name
	objects = EmpUser.objects.all()
	context = {
		'group': group, 'objects': objects,
		'title': 'Lista Utilizador', 'legend': 'Lista Utilizador',
		'link_antes': [{'link_name':"u-list",'link_text':"Lista Utilizador"}],
        
	}
	return render(request, 'users/list.html', context)


@login_required
def emp_detail(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    position = EmpPosition.objects.filter(employee=emp).first()
    division = EmpDivision.objects.filter(employee=emp).first()
    empuser = EmpUser.objects.filter(emp=emp).first()
    context = {
        'legend': 'Detallu Funcionariu',
        'title': 'Detallu Funcionariu',
        'emp': emp,
        'position': position,
        'division': division,
        'empuser': empuser,
        'link_antes': [
        		{'link_name':"u-list",'link_text':"Lista Utilizador"},
        		 {'link_name':'emp-detail','link_text':'Dados Pessoal','link_param': emp.pk}
        		],
    }
    return render(request, 'users/detail.html', context)

@login_required
@allowed_users(allowed_roles=['admin'])
def EmpAdd(request):
	group = request.user.groups.all()[0].name
	if request.method == 'POST':
		form = EmpForm(request.POST)
		if form.is_valid():
			instance = form.save(commit=False)
			instance.save()
			messages.success(request, f'Aumenta ona.')
			return redirect('emp-detail', pk=instance.pk)
	else: form = EmpForm()
	context = {
		'form': form,'group':group,
		'title': 'Aumenta User', 'legend': 'Aumenta User'
	}
	return render(request, 'users/form.html', context)

@login_required
def emp_update(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    form = EmpForm(request.POST or None, instance=emp)
    if form.is_valid():
        form.save()
        messages.success(request, 'Dadus Funcionariu atualiza ho susesu!')
        return redirect('emp-detail', pk=emp.pk)
    context = {
        'legend': 'Atualiza Dadus Funcionariu',
        'form': form,
        'emp': emp,
    }
    return render(request, 'users/form.html', context)


@login_required
def emp_delete(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    if request.method == 'POST':
        emp.delete()
        messages.success(request, 'Funcionariu halakon ho susesu!')
        return redirect('emp-list')
    context = {
        'legend': 'Halakon Funcionariu',
        'emp': emp,
    }
    return render(request, 'emp/emp_confirm_delete.html', context)


@login_required
def empposition_update(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    instance = EmpPosition.objects.filter(employee=emp).first()
    form = EmpPositionForm(request.POST or None, instance=instance)

    if form.is_valid():
        instance = form.save(commit=False)
        instance.employee = emp
        instance.save()
        emp_division   = EmpDivision.objects.filter(employee=emp).first()
        position_name  = instance.position.name if instance.position else ""
        has_gabinete   = emp_division and emp_division.gabinete is not None
        has_diresaun   = emp_division and emp_division.dn is not None
        has_departamento = emp_division and emp_division.department is not None
        diresaun_code  = emp_division.dn.code.upper()  if (emp_division and emp_division.dn)  else ""
        dept_name      = emp_division.department.name.upper() if (emp_division and emp_division.department) else ""
        group_name = None
        if has_gabinete and not has_diresaun and not has_departamento:
            if "DIRECTOR GERAL" in position_name.upper():
                group_name = "admin"
            else:
                group_name = "staff"
        elif has_gabinete and has_diresaun and diresaun_code == "DNADMPEME":
            if not has_departamento:
                if "Xefe Departamento" in position_name.upper():
                    group_name = "XFD"
                else:
                    group_name = "staff"
            else:
                if "KREDITU SUAVE" in dept_name:
                    group_name = "KS"
                elif "KNI" in dept_name or "KOMPETISAUN" in dept_name:
                    group_name = "KNI"
                else:
                    group_name = "staff"
        elif has_gabinete and has_diresaun and diresaun_code == "DNIM":
            group_name = "dnim"
        else:
            group_name = "staff"
        name     = emp.name or ""
        first_word = (emp.name or "").strip().split()[0].lower()
        names = (emp.name or "").strip().split()
        first_name =  names[0] if len(names) >= 1 else ""
        last_name = " ".join(names[1:])  if len(names) >  1 else ""
        username   = f"{first_word}@#mci"
        if User.objects.filter(username=f"{first_word}@#mci{emp.id}").exists():
            username = f"{username}.{instance.id}"
        obj = User(
            username=username,
            password=make_password('MCI@#2026'),
            first_name=first_name,
            last_name=last_name,
        )
        obj.save()
        obj2 =  EmpUser(user=obj, emp=emp)
        obj2.save()
        if group_name:
            try:
                group = Group.objects.get(name=group_name)
                obj.groups.add(group)
            except Group.DoesNotExist:
                messages.warning(
                    request,
                    f"Group '{group_name}' la hetan iha sistema. "
                    f"User kria ona maibé laiha group."
                )

        messages.success(
            request,
            f"Pojisaun atualiza ho susesu! "
            f"User '{username}' kria ho group '{group_name}'. "
            f"Password default: MCI@#2026"
        )
        return redirect('emp-detail', pk=emp.pk)

    context = {
        'legend': 'Atualiza Pojisaun',
        'form': form,
        'emp': emp,
    }
    return render(request, 'users/form.html', context)

# ─── EMP DIVISION ────────────────────────────────────────────────────────────

@login_required
def empdivision_update(request, pk):
    emp = get_object_or_404(Emp, pk=pk)
    instance = EmpDivision.objects.filter(employee=emp).first()
    form = EmpDivisionForm(request.POST or None, instance=instance)
    if form.is_valid():
        obj = form.save(commit=False)
        obj.employee = emp
        obj.save()
        messages.success(request, 'Divizaun atualiza ho susesu!')
        return redirect('emp-detail', pk=emp.pk)
    context = {
        'legend': 'Atualiza Divizaun',
        'form': form,
        'emp': emp,
    }
    return render(request, 'users/form.html', context)




@login_required
def audit_login_list(request):
    from .models import AuditLogin
    logs = AuditLogin.objects.all().order_by('-login_time')
    context = {
        'legend': 'Audit Login',
        'logs': logs,
    }
    return render(request, 'emp/audit_login_list.html', context)