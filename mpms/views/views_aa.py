import csv, io, datetime, hashlib
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from kni.models import Business, LocBussiness, Program, Employee, Finance
from mpms.models import mpmsEmpresa, mpmsLokalizasaun, mpmsLisensamentu,\
    mpmsKapital, mpmsEmpregador, mpmsMateriaPrima,  mpmsAtividade
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from custom.models import Year, Faze, Municipality
from config.decorators import allowed_users
from mpms.models import mpmsEmpresa, mpmsLokalizasaun,  mpmsLisensamentu, mpmsKapital,\
    mpmsEmpregador, mpmsMateriaPrima, mpmsAtividade
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo
from django.db.models import Q, Sum, Count

def calculate_progress(empresa):
    steps = 6
    done = 0

    if hasattr(empresa, 'lokalizasaun'):
        done += 1
    if hasattr(empresa, 'lisensamentu'):
        done += 1
    if hasattr(empresa, 'kapital'):
        done += 1
    if hasattr(empresa, 'empregador'):
        done += 1
    if hasattr(empresa, 'materia_prima'):
        done += 1
    if empresa.atividades.exists():
        done += 1

    return int((done / steps) * 100)


@login_required
def dash_mpms(request):
    group = request.user.groups.all()[0].name
    mun = Municipality.active_objects.all().order_by('code')
    faze = Faze.active_objects.filter(name="mpms").all()
    tinan = Year.active_objects.all().order_by('-year')
    paginator = Paginator(tinan, 4)
    page = request.GET.get('page', 1)
    tinan_page = paginator.get_page(page)
    sura_faze = faze.count()
    dg = []
    for t in tinan_page:
        first_row_for_year = True
        for f in faze:
            hash_string = f"{t.year}-{f.name}-mpms"
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
                total = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS",Pnegosiu__year=t, Pnegosiu__faze=f, locnegosiu__municipality=m).distinct().count()
                row['mun'][m.name] = total
                row['total'] += total

            dg.append(row)
            first_row_for_year = False

    context = {
        'title': "MPMS Dashboard",
        'legend': "Painel Monitoring MPMS",
        'group': group,
        'mun_list': mun,
        'years_page': tinan_page,
        'dg': dg,
    }

    return render(request, 'Dash/mpms.html', context)

# Ganti fungsi mpms_detail di views.py dengan ini:

@login_required
@allowed_users(allowed_roles=['mpms'])
def mpms_detail(request, hashid):
    group  = request.user.groups.all()[0].name
    benef  = get_object_or_404(Benefisiariu, hashed=hashid)

    businesses     = Business.objects.filter(benefisiariu=benef)
    programs       = Program.objects.filter(benefisiariu=benef)
    employees      = Employee.objects.filter(business__in=businesses)
    finances       = Finance.objects.filter(business__in=businesses)
    addtl          = getattr(benef, 'addresstl', None)
    address_origin = getattr(benef, 'addressorigin', None)
    photo          = getattr(benef, 'photo', None)
    location       = LocBussiness.objects.filter(benefisiariu=benef).first()
    total_program  = programs.aggregate(total=Sum('amount'))['total'] or 0

    empresa      = mpmsEmpresa.objects.filter(benefisiariu=benef).first()
    progress     = 0
    lokal        = None
    lisensamentu = None
    kapital      = None
    empregador   = None
    materia      = None
    atividades   = []

    if empresa:
        progress = calculate_progress(empresa)
        if progress == 100 and not empresa.is_completed:
            empresa.is_completed = True
            empresa.save(update_fields=['is_completed'])
        lokal        = getattr(empresa, 'lokalizasaun', None)
        lisensamentu = getattr(empresa, 'lisensamentu', None)
        kapital      = getattr(empresa, 'kapital', None)
        empregador   = getattr(empresa, 'empregador', None)
        materia      = getattr(empresa, 'materia_prima', None)
        atividades   = empresa.atividades.all()

    context = {
        'group':          group,
        'benef':          benef,
        'photo':          photo,
        'addtl':          addtl,
        'address_origin': address_origin,
        'location':       location,
        'businesses':     businesses,
        'programs':       programs,
        'employees':      employees,
        'finances':       finances,
        'total_program':  total_program,
        'empresa':        empresa,
        'progress':       progress,
        'lokal':          lokal,
        'lisensamentu':   lisensamentu,
        'kapital':        kapital,
        'empregador':     empregador,
        'materia':        materia,
        'atividades':     atividades,
        'title':          'MPMS Full Detail Dashboard',
        'legend':         'Benefisiariu + Company Progress',
    }
    return render(request, 'mpms/detaill_dash.html', context)

@login_required
@allowed_users(allowed_roles=['mpms'])
def mpms_empresa_list(request):
    group = request.user.groups.all()[0].name
    data = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="MPMS").distinct().order_by('name')
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
        'title'     : 'Lista Jeral Benefisiariu MPMS',
        'legend'    : 'Lista Jeral Benefisiariu MPMS',
    }

    return render(request, 'mpms/list.html', context)
