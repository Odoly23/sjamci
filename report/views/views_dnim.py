from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from config.decorators import allowed_users
from django.core.paginator import Paginator
from django.db.models import Sum, Count, Q
from custom.models import Municipality, Year, IndustryType, Tipu_Apoio
from manufatureira.models import Manufatur, Lokalizasaun, Membro, Aktividade

@login_required
@allowed_users(allowed_roles=['admin', 'dnim'])
def tab_dnim(request):
    group = request.user.groups.all()[0].name
    total_grupu  = Manufatur.active_objects.count()
    total_mane   = Membro.active_objects.aggregate(total=Sum('male'))['total'] or 0
    total_feto   = Membro.active_objects.aggregate(total=Sum('female'))['total'] or 0
    total_ativo  = Manufatur.active_objects.filter(status='Ativo').count()
    total_parado = Manufatur.active_objects.filter(status='Parado').count()
    mun = Municipality.active_objects.all().order_by('name')
    tipu_industria = IndustryType.active_objects.filter(aktividade__isnull=False).distinct().order_by('name')
    iha_industria  = tipu_industria.exists()
    if iha_industria:
        tipu_industria = list(tipu_industria)
        industria_count = (
            Manufatur.active_objects
            .filter(atividades__industry_type__in=tipu_industria, lokalidade__municipality__in=mun)
            .values('lokalidade__municipality__name', 'atividades__industry_type__name')
            .annotate(total=Count('id', distinct=True))
        )
        industria_map = {
            (row['lokalidade__municipality__name'], row['atividades__industry_type__name']): row['total']
            for row in industria_count
        }
    else:
        tipu_industria = [
            'Carpintaria', 'Alfaiate', 'Soru Tais', 'Oficina',
            'Arte Kultura', 'Bambu', 'Homan', "Mina Nu'u", 'Rotan'
        ]
        industria_map = {}

    objects1 = []
    for m in mun:
        row_data  = []
        total_all = 0
        for tipu in tipu_industria:
            nama_tipu = tipu.name if iha_industria else tipu
            jumlah    = industria_map.get((m.name, nama_tipu), 0)
            total_all += jumlah
            row_data.append({'tipu': nama_tipu, 'jumlah': jumlah})

        if total_all > 0:
            objects1.append({'municipio': m, 'data': row_data, 'total': total_all})

    tinan      = Year.active_objects.all().order_by('-year')
    paginator  = Paginator(tinan, 10)
    page       = request.GET.get('page', 1)
    tinan_page = paginator.get_page(page)

    tipu_apoio = Tipu_Apoio.active_objects.filter(aktividade__isnull=False).distinct().order_by('name')
    iha_apoio  = tipu_apoio.exists()

    if iha_apoio:
        tipu_apoio = list(tipu_apoio)
        year_ids = [t.id for t in tinan_page]
        apoio_amount = (
            Aktividade.active_objects
            .filter(year_id__in=year_ids, support_type__in=tipu_apoio)
            .values('year__year', 'support_type__name')
            .annotate(total=Sum('amount'))
        )
        apoio_map = {
            (row['year__year'], row['support_type__name']): row['total'] or 0
            for row in apoio_amount
        }
    else:
        tipu_apoio = ['Subvensões', 'Formasaun', 'Kopersaun', 'Subvensões Públicas', 'KNI']
        apoio_map = {}

    objects2 = []
    for t in tinan_page:
        row_data  = []
        total_all = 0
        for apoio in tipu_apoio:
            nama_apoio = apoio.name if iha_apoio else apoio
            valor      = apoio_map.get((t.year, nama_apoio), 0)
            total_all += valor
            row_data.append({'apoio': nama_apoio, 'amount': valor})

        objects2.append({'year': t, 'data': row_data, 'total': total_all})

    atividade_list = (
        Aktividade.active_objects
        .select_related(
            'manufatur', 'manufatur__lokalidade', 'manufatur__lokalidade__municipality',
            'manufatur__lokalidade__administrativepost', 'manufatur__lokalidade__village',
            'manufatur__members_data', 'industry_type', 'support_type', 'year',
        )
        .order_by('manufatur__name', '-year__year')
    )
    grupu_paginator = Paginator(atividade_list, 15)
    grupu_page_no   = request.GET.get('grupu_page', 1)
    grupu_page      = grupu_paginator.get_page(grupu_page_no)

    objects3 = []
    for a in grupu_page:
        grupu  = a.manufatur
        lok    = getattr(grupu, 'lokalidade', None)
        membro = getattr(grupu, 'members_data', None)

        objects3.append({
            'grupu':               grupu,
            'leader_name':         grupu.leader_name,
            'phone':                grupu.phone,
            'municipio':            lok.municipality if lok else None,
            'administrativepost':   lok.administrativepost if lok else None,
            'village':              lok.village if lok else None,
            'aldeia':               lok.aldeia if lok else None,
            'tipu_industria':       a.industry_type,
            'tipu_apoio':           a.support_type,
            'tinan':                a.year,
            'amount':               a.amount or 0,
            'membro':               membro.members if membro else 0,
            'mane':                 membro.male if membro else 0,
            'feto':                 membro.female if membro else 0,
            'status':               grupu.status,
        })

    context = {
        'group': group,
        'title': 'Painel Tabel DNIM - Manufatureira',
        'legend': 'PAINEL REKAPITULASAUN MANUFATUREIRA',

        'total_grupu': total_grupu,
        'total_mane': total_mane,
        'total_feto': total_feto,
        'total_ativo': total_ativo,
        'total_parado': total_parado,

        'tipu_industria_list': tipu_industria,
        'objects1': objects1,

        'tipu_apoio_list': tipu_apoio,
        'objects2': objects2,
        'years_page': tinan_page,

        'objects3': objects3,
        'grupu_page': grupu_page,
    }

    return render(request, 'Dash_R/DNIM/tab_dnim.html', context)

