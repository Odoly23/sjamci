import hashlib
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from config.decorators import allowed_users
from custom.models import Municipality, Year, Faze
from benefisiariu.models import Benefisiariu


@login_required
@allowed_users(allowed_roles=['admin', 'KS', 'XFD'])
def dash_ks(request):
    group = request.user.groups.all()[0].name
    mun = Municipality.active_objects.all().order_by('code')
    faze = Faze.active_objects.filter(name="KREDITU")
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
                total = Benefisiariu.active_objects.filter(
                    Pnegosiu__program_type__name="KREDITU SUAVE",
                    Pnegosiu__year=t,
                    Pnegosiu__faze=f,
                    locnegosiu__municipality=m
                ).distinct().count()
                row['mun'][m.name] = total
                row['total'] += total
            dg.append(row)
            first_row_for_year = False
    context = {
        'title': "Painel Kreditu Suave",
        'legend': "Painel Kreditu Suave",
        'group': group,
        'mun_list': mun,
        'years_page': tinan_page,
        'dg': dg,
    }
    return render(request, 'Dash_ks/ks.html', context)


@login_required
@allowed_users(allowed_roles=['admin', 'KS', 'XFD'])
def list_ks(request, year, faze, mun):
    group = request.user.groups.all()[0].name
    data = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE", Pnegosiu__year__year=year,
                Pnegosiu__faze__name=faze, locnegosiu__municipality__name=mun).distinct()
    context = {
        'data': data,
        'title': f'Lista Benefisiariu {mun} no Faze {faze}',
        'legend': f'Lista Benefisiariu {mun} no Faze {faze}',
        'year': year,
        'faze': faze,
        'mun': mun,
        'group': group,
    }

    return render(request, 'Dash_ks/list.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'KS', 'XFD'])
def total_ks(request, year, faze):
    group = request.user.groups.all()[0].name
    data = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE",
           Pnegosiu__year__year=year, Pnegosiu__faze__name=faze).distinct()
    context = {
        'data': data,
        'title': 'Lista Benefisiariu Programa Kreditu Suave',
        'legend': 'Lista Benefisiariu Programa Kreditu Suave',
        'year': year,
        'faze': faze,
        'group': group,
    }

    return render(request, 'Dash_ks/list.html', context)


@login_required
@allowed_users(allowed_roles=['admin', 'KS', 'XFD'])
def geral_ks(request):
    group = request.user.groups.all()[0].name
    data = Benefisiariu.active_objects.filter(Pnegosiu__program_type__name="KREDITU SUAVE").distinct().order_by('name')
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
        'data'   : data,
        'group'  : group,
        'years'  : Year.active_objects.all().order_by('-year'),
        'fazes'  : Faze.active_objects.filter(name="KREDITU"),  
        'muns'   : Municipality.active_objects.all().order_by('code'),
        'year'   : year,
        'faze'   : faze,
        'mun'    : mun,
        'title'  : 'Lista Jeral Benefisiariu Kreditu Suave',
        'legend' : 'Lista Jeral Benefisiariu Kreditu Suave',
    }
    return render(request, 'Dash_ks/list_geral.html', context)


@login_required
@allowed_users(allowed_roles=['admin', 'staff', 'KS'])
def benef_detail_ks(request, hashid):
    group = request.user.groups.all()[0].name
    benef = get_object_or_404(Benefisiariu, hashed=hashid)
    addtl  = getattr(benef, 'addresstl',     None)
    addori = getattr(benef, 'addressorigin', None)
    photo  = getattr(benef, 'photo',         None)
    businesses = Business.objects.filter(benefisiariu=benef)
    programs   = Program.objects.filter(
        business__in=businesses,
        program_type='KREDIT'          
    )
    employees = Employee.objects.filter(business__in=businesses)
    finances  = Finance.objects.filter(business__in=businesses)
    kredits   = Kredit.objects.filter(benefisiariu=benef)
    monitoring = None
    kredit_business = businesses.filter(
        program__program_type='KREDIT'
    ).first()
    if kredit_business:
        financial = getattr(kredit_business, 'financial_assessment', None)
        monitoring = {
            'business':    kredit_business,
            'products':    ProductService.objects.filter(business=kredit_business),
            'membro':      EkipaMember.objects.filter(benefisiariu=benef),
            'customers':   MainCustomer.objects.filter(business=kredit_business),
            'competitors': Competitor.objects.filter(business=kredit_business),
            'market':      getattr(kredit_business, 'market_assessment', None),
            'financial':   financial,
            'assets':      FixedAsset.objects.filter(financial=financial) if financial else [],
            'credit_info': getattr(kredit_business, 'credit_info', None),
        }

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
        'kredits':    kredits,
        'monitoring': monitoring,
        'title':      'Detalha Benefisiariu KS',
        'legend':     'Detalha Benefisiariu — Kreditu Suave',
        'link_antes': [
            {'link_name': 'dash_kredit', 'link_text': 'Painel Kreditu Suave'},
        ],
    }
    return render(request, 'suave/benef_detail_ks.html', context)