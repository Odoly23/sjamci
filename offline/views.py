import json
import logging
import uuid as uuid_lib

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import constants as message_levels
from django.db import transaction
from django.http import HttpResponse, JsonResponse, QueryDict
from django.shortcuts import render
from django.templatetags.static import static
from django.urls import Resolver404, resolve, reverse
from django.utils import timezone
from django.utils.datastructures import MultiValueDict
from django.utils.dateparse import parse_datetime
from django.views.decorators.http import require_POST

from config.decorators import user_group
from custom.models import AdministrativePost, Municipality, Village

from .models import OfflineSubmission
from .modules import HIDDEN_FIELDS, MODULES, OPTIONAL_STEPS, STEP_LABELS, STEP_ORDER

log = logging.getLogger('sjamci.security')


class StepFailed(Exception):
    def __init__(self, step, texts):
        super().__init__(step)
        self.step = step
        self.texts = texts


def _modules_for(user):
    group = user_group(user)
    return {key: cfg for key, cfg in MODULES.items() if cfg['role'] == group}


# ══════════════════════════════════════════════════════════════
#  PWA: manifest, service worker
# ══════════════════════════════════════════════════════════════
def manifest(request):
    return JsonResponse({
        'name': 'SJAMCI — Ministério do Comércio e Indústria',
        'short_name': 'SJAMCI',
        'description': 'Rejistu dadus benefisiáriu KNI, Kreditu Suave no MPMS — bele uza offline.',
        'start_url': reverse('offline-hub'),
        'scope': '/',
        'display': 'standalone',
        'background_color': '#f4f6f9',
        'theme_color': '#1f3864',
        'lang': 'tet',
        'icons': [
            {'src': static('offline/icon-192.png'), 'sizes': '192x192', 'type': 'image/png'},
            {'src': static('offline/icon-512.png'), 'sizes': '512x512', 'type': 'image/png'},
            {'src': static('offline/icon-maskable-512.png'), 'sizes': '512x512', 'type': 'image/png',
             'purpose': 'maskable'},
        ],
    }, content_type='application/manifest+json')


def service_worker(request):
    pages = [reverse('offline-hub')] + [reverse('offline-form', args=[key]) for key in MODULES]
    assets = [static(f'offline/{name}') for name in
              ('app.css', 'store.js', 'hub.js', 'form.js', 'icon-192.png')]
    response = render(request, 'offline/sw.js', {
        'version': settings.OFFLINE_CACHE_VERSION,
        'pages_json': json.dumps(pages),
        'assets_json': json.dumps(assets),
        'hub': reverse('offline-hub'),
    }, content_type='application/javascript')
    response['Service-Worker-Allowed'] = '/'
    response['Cache-Control'] = 'no-cache'
    return response


# ══════════════════════════════════════════════════════════════
#  PAJINA
# ══════════════════════════════════════════════════════════════
@login_required
def hub(request):
    return render(request, 'offline/hub.html', {
        'modules': [{'key': key, 'label': cfg['label']} for key, cfg in _modules_for(request.user).items()],
        'username': request.user.username,
    })


def _field_rows(form, step):
    hidden = HIDDEN_FIELDS.get(step, set())
    return [field for field in form if field.name not in hidden]


@login_required
def form_page(request, module):
    cfg = MODULES.get(module)
    if cfg is None or cfg['role'] != user_group(request.user):
        return render(request, 'auth/403.html', status=403)

    steps = []
    for step in STEP_ORDER:
        form_class, _view = cfg['steps'][step]
        form = form_class(auto_id=f'{step}_%s')
        if step == 'location':
            # Lista postu/suku tomak mai husi JSON iha pajina (kaskata la'o offline)
            for name in ('municipality', 'administrativepost', 'village'):
                form.fields[name].widget.attrs['data-geo'] = name
            form.fields['administrativepost'].required = False
            form.fields['village'].required = False
            form.fields['municipality'].required = False
        steps.append({
            'key': step,
            'label': STEP_LABELS[step],
            'optional': step in OPTIONAL_STEPS,
            'fields': _field_rows(form, step),
        })

    geo = {
        'posts': list(AdministrativePost.objects.order_by('name').values('id', 'name', 'municipality_id')),
        'villages': list(Village.objects.order_by('name').values('id', 'name', 'administrativepost_id')),
    }
    return render(request, 'offline/form.html', {
        'module': module,
        'label': cfg['label'],
        'steps': steps,
        'geo': geo,
        'username': request.user.username,
    })


# ══════════════════════════════════════════════════════════════
#  SINKRONIZASAUN
# ══════════════════════════════════════════════════════════════
def _split_steps(request):
    """Fahe kampu 'pasu.kampu' ba QueryDict/ficheiru kada pasu."""
    data = {step: QueryDict(mutable=True) for step in STEP_ORDER}
    files = {step: MultiValueDict() for step in STEP_ORDER}
    for key in request.POST:
        step, _, name = key.partition('.')
        if step in data and name:
            data[step].setlist(name, request.POST.getlist(key))
    for key in request.FILES:
        step, _, name = key.partition('.')
        if step in files and name:
            files[step].setlist(name, request.FILES.getlist(key))
    return data, files


