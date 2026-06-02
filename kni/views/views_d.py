import csv, io, datetime, hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from config.decorators import allowed_users
from django.db.models import Count, Max, Q, Prefetch, Exists, OuterRef, Sum
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.http import JsonResponse
from custom.models import Minister, Diresaun, Position, Municipality, AdministrativePost, Village, \
							Sector, Status, Bussines_size, Category_Emp, Year, Faze
from benefisiariu.models import Benefisiariu, AddressTL, Photo, AddressOrigin
from kni.models import    Business, LocBussiness, Program, Employee, Finance
from itertools import groupby
from operator import itemgetter
from django.core.paginator import Paginator
from django.conf import settings
from monitoring.models import (
    BusinessImpactMonitoring,
    FundUsage,
    BusinessAsset,
    CashFlow,
    FinancialBook,
)
# Create your views here.
@login_required
@allowed_users(allowed_roles=['admin', 'KNI', 'XFD'])
def dash_kni(request):
    group = request.user.groups.all()[0].name
    mun = Municipality.active_objects.all().order_by('code')
    faze = Faze.active_objects.exclude(name__in=["KREDITU", "mpms",'manufatur'])
    tinan = Year.active_objects.all().order_by('-year')
    paginator = Paginator(tinan, 4)
    page = request.GET.get('page', 1)
    tinan_page = paginator.get_page(page)
    sura_faze = faze.count()
    dg = []
    for t in tinan_page:
        first_row_for_year = True
        for f in faze:
            hash_string = f"{t.year}-{f.name}"
            row_hashed = hashlib.blake2b(hash_string.encode()).hexdigest()
            row = {
                'year': t.year,
                'faze': f.name,
                'mun': {},
                'hashed': row_hashed,
                'total': 0,
                'year_rowspan': sura_faze if first_row_for_year else 0
            }
            for m in mun:
                total = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI",Pnegosiu__year=t, 
                	Pnegosiu__faze=f, locnegosiu__municipality=m).distinct().count()
                row['mun'][m.name] = total
                row['total'] += total
            dg.append(row)
            first_row_for_year = False

    context = {
        'title': "Painel Kompetisaun Negosiu Inovativu",
        'legend': "Painel Kompetisaun Negosiu Inovativu",
        'group': group, 'mun_list': mun, 'years_page': tinan_page, 'dg': dg,
    }
    return render(request, 'Dash/kni.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'KNI', 'XFD'])
def list_kni(request, year, faze, mun):
	group = request.user.groups.all()[0].name
	data = Benefisiariu.active_objects.filter( Pnegosiu__program_type__name="KNI", 
		Pnegosiu__year__year=year, Pnegosiu__faze__name=faze, locnegosiu__municipality__name=mun).distinct()
	context = {
        'data': data,
        'title': f'Lista Benefisiariu {mun} no faze {faze}',
        'legend': f'Lista Benefisiariu {mun} no Faze {faze}',
        'year': year,
        'faze': faze,
        'mun': mun,
        'group':group
    }
	return render(request, 'Dash/list.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'KNI', 'XFD'])
def total_kni(request, year, faze):
	group = request.user.groups.all()[0].name
	data = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI", 
		Pnegosiu__year__year=year, Pnegosiu__faze__name=faze).distinct()
	context = {
        'data': data,
        'title': 'Lista Benefisiariu Programa KNI',
        'legend': 'Lista Benefisiariu Programa KNI',
        'year': year,
        'faze': faze,
    }
	return render(request, 'Dash/list.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'KNI', 'XFD'])
def geral_kni(request):
    group = request.user.groups.all()[0].name
    data = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KNI").distinct().order_by('name')
    year = request.GET.get('year')
    faze = request.GET.get('faze')
    mun  = request.GET.get('mun')
    if year:
        data = data.filter(Pnegosiu__year__year=year)
    if faze:
        data = data.filter(Pnegosiu__faze__name=faze)
    if mun:
        data = data.filter(locnegosiu__municipality__name=mun)
    context = {
        'data'      : data,
        'group'     : group,
        'years'     : Year.active_objects.all().order_by('-year'),
        'fazes'     : Faze.active_objects.exclude(name="KREDITU"),
        'muns'      : Municipality.active_objects.all().order_by('code'),
        'year'      : year,
        'faze'      : faze,
        'mun'       : mun,
        'title'     : 'Lista Jeral Benefisiariu KNI',
        'legend'    : 'Lista Jeral Benefisiariu KNI',
    }
    return render(request, 'Dash/list_geral_kni.html', context)


@login_required
@allowed_users(allowed_roles=['admin', 'staff', 'KNI'])
def benef_detail_kni2(request, hashid):
    group = request.user.groups.all()[0].name
    benef = get_object_or_404(Benefisiariu, hashed=hashid)
    addtl  = getattr(benef, 'addresstl',     None)
    addori = getattr(benef, 'addressorigin', None)
    photo  = getattr(benef, 'photo',         None)
    businesses = Business.active_objects.filter(benefisiariu=benef)
    programs   = Program.active_objects.filter(benefisiariu=benef, program_type__name='KNI')
    total_amount = programs.aggregate(total=Sum('amount'))['total'] or 0
    local = LocBussiness.active_objects.filter(benefisiariu=benef).first()
    employees = Employee.active_objects.filter(business__in=businesses)
    finances  = Finance.active_objects.filter(business__in=businesses)
    context = {
        'group':      group,
        'benef':      benef,
        'addtl':      addtl,
        'addori':     addori,
        'photo':      photo,
        'businesses': businesses,
        'programs':   programs,
        'employees':  employees,
        'finances':   finances,
        'total_amount': total_amount,
        'local':local,
        'title':      'Detalha Benefisiariu KNI',
        'legend':     'Detalha Benefisiariu — Kompetisaun Negósiu Inovativu',
        'MAPBOX_TOKEN': settings.MAPBOX_TOKEN,
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
        ],
    }
    return render(request, 'kni/benef_detail_kni.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'staff', 'KNI'])
def benef_detail_kni(request, hashid):
    group = request.user.groups.all()[0].name
    benef = get_object_or_404(Benefisiariu, hashed=hashid)
    addtl  = getattr(benef, 'addresstl',     None)
    addori = getattr(benef, 'addressorigin', None)
    photo  = getattr(benef, 'photo',         None)
    businesses = Business.active_objects.filter(benefisiariu=benef)
    programs   = Program.active_objects.filter(benefisiariu=benef, program_type__name='KNI')
    total_amount = programs.aggregate(total=Sum('amount'))['total'] or 0
    local = LocBussiness.active_objects.filter(benefisiariu=benef).first()
    employees = Employee.active_objects.filter(business__in=businesses)
    finances  = Finance.active_objects.filter(business__in=businesses)
    
    # ========== TAMBAHAN UNTUK IMPACT MONITORING ==========
    # Ambil semua impact monitoring untuk setiap business
    impact_monitorings = []
    for business in businesses:
        monitorings = BusinessImpactMonitoring.active_objects.filter(business=business)
        for mon in monitorings:
            impact_monitorings.append({
                'monitoring': mon,
                'business': business,
                'fund_usages': mon.fund_usages.all(),
                'assets': mon.assets.all(),
                'cashflows': mon.cashflows.all(),
                'financial_books': mon.financial_books.all(),
            })
    # ======================================================
    
    context = {
        'group':      group,
        'benef':      benef,
        'addtl':      addtl,
        'addori':     addori,
        'photo':      photo,
        'businesses': businesses,
        'programs':   programs,
        'employees':  employees,
        'finances':   finances,
        'total_amount': total_amount,
        'local':      local,
        'impact_monitorings': impact_monitorings,  # <-- TAMBAHAN
        'title':      'Detalha Benefisiariu KNI',
        'legend':     'Detalha Benefisiariu — Kompetisaun Negósiu Inovativu',
        'MAPBOX_TOKEN': settings.MAPBOX_TOKEN,
        'link_antes': [
            {'link_name': 'kni-dash', 'link_text': 'Painel KNI'},
        ],
    }
    return render(request, 'kni/benef_detail_kni.html', context)