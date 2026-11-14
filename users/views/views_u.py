import io, csv, datetime, hashlib, uuid
from config.decorators import allowed_users
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from users.models import Emp, EmpDivision, EmpPosition, EmpUser,  EmpPhoto, AuditLogin
from django.http import JsonResponse
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from seguransa.utils import password_was_changed, log_security_event

@login_required
def UserProfile(request):
    user_groups = request.user.groups.all()
    group = user_groups[0].name if user_groups.exists() else "No Group"
    emp_user = get_object_or_404(EmpUser, user=request.user)
    profile = emp_user.emp  
    photo = getattr(profile, 'photo', None)
    division = profile.divisions.filter(is_active=True).first()
    position = profile.positions.filter(is_active=True).first()
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
    return render(request, 'profile.html', context)

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
        try:
            empuser = EmpUser.objects.get(user=request.user)
            emp = empuser.emp
            photo, created = EmpPhoto.objects.get_or_create(emp=emp)            
            if request.FILES.get('image'):
                photo.image = request.FILES.get('image')
                photo.save()
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Laiha dokumentu imajen ne\'ebé simu'})
        except EmpUser.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User la terdaftar iha data Kariawan'})
    return JsonResponse({'status': 'error', 'message': 'Metodu tenke POST'})
    
@login_required
def manage_account_ajax(request):
    if request.method == "POST":
        user = request.user
        user.username = request.POST.get('username')
        user.email = request.POST.get('email')
        password = request.POST.get('password')
        if password:
            try:
                validate_password(password, user)
            except ValidationError as exc:
                return JsonResponse({'status': 'error', 'message': ' '.join(exc.messages)})
            user.set_password(password)
        user.save()
        if password:
            update_session_auth_hash(request, user)
            password_was_changed(user)
            log_security_event(request, 'Troka password', user)
        return JsonResponse({
            'status': 'success'
        })
    return JsonResponse({
        'status': 'error'
    })