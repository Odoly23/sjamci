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
from suave.models import CreditInfo
from collections import defaultdict

class APISumarioProgram(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        program_list = [
            ('KNI', 'KNI'),
            ('Kreditu Suave', 'KREDITU SUAVE'),
            ('MPMS', 'MPMS'),
            ('Manufatureira', 'MANUFATUREIRA'),
            ('DNDI', 'DNDI'),
        ]

        label = []
        obj = []
        locations = []

        for display_name, program_type_name in program_list:
            benefisiariu_qs = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name=program_type_name).distinct()
            total = benefisiariu_qs.count()
            label.append(display_name)
            obj.append(total)
            mapobjects = LocBussiness.objects.filter(benefisiariu__in=benefisiariu_qs).select_related(
                'benefisiariu','benefisiariu__photo',
                'municipality', 'administrativepost',
                'village',).distinct()
            for m in mapobjects:
                if m.latitude and m.longitude:
                    photo_url = None
                    if hasattr(m.benefisiariu, 'photo') and m.benefisiariu.photo:
                        photo_url = request.build_absolute_uri(m.benefisiariu.photo.image.url)

                    locations.append({
                        'program': display_name,
                        'latitude': m.latitude,
                        'longitude': m.longitude,
                        'benefisiariu_name': m.benefisiariu.name,
                        'address': m.address,
                        'municipality': m.municipality.name if m.municipality else None,
                        'administrativepost': m.administrativepost.name if m.administrativepost else None,
                        'village': m.village.name if m.village else None,
                        'aldeia': m.aldeia,
                        'photo_url': photo_url,
                    })

        return Response({
            'label': label,
            'obj': obj,
            'total': sum(obj),
            'locations': locations,
        })