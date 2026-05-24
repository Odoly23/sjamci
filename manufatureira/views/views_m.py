import hashlib
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from config.decorators import allowed_users
from custom.models import Municipality, Year
from benefisiariu.models import Benefisiariu
from manufatureira.models import  Manufatur, Lokalizasaun, Membro, Aktividade
from django.db.models import Count

@login_required
@allowed_users(allowed_roles=['admin', 'MAN', 'XFD','dnim'])
def dash_man(request):
    group = request.user.groups.all()[0].name
    mun   = Municipality.active_objects.all().order_by('code')
    tinan = Year.active_objects.all().order_by('-year')
    paginator  = Paginator(tinan, 4)
    page       = request.GET.get('page', 1)
    tinan_page = paginator.get_page(page)
    year_ids = [t.id for t in tinan_page]
    mun_ids  = [m.id for m in mun]
    counts = (Manufatur.objects.filter(atividades__year_id__in=year_ids, lokalidade__municipality_id__in=mun_ids,)
        .values('atividades__year__year', 'lokalidade__municipality__name')
        .annotate(total=Count('id', distinct=True))
    )
    count_map = {(row['atividades__year__year'], row['lokalidade__municipality__name']): row['total']
        for row in counts
    }
    dg = []
    for t in tinan_page:
        row_hashed = hashlib.blake2b(str(t.year).encode()).hexdigest()
        row = {
            'year':   t.year,
            'mun':    {},
            'hashed': row_hashed,
            'total':  0,
        }
        for m in mun:
            val = count_map.get((t.year, m.name), 0)
            row['mun'][m.name] = val
            row['total']       += val
        dg.append(row)
 
    context = {
        'title':      'Painel Manufatura',
        'legend':     'Painel Manufatura',
        'group':      group,
        'mun_list':   mun,
        'years_page': tinan_page,
        'dg':         dg,
    }
    return render(request, 'Dash_dnim/manufatura.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'MAN', 'XFD','dnim'])
def list_man(request, year, mun):
    group = request.user.groups.all()[0].name
    data = Manufatur.objects.filter(atividades__year__year=year, lokalidade__municipality__name=mun).distinct().order_by('name')
    context = {
        'data': data,
        'group': group,
        'year': year,
        'mun': mun,
        'title': f'Lista Manufatura {mun}',
        'legend': f'Lista Manufatura {mun}',
    }
    return render(request, 'Dash_dnim/list.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'MAN', 'XFD','dnim'])
def total_man(request, year):
    group = request.user.groups.all()[0].name
    data = Manufatur.objects.filter(atividades__year__year=year ).distinct().order_by('name')
    context = {
        'data': data,
        'group': group,
        'year': year,
        'title': 'Lista Jeral Manufatura',
        'legend': 'Lista Jeral Manufatura',
    }

    return render(request, 'Dash_dnim/list_man.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'MAN', 'XFD','dnim'])
def geral_man(request):
    group = request.user.groups.all()[0].name
    data = Manufatur.objects.all().distinct().order_by('name')
    year = request.GET.get('year')
    mun  = request.GET.get('mun')
    if year:
        data = data.filter(atividades__year__year=year)
    if mun:
        data = data.filter(lokalidade__municipality__name=mun)
    context = {
        'data': data,
        'group': group,
        'years': Year.active_objects.all().order_by('-year'),
        'muns': Municipality.active_objects.all().order_by('code'),
        'year': year,
        'mun': mun,
        'title': 'Lista Jeral Manufatura',
        'legend': 'Lista Jeral Manufatura',
    }
    return render(request, 'Dash_dnim/list_geral.html', context)


@login_required
@allowed_users(allowed_roles=['admin', 'MAN', 'XFD','dnim'])
def detail_man(request, hashid):
    group = request.user.groups.all()[0].name
    manufatur = Manufatur.objects.get(hashed=hashid)
    lokalidade = getattr(manufatur,'lokalidade', None)
    membro = getattr(manufatur, 'members_data', None)
    atividades = Aktividade.objects.filter(manufatur=manufatur)
    benef = manufatur.benefisiariu
    context = {
        'group': group,
        'manufatur': manufatur,
        'lokalidade': lokalidade,
        'membro': membro,
        'atividades': atividades,
        'benef': benef,
        'title': 'Detalha Manufatura',
        'legend': 'Detalha Manufatura',
    }

    return render(request, 'Dash_dnim/detail_man.html', context)