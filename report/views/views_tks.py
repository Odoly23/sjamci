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


@login_required
@allowed_users(allowed_roles=['admin','KS','XFD'])
def tab_ks(request):
	group = request.user.groups.all()[0].name
	totalp = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").count()
	totm = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KREDITU SUAVE").count()
	totf = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KREDITU SUAVE").count()
	context = {
		'totalp':totalp,'totm':totm, 'totf':totf,
        'group':  group,
        'title':  'Sumario Tabela',
        'legend': 'Sumario Tabela Kreditu Suave',
        'link_antes': [
            {'link_name': 'dash-ks',  'link_text': 'Painel Kreditu Suave'},
            {'link_name': 'sum-gr', 'link_text': 'Painel Geral'},
            {'link_name': 'tab-ks', 'link_text': 'Tabela Kreditu Suave'},
        ],
	}
	return render(request, 'Dash_R/KS/tab_ks.html', context)