@login_required
@allowed_users(allowed_roles=['admin', 'dnim'])
def manufatura_detail_dnim(request):

    group = request.user.groups.all()[0].name

    tipo = request.GET.get('tipo')
    municipio = request.GET.get('municipio')
    industria = request.GET.get('industria')
    apoio = request.GET.get('apoio')
    year = request.GET.get('year')

    data = Manufatur.objects.select_related(
        'lokalidade'
    ).prefetch_related(
        'atividades'
    ).distinct()

    title = "Dadus Detallu"

    # =========================
    # KPI
    # =========================

    if tipo == "grupu":
        title = "Lista Grupu Manufatura"

    elif tipo == "ativo":
        title = "Lista Manufatura Ativu"
        data = data.filter(status='Ativo')

    elif tipo == "parado":
        title = "Lista Manufatura Parado"
        data = data.filter(status='Parado')

    elif tipo == "mane":
        title = "Lista Dadus Mane"
        data = data.filter(members_data__male__gt=0)

    elif tipo == "feto":
        title = "Lista Dadus Feto"
        data = data.filter(members_data__female__gt=0)

    # =========================
    # MUNICIPIO + INDUSTRIA
    # =========================

    elif tipo == "municipio_industria":

        title = f"{municipio} - {industria}"

        data = data.filter(
            lokalidade__municipality__name=municipio,
            atividades__industry_type__name=industria
        )

    # =========================
    # YEAR + APOIO
    # =========================

    elif tipo == "apoio_year":

        title = f"{apoio} - {year}"

        data = data.filter(
            atividades__support_type__name=apoio,
            atividades__year__year=year
        )

    # =========================
    # FILTER
    # =========================

    years = Year.objects.all().order_by('-year')
    municipios = Municipality.objects.all().order_by('name')
    industrias = IndustryType.objects.all().order_by('name')
    apoios = Tipu_Apoio.objects.all().order_by('name')

    filtro_year = request.GET.get('filter_year')
    filtro_mun = request.GET.get('filter_mun')

    if filtro_year:
        data = data.filter(
            atividades__year__year=filtro_year
        )

    if filtro_mun:
        data = data.filter(
            lokalidade__municipality__name=filtro_mun
        )

    context = {
        'group': group,
        'legend': title,
        'data': data.distinct(),

        'years': years,
        'municipios': municipios,
        'industrias': industrias,
        'apoios': apoios,

        'filter_year': filtro_year,
        'filter_mun': filtro_mun,
    }

    return render(
        request,
        'Dash_R/DNIM/detail_dnim.html',
        context
    )