import uuid
from django.shortcuts import render
from benefisiariu.models import BenefisiariuUser
from django.shortcuts import render, redirect, get_object_or_404
from benefisiariu.models import BenefisiariuUser
from benefisiariu.forms import BenefisiariuUserForm
from config.decorators import allowed_users
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def benefisiariu_user_list(request):
    group = request.user.groups.all()[0].name
    data = BenefisiariuUser.objects.select_related("benefisiariu", "user").order_by("benefisiariu__name")
    context = {
        'group':group,
        "data": data,
        "legend": "Benefisiariu User",
        "title": "Benefisiariu User",
        
    }
    return render(request, "benefisiariu_user/list.html", context)

@login_required
def benefisiariu_user_edit(request, pk):
    obj = get_object_or_404(BenefisiariuUser, pk=pk)
    if request.method == "POST":
        form = BenefisiariuUserForm(request.POST, instance=obj)
        if form.is_valid():
            form.save()
            return redirect("benefisiariu-user-list")
    else:
        form = BenefisiariuUserForm(instance=obj)
    context = {
            "form": form,
            "legend": "Edit Benefisiariu User",
    },
    return render(request, "benefisiariu_user/form.html", context)

@login_required
def benefisiariu_user_delete(request, pk):
    obj = get_object_or_404(BenefisiariuUser, pk=pk)
    obj.delete()
    messages.danger(request, f'Suseso Elimina ona dados')
    return redirect("benefisiariu-user-list")

@login_required
def benefisiariu_user_reset_password(request, pk):
    obj = get_object_or_404(BenefisiariuUser, pk=pk)
    user_account = obj.user 
    default_password = "Password_123"
    user_account.set_password(default_password)
    user_account.save()
    messages.success(request, f'Password ba user {user_account.username} reset ona ba: {default_password}')
    return redirect("benefisiariu-user-list")