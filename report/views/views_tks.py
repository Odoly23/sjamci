import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from config.decorators import allowed_users
from custom.models import Municipality, Year, Faze, TIpu_Programa
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, Sum
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo
from kni.models import Business, LocBussiness, Program, Employee, Finance
from manufatureira.models import  Manufatur, Lokalizasaun, Membro, Aktividade
from config.decorators import allowed_users
from custom.models import TIpu_Programa, Status, Municipality, AdministrativePost, Village, Sector, Bussines_size
from django.core.paginator import Paginator
from suave.models import CreditInfo


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
	totek = Benefisiariu.active_objects.filter(team_members__role="Xefi").count()
	tottk = Benefisiariu.active_objects.filter(team_members__role="Tekniko").count()
	totmk = Benefisiariu.active_objects.filter(team_members__role="Membro").count()
	tot_amount = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE").aggregate(total=Sum('amount'))['total'] or 0
	tot_problem = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", has_repayment_problem=True).count()
	tot_cont = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", program_continuation=True).count()
	mun = Municipality.active_objects.all()
	sec = Sector.active_objects.all()
	totsec = sec.count()
	ano = Year.active_objects.all().order_by('-year')
	paginator = Paginator(ano, 13)
	page = request.GET.get('page', 1)
	tinan_page = paginator.get_page(page)
	size = Bussines_size.active_objects.all()
	tot_size = size.count()
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
	for m in mun:
		total_ben = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE", addresstl__municipality__name=m).count()
		total_amt = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", business__benefisiariu__addresstl__municipality__name=m).aggregate(total=Sum('amount'))['total'] or 0
		total_col = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", business__benefisiariu__addresstl__municipality__name=m).aggregate(total=Sum('collateral_amount'))['total'] or 0
		objects4.append([m, total_ben, total_amt, total_col])
	for m in mun:
		on_time = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", business__benefisiariu__addresstl__municipality__name=m, repayment_status="OnTime").count()
		late    = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", business__benefisiariu__addresstl__municipality__name=m, repayment_status="Late").count()
		stuck   = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", business__benefisiariu__addresstl__municipality__name=m, repayment_status="Stuck").count()
		done    = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", business__benefisiariu__addresstl__municipality__name=m, repayment_status="Done").count()
		failed  = CreditInfo.objects.filter(business__benefisiariu__Pnegosiu__program_type__name="KREDITU SUAVE", business__benefisiariu__addresstl__municipality__name=m, repayment_status="Failed").count()
		total_all = on_time + late + stuck + done + failed
		objects5.append([m, on_time, late, stuck, done, failed, total_all])
	context = {
		'totalp':totalp, 'totm':totm, 'totf':totf, 'totek':totek, 'tottk':tottk, 'totmk':totmk,
		'group':group, 'totparado':totparado, 'totativu':totativu,
		'tot_amount':tot_amount, 'tot_problem':tot_problem, 'tot_cont':tot_cont,
		'objects1':objects1, 'objects2':objects2, 'objects3':objects3,
		'objects4':objects4, 'objects5':objects5,
		'title':'Sumario Tabela', 'sec':sec, 'totsec':totsec, 'years_page':tinan_page,
		'tot_size':tot_size, 'size':size,
		'legend':'Sumario Tabela Kreditu Suave',
		'link_antes': [
			{'link_name': 'dash-ks',  'link_text': 'Painel Kreditu Suave'},
			{'link_name': 'sum-gr', 'link_text': 'Painel Geral'},
			{'link_name': 'tab-ks', 'link_text': 'Tabela Kreditu Suave'},
		],
	}
	return render(request, 'Dash_R/KS/tab_ks.html', context)


@login_required
@allowed_users(allowed_roles=['admin', 'KS', 'XFD'])
def ks_benef_list(request, filter_type):
    group = request.user.groups.all()[0].name
    objects = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").distinct()
    title = "Lista Benefisiariu KS"
    legend_parts = []
    sex = request.GET.get('sex')
    if sex:
        objects = objects.filter(sex=sex)
        legend_parts.append(f"Sex: {sex}")
    status = request.GET.get('status')
    if status:
        objects = objects.filter(status__name=status)
        legend_parts.append(f"Status: {status}")
    municipality = request.GET.get('municipality')
    if municipality:
        objects = objects.filter(addresstl__municipality__name=municipality)
        legend_parts.append(f"Munisipiu: {municipality}")
    sector = request.GET.get('sector')
    if sector:
        objects = objects.filter(negosiu__sector__name=sector)
        legend_parts.append(f"Sector: {sector}")
    year = request.GET.get('year')
    if year:
        objects = objects.filter(Pnegosiu__year__year=year)
        legend_parts.append(f"Tinan: {year}")
    size = request.GET.get('size')
    if size:
        objects = objects.filter(negosiu__size__name=size)
        legend_parts.append(f"Bussines Size: {size}")
    repayment_status = request.GET.get('repayment_status')
    if repayment_status:
        objects = objects.filter(
            negosiu__finance__business__creditinfo__repayment_status=repayment_status
        ).distinct()

        legend_parts.append(f"Repayment: {repayment_status}")
    if legend_parts:
        legend = "" + " | ".join(legend_parts)
    else:
        legend = "Lista Kompletu Benefisiariu Kreditu Suave"
    paginator = Paginator(objects, 25)
    page = request.GET.get('page')
    page_obj = paginator.get_page(page)
    context = {
        "group": group,
        "page_obj": page_obj,
        "filter_type": filter_type,
        "title": title,
        "legend": legend,
    }
    return render(request, "Dash_R/KS/list_benef_ks.html", context)