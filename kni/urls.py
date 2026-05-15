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
    path('Lista-Avalisaun.html/', views.avalia_list, name='list-ava'),
    path('rejistu-Avalisaun/<str:hashid>/', views.evaluate_benef, name="benef-evaluation"),
    path('lista-avaliasaun/', views.benef_evaluation_list, name='benef-evaluation-list'),


    #Importasaun Excel)
    path('Importa-excel/kni/.html', views.import_kni_excel, name='import_kni_excel'),
]