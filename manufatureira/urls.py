from django.urls import path
from . import views

urlpatterns = [
    path('Manufatura/Dashboard/', views.dash_man, name='dash-man'),
    path('Manufatura/List/<str:year>/<str:mun>/', views.list_man, name='list_man'),
    path('Manufatura/Total/<str:year>/', views.total_man, name='total_man'),
    path('Manufatura/Lista-Jeral/', views.geral_man, name='geral_man'),
    path('Manufatura/Detail/<str:hashid>/', views.detail_man, name='detail_man'),

    # BENEF
    path('dnim/benef/add/', views.add_benef_dnim, name='add-benef-dnim'),
    path('dnim/benef/edit/<str:hashid>/', views.edit_benef_dnim, name='edit-benef-dnim'),
    #addrestl
    path('dnim/addres/add/<str:hashid>/', views.AddressTLUpdate_dnim, name='dn-addres'),
    path('dnim/addres/ori/add/<str:hashid>/', views.AddressOriginUpdate_dnim, name='dn-orig'),
    #negosiu
    path('dnim/locali/add/<str:hashid>/', views.Localidade_Add_dnim, name='dn-loc'),
    path('dnim/bussiness/add/<str:hashid>/', views.Business_Add_dnim, name='dn-bus'),
    path('dnim/bussiness/edit/<str:hashid>/', views.Business_Edit_dnim, name='dn-bus-ed'),
    path('dnim/programa/add/<str:hashid>/', views.Program_Add_dnim, name='dn-prog'),
    path('dnim/employee/add/<str:hashid>/', views.Employee_Add_dnim, name='dn-emp'),
    # MANUFATUR
    path('dnim/manuf/add/<str:hashid>/', views.Manufatur_Add_dnim, name='manuf-add-dnim'),
    path('dnim/manuf/detail/<str:hashid>/', views.manuf_detail_dnim, name='manuf-detail-dnim'),

    path('manuf-edit/<str:hashid>/',  views.Manufatur_Add_dnim,    name='dn-manuf-edit'),
    path('manuf-lok/<str:hashid>/',   views.Lokalizasaun_Add_dnim,  name='dn-manuf-lok'),
    path('membro/<str:hashid>/',      views.Membro_Add_dnim,        name='dn-membro'),
    path('atividade/<str:hashid>/',   views.Aktividade_Add_dnim,    name='dn-atividade'),

    # LOKAL
    path('dnim/manuf/lokal/<str:hashid>/', views.Lokalizasaun_Add_dnim, name='manuf-lokal-add'),

    # MEMBRO
    path('dnim/manuf/membro/<str:hashid>/', views.Membro_Add_dnim, name='manuf-membro-add'),

    # AKTIVIDADE
    path('dnim/manuf/aktividade/<str:hashid>/', views.Aktividade_Add_dnim, name='manuf-aktividade-add'),



    #Avaliasaun
    path('Pajina-Avaliasaun/.html/', views.avaliasaun_dnim, name='dmin-ava'),
]