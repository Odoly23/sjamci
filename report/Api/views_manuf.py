from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from config.decorators import allowed_users
from django.db.models import Sum, Count, F, Max, Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from custom.models import Municipality
from benefisiariu.models import Benefisiariu
from manufatureira.models import Manufatur, Lokalizasaun, Membro, Aktividade


# =========================================================
# 1. GRUPU ATIVO VS PARADO PER MUNICIPIU (Stacked Bar)
# =========================================================

class APIGrupuStatusPerMunicipiu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        ativo_data = []
        parado_data = []

        municipios = Municipality.objects.all().order_by('name')

        for m in municipios:
            total_ativo = Manufatur.objects.filter(
                lokalidade__municipality=m,
                status='Ativu'
            ).count()

            total_parado = Manufatur.objects.filter(
                lokalidade__municipality=m,
                status='Parado'
            ).count()

            if total_ativo > 0 or total_parado > 0:
                labels.append(m.name)
                ativo_data.append(total_ativo)
                parado_data.append(total_parado)

        return Response({
            'labels': labels,
            'ativo': ativo_data,
            'parado': parado_data,
        })


# =========================================================
# 2. DISTRIBUSI TIPU INDUSTRIA (Pie Chart)
# =========================================================

class APIDistribusiTipuIndustria(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        data = []

        # Ambil dari Aktividade.industry_type
        results = Aktividade.objects.values('industry_type__name').annotate(
            total=Count('id', distinct=True)
        ).order_by('-total')

        for item in results:
            if item['industry_type__name']:
                labels.append(item['industry_type__name'])
                data.append(item['total'])

        # Jika tidak ada data dari Aktividade, fallback ke Manufatur
        if not labels:
            results2 = Manufatur.objects.values('tipu_industria').annotate(
                total=Count('id')
            ).order_by('-total')
            for item in results2:
                if item['tipu_industria']:
                    labels.append(item['tipu_industria'])
                    data.append(item['total'])

        return Response({
            'labels': labels,
            'data': data,
        })


# =========================================================
# 3. TOTAL VALOR APOIO PER MUNICIPIU (Bar Chart)
# =========================================================

class APITotalValorPerMunicipiu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        data = []

        municipios = Municipality.objects.all().order_by('name')

        for m in municipios:
            total = Aktividade.objects.filter(
                manufatur__lokalidade__municipality=m,
                amount__isnull=False
            ).aggregate(total=Sum('amount'))['total'] or 0

            if total > 0:
                labels.append(m.name)
                data.append(float(total))

        return Response({
            'labels': labels,
            'data': data,
        })


# =========================================================
# 4. TOTAL VALOR APOIO PER TINAN (Line Chart)
# =========================================================

class APITotalValorPerTinan(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        data = []

        # Group by year from Aktividade
        results = Aktividade.objects.values('year__year').annotate(
            total=Sum('amount')
        ).order_by('year__year')

        for item in results:
            if item['year__year']:
                labels.append(str(item['year__year']))
                data.append(float(item['total'] or 0))

        return Response({
            'labels': labels,
            'data': data,
        })


# =========================================================
# 5. TOP 10 GRUPU DENGAN VALOR TERBESAR (Horizontal Bar)
# =========================================================

class APITop10GrupuValor(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        data = []

        # Get top 10 groups by total amount from Aktividade
        results = Manufatur.objects.annotate(
            total_valor=Sum('atividades__amount')
        ).filter(
            total_valor__gt=0
        ).order_by('-total_valor')[:10]

        for item in results:
            labels.append(item.name[:30])
            data.append(float(item.total_valor or 0))

        return Response({
            'labels': labels,
            'data': data,
        })


# =========================================================
# 6. DISTRIBUSI TIPU APOIO (Pie Chart)
# =========================================================

class APIDistribusiTipuApoio(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        data = []

        results = Aktividade.objects.values('support_type__name').annotate(
            total=Count('id')
        ).order_by('-total')

        for item in results:
            if item['support_type__name']:
                labels.append(item['support_type__name'])
                data.append(item['total'])

        return Response({
            'labels': labels,
            'data': data,
        })


# =========================================================
# 7. JUMLAH MEMBRO (MANE vs FETO) PER MUNICIPIU (Grouped Bar)
# =========================================================

class APIJumlahMembroPerMunicipiu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        mane_data = []
        feto_data = []

        municipios = Municipality.objects.all().order_by('name')

        for m in municipios:
            total_mane = Membro.objects.filter(
                manufatur__lokalidade__municipality=m
            ).aggregate(total=Sum('male'))['total'] or 0

            total_feto = Membro.objects.filter(
                manufatur__lokalidade__municipality=m
            ).aggregate(total=Sum('female'))['total'] or 0

            if total_mane > 0 or total_feto > 0:
                labels.append(m.name)
                mane_data.append(total_mane)
                feto_data.append(total_feto)

        return Response({
            'labels': labels,
            'mane': mane_data,
            'feto': feto_data,
        })


# =========================================================
# 8. RASIO MANE:FETO PER MUNICIPIU (Stacked Bar - Percent)
# =========================================================

class APIRasioManeFeto(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        mane_percent = []
        feto_percent = []

        municipios = Municipality.objects.all().order_by('name')

        for m in municipios:
            total_mane = Membro.objects.filter(
                manufatur__lokalidade__municipality=m
            ).aggregate(total=Sum('male'))['total'] or 0

            total_feto = Membro.objects.filter(
                manufatur__lokalidade__municipality=m
            ).aggregate(total=Sum('female'))['total'] or 0

            total = total_mane + total_feto

            if total > 0:
                labels.append(m.name)
                mane_percent.append(round((total_mane / total) * 100, 1))
                feto_percent.append(round((total_feto / total) * 100, 1))

        return Response({
            'labels': labels,
            'mane': mane_percent,
            'feto': feto_percent,
        })


# =========================================================
# 9. STATUS ATIVO VS PARADO (OVERALL) - Pie Chart
# =========================================================

class APIStatusOverall(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        total_ativo = Manufatur.objects.filter(status='Ativo').count()
        total_parado = Manufatur.objects.filter(status='Parado').count()
        total_outro = Manufatur.objects.exclude(
            status__in=['Ativo', 'Parado']
        ).exclude(status__isnull=True).count()
        total_tidak_diketahui = Manufatur.objects.filter(status__isnull=True).count()

        labels = []
        data = []

        if total_ativo > 0:
            labels.append('Ativo')
            data.append(total_ativo)

        if total_parado > 0:
            labels.append('Parado')
            data.append(total_parado)

        if total_outro > 0:
            labels.append('Outro')
            data.append(total_outro)

        if total_tidak_diketahui > 0:
            labels.append('La iha dadus')
            data.append(total_tidak_diketahui)

        return Response({
            'labels': labels,
            'data': data,
        })


# =========================================================
# 10. TOP MUNICIPIU DENGAN GRUPU TERBANYAK (Bar Chart)
# =========================================================

class APITopMunicipiu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        labels = []
        data = []

        results = Manufatur.objects.values('lokalidade__municipality__name').annotate(
            total=Count('id')
        ).filter(
            total__gt=0,
            lokalidade__municipality__name__isnull=False
        ).order_by('-total')[:10]

        for item in results:
            labels.append(item['lokalidade__municipality__name'])
            data.append(item['total'])

        return Response({
            'labels': labels,
            'data': data,
        })


# =========================================================
# KPI DASHBOARD DNIM
# =========================================================

class APIKPIDnim(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [AllowAny]

    def get(self, request, format=None):
        total_grupu = Manufatur.objects.filter(
            status='Ativo'
        ).count()

        total_parado = Manufatur.objects.filter(
            status='Parado'
        ).count()

        total_grupu_all = Manufatur.objects.all().count()

        total_valor = Aktividade.objects.aggregate(
            total=Sum('amount')
        )['total'] or 0

        total_membro = Membro.objects.aggregate(
            total_mane=Sum('male'),
            total_feto=Sum('female'),
        )

        total_mane = total_membro['total_mane'] or 0
        total_feto = total_membro['total_feto'] or 0

        return Response({
            'total_grupu': total_grupu,
            'total_parado': total_parado,
            'total_grupu_all': total_grupu_all,
            'total_valor': float(total_valor),
            'total_mane': total_mane,
            'total_feto': total_feto,
            'total_membro': total_mane + total_feto,
        })