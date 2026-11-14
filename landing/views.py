import csv

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_GET

from . import i18n, stats
from .models import Announcement, Slide

LANG_COOKIE = 'landing_lang'


def current_lang(request):
    lang = request.COOKIES.get(LANG_COOKIE)
    return lang if lang in i18n.CODES else i18n.DEFAULT


def _year(request):
    value = request.GET.get('year', '')
    return int(value) if value.isdigit() and 1990 <= int(value) <= 2100 else None


@require_GET
def landing(request):
    if request.user.is_authenticated:
        return redirect('home')
    lang = current_lang(request)
    t = i18n.strings(lang)

    slides = [{'title': s.text('title', lang), 'subtitle': s.text('subtitle', lang),
               'image': s.image.url if s.image else ''} for s in Slide.objects.filter(is_active=True)]
    if not slides:
        slides = [{'title': t[f'slide{i}_title'], 'subtitle': t[f'slide{i}_sub'], 'image': ''} for i in (1, 2, 3)]

    announcements = [{'title': a.text('title', lang), 'body': a.text('body', lang), 'level': a.level,
                      'date': a.publish_date} for a in Announcement.objects.filter(is_published=True)[:6]]

    return render(request, 'landing/landing.html', {
        't': t,
        'lang': lang,
        'languages': i18n.LANGUAGES,
        'slides': slides,
        'announcements': announcements,
        'years': stats.available_years(),
        'totals': stats.get()['totals'],
        'contact': {'phone': settings.LANDING_PHONE, 'email': settings.LANDING_EMAIL,
                    'address': settings.LANDING_ADDRESS},
        'js_strings': {key: t[key] for key in (
            'all_years', 'beneficiaries', 'municipality', 'total', 'no_data', 'load_error', 'male', 'female',
            'unknown', 'no_location', 'updated', 'slide_pause', 'slide_play')},
    })


@require_GET
def set_language(request, code):
    """Troka lian (bolu bainhira klik bandeira) no fila ba pajina uluk."""
    target = request.GET.get('next') or request.META.get('HTTP_REFERER') or '/'
    if not url_has_allowed_host_and_scheme(target, allowed_hosts={request.get_host()},
                                           require_https=request.is_secure()):
        target = '/'
    response = redirect(target)
    if code in i18n.CODES:
        response.set_cookie(LANG_COOKIE, code, max_age=365 * 24 * 3600, samesite='Lax',
                            secure=request.is_secure())
    return response


@require_GET
def public_stats(request):
    return JsonResponse(stats.get(_year(request)))


@require_GET
def public_stats_csv(request):
    year = _year(request)
    data = stats.get(year)
    t = i18n.strings(current_lang(request))
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="benefisiariu_munisipiu_{year or "hotu"}.csv"'
    response.write('﻿')
    writer = csv.writer(response)
    writer.writerow([t['municipality'], t['year_label'], t['beneficiaries']])
    for row in data['municipalities']:
        writer.writerow([row['name'], year or t['all_years'], row['count']])
    if data['unlocated']:
        writer.writerow([t['no_location'], year or t['all_years'], data['unlocated']])
    writer.writerow([t['total'], year or t['all_years'], data['totals']['beneficiaries']])
    return response
