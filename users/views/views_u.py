import io, csv, datetime, hashlib, uuid
from config.decorators import allowed_users
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from users.models import Emp, EmpDivision, EmpPosition, EmpUser,  EmpPhoto, AuditLogin
from django.http import JsonResponse

@login_required
def UserProfile(request):
    group = request.user.groups.all()[0].name
    emp_user = get_object_or_404(EmpUser, user=request.user )
    profile = emp_user.emp
    photo = getattr(profile, 'empphoto',   None  )
    division = getattr(profile, 'employeedivision',  None  )
    position = getattr(profile, 'employeeposition',   None   )
    last_login = AuditLogin.objects.filter(user=request.user).order_by('-login_time').first()
    context = {
        'group': group,
        'profile': profile,
        'photo': photo,
        'division': division,
        'position': position,
        'last_login': last_login,
        'title': 'Profile Utilizador',
        'legend': 'Profile Utilizador',
    }
    return render( request, 'profile.html', context)


@login_required
def update_profile_ajax(request):
    if request.method == "POST":
        empuser = EmpUser.objects.get(user=request.user)
        emp = empuser.emp
        emp.name = request.POST.get('name')
        emp.sexo = request.POST.get('sexo')
        emp.phone = request.POST.get('phone')
        emp.save()
        return JsonResponse({
            'status': 'success'
        })
    return JsonResponse({
        'status': 'error'
    })

@login_required
def update_photo_ajax(request):

    if request.method == "POST":

        empuser = EmpUser.objects.get(user=request.user)
        emp = empuser.emp

        photo, created = EmpPhoto.objects.get_or_create(
            emp=emp
        )

        if request.FILES.get('image'):
            photo.image = request.FILES.get('image')
            photo.save()

        return JsonResponse({
            'status': 'success'
        })

    return JsonResponse({
        'status': 'error'
    })

@login_required
def manage_account_ajax(request):

    if request.method == "POST":

        user = request.user

        user.username = request.POST.get('username')
        user.email = request.POST.get('email')

        password = request.POST.get('password')

        if password:
            user.set_password(password)

        user.save()

        return JsonResponse({
            'status': 'success'
        })

    return JsonResponse({
        'status': 'error'
    })