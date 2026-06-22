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
        selected_municipality_id = request.GET.get('municipality')
        program_names = ['KNI', 'KREDITU SUAVE', 'MPMS', 'MANUFATUREIRA', 'DNDI']
        mapobjects = LocBussiness.objects.filter(
            benefisiariu__in=Benefisiariu.active_objects.filter(
                Pnegosiu__program_type__name__in=program_names
            )
        ).select_related(
            'benefisiariu',
            'benefisiariu__photo',
            'municipality',
            'administrativepost',
            'village',
        ).distinct()

        if selected_municipality_id:
            mapobjects = mapobjects.filter(municipality_id=selected_municipality_id)

        total_benefisiariu = Benefisiariu.active_objects.filter(
            Pnegosiu__program_type__name__in=program_names
        ).distinct().count()

        total_business = Business.objects.filter(
            benefisiariu__in=Benefisiariu.active_objects.filter(
                Pnegosiu__program_type__name__in=program_names
            )
        ).distinct().count()

        locations = []
        for m in mapobjects:
            if m.latitude and m.longitude:
                photo_url = None
                if hasattr(m.benefisiariu, 'photo') and m.benefisiariu.photo:
                    photo_url = request.build_absolute_uri(m.benefisiariu.photo.image.url)

                locations.append({
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
            'total_benefisiariu': total_benefisiariu,
            'total_business': total_business,
            'selected_municipality_id': selected_municipality_id,
            'locations': locations,
        })