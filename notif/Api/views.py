from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Count, Q
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from notif.models import Notification

class APINotifBadge(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        data = {
            "total": Notification.objects.filter(receiver=request.user, is_read=False).count(),
            "pedidu": Notification.objects.filter(receiver=request.user, is_read=False, notif_type='PEDIDU').count(),
            "fund": Notification.objects.filter(receiver=request.user, is_read=False, notif_type='FUND').count(),
            "cash": Notification.objects.filter(receiver=request.user, is_read=False, notif_type='CASHFLOW').count()
        }
        return Response(data)

class APINotifList(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(receiver=request.user, is_read=False).select_related('sender').order_by('-id')[:10]
        data = []
        for x in qs:
            data.append({
                'id': x.id,
                'title': x.title,
                'message': x.message,
                'read': x.is_read,
                'type': x.notif_type,
                'link': x.link,
                'sender': x.sender.username,
                'created_at': x.created_at if hasattr(x, 'created_at') else None
            })

        return Response(data)

class APINotifRead(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request, pk):
        notif = get_object_or_404(Notification, pk=pk,  receiver=request.user)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
        return Response({"success": True})