def _has_values(querydict):
    return any(value.strip() for values in querydict.lists() for value in values[1])


def _replay(request, view, data, files, **kwargs):
    """Halo *view* online nian ho dadus pasu ida; fó fali (response, mensajen foun)."""
    storage = messages.get_messages(request)
    queued = storage._queued_messages
    start = len(queued)
    saved = (request.method, request._post, request._files)
    request.method, request._post, request._files = 'POST', data, files
    try:
        response = view(request, **kwargs)
    finally:
        request.method, request._post, request._files = saved
    new = list(queued[start:])
    del queued[start:]
    return response, new


def _run_step(request, step, view, data, files, **kwargs):
    response, new = _replay(request, view, data, files, **kwargs)
    problems = [str(m) for m in new if m.level >= message_levels.WARNING]
    if response.status_code != 302 or problems:
        raise StepFailed(step, problems or ['Dadus la simu husi sistema. Favor verifika kampu sira.'])
    return response, [str(m) for m in new]


@require_POST
def sync(request):
    if not request.user.is_authenticated:
        return JsonResponse({'status': 'auth', 'message': 'Presiza login fali atu sinkroniza.'}, status=401)

    module = request.POST.get('module', '')
    cfg = MODULES.get(module)
    if cfg is None or cfg['role'] != user_group(request.user):
        return JsonResponse({'status': 'forbidden',
                             'message': "Ita-boot la iha permisaun ba módulu ida-ne'e."}, status=403)
    try:
        submission_id = uuid_lib.UUID(request.POST.get('uuid', ''))
    except ValueError:
        return JsonResponse({'status': 'invalid', 'message': 'UUID la válidu.'}, status=400)

    previous = OfflineSubmission.objects.filter(uuid=submission_id).select_related('benefisiariu').first()
    if previous is not None:
        if previous.user_id != request.user.id:
            return JsonResponse({'status': 'forbidden', 'message': 'Rejistu ne\'e husi utilizador seluk.'}, status=403)
        url = reverse(cfg['detail_url'], args=[previous.benefisiariu.hashed]) if previous.benefisiariu else ''
        return JsonResponse({'status': 'ok', 'duplicate': True, 'url': url,
                             'messages': ['Rejistu ne\'e sinkroniza tiha ona.']})

    data, files = _split_steps(request)
    steps = [s for s in STEP_ORDER if s not in OPTIONAL_STEPS or _has_values(data[s])]

    # 1) Validasaun ho form online nian → erru kada kampu
    errors = {}
    for step in steps:
        form_class, _view = cfg['steps'][step]
        payload = data[step].copy()
        form = form_class(payload, files[step]) if step == 'benef' else form_class(payload)
        if not form.is_valid():
            errors[step] = {name: [str(e) for e in errs] for name, errs in form.errors.items()}
    if errors:
        return JsonResponse({'status': 'invalid', 'errors': errors,
                             'message': 'Kampu balu la válidu. Favor hadia no haruka fali.'}, status=422)

    # 2) Rai liuhusi view online nian, hotu iha tranzasaun ida
    notes = []
    try:
        with transaction.atomic():
            response, new = _run_step(request, 'benef', cfg['steps']['benef'][1], data['benef'], files['benef'])
            notes += new
            try:
                hashid = resolve(response['Location']).kwargs['hashid']
            except (Resolver404, KeyError):
                raise StepFailed('benef', ['Sistema la fó fali identifikasaun benefisiáriu.'])
            for step in steps[1:]:
                _response, new = _run_step(request, step, cfg['steps'][step][1], data[step], files[step],
                                           hashid=hashid)
                notes += new
            from benefisiariu.models import Benefisiariu
            benef = Benefisiariu.objects.get(hashed=hashid)
            OfflineSubmission.objects.create(
                uuid=submission_id, user=request.user, module=module, benefisiariu=benef,
                filled_at=parse_datetime(request.POST.get('filled_at', '') or '') or timezone.now(),
            )
    except StepFailed as failure:
        return JsonResponse({'status': 'rejected', 'step': failure.step,
                             'message': f"{STEP_LABELS[failure.step]}: {' '.join(failure.texts)}"}, status=422)
    except Exception:  # noqa: BLE001 — la husik rejistu balun de'it iha baze-dadus
        log.exception('offline sync failed: module=%s user=%s', module, request.user.username)
        return JsonResponse({'status': 'error',
                             'message': 'Erru iha servidór bainhira rai dadus. Rejistu sei hein iha dispozitivu.'},
                            status=500)

    log.info('offline sync ok: module=%s user=%s benef=%s', module, request.user.username, benef.pk)
    return JsonResponse({'status': 'ok', 'url': reverse(cfg['detail_url'], args=[hashid]), 'messages': notes})
