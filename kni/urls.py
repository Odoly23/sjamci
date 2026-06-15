from django.urls import path
from . import views

urlpatterns = [
    # ── Dashboard ─────────────────────────────────────────────
    path('dashboard/', views.dash_kni,  name='kni-dash'),

    # ── Detail ────────────────────────────────────────────────
    path('detail/<str:hashid>/',  views.benef_detail_kni,  name='benef-detail-kni'),

    # ── Lista & Filtrasaun ────────────────────────────────────
    path('lista-jeral/',      views.geral_kni,    name='geral-kni'),
    path('lista/<int:year>/<str:faze>/<str:mun>/', views.list_kni,  name='list_kni'),
    path('total/<int:year>/<str:faze>/', views.total_kni,               name='total_kni'),

    # ── Rejistu Benefisiariu ──────────────────────────────────
    path('rejistu/',   views.add_benef_kni,     name='add-benef-kni'),
    path('update/benef/<str:hashid>/', views.edit_benef_kni, name="edit-benef"),

    # ── Enderesu & Lokasaun ───────────────────────────────────
    path('enderesu/<str:hashid>/',  views.AddressTLUpdate_kni,  name='kni-addtl-update'),
    path('enderesu-origin/<str:hashid>/',  views.AddressOriginUpdate_kni,  name='kni-addori-update'),
    path('lokasaun/<str:hashid>/',  views.Localidade_Add,   name='kni-loc-add'),

    # ── Negosiu, Programa, Trabalhadores, Finansiamento ──────
    path('negosiu/<str:hashid>/', views.Business_Add,    name='kni-business-add'),
    path('programa/<str:hashid>/',  views.Program_Add,     name='kni-program-add'),
    path('trabalhadores/<str:hashid>/',  views.Employee_Add,   name='kni-employee-add'),
    path('finansiamento/<str:hashid>/',  views.Finance_Add, name='kni-finance-add'),


    #  ── Avaliasaun ──────
    path('Pajina-Avaliasaun.html/', views.avaliasaun, name='av-dash'),
    path('Lista-Avalisaun.html/', views.avalia_list, name='list-ava'),
    path('rejistu-Avalisaun/<str:hashid>/', views.evaluate_benef, name="benef-evaluation"),
    path('lista-avaliasaun/', views.benef_evaluation_list, name='benef-evaluation-list'),


    #Importasaun Excel)
    path('Importa-excel/kni/.html', views.import_kni_excel, name='import_kni_excel'),

    #print sert
    path('Print/sertifikado/<str:hashid>/', views.print_sertifikat_kni, name='print_sertifikat_kni'),

    #monitorizasaun/Avaliasaun
    path('Lista-Avalisaun-Finasaira/', views.avalia_list2, name='av-list2'),
    path('Adisiona-Avalisaun/<str:hashid>/.html', views.monitoring_create, name='add-monits'),

    # BASELINE
    path('Adisiona-Baseline/<str:hashid>/.html',  views.baseline_create,   name='add-baseline'),
    path('Adisiona-Avalisaun/<str:hashid>/.html', views.monitoring_create, name='add-monits'),
    # LIST BASELINE
    path('Lista-Baseline/', views.baseline_list, name='baseline-list'),
    path('Lista-Monitoring/', views.monitoring_list, name='monitoring-list'),



    path("export/",       views.export_page_kni,  name="export-kni"),
    path("export/excel/", views.export_excel_kni, name="export-excel-kni"),
    path("export/pdf/",   views.export_pdf_kni,   name="export-pdf-kni"),

    #pedido
    path('pedidu/', views.pedidu_list, name='pedidu-list'),
    path('pedidu/<str:hashed>/', views.pedidu_detail, name='pedidu-detail'),
    path('pedidu/<int:pk>/update/', views.pedidu_update_status, name='pedidu-update'),


    #cash_Flow
    path('cashflow/', views.cashflow_list, name='cashflow-list'),
    path('cashflow/<int:pk>/', views.cashflow_detail, name='cashflow-detail'),

    # finansial Book
    path('financial-book/', views.financial_book_list, name='financial-book-list'),
    path('financial-book/<int:pk>/', views.financial_book_detail, name='financial-book-detail'),
]