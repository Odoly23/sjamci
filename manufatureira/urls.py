from django.urls import path
from . import views

urlpatterns = [
    path('Manufatura/Dashboard/', views.dash_man, name='dash-man'),
    path('Manufatura/List/<str:year>/<str:mun>/', views.list_man, name='list_man'),
    path('Manufatura/Total/<str:year>/', views.total_man, name='total_man'),
    path('Manufatura/Lista-Jeral/', views.geral_man, name='geral_man'),
    path('Manufatura/Detail/<str:hashid>/', views.detail_man, name='detail_man'),
]