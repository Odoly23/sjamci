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
    
    # ========== KPI ==========
    total_grupu = Manufatur.objects.all().count()
    total_mane = Membro.objects.aggregate(total=Sum('male'))['total'] or 0
    total_feto = Membro.objects.aggregate(total=Sum('female'))['total'] or 0
    total_ativo = Manufatur.objects.filter(status='Ativo').count()
    total_parado = Manufatur.objects.filter(status='Parado').count()
    
    # ========== TABEL 1: Rekapitulasi per Municipiu & Tipu Industria ==========
    # Ambil semua municipiu
    municipios = Municipality.objects.all().order_by('name')
    
    # Ambil semua Industry Type (Tipu Industria) dari model IndustryType
    # yang terhubung melalui Aktividade.industry_type
    tipu_industria_list = IndustryType.objects.filter(
        aktividade__isnull=False
    ).distinct().order_by('name')
    
    # Jika tidak ada data dari Aktividade, ambil dari Manufatur (fallback)
    if not tipu_industria_list:
        # Fallback: gunakan list manual dari Excel
        tipu_industria_list = [
            'Carpintaria', 'Alfaiate', 'Soru Tais', 'Oficina', 
            'Arte Kultura', 'Bambu', 'Homan', 'Mina Nu\'u', 'Rotan'
        ]
    
    objects1 = []
    for m in municipios:
        row_data = []
        total_all = 0
        
        for tipu in tipu_industria_list:
            # Cari Manufatur yang punya aktividade dengan industry_type tertentu
            # dan berlokasi di municipiu tersebut
            if hasattr(tipu, 'id'):  # Jika tipu adalah object IndustryType
                jumlah = Manufatur.objects.filter(
                    lokalidade__municipality=m,
                    atividades__industry_type=tipu
                ).distinct().count()
            else:  # Jika tipu adalah string (fallback)
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
    
    # ========== TABEL 2: Rekapitulasi per Tahun & Tipu Apoio ==========
    years = Year.objects.all().order_by('-year')
    paginator = Paginator(years, 10)
    page = request.GET.get('page', 1)
    years_page = paginator.get_page(page)
    
    # Ambil semua Tipu Apoio dari model Tipu_Apoio
    tipu_apoio_list = Tipu_Apoio.objects.filter(
        aktividade__isnull=False
    ).distinct().order_by('name')
    
    # Fallback jika tidak ada data
    if not tipu_apoio_list:
        tipu_apoio_list = [
            'Subvensões', 'Formasaun', 'Kopersaun', 'Subvensões Públicas', 'KNI'
        ]
    
    objects2 = []
    for y in years_page:
        row_data = []
        total_all = 0
        
        for apoio in tipu_apoio_list:
            if hasattr(apoio, 'id'):  # Jika apoio adalah object Tipu_Apoio
                total_amount = Aktividade.objects.filter(
                    year=y,
                    support_type=apoio
                ).aggregate(total=Sum('amount'))['total'] or 0
            else:  # Fallback string
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
        
        # KPI
        'total_grupu': total_grupu,
        'total_mane': total_mane,
        'total_feto': total_feto,
        'total_ativo': total_ativo,
        'total_parado': total_parado,
        
        # Tabel per Municipiu
        'municipios': municipios,
        'tipu_industria_list': tipu_industria_list,
        'objects1': objects1,
        
        # Tabel per Tahun
        'tipu_apoio_list': tipu_apoio_list,
        'objects2': objects2,
        'years_page': years_page,
    }
    
    return render(request, 'Dash_R/DNIM/tab_dnim.html', context)