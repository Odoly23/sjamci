"""Konfigurasaun módulu ne'ebé bele prienxe offline.

Kada módulu uza *view* no *form* online nian rasik, atu dadus ne'ebé
sinkroniza liuhusi offline pasa regra hanesan ho rejistu online.
"""
from benefisiariu.forms import BenefisiariuForm
from kni import views as kni_views
from kni.forms import BusinessKNIForm, LocBusinessKNIForm, ProgramKNIForm
from mpms import views as mpms_views
from mpms.forms import BusinessMPMSForm, ProgramMPMSForm
from suave import views as ks_views
from suave.forms import BusinessKSForm, LocBusinessKSForm, ProgramKSForm

# Orden pasu: benefisiáriu → negósiu → lokalizasaun (opsionál) → programa
STEP_LABELS = {
    'benef': 'Dadus Benefisiáriu',
    'business': 'Negósiu',
    'location': 'Lokalizasaun Negósiu',
    'program': 'Programa / Apoiu',
}
STEP_ORDER = ['benef', 'business', 'location', 'program']
OPTIONAL_STEPS = {'location'}

MODULES = {
    'kni': {
        'label': 'KNI',
        'role': 'KNI',
        'detail_url': 'benef-detail-kni',
        'steps': {
            'benef': (BenefisiariuForm, kni_views.add_benef_kni),
            'business': (BusinessKNIForm, kni_views.Business_Add),
            'location': (LocBusinessKNIForm, kni_views.Localidade_Add),
            'program': (ProgramKNIForm, kni_views.Program_Add),
        },
    },
    'ks': {
        'label': 'Kreditu Suave',
        'role': 'KS',
        'detail_url': 'benef-detail-ks',
        'steps': {
            'benef': (BenefisiariuForm, ks_views.add_benef_ks),
            'business': (BusinessKSForm, ks_views.Business_Add_ks),
            'location': (LocBusinessKSForm, ks_views.Localidade_Add_ks),
            'program': (ProgramKSForm, ks_views.Program_Add_ks),
        },
    },
    'mpms': {
        'label': 'MPMS',
        'role': 'mpms',
        'detail_url': 'mpms-detail',
        'steps': {
            'benef': (BenefisiariuForm, mpms_views.add_benef_mpms),
            'business': (BusinessMPMSForm, mpms_views.Business_Add_mpms),
            'location': (LocBusinessKNIForm, mpms_views.Localidade_Add_mpms),
            'program': (ProgramMPMSForm, mpms_views.Program_Add_mpms),
        },
    },
}

# Kampu ne'ebé sistema prenxe automátiku (la hatudu iha formuláriu offline)
HIDDEN_FIELDS = {'benef': {'status'}, 'location': {'area_polygon'}}
