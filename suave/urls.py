from django.urls import path
from . import views

urlpatterns = [
    path('Kreditu-Suave/Dashboard/', views.dash_ks, name='dash-ks'),
    path('Kreditu-Suave/List/<str:year>/<str:faze>/<str:mun>/', views.list_ks, name='list_ks'),
    path('Kreditu-Suave/Total/<str:year>/<str:faze>/', views.total_ks, name='total_ks'),
    path('Kreditu-Suave/Lista-Jeral/', views.geral_ks, name='geral-ks'),
]