from django.urls import path
from . import views

urlpatterns = [
    path('Kreditu-Suave/Dashboard/', views.dash_ks, name='dash-ks'),
    path('Kreditu-Suave/List/<str:year>/<str:faze>/<str:mun>/', views.list_ks, name='list_ks'),
    path('Kreditu-Suave/Total/<str:year>/<str:faze>/', views.total_ks, name='total_ks'),
    path('Kreditu-Suave/Lista-Jeral/', views.geral_ks, name='geral-ks'),
    # ── Detail ────────────────────────────────────────────────
    path('detail/<str:hashid>/',  views.benef_detail_ks,   name='benef-detail-ks'),
    # ── Rejistu & Edit Benefisiariu ───────────────────────────
    path('rejistu/',   views.add_benef_ks,  name='add-benef-ks'),
    path('edit/<str:hashid>/', views.edit_benef_ks,  name='edit-benef-ks'),
    # ── Enderesu & Lokasaun ───────────────────────────────────
    path('enderesu/<str:hashid>/', views.AddressTLUpdate_ks,  name='ks-addtl-update'),
    path('enderesu-origin/<str:hashid>/',   views.AddressOriginUpdate_ks,   name='ks-addori-update'),
    path('lokasaun/<str:hashid>/', views.Localidade_Add_ks,  name='ks-loc-add'),
    # ── Negosiu & Programa ────────────────────────────────────
    path('negosiu/<str:hashid>/',  views.Business_Add_ks, name='ks-business-add'),
    path('programa/<str:hashid>/', views.Program_Add_ks, name='ks-program-add'),
    # ── Trabalhadores & Finansiamento ─────────────────────────
    path('trabalhadores/<str:hashid>/', views.Employee_Add_ks,  name='ks-employee-add'),
    path('finansiamento/<str:hashid>/', views.Finance_Add_ks,  name='ks-finance-add'),
    # ── Monitoring ───────────────────────────────────────────
    path('ekipa/add/<str:hashid>/', views.EkipaMember_Add,  name='ks-ekipa-add'),
    path('produto/<str:hashid>/',  views.ProductService_Add, name='ks-product-add'),
    path('kliente/<str:hashid>/',  views.MainCustomer_Add,  name='ks-customer-add'),
    path('kompetitor/<str:hashid>/',views.Competitor_Add,  name='ks-competitor-add'),
    path('merkadu/<str:hashid>/',   views.MarketAssessment_Add,  name='ks-market-add'),
    path('finanseiru/<str:hashid>/', views.FinancialAssessment_Add,  name='ks-financial-add'),
    path('asset/<str:hashid>/',   views.FixedAsset_Add,    name='ks-asset-add'),
    path('info-kredit/<str:hashid>/', views.CreditInfo_Add,   name='ks-creditinfo-add'),
    path('Sasa/grafiku/gis/', views.APIGISKS, name='api-gis-ks'),
    path('ks/benef/<str:hashid>/employee/<int:pk>/edit/',   views.Employee_Edit_ks,  name='ks-employee-edit'),
    path('ks/benef/<str:hashid>/finance/<int:pk>/edit/',    views.Finance_Edit_ks,  name='ks-finance-edit'),
    path('ks/benef/<str:hashid>/ekipa/<int:pk>/edit/',      views.EkipaMember_Edit,  name='ks-ekipa-edit'),
    path('ks/benef/<str:hashid>/product/<int:pk>/edit/',    views.ProductService_Edit, name='ks-product-edit'),
    path('ks/benef/<str:hashid>/customer/<int:pk>/edit/',   views.MainCustomer_Edit, name='ks-customer-edit'),
    path('ks/benef/<str:hashid>/competitor/<int:pk>/edit/', views.Competitor_Edit,   name='ks-competitor-edit'),
    path('ks/benef/<str:hashid>/market/<int:pk>/edit/',     views.MarketAssessment_Edit,   name='ks-market-edit'),
    path('ks/benef/<str:hashid>/financial/<int:pk>/edit/',  views.FinancialAssessment_Edit,name='ks-financial-edit'),
    path('ks/benef/<str:hashid>/asset/<int:pk>/edit/',      views.FixedAsset_Edit,  name='ks-asset-edit'),
    path('ks/benef/<str:hashid>/creditinfo/<int:pk>/edit/', views.CreditInfo_Edit,    name='ks-creditinfo-edit'),
    # ── DELETE ───────────────────────────────────────────────
    path('ks/benef/<str:hashid>/ekipa/<int:pk>/delete/',      views.EkipaMember_Delete,    name='ks-ekipa-delete'),
    path('ks/benef/<str:hashid>/product/<int:pk>/delete/',    views.ProductService_Delete, name='ks-product-delete'),
    path('ks/benef/<str:hashid>/customer/<int:pk>/delete/',   views.MainCustomer_Delete,   name='ks-customer-delete'),
    path('ks/benef/<str:hashid>/competitor/<int:pk>/delete/', views.Competitor_Delete,     name='ks-competitor-delete'),
    path('ks/benef/<str:hashid>/asset/<int:pk>/delete/',      views.FixedAsset_Delete,     name='ks-asset-delete'),


    #avaliasaun
    path('KS/Avaliasaun/', views.ks_avaliasaun, name='ks-ava'),
    path('KS/Avaliasaun/Statuto/', views.avalia_list_ks, name='st-ks-list'),
    path('KS/Avaliasaun/add/<str:hashid>/', views.evaluate_benef_ks, name="eva-ks"),
    path('Lista-Avaliasaun-Finisih/', views.benef_evaluation_list_ks, name='ava-fh'),
    path('Lista-Avaliasaun-Rendimento/', views.avalia_list2_ks, name='ava-re-ks'),
    path('Avaliasaun-Antes/<str:hashid>/', views.baseline_create, name='antes-ava'),
    path('Avaliasaun-Depois/<str:hashid>/', views.monitoring_create_ks, name='depois-ava'),


    path('import/excel/', views.import_kreditu_suave_excel, name='import_ks_excel'),
    path('export/excel/', views.export_kreditu_suave_excel, name='export_ks_excel'),
]