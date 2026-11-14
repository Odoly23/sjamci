from django.urls import path
from . import views

urlpatterns = [
    path('painel/', views.home, name="home"),

]