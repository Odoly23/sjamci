from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from config.decorators import allowed_users
from django.db.models import Sum, Count, F, Max
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from custom.models import Minister, Diresaun, Position, Municipality, AdministrativePost, Village, \
							Sector, Status, Bussines_size, Category_Emp, Year, Faze
from benefisiariu.models import Benefisiariu, AddressTL, Photo, AddressOrigin
from kni.models import    Business, LocBussiness, Program, Employee, Finance


class APISexu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    def get(self, request, format=None):
        label = []
        obj = []
        sexu_choices = ['Mane', 'Feto']
        for s in sexu_choices:
            total = Benefisiariu.objects.filter(sex=s).count()
            label.append(s)
            obj.append(total)
        data = {
            'label': label,
            'obj': obj
        }
        return Response(data)