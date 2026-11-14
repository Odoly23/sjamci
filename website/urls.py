from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('lian/<str:code>/', views.set_language, name='set-lang'),
    path('publiku/estatistika/', views.public_stats, name='public-stats'),
    path('publiku/estatistika.csv', views.public_stats_csv, name='public-stats-csv'),
]
