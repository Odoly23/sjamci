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
# =========================================================
# 1. SEXU BENEFISIARIU
# =========================================================

class APISexu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        label = []
        obj = []

        sexu_choices = ['Mane', 'Feto']

        for s in sexu_choices:

            total = Benefisiariu.active_objects.filter(
                Pnegosiu__program_type__name="KNI",
                sex=s
            ).distinct().count()

            label.append(s)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 2. MUNICIPIU BENEFISIARIU
# =========================================================

class APIMunicipiu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        label = []
        obj = []

        municipios = Municipality.objects.all().order_by('name')

        for m in municipios:

            total = Benefisiariu.active_objects.filter(
                Pnegosiu__program_type__name="KNI",
                locnegosiu__municipality=m
            ).distinct().count()

            label.append(m.name)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 3. STATUS PROGRAMA
# =========================================================

class APIStatusPrograma(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        label = []
        obj = []

        statuss = Status.objects.all()

        for s in statuss:

            total = Program.objects.filter(
                program_type__name="KNI",
                status=s
            ).count()

            label.append(s.name)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 4. APOIU KADA TINAN
# =========================================================

class APIApoiuTinan(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        label = []
        obj = []

        years = Year.objects.all().order_by('year')

        for y in years:

            total = Program.objects.filter(
                program_type__name="KNI",
                year=y
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            label.append(str(y.year))
            obj.append(float(total))

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 5. APOIU TUIR FAZE
# =========================================================

class APIFaze(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        label = []
        obj = []

        fazes = Faze.objects.exclude(name__in=["KREDITU", "mpms",'manufatur'])

        for f in fazes:

            total = Program.objects.filter(
                program_type__name="KNI",
                faze=f
            ).count()

            label.append(f.name)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 6. SECTOR NEGOSIU
# =========================================================

class APISector(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        label = []
        obj = []

        sectors = Sector.objects.all()

        for s in sectors:

            total = Business.objects.filter(
                benefisiariu__Pnegosiu__program_type__name="KNI",
                sector=s
            ).distinct().count()

            label.append(s.name)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 7. TRABALHADOR
# =========================================================

class APIEmployee(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        employees = Employee.objects.filter(
            business__benefisiariu__Pnegosiu__program_type__name="KNI"
        ).distinct()

        total_male = employees.aggregate(
            total=Sum('male')
        )['total'] or 0

        total_female = employees.aggregate(
            total=Sum('female')
        )['total'] or 0

        total_all = employees.aggregate(
            total=Sum('total')
        )['total'] or 0

        return Response({
            'label': ['Mane', 'Feto', 'Total'],
            'obj': [
                total_male,
                total_female,
                total_all
            ]
        })


# =========================================================
# 8. CREDIT REPAYMENT
# =========================================================

class APICreditRepayment(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        label = []
        obj = []

        repayment_choices = [
            'OnTime',
            'Late',
            'Stuck',
            'Done',
            'Failed',
            'Other',
        ]

        for r in repayment_choices:

            total = CreditInfo.objects.filter(
                business__benefisiariu__Pnegosiu__program_type__name="KNI",
                repayment_status=r
            ).count()

            label.append(r)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 9. KPI DASHBOARD
# =========================================================

class APIKPI(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):

        total_benef = Benefisiariu.active_objects.filter(
            Pnegosiu__program_type__name="KNI"
        ).distinct().count()

        total_business = Business.objects.filter(
            benefisiariu__Pnegosiu__program_type__name="KNI"
        ).distinct().count()

        total_budget = Program.objects.filter(
            program_type__name="KNI"
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_employee = Employee.objects.filter(
            business__benefisiariu__Pnegosiu__program_type__name="KNI"
        ).aggregate(
            total=Sum('total')
        )['total'] or 0

        return Response({
            'total_benefisiariu': total_benef,
            'total_business': total_business,
            'total_budget': float(total_budget),
            'total_employee': total_employee,
        })


class APIMun(APIView):
    permission_classes = [AllowAny]
    def get(self, request, format=None):
        muns = Municipality.objects.all().order_by('name')
        beneficiary_stats = (
            Benefisiariu.active_objects 
            .values(
                'addresstl__municipality__name',
                'sex',
                'marital'
            )
            .annotate(total=Count('id', distinct=True))
        )
        data_map = defaultdict(int)
        detail_pivot = defaultdict(lambda: {"Mane": 0, "Feto": 0, "Total": 0})

        for item in beneficiary_stats:
            mun_name = item.get('addresstl__municipality__name')
            sex = item.get('sex') or "Tidak Diketahui"
            count = item.get('total', 0)

            if mun_name:
                data_map[mun_name] += count
                if sex in ["Mane", "Feto"]:
                    detail_pivot[mun_name][sex] += count
                detail_pivot[mun_name]["Total"] += count
        map_data = [
            {
                "name": m.name,
                "hc-key": m.hckey,
                "value": data_map.get(m.name, 0)
            }
            for m in muns
        ]
        detail_table = [
            {
                "municipality": m.name,
                "mane_total": detail_pivot[m.name]["Mane"],
                "feto_total": detail_pivot[m.name]["Feto"],
                "total_benefisiariu": detail_pivot[m.name]["Total"]
            }
            for m in muns
        ]
        return Response({
            "map": map_data,
            "municipalities": list(muns.values("id", "name", "hckey")),
            "table": detail_table,
            "total_global": sum(data_map.values())
        })