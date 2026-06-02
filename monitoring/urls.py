from django.urls import path
from . import views

urlpatterns = [
	path('business/<str:business_hashid>/impact/', views.impact_monitoring_list, name='business_impact_list'),
	path('business/<str:business_hashid>/impact/add/', views.impact_monitoring_add, name='business_impact_add'),
	path('business/<str:business_hashid>/impact/<int:pk>/detail/', views.impact_monitoring_detail, name='business_impact_detail'),
	path('business/<str:business_hashid>/impact/<int:pk>/edit/', views.impact_monitoring_edit, name='business_impact_edit'),
	path('business/<str:business_hashid>/impact/<int:pk>/delete/', views.impact_monitoring_delete, name='business_impact_delete'),

	# Fund Usage (Utilizasaun Fundus)
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/fundusage/add/', views.fund_usage_add, name='fund_usage_add'),
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/fundusage/<int:pk>/edit/', views.fund_usage_edit, name='fund_usage_edit'),
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/fundusage/<int:pk>/delete/', views.fund_usage_delete, name='fund_usage_delete'),

	# Business Asset
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/asset/add/', views.business_asset_add, name='business_asset_add'),
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/asset/<int:pk>/edit/', views.business_asset_edit, name='business_asset_edit'),
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/asset/<int:pk>/delete/', views.business_asset_delete, name='business_asset_delete'),

	# Cash Flow (Fluxu Osan)
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/cashflow/add/', views.cashflow_add, name='cashflow_add'),
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/cashflow/<int:pk>/edit/', views.cashflow_edit, name='cashflow_edit'),
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/cashflow/<int:pk>/delete/', views.cashflow_delete, name='cashflow_delete'),

	# Financial Book (Livru Kontabilidade)
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/financialbook/add/', views.financial_book_add, name='financial_book_add'),
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/financialbook/<int:pk>/edit/', views.financial_book_edit, name='financial_book_edit'),
	path('business/<str:business_hashid>/impact/<int:monitoring_pk>/financialbook/<int:pk>/delete/', views.financial_book_delete, name='financial_book_delete'),
]