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
from custom.models import TIpu_Programa, Status, Municipality, AdministrativePost, Village, Sector, Bussines_size
from django.core.paginator import Paginator

@login_required
@allowed_users(allowed_roles=['admin','KS','XFD'])
def tab_ks(request):
	group = request.user.groups.all()[0].name
	objects1, objects2, objects3, objects4, objects5 = [],[],[],[],[]
	totalp = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").count()
	totm = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KREDITU SUAVE").count()
	totf = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KREDITU SUAVE").count()
	totativu = Benefisiariu.active_objects.filter(status__name="Ativu", Pnegosiu__program_type__name="KREDITU SUAVE").count()
	totparado = Benefisiariu.active_objects.filter(status__name="Parado", Pnegosiu__program_type__name="KREDITU SUAVE").count()
	totek = Benefisiariu.active_objects.filter(team_members__role="Xefi Ekipa").count()
	tottk = Benefisiariu.active_objects.filter(team_members__role="Tekniko").count()
	totmk = Benefisiariu.active_objects.filter(team_members__role="Membro").count()
	mun = Municipality.active_objects.all()
	sec = Sector.active_objects.all()
	totsec = Sector.active_objects.all().count()
	ano = Year.active_objects.all().order_by('-year')
	paginator = Paginator(ano, 13)
	page = request.GET.get('page', 1)
	tinan_page = paginator.get_page(page)
	size = Bussines_size.active_objects.all()
	tot_size = Bussines_size.active_objects.all().count()
	for m in mun:
			m1 = Benefisiariu.active_objects.filter(sex="Mane", addresstl__municipality__name=m, Pnegosiu__program_type__name="KREDITU SUAVE").count()
			m2 = Benefisiariu.active_objects.filter(sex="Feto", addresstl__municipality__name=m, Pnegosiu__program_type__name="KREDITU SUAVE").count()
			total = m1 + m2
			objects1.append([m, m1, m2, total])
	for a in tinan_page:
		obj1 = []
		for s in sec:
			s1 = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE", Pnegosiu__year=a, negosiu__sector__name=s).count()
			obj1.append([s, s1])

		objects2.append([a, obj1])
	for m in mun:
			obj2 = []
			total_all = 0
			for s in size:
				m1 = Benefisiariu.active_objects.filter(sex="Mane", addresstl__municipality__name=m, Pnegosiu__program_type__name="KREDITU SUAVE", negosiu__size__name=s).count()
				m2 = Benefisiariu.active_objects.filter(sex="Feto", addresstl__municipality__name=m, Pnegosiu__program_type__name="KREDITU SUAVE", negosiu__size__name=s).count()
				subtotal = m1 + m2
				total_all += subtotal
				obj2.append([s, m1, m2, subtotal])
			objects3.append([m, obj2, total_all])
	context = {
		'totalp':totalp,'totm':totm, 'totf':totf,'totek':totek,'tottk':tottk,'totmk':totmk,
        'group':  group,'totparado':totparado, 'totativu':totativu, 'objects1':objects1,
        'title':  'Sumario Tabela', 'objects2':objects2,'sec':sec,'totsec':totsec,'years_page': tinan_page,
        'objects3':objects3,'tot_size':tot_size,'size':size,
        'legend': 'Sumario Tabela Kreditu Suave',
        'link_antes': [
            {'link_name': 'dash-ks',  'link_text': 'Painel Kreditu Suave'},
            {'link_name': 'sum-gr', 'link_text': 'Painel Geral'},
            {'link_name': 'tab-ks', 'link_text': 'Tabela Kreditu Suave'},
        ],
	}
	return render(request, 'Dash_R/KS/tab_ks.html', context)
