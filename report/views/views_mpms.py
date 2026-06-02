import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from config.decorators import allowed_users
from custom.models import Municipality, Year, Faze, TIpu_Programa, Tipu_Fundus_Kapital
from django.contrib import messages
from django.db import transaction
from django.db.models import Q
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo
from kni.models import Business, LocBussiness, Program, Employee, Finance
from manufatureira.models import  Manufatur, Lokalizasaun, Membro, Aktividade
from config.decorators import allowed_users
from mpms.models import mpmsEmpresa, mpmsLokalizasaun,  mpmsLisensamentu, mpmsKapital,\
    mpmsEmpregador, mpmsMateriaPrima, mpmsAtividade
from config.decorators import allowed_users
from django.core.paginator import Paginator

@login_required
@allowed_users(allowed_roles=['mpms','admin','staff','xfd'])
def tab_mpms(request):
	group = request.user.groups.all()[0].name
	objects1, objects2, objects3, objects4 = [],[],[],[]
	mun = Municipality.active_objects.all()
	fun = Tipu_Fundus_Kapital.active_objects.all()
	year =  Year.active_objects.order_by('-year').all()
	paginator = Paginator(year, 13)
	page = request.GET.get('page', 1)
	tinan_page = paginator.get_page(page)
	totb = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS").distinct().count()
	totm = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="MPMS").distinct().count()
	totf = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="MPMS").distinct().count()
	tota = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS", status__name="Ativu").distinct().count()
	totp = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS", status__name="Parado").distinct().count()
	tots = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS", status__name="Suspende").distinct().count()
	totpd = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS", status__name="Pending").distinct().count()
	for m in mun:
		obj1 = []
		total_all = 0
		for f in fun:
			m1 = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="MPMS", locnegosiu__municipality=m, Pnegosiu__t_fundus=f).distinct().count()
			m2 = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="MPMS", locnegosiu__municipality=m, Pnegosiu__t_fundus=f).distinct().count()
			total = m1 + m2
			total_all += total
			obj1.append([f, m1, m2])
		objects1.append([m, obj1, total_all])

	for y in tinan_page:
		obj2 = []
		total_all=0
		for s in fun:
			f1 = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="MPMS", Pnegosiu__year=y, Pnegosiu__t_fundus=s).distinct().count()
			f2 = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="MPMS", Pnegosiu__year=y, Pnegosiu__t_fundus=s).distinct().count()
			total = f1 + f2
			total_all += total
			obj2.append([s, f1, f2])
		objects2.append([y, obj2, total_all])

	for m in mun:
		ml = mpmsEmpregador.objects.filter(
			empresa__lokalizasaun__municipality=m
		).aggregate(total=__import__('django.db.models', fromlist=['Sum']).Sum('nasional_mane'))['total'] or 0
		fl = mpmsEmpregador.objects.filter(
			empresa__lokalizasaun__municipality=m
		).aggregate(total=__import__('django.db.models', fromlist=['Sum']).Sum('nasional_feto'))['total'] or 0
		me = mpmsEmpregador.objects.filter(
			empresa__lokalizasaun__municipality=m
		).aggregate(total=__import__('django.db.models', fromlist=['Sum']).Sum('internasional_mane'))['total'] or 0
		fe = mpmsEmpregador.objects.filter(
			empresa__lokalizasaun__municipality=m
		).aggregate(total=__import__('django.db.models', fromlist=['Sum']).Sum('internasional_feto'))['total'] or 0
		total_all = ml + fl + me + fe
		objects3.append([m, ml, fl, me, fe, total_all])

	for m in mun:
		mane = mpmsEmpresa.objects.filter(
			benefisiariu__sex="Mane",
			lokalizasaun__municipality=m
		).distinct().count()
		feto = mpmsEmpresa.objects.filter(
			benefisiariu__sex="Feto",
			lokalizasaun__municipality=m
		).distinct().count()
		total_all = mane + feto
		objects4.append([m, mane, feto, total_all])

	context ={
		'group':group,
		'mun':mun, 'totm':totm, 'totf':totf,
		'tota':tota, 'totp':totp, 'tots':tots, 'totpd':totpd, 'totb':totb,
		'objects1':objects1, 'objects2':objects2,
		'objects3':objects3, 'objects4':objects4,
		'title':'Painel Tabel MPMS', 'fun':fun, 'years_page': tinan_page,
		'legend':'Painel Tabel MPMS'
	}
	return render(request, 'Dash_R/MPMS/tabs.html', context)



@login_required
@allowed_users(allowed_roles=['admin','XFD','mpms'])
def grafiku_mpms(request):
	group = request.user.groups.all()[0].name
	context = {
		'title':"Sumario Geral",
		'legend':"Sumario Geral",
		'group':group,
	}
	return render(request, 'Dash_R/Grafiku_mpms.html', context)