from django.urls import path

from . import views

urlpatterns = [
    path('manifest.webmanifest', views.manifest, name='pwa-manifest'),
    path('sw.js', views.service_worker, name='pwa-sw'),
    path('offline/', views.hub, name='offline-hub'),
    path('offline/rejistu/<str:module>/', views.form_page, name='offline-form'),
    path('offline/sync/', views.sync, name='offline-sync'),
]
