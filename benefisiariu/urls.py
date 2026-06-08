# cliente/urls.py  (atau tambah ke urls.py utama)
from django.urls import path
from . import views

urlpatterns = [
    path('cliente/dashboard/',       views.cliente_dashboard,      name='cliente-dashboard'),
    path('cliente/perfil/update/',   views.cliente_perfil_update,  name='cliente-perfil'),
    path('cliente/foto/update/',     views.cliente_photo_update,   name='cliente-foto'),
    path('cliente/enderesu/update/', views.cliente_address_update, name='cliente-address'),
    path('cliente/programa/',        views.cliente_programa,       name='cliente-programa'),
    path('cliente/pedidu/',          views.cliente_pedidu,         name='cliente-pedidu'),


]