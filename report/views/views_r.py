import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from config.decorators import allowed_users
from custom.models import Municipality, Year, Faze, TIpu_Programa
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo
from kni.models import Business, LocBussiness, Program, Employee, Finance
from manufatureira.models import  Manufatur, Lokalizasaun, Membro, Aktividade
from config.decorators import allowed_users

# Create your views here.

@login_required
@allowed_users(allowed_roles=['admin','KS','KNI','XFD','dnim','mpms'])
def Sumario(request):
	group = request.user.groups.all()[0].name
	kni = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI").count()
	ks = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").count()
	mpms = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS").count()
	mf = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MANUFATUREIRA").count()
	context = {
		'title':"Sumario Geral",
		'legend':"Sumario Geral",
		'group':group,'kni':kni, 'ks':ks, 'mf':mf,'mpms':mpms
	}
	return render(request, 'Dash_R/Sumary.html', context)

@login_required
@allowed_users(allowed_roles=['admin','KNI','XFD','dnim'])
def grafiku_kni(request):
	group = request.user.groups.all()[0].name
	context = {
		'title':"Sumario Geral",
		'legend':"Sumario Geral",
		'group':group,
	}
	return render(request, 'Dash_R/Grafiku_kni.html', context)

@login_required
@allowed_users(allowed_roles=['admin','KS','XFD','dnim'])
def grafiku_ks(request):
	group = request.user.groups.all()[0].name
	context = {
		'title':"Sumario Geral",
		'legend':"Sumario Geral",
		'group':group,
	}
	return render(request, 'Dash_R/Grafiku_ks.html', context)

@login_required
@allowed_users(allowed_roles=['admin','KS','KNI','XFD','dnim'])
def tab_kni(request):
	group = request.user.groups.all()[0].name
	context = {
		'title':'Tabular KNI',
		'legend': 'Tabular KNI',
		'group': group
	}
	return render(request, 'Dash_R/tabular_kni.html', context)

