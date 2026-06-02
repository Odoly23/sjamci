from django.urls import path
from . import views

urlpatterns = [
    path('Sumario-Geral.html/', views.Sumario, name='sum-gr'),

    #kni
    path('Sumario-Tabular-kni.html/', views.tab_kni, name='kni-tab'),


    #sumario-Grafiku
    path('Sumario-Grafiku-kni.html/', views.grafiku_kni, name='g-kni'),
    path('Sumario-Grafiku-ks.html/', views.grafiku_ks, name='g-ks'),
    path('Sumario-Grafiku-Dnim.html/', views.grafiku_dnim, name='g-dnim'),
    path('Sumario-Grafiku-MPMS.html/', views.grafiku_mpms, name='g-mpms'),
    #Sumario Kreditu Suave
    path('Sumario-Tabela-Suave.html/', views.tab_ks, name='tab-ks'),



    path('Sumario-Tabela-MPMS/', views.tab_mpms, name="tab-mpms"),

    #tabela dnim
    path('Sumario-Tabela-dnim/', views.tab_dnim, name='tab_dnim'),
    path('DNIM/manufatura/detail/', views.manufatura_detail_dnim, name='manufatura_detail_dnim'),

]