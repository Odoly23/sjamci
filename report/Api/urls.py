from django.urls import path
from . import views_kni

urlpatterns=[
	path('grafiku/sexu/', views_kni.APISexu.as_view()),
]