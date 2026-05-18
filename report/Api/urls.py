from django.urls import path
from . import views_kni
from . import views_ks

urlpatterns = [

    path('grafiku/sexu/', views_kni.APISexu.as_view()),
    path('grafiku/municipiu/', views_kni.APIMunicipiu.as_view()),
    path('grafiku/status/', views_kni.APIStatusPrograma.as_view()),
    path('grafiku/tinan/', views_kni.APIApoiuTinan.as_view()),
    path('grafiku/faze/',  views_kni.APIFaze.as_view()),
    path('grafiku/sector/',  views_kni.APISector.as_view()),
    path('grafiku/trabalhador/', views_kni.APIEmployee.as_view()),
    path('grafiku/credit/',  views_kni.APICreditRepayment.as_view()),
    path('grafiku/kpi/',   views_kni.APIKPI.as_view()),
# suave/api/urls.py
    # =====================================================
    # KPI
    # =====================================================

    path('grafiku/kpi/',    views_ks.APIKPIKS.as_view(),  name='api-kpi-ks'),
    path('grafiku/sexu/', views_ks.APISexuKS.as_view(), name='api-sexu-ks'),
    path('grafiku/team/', views_ks.APITeamKS.as_view(), name='api-team-ks'),
    path('grafiku/municipiu/', views_ks.APIMunicipiuKS.as_view(), name='api-municipiu-ks'),
    path('grafiku/sector/', views_ks.APISectorKS.as_view(), name='api-sector-ks'),
    path('grafiku/employee/', views_ks.APIEmployeeKS.as_view(), name='api-employee-ks'),
    path('grafiku/status/', views_ks.APIStatusProgramaKS.as_view(), name='api-status-ks'),
    path('grafiku/budget-municipiu/', views_ks.APIBudgetMunicipiuKS.as_view(), name='api-budget-municipiu-ks'),
    path('grafiku/credit/', views_ks.APICreditRepaymentKS.as_view(), name='api-credit-ks'),
    path('grafiku/risk/', views_ks.APIRiskKS.as_view(), name='api-risk-ks'),
    path('grafiku/growth/', views_ks.APIRevenueGrowthKS.as_view(), name='api-growth-ks'),
    path('grafiku/revenue-sector/', views_ks.APIRevenueSectorKS.as_view(), name='api-revenue-sector-ks'),
    path('grafiku/top-municipality/', views_ks.APITopMunicipalityKS.as_view(), name='api-top-municipality-ks'),
    path('grafiku/top-sector/', views_ks.APITopSectorKS.as_view(), name='api-top-sector-ks'),
    path('map/benefisiariu/', views_ks.APIGISKS.as_view(), name='api-gis-ks'),

]