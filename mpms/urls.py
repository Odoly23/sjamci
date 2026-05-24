# mpms/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('mpms/list/', views.mpms_empresa_list, name='mpms-list'),
    path('mpms/empresa/add/<str:benef_hash>/', views.mpms_empresa_create, name='mpms-empresa-add'),
    path('mpms/empresa/<str:hashid>/', views.mpms_detail, name='mpms-detail'),
    path('mpms/lokalizasaun/add/<str:hashid>/', views.mpms_lokalizasaun_create, name='mpms-lokalizasaun-add'),
    path('mpms/lisensamentu/add/<str:hashid>/', views.mpms_lisensamentu_create, name='mpms-lisensamentu-add'),
    path('mpms/kapital/add/<str:hashid>/', views.mpms_kapital_create, name='mpms-kapital-add'),
    path('mpms/empregador/add/<str:hashid>/', views.mpms_empregador_create, name='mpms-empregador-add'),
    path('mpms/materia-prima/add/<str:hashid>/', views.mpms_materia_create, name='mpms-materia-add'),
    path('mpms/atividade/add/<str:hashid>/', views.mpms_atividade_create, name='mpms-atividade-add'),



    #handle views no crud
     path('mpms/<str:hashid>/detail/', views.mpms_detail_dashboard, name='mpms-detail'),
     path('mpms-dashboard/', views.dash_mpms, name='dash-mpms'),
]