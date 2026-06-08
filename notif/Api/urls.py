from django.urls import path
from . import views

urlpatterns = [
    path('notification/badge/distribution/request/', views.APINotifBadge.as_view()),
    path('notification/list/', views.APINotifList.as_view()),
    path('notification/read/<int:pk>/', views.APINotifRead.as_view(), name='notification-read'),

]