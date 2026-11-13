import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST

from benefisiariu.forms import BenefisiariuUserForm
from benefisiariu.models import BenefisiariuUser
from config.decorators import allowed_users, user_group
from users.passwords import temporary_password

security_log = logging.getLogger('sjamci.security')

# Só administradór no ekipa KNI mak bele jere konta benefisiáriu
_ROLES = ['admin', 'KNI']


@login_required
@allowed_users(allowed_roles=_ROLES)
def benefisiariu_user_list(request):
    data = BenefisiariuUser.objects.select_related("benefisiariu", "user").order_by("benefisiariu__name")
    context = {
        'group': user_group(request.user),
        "data": data,
        "legend": "Benefisiariu User",
        "title": "Benefisiariu User",
    }
    return render(request, "benefisiariu_user/list.html", context)


@login_required
@allowed_users(allowed_roles=_ROLES)
def benefisiariu_user_edit(request, pk):
    obj = get_object_or_404(BenefisiariuUser, pk=pk)
    if request.method == "POST":
        form = BenefisiariuUserForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dadus utilizador atualiza ho susesu.')
            return redirect("benefisiariu-user-list")
    else:
        form = BenefisiariuUserForm(instance=obj)
    context = {
        'group': user_group(request.user),
        "form": form,
        "title": "Edit Benefisiariu User",
        "legend": "Edit Benefisiariu User",
    }
    return render(request, "shared/form.html", context)


@login_required
@allowed_users(allowed_roles=_ROLES)
def benefisiariu_user_delete(request, pk):
    obj = get_object_or_404(BenefisiariuUser, pk=pk)
    if request.method == 'POST':
        security_log.info('benefisiariu user deleted: target=%s by=%s', obj.user.username, request.user.username)
        obj.delete()
        messages.success(request, 'Dadus elimina ona ho susesu.')
        return redirect("benefisiariu-user-list")
    context = {
        'group': user_group(request.user),
        'obj': obj,
        'title': 'Hamoos Benefisiariu User',
        'cancel_url': reverse('benefisiariu-user-list'),
    }
    return render(request, 'shared/confirm_delete.html', context)


@login_required
@allowed_users(allowed_roles=_ROLES)
@require_POST
def benefisiariu_user_reset_password(request, pk):
    obj = get_object_or_404(BenefisiariuUser, pk=pk)
    user_account = obj.user
    new_password = temporary_password()
    user_account.set_password(new_password)
    user_account.save()
    security_log.info('password reset: target=%s by=%s', user_account.username, request.user.username)
    messages.success(
        request,
        f"Password ba user {user_account.username} reset ona. Password temporáriu: {new_password} (hatudu dala ida de'it)",
    )
    return redirect("benefisiariu-user-list")
