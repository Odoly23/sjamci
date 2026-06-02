from django.urls import path
from . import views

urlpatterns = [
    # Dashboard & List
    path('mpms-dashboard/',             views.dash_mpms,                  name='dash-mpms'),
    path('mpms/list/',                  views.mpms_empresa_list,           name='mpms-list'),
    # Benefisiariu
    path('mpms/add/benef/',             views.add_benef_mpms,              name='add-bf-mpms'),
    path('mpms/edit/benef/<str:hashid>/', views.edit_benef_mpms,           name='edit-benef-mpms'),
    # Detail
    path('mpms/detail/<str:hashid>/',   views.mpms_detail,                 name='mpms-detail'),
    # Address
    path('mpms/address/<str:hashid>/',        views.AddressTLUpdate_mpms,    name='address-mpms'),
    path('mpms/address-origin/<str:hashid>/', views.AddressOriginUpdate_mpms, name='address-origin-mpms'),
    # Negosiu (Business KNI) — pintu masuk utama, otomatis buat mpmsEmpresa
    path('mpms/business/add/<str:hashid>/',        views.Business_Add_mpms,  name='mpms-business-add'),
    path('mpms/business/edit/<str:hashid>/',       views.Business_Edit_mpms, name='mpms-business-edit'),
    # Lokalizasaun — isi LocBussiness, sync ke mpmsLokalizasaun
    path('mpms/lokalizasaun/add/<str:hashid>/',    views.Localidade_Add_mpms,         name='mpms-lokalizasaun-add'),
    # Program — sync ke mpmsAtividade
    path('mpms/program/add/<str:hashid>/',         views.Program_Add_mpms,            name='mpms-program-add'),
    # Employee — sync ke mpmsEmpregador
    path('mpms/employee/add/<str:hashid>/',        views.Employee_Add_mpms,           name='mpms-employee-add'),
    # Finance
    path('mpms/finance/add/<str:hashid>/',         views.Finance_Add_mpms,            name='mpms-finance-add'),
    # MPMS-specific (pakai empresa.hashed)
    path('mpms/lisensamentu/add/<str:hashid>/',    views.mpms_lisensamentu_create,    name='mpms-lisensamentu-add'),
    path('mpms/kapital/add/<str:hashid>/',         views.mpms_kapital_create,         name='mpms-kapital-add'),
    path('mpms/empregador/add/<str:hashid>/',      views.mpms_empregador_create,      name='mpms-empregador-add'),
    path('mpms/materia-prima/add/<str:hashid>/',   views.mpms_materia_create,         name='mpms-materia-add'),
    path('mpms/atividade/add/<str:hashid>/',       views.mpms_atividade_create,       name='mpms-atividade-add'),
    # Avaliasaun
    path('mpms/avaliasaun/',                       views.avaliasaun_mpms,             name='ava-mpms'),



    path("export/",       views.export_page_mpms,  name="export-mpms"),
    path("export/excel/", views.export_excel_mpms, name="export-excel-mpms"),
    path("export/pdf/",   views.export_pdf_mpms,   name="export-pdf-mpms"),
]