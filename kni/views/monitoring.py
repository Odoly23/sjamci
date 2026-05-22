@login_required
@allowed_users(allowed_roles=['KNI', 'Officer'])
@transaction.atomic
def monitoring_review(request, hashid):

    obj = get_object_or_404(BusinessMonitoring, hashed=hashid)

    if request.method == 'POST':

        action = request.POST.get('action')

        if action == 'verify':

            obj.verification_status = 'Verified'

            messages.success(request, "Monitoring verifikadu.")

        elif action == 'reject':

            obj.verification_status = 'Rejected'

            messages.warning(request, "Monitoring rejeitadu.")

        obj.save()

        return redirect('monitoring-detail', hashid=hashid)

    context = {
        'obj': obj,
        'title': 'Review Monitoring',
        'legend': 'Officer Verification'
    }

    return render(
        request,
        'monitoring/review.html',
        context
    )

@login_required
@allowed_users(allowed_roles=['Officer', 'KNI'])
def monitoring_pending_list(request):

    objects = BusinessMonitoring.objects.filter(
        verification_status='Pending'
    ).order_by('-monitoring_date')

    return render(
        request,
        'monitoring/pending_list.html',
        {'objects': objects}
    )