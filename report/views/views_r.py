import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from config.decorators import allowed_users
from custom.models import Municipality, Year, Faze, TIpu_Programa, Tipu_Fundus_Kapital, Category_Emp, Bussines_size
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
@allowed_users(allowed_roles=['admin','KS','XFD','dnim'])
def grafiku_dnim(request):
	group = request.user.groups.all()[0].name
	context = {
		'title':"Sumario Geral",
		'legend':"Sumario Geral",
		'group':group,
	}
	return render(request, 'Dash_R/Grafiku_dnim.html', context)

@login_required
@allowed_users(allowed_roles=['admin','KS','KNI','XFD','dnim'])
def tab_knies(request):
	group = request.user.groups.all()[0].name
	objects1, objects2, objects3, objects4 = [],[],[],[]
	mun = Municipality.active_objects.all()
	fun = Tipu_Fundus_Kapital.active_objects.all()
	year = Year.active_objects.order_by('-year').all()
	paginator = Paginator(year, 13)
	page = request.GET.get('page', 1)
	tinan_page = paginator.get_page(page)
	totb = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI").distinct().count()
	totm = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KNI").distinct().count()
	totf = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KNI").distinct().count()
	tota = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI", status__name="Ativu").distinct().count()
	totp = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI", status__name="Parado").distinct().count()
	for m in mun:
		obj1 = []
		total_all = 0
		for f in fun:
			m1 = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KNI", locnegosiu__municipality=m, Pnegosiu__t_fundus=f).distinct().count()
			m2 = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KNI", locnegosiu__municipality=m, Pnegosiu__t_fundus=f).distinct().count()
			total = m1 + m2
			total_all += total
			obj1.append([f, m1, m2])
		objects1.append([m, obj1, total_all])
	for y in tinan_page:
		obj2 = []
		total_all = 0
		for s in fun:
			f1 = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KNI", Pnegosiu__year=y, Pnegosiu__t_fundus=s).distinct().count()
			f2 = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KNI", Pnegosiu__year=y, Pnegosiu__t_fundus=s).distinct().count()
			total = f1 + f2
			total_all += total
			obj2.append([s, f1, f2])
		objects2.append([y, obj2, total_all])
	for m in mun:
		from django.db.models import Sum
		ml = Employee.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KNI", business__benefisiariu__locnegosiu__municipality=m).aggregate(total=Sum('male'))['total'] or 0
		fl = Employee.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KNI", business__benefisiariu__locnegosiu__municipality=m).aggregate(total=Sum('female'))['total'] or 0
		total_all = ml + fl
		objects3.append([m, ml, fl, total_all])
	for m in mun:
		mane = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KNI", locnegosiu__municipality=m).distinct().count()
		feto = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KNI", locnegosiu__municipality=m).distinct().count()
		total_all = mane + feto
		objects4.append([m, mane, feto, total_all])
	context = {
		'group': group,
		'mun': mun, 'totm': totm, 'totf': totf,
		'tota': tota, 'totp': totp, 'totb': totb,
		'objects1': objects1, 'objects2': objects2,
		'objects3': objects3, 'objects4': objects4,
		'title': 'Painel Tabel KNI', 'fun': fun, 'years_page': tinan_page,
		'legend': 'Painel Tabel KNI'
	}
	return render(request, 'Dash_R/tabular_kni.html', context)

@login_required
@allowed_users(allowed_roles=['admin','KS','KNI','XFD','dnim'])
def tab_kni(request):
	group = request.user.groups.all()[0].name
	objects1, objects2, objects3, objects4 = [],[],[],[]
	mun = Municipality.active_objects.all()
	cat = Category_Emp.active_objects.all()
	size = Bussines_size.active_objects.all()
	year = Year.active_objects.order_by('-year').all()
	paginator = Paginator(year, 13)
	page = request.GET.get('page', 1)
	tinan_page = paginator.get_page(page)
	totb = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI").distinct().count()
	totm = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KNI").distinct().count()
	totf = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KNI").distinct().count()
	tota = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI", status__name="Ativu").distinct().count()
	totp = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI", status__name="Parado").distinct().count()
	for m in mun:
		obj1 = []
		total_all = 0
		for c in cat:
			m1 = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KNI", locnegosiu__municipality=m, negosiu__category=c).distinct().count()
			m2 = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KNI", locnegosiu__municipality=m, negosiu__category=c).distinct().count()
			total = m1 + m2
			total_all += total
			obj1.append([c, m1, m2])
		objects1.append([m, obj1, total_all])
	for y in tinan_page:
		obj2 = []
		total_all = 0
		for s in size:
			f1 = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KNI", Pnegosiu__year=y, negosiu__size=s).distinct().count()
			f2 = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KNI", Pnegosiu__year=y, negosiu__size=s).distinct().count()
			total = f1 + f2
			total_all += total
			obj2.append([s, f1, f2])
		objects2.append([y, obj2, total_all])
	for m in mun:
		from django.db.models import Sum
		ml = Employee.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KNI", business__benefisiariu__locnegosiu__municipality=m).aggregate(total=Sum('male'))['total'] or 0
		fl = Employee.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KNI", business__benefisiariu__locnegosiu__municipality=m).aggregate(total=Sum('female'))['total'] or 0
		total_all = ml + fl
		objects3.append([m, ml, fl, total_all])
	for m in mun:
		mane = Benefisiariu.active_objects.filter(sex="Mane", Pnegosiu__program_type__name="KNI", locnegosiu__municipality=m).distinct().count()
		feto = Benefisiariu.active_objects.filter(sex="Feto", Pnegosiu__program_type__name="KNI", locnegosiu__municipality=m).distinct().count()
		total_all = mane + feto
		objects4.append([m, mane, feto, total_all])
	context = {
		'group': group,
		'mun': mun, 'totm': totm, 'totf': totf,
		'tota': tota, 'totp': totp, 'totb': totb,
		'objects1': objects1, 'objects2': objects2,
		'objects3': objects3, 'objects4': objects4,
		'title': 'Painel Tabel KNI', 'cat': cat, 'size': size, 'years_page': tinan_page,
		'legend': 'Painel Tabel KNI'
	}
	return render(request, 'Dash_R/tabular_kni.html', context)