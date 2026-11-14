from django.urls import path

from . import views

urlpatterns = [
    path('konta/password/', views.password_change, name='password-change'),
    path('konta/verifikasaun-pasu-2/', views.two_factor_settings, name='two-factor'),
    path('konta/verifikasaun-pasu-2/desativa/', views.two_factor_disable, name='two-factor-disable'),
    path('login/verifikasaun/', views.two_factor_verify, name='two-factor-verify'),
    path('auditoria/atividade/', views.activity_log_list, name='activity-log'),
    path('auditoria/atividade/export/', views.activity_log_export, name='activity-log-export'),
    path('healthz/', views.healthz, name='healthz'),
]
