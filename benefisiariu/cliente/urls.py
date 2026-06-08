from django.urls import path
from . import views

urlpatterns = [
    path('cliente/dashboard/',       views.cliente_dashboard,      name='cliente-dashboard'),
    path('cliente/perfil/update/',   views.cliente_perfil_update,  name='cliente-perfil'),
    path('cliente/foto/update/',     views.cliente_photo_update,   name='cliente-foto'),
    path('cliente/enderesu/update/', views.cliente_address_update, name='cliente-address'),
    path('cliente/programa/',        views.cliente_programa,       name='cliente-programa'),
    path('cliente/pedidu/',          views.cliente_pedidu,         name='cliente-pedidu'),

    path('fundusage/add/<int:business_id>/', views.cliente_fund_usage_add, name='cliente-fundusage-add'),
    path('fundusage/edit/<int:pk>/', views.cliente_fund_usage_edit, name='cliente-fundusage-edit'),
    path('fundusage/delete/<int:pk>/', views.cliente_fund_usage_delete, name='cliente-fundusage-delete'),
    path('asset/add/<int:business_id>/', views.cliente_asset_add, name='cliente-asset-add'),
    path('asset/edit/<int:pk>/', views.cliente_asset_edit, name='cliente-asset-edit'),
    path('asset/delete/<int:pk>/', views.cliente_asset_delete, name='cliente-asset-delete'),
    path('cashflow/add/<int:business_id>/', views.cliente_cashflow_add, name='cliente-cashflow-add'),
    path('cashflow/edit/<int:pk>/', views.cliente_cashflow_edit, name='cliente-cashflow-edit'),
    path('cashflow/delete/<int:pk>/', views.cliente_cashflow_delete, name='cliente-cashflow-delete'),
    path('financialbook/add/<int:business_id>/', views.cliente_financial_book_add, name='cliente-financialbook-add'),
    path('financialbook/delete/<int:pk>/', views.cliente_financial_book_delete, name='cliente-financialbook-delete'),
]   