from django.db.models import Sum, Count, Avg
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated
from benefisiariu.models import Benefisiariu
from kni.models import  Business, Program, Employee, Finance, BusinessMonitoring, LocBussiness
from suave.models import EkipaMember, FinancialAssessment, CreditInfo
from custom.models import Municipality, Sector, Status

KS_PROGRAM = "KREDITU SUAVE"


class APIKPIKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        total_benefisiariu = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").count()
        total_business = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").count()
        total_budget = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").aggregate(total=Sum('amount'))['total'] or 0
        total_employee = Employee.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE").aggregate(total=Sum('total'))['total'] or 0
        total_team = EkipaMember.objects.filter(benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE").count()
        total_revenue = FinancialAssessment.objects.filter(business__benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM).aggregate(total=Sum('annual_revenue'))['total'] or 0
        total_asset = FinancialAssessment.objects.filter(business__benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM).aggregate(total=Sum('total_assets'))['total'] or 0
        return Response({
            'total_benefisiariu': total_benefisiariu,
            'total_business': total_business,
            'total_budget': float(total_budget),
            'total_employee': total_employee,
            'total_team': total_team,
            'total_revenue': float(total_revenue),
            'total_asset': float(total_asset),
        })


# =========================================================
# 2. SEXU
# =========================================================

class APISexuKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        for s in ['Mane', 'Feto']:

            total = Benefisiariu.active_objects.filter(
                Pnegosiu__program_type__name=KS_PROGRAM,
                sex=s
            ).distinct().count()

            label.append(s)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 3. MUNICIPIU
# =========================================================

class APIMunicipiuKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        municipios = Municipality.objects.all().order_by('name')

        for m in municipios:

            total = Benefisiariu.active_objects.filter(
                Pnegosiu__program_type__name=KS_PROGRAM,
                locnegosiu__municipality=m
            ).distinct().count()

            label.append(m.name)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 4. SECTOR
# =========================================================

class APISectorKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        sectors = Sector.objects.all().order_by('name')

        for s in sectors:

            total = Business.objects.filter(
                benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM,
                sector=s
            ).distinct().count()

            label.append(s.name)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# TEAM MEMBER
# =========================================================

class APITeamKS(APIView):

    authentication_classes = [
        SessionAuthentication,
        BasicAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]

    def get(self, request, format=None):

        label = []

        obj = []

        roles = [
            'Xefi',
            'Tekniko'
        ]

        for r in roles:

            total = EkipaMember.objects.filter(
                benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE",
                role=r
            ).count()

            label.append(r)

            obj.append(total)

        return Response({

            'label': label,

            'obj': obj

        })
# =========================================================
# 5. EMPLOYEE
# =========================================================

class APIEmployeeKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        employees = Employee.objects.filter(
            business__benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM
        )

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
# 6. STATUS PROGRAMA
# =========================================================

class APIStatusProgramaKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        statuss = Status.objects.all()

        for s in statuss:

            total = Program.objects.filter(
                program_type__name=KS_PROGRAM,
                status=s
            ).count()

            label.append(s.name)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 7. BUDGET PER MUNICIPIU
# =========================================================

class APIBudgetMunicipiuKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        municipios = Municipality.objects.all().order_by('name')

        for m in municipios:

            total = Program.objects.filter(
                program_type__name=KS_PROGRAM,
                benefisiariu__locnegosiu__municipality=m
            ).aggregate(
                total=Sum('amount')
            )['total'] or 0

            label.append(m.name)
            obj.append(float(total))

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 8. CREDIT REPAYMENT
# =========================================================

class APICreditRepaymentKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

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
                business__benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM,
                repayment_status=r
            ).count()

            label.append(r)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 9. RISK CLASSIFICATION
# =========================================================

class APIRiskKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        risks = [
            'Normal',
            'Risk',
            'Critical',
            'Inactive'
        ]

        for r in risks:

            total = BusinessMonitoring.objects.filter(
                business__benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM,
                monitoring_status=r
            ).count()

            label.append(r)
            obj.append(total)

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 10. REVENUE GROWTH
# =========================================================

class APIRevenueGrowthKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        data = BusinessMonitoring.objects.filter(
            business__benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM
        ).order_by('month')

        for d in data:

            label.append(str(d.month))

            obj.append(
                float(d.growth_percentage or 0)
            )

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 11. REVENUE PER SECTOR
# =========================================================

class APIRevenueSectorKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        sectors = Sector.objects.all()

        for s in sectors:

            total = FinancialAssessment.objects.filter(
                business__benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM,
                business__sector=s
            ).aggregate(
                total=Sum('annual_revenue')
            )['total'] or 0

            label.append(s.name)

            obj.append(
                float(total)
            )

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 12. TOP MUNICIPALITY
# =========================================================

class APITopMunicipalityKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        municipios = Municipality.objects.all()

        results = []

        for m in municipios:

            total = Benefisiariu.active_objects.filter(
                Pnegosiu__program_type__name=KS_PROGRAM,
                locnegosiu__municipality=m
            ).distinct().count()

            results.append({
                'name': m.name,
                'total': total
            })

        results = sorted(
            results,
            key=lambda x: x['total'],
            reverse=True
        )[:10]

        for r in results:

            label.append(r['name'])
            obj.append(r['total'])

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 13. TOP SECTOR
# =========================================================

class APITopSectorKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        label = []
        obj = []

        sectors = Sector.objects.all()

        results = []

        for s in sectors:

            total = Business.objects.filter(
                benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM,
                sector=s
            ).distinct().count()

            results.append({
                'name': s.name,
                'total': total
            })

        results = sorted(
            results,
            key=lambda x: x['total'],
            reverse=True
        )[:10]

        for r in results:

            label.append(r['name'])
            obj.append(r['total'])

        return Response({
            'label': label,
            'obj': obj
        })


# =========================================================
# 14. GIS MAP
# =========================================================

class APIGISKS(APIView):

    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):

        data = []

        locations = LocBussiness.objects.filter(
            benefisiariu__Pnegosiu__program_type__name=KS_PROGRAM
        ).exclude(
            latitude__isnull=True
        ).exclude(
            longitude__isnull=True
        )

        for loc in locations:

            data.append({

                'name':
                    str(loc.benefisiariu),

                'municipality':
                    str(loc.municipality),

                'latitude':
                    loc.latitude,

                'longitude':
                    loc.longitude,

            })

        return Response(data)