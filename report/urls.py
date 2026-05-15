from django.urls import path
from . import views

urlpatterns = [
    path('Sumario-Geral.html/', views.Sumario, name='sum-gr'),

    #kni
    path('Sumario-Tabular-kni.html/', views.tab_kni, name='kni-tab'),


    #sumario-Grafiku
    path('Sumario-Grafiku-kni/.html', views.grafiku_kni, name='g-kni')

]