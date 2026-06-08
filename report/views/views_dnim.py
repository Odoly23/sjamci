# Di manufatureira/views.py

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
    total_grupu = Manufatur.objects.all().count()
    total_mane = Membro.objects.aggregate(total=Sum('male'))['total'] or 0
    total_feto = Membro.objects.aggregate(total=Sum('female'))['total'] or 0
    total_ativo = Manufatur.objects.filter(status='Ativo').count()
    total_parado = Manufatur.objects.filter(status='Parado').count()
    municipios = Municipality.objects.all().order_by('name')
    tipu_industria_list = IndustryType.objects.filter(aktividade__isnull=False).distinct().order_by('name')
    if not tipu_industria_list:
        tipu_industria_list = [
            'Carpintaria', 'Alfaiate', 'Soru Tais', 'Oficina', 
            'Arte Kultura', 'Bambu', 'Homan', 'Mina Nu\'u', 'Rotan'
        ]
    
    objects1 = []
    for m in municipios:
        row_data = []
        total_all = 0        
        for tipu in tipu_industria_list:
            if hasattr(tipu, 'id'):     
                jumlah = Manufatur.objects.filter(
                    lokalidade__municipality=m,
                    atividades__industry_type=tipu
                ).distinct().count()
            else:  
                jumlah = 0
            
            total_all += jumlah
            row_data.append({
                'tipu': tipu.name if hasattr(tipu, 'name') else tipu,
                'jumlah': jumlah
            })
        
        if total_all > 0:
            objects1.append({
                'municipio': m,
                'data': row_data,
                'total': total_all
            })
    
    years = Year.objects.all().order_by('-year')
    paginator = Paginator(years, 10)
    page = request.GET.get('page', 1)
    years_page = paginator.get_page(page)
    tipu_apoio_list = Tipu_Apoio.objects.filter(aktividade__isnull=False).distinct().order_by('name')
    if not tipu_apoio_list:
        tipu_apoio_list = [
            'Subvensões', 'Formasaun', 'Kopersaun', 'Subvensões Públicas', 'KNI'
        ]
    objects2 = []
    for y in years_page:
        row_data = []
        total_all = 0        
        for apoio in tipu_apoio_list:
            if hasattr(apoio, 'id'): 
                total_amount = Aktividade.objects.filter(year=y, support_type=apoio).aggregate(total=Sum('amount'))['total'] or 0
            else:
                total_amount = 0
            total_all += total_amount
            row_data.append({
                'apoio': apoio.name if hasattr(apoio, 'name') else apoio,
                'amount': total_amount
            })
        
        objects2.append({
            'year': y,
            'data': row_data,
            'total': total_all
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
        
        'municipios': municipios,
        'tipu_industria_list': tipu_industria_list,
        'objects1': objects1,
        
        'tipu_apoio_list': tipu_apoio_list,
        'objects2': objects2,
        'years_page': years_page,
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