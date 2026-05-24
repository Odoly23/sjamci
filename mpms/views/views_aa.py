from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from kni.models import Business
from mpms.models import (
    mpmsEmpresa,
    mpmsLokalizasaun,
    mpmsLisensamentu,
    mpmsKapital,
    mpmsEmpregador,
    mpmsMateriaPrima,
    mpmsAtividade
)

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

import hashlib
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from kni.models import Municipality
from custom.models import Year, Faze

from mpms.models import mpmsEmpresa


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
                total = mpmsEmpresa.objects.filter(
                    lokalizasaun__municipality=m,
                    atividades__year=t,
                    atividades__status__name=f.name
                ).distinct().count()

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


@login_required
def mpms_detail_dashboard(request, hashid):
    empresa = get_object_or_404(mpmsEmpresa, hashed=hashid)

    progress = calculate_progress(empresa)

    # AUTO LOCK
    if progress == 100:
        empresa.is_completed = True
        empresa.save()

    context = {
        'empresa': empresa,
        'benef': empresa.benefisiariu,
        'progress': progress,

        # relations
        'lokal': getattr(empresa, 'lokalizasaun', None),
        'lisensamentu': getattr(empresa, 'lisensamentu', None),
        'kapital': getattr(empresa, 'kapital', None),
        'empregador': getattr(empresa, 'empregador', None),
        'materia': getattr(empresa, 'materia_prima', None),
        'atividades': empresa.atividades.all(),

        'title': 'MPMS Dashboard Detail',
        'legend': 'MPMS Progress Detail',
    }

    return render(request, 'mpms/detail_dash.html', context)