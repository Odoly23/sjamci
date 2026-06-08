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
from benefisiariu.models import Benefisiariu, AddressTL, Photo, AddressOrigin, Pedidu
from kni.models import    Business, LocBussiness, Program, Employee, Finance
from itertools import groupby
from operator import itemgetter
from django.core.paginator import Paginator
from django.conf import settings
from monitoring.models import   BusinessImpactMonitoring, FundUsage,  BusinessAsset, CashFlow,  FinancialBook


@login_required
@allowed_users(allowed_roles=['KNI'])
def pedidu_list(request):
    status = request.GET.get('status')
    pedidus = Pedidu.objects.all().select_related('benefisiariu')
    if status:
        pedidus = pedidus.filter(status=status)
    context = {
        'pedidus': pedidus,
        'status': status,
        'title':'Lista Pedido',
        'legend':'Lista Pedido'
    }
    return render(request, 'infos/pedidu_list.html', context)

@login_required
def pedidu_detail(request, hashed):
    pedidu = get_object_or_404(Pedidu, hashed=hashed)
    context =  {
        'pedidu': pedidu,
        'title':f'Detaillu Pedido {pedidu.benefisiariu}',
        'legend':f'Detaillu Pedido {pedidu.benefisiariu}',
    }
    return render(request, 'infos/pedidu_detail.html', context)

@login_required
@allowed_users(allowed_roles=['KNI'])
def pedidu_update_status(request, pk):
    pedidu = get_object_or_404(Pedidu, id=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        resposta = request.POST.get('resposta')
        pedidu.status = status
        pedidu.resposta = resposta
        pedidu.resolvidu_by = request.user
        pedidu.save()
        return redirect('pedidu-list')
    context = {
        'pedidu': pedidu,
        'title': 'Altera Statutu Pedidu',   
        'legend': 'Altera Statutu Pedidu'
    }
    return render(request, 'infos/pedidu_update.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def cashflow_list(request):
    status = request.GET.get('type')
    qs = CashFlow.objects.select_related('monitoring', 'monitoring__business')
    if status:
        qs = qs.filter(transaction_type=status)
    context = {
        'cashflows': qs,
        'status': status,
        'title':'Lista Utilizasaun Fundus',
        'legend':'Lista Utilizasaun Fundus',
    }
    return render(request, 'infos/cashflow_list.html', context)

@login_required
def cashflow_detail(request, pk):
    obj = get_object_or_404(CashFlow, id=pk)
    context = {
        'cashflow': obj,
        'title':'Detaillu Utilizasaun Fundus',
        'legend':'Detaillu Utilizasaun Fundus',
    }
    return render(request, 'infos/cashflow_detail.html', context)


@login_required
@allowed_users(allowed_roles=['KNI'])
def financial_book_list(request):
    qs = FinancialBook.objects.select_related('monitoring', 'monitoring__business')
    context = {
        'books': qs,
        'title':'Lista Submisaun Livro kontabilidade',
        'legend':'Lista Submisaun Livro kontabilidade',
    }
    return render(request, 'infos/financial_book_list.html', context)

@login_required
def financial_book_detail(request, pk):
    obj = get_object_or_404(FinancialBook, id=pk)
    context = {
        'book': obj,
        'title':'Detaillu Submisaun Livro kontabilidade',
        'legend':'Detaillu Submisaun Livro kontabilidade',
    
    }
    return render(request, 'infos/financial_book_detail.html', context)
