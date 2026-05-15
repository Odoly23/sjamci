import re
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect
from django.db import transaction
from config.decorators import allowed_users
from custom.models import (Minister, Diresaun, Position, Municipality, AdministrativePost,
                            Village, Sector, Status, Bussines_size, Category_Emp,
                            Year, Faze, TIpu_Programa)
from benefisiariu.models import Benefisiariu, AddressTL, Photo, AddressOrigin
from kni.models import Business, LocBussiness, Program, Employee, Finance
import openpyxl


# ══════════════════════════════════════════════════════════════════
# NORMALIZATION MAPS — typo / variasi penulisan → nama canonical
# ══════════════════════════════════════════════════════════════════

# Key: lowercase variasi di Excel  |  Value: lowercase nama di DB
MUNICIPALITY_ALIASES = {
    # Liquiçá — berbagai variasi ejaan → resolve ke nama DB
    'liquiça' : 'liquiçá',
    'liquica' : 'liquiçá',
    'liquisa' : 'liquiçá',
    'likisa'  : 'liquiçá',
    'liqisa'  : 'liquiçá',
    # Oe-Cusse / RAEOA
    'oe-cusse': 'regiao administrativa especial oe-cusse ambeno',
    'oecusse' : 'regiao administrativa especial oe-cusse ambeno',
    'oe cusse': 'regiao administrativa especial oe-cusse ambeno',
    'raeoa'   : 'regiao administrativa especial oe-cusse ambeno',
}

# Atauro bukan munisipiu — masuk Dili, dan AP = Atauro
MUNICIPALITY_AP_OVERRIDE = {
    'atauro': ('dili', 'atauro'),   # (mun_lowercase, ap_lowercase)
}

SECTOR_ALIASES = {
    'turizmu'    : 'turismu',
    'turismo'    : 'turismu',
    'turisme'    : 'turismu',
    'indusria'   : 'industria',
    'industri'   : 'industria',
    'industrias' : 'industria',
    'pesca'      : 'peska',
    'teknologia' : 'teknolojia',
    'teknologi'  : 'teknolojia',
    'komercio'   : 'komersiu',
    'komerciu'   : 'komersiu',
    'komersio'   : 'komersiu',
    'agricultura': 'agrikultura',
}


# ══════════════════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════════════════

def _clean(val):
    if val is None:
        return None
    s = str(val).strip()
    return s if s else None


def _safe_int(val, default=0):
    try:
        return int(val) if val is not None else default
    except (ValueError, TypeError):
        return default


def _safe_float(val):
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _normalize_municipality(raw):
    """
    Kembalikan (mun_canonical_lowercase, forced_ap_lowercase_or_None).
      Atauro        → ('dili', 'atauro')
      Liquica/variasi → ('liquica', None)  — sesuaikan dengan nama DB Anda
      Oe-cusse/variasi → nama lengkap RAEOA lowercase
    """
    if not raw:
        return None, None
    key = raw.strip().lower()
    if key in MUNICIPALITY_AP_OVERRIDE:
        mun, ap = MUNICIPALITY_AP_OVERRIDE[key]
        return mun, ap
    return MUNICIPALITY_ALIASES.get(key, key), None


def _normalize_sector(raw):
    if not raw:
        return None
    key = raw.strip().lower()
    return SECTOR_ALIASES.get(key, key)


def _parse_kni(kni_value):
    """
    Parse kolom KNI dengan berbagai format:
      'I 2021'               → ('I',   2021)
      'II 2022'              → ('II',  2022)
      'III 2022'             → ('III', 2022)
      'I Raeoa 2023'         → ('I',   2023)   kata tengah dibuang
      'KNI IV 2023'          → ('IV',  2023)   prefix KNI dihapus
      'kNI V 2025'           → ('V',   2025)   case-insensitive
      'KNI Karpintaria 2023' → ('KNI', 2023)   faze = KNI langsung
    """
    if not kni_value:
        return None, None
    s = str(kni_value).strip()

    # 1. Format bersih: "I 2021", "IV 2023", "V 2025"
    m = re.match(r'^(I{1,3}|IV|V)\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        return m.group(1).upper(), int(m.group(2))

    # 2. Faze romawi + kata tengah + tahun: "I Raeoa 2023", "II Dili 2022"
    #    → ambil faze & tahun, buang kata tengah
    m = re.match(r'^(I{1,3}|IV|V)\s+\S+\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        return m.group(1).upper(), int(m.group(2))

    # 3. Prefix KNI + faze romawi: "KNI IV 2023", "kNI V 2025"
    m = re.match(r'^KNI\s+(I{1,3}|IV|V)\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        return m.group(1).upper(), int(m.group(2))

    # 4. KNI + kata lain + tahun: "KNI Karpintaria 2023" → faze = KNI
    m = re.match(r'^KNI\s+\w.*?\s+(\d{4})$', s, re.IGNORECASE)
    if m:
        return 'KNI', int(m.group(1))

    # 5. Fallback: ambil tahun saja, faze None
    m = re.search(r'(\d{4})', s)
    return None, (int(m.group(1)) if m else None)


# ══════════════════════════════════════════════════════════════════
# MAIN VIEW
# ══════════════════════════════════════════════════════════════════

@login_required
@allowed_users(allowed_roles=['KNI'])
def import_kni_excel(request):
    """
    Upload dan proses file Excel KNI.

    Kolom Excel (row 1 = header, data mulai row 2):
      [0]  No
      [1]  Naran Kompletu
      [2]  Genero
      [3]  No. Tlp.
      [4]  Naran Negocio/Empresa
      [5]  Ideia Negocio
      [6]  Seitor Prinsipal
      [7]  Total Trabalhador
      [8]  Feto
      [9]  Mane
      [10] Lokalizasaun negosiu
      [11] Munisipiu
      [12] Postu-Administrativu
      [13] Suku
      [14] Aldeia
      [15] KNI          ← di-parse → Faze + Year
      [16] Total Orsamento
    """

    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        # ── validasi file ──────────────────────────────────────
        if not excel_file:
            messages.error(request, "Favor hili arquivo Excel ida!")
            return redirect('import_kni_excel')

        if not excel_file.name.endswith(('.xlsx', '.xls')):
            messages.error(request, "Arquivo tenke iha formatu .xlsx ka .xls!")
            return redirect('import_kni_excel')

        try:
            wb = openpyxl.load_workbook(excel_file, read_only=True, data_only=True)
            ws = wb.active
        except Exception as e:
            messages.error(request, f"La konsege loke arquivo Excel: {e}")
            return redirect('import_kni_excel')

        # ── cache data master (query sekali saja) ──────────────
        status_default   = Status.objects.get(pk=1)

        program_type_kni = TIpu_Programa.objects.filter(name='KNI').first()
        if not program_type_kni:
            messages.error(request, "Tipu Programa 'KNI' la iha iha sistema. Favor kria uluk!")
            return redirect('import_kni_excel')

        municipalities = {m.name.lower(): m for m in Municipality.objects.all()}
        admin_posts    = {a.name.lower(): a for a in AdministrativePost.objects.all()}
        villages       = {v.name.lower(): v for v in Village.objects.all()}
        sectors        = {s.name.lower(): s for s in Sector.objects.all()}
        fazes          = {f.name.upper(): f for f in Faze.objects.all()}   # include KNI & KREDITU
        years          = {y.year: y for y in Year.objects.all()}

        # ── iterasi baris ──────────────────────────────────────
        success_count = 0
        error_rows    = []   # [(row_num, pesan_error)]

        for idx, row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=2):
            try:
                # ── baca kolom ─────────────────────────────────
                col_name     = _clean(row[1])
                col_genero   = _clean(row[2])
                col_phone    = _clean(row[3])
                col_biz_name = _clean(row[4])
                col_idea     = _clean(row[5])
                col_sector   = _clean(row[6])
                col_feto     = _safe_int(row[8])
                col_mane     = _safe_int(row[9])
                col_address  = _clean(row[10])
                col_mun_raw  = _clean(row[11])
                col_ap_raw   = _clean(row[12])
                col_village  = _clean(row[13])
                col_aldeia   = _clean(row[14])
                col_kni      = _clean(row[15])
                col_budget   = _safe_float(row[16])

                # skip baris kosong
                if not col_name and not col_biz_name:
                    continue

                # ── resolve Municipality ────────────────────────
                mun_canonical, forced_ap = _normalize_municipality(col_mun_raw)
                mun_obj = municipalities.get(mun_canonical) if mun_canonical else None
                if col_mun_raw and not mun_obj:
                    error_rows.append((idx,
                        f"Munisipiu '{col_mun_raw}' la konsege resolve "
                        f"(tenta '{mun_canonical}') — la iha iha sistema"))
                    continue

                # ── resolve Administrative Post ─────────────────
                # Atauro → forced AP 'atauro'; selainnya pakai kolom Excel
                if forced_ap:
                    ap_obj = admin_posts.get(forced_ap)
                else:
                    ap_obj = admin_posts.get(col_ap_raw.lower()) if col_ap_raw else None

                # ── resolve Village ─────────────────────────────
                vil_obj = villages.get(col_village.lower()) if col_village else None

                # ── resolve Sector ──────────────────────────────
                sector_canonical = _normalize_sector(col_sector)
                sector_obj = sectors.get(sector_canonical) if sector_canonical else None
                if col_sector and not sector_obj:
                    error_rows.append((idx,
                        f"Setor '{col_sector}' la konsege resolve "
                        f"(tenta '{sector_canonical}') — la iha iha sistema"))
                    continue

                # ── parse KNI → Faze + Year ─────────────────────
                faze_name, year_int = _parse_kni(col_kni)
                faze_obj = fazes.get(faze_name.upper()) if faze_name else None
                year_obj = years.get(year_int) if year_int else None

                if col_kni and not faze_obj:
                    error_rows.append((idx,
                        f"Faze '{faze_name}' husi KNI '{col_kni}' la iha iha sistema"))
                    continue

                if col_kni and not year_obj:
                    error_rows.append((idx,
                        f"Tinan '{year_int}' husi KNI '{col_kni}' la iha iha sistema"))
                    continue

                # ── simpan ke DB (transaksi per baris) ──────────
                with transaction.atomic():

                    # Benefisiariu
                    benefisiariu = Benefisiariu.objects.create(
                        name   = col_name,
                        sex    = col_genero,
                        phone  = col_phone,
                        status = status_default,
                    )

                    # AddressTL (OneToOne)
                    AddressTL.objects.create(
                        benefisiariu       = benefisiariu,
                        address            = col_address,
                        municipality       = mun_obj,
                        administrativepost = ap_obj,
                        village            = vil_obj,
                        aldeia             = col_aldeia,
                    )

                    # Business
                    business = Business.objects.create(
                        benefisiariu = benefisiariu,
                        name         = col_biz_name or col_name,
                        idea         = col_idea,
                        sector       = sector_obj,
                    )

                    # LocBussiness (sama dengan AddressTL; admin edit nanti jika beda)
                    LocBussiness.objects.create(
                        benefisiariu       = benefisiariu,
                        address            = col_address,
                        municipality       = mun_obj,
                        administrativepost = ap_obj,
                        village            = vil_obj,
                        aldeia             = col_aldeia,
                    )

                    # Program — faze & year dari parse KNI
                    # Program.save() akan override status sesuai benefisiariu.status
                    Program.objects.create(
                        benefisiariu    = benefisiariu,
                        program_type    = program_type_kni,
                        faze            = faze_obj,
                        year            = year_obj,
                        approved_amount = col_budget,
                        amount          = col_budget,
                        status          = status_default,
                    )

                    # Employee — total dihitung otomatis oleh Employee.save()
                    Employee.objects.create(
                        business = business,
                        male     = col_mane,
                        female   = col_feto,
                    )

                    # Finance
                    Finance.objects.create(
                        business = business,
                        budget   = col_budget,
                    )

                success_count += 1

            except Exception as e:
                error_rows.append((idx, str(e)))

        # ── ringkasan hasil ────────────────────────────────────
        if success_count:
            messages.success(request, f"✅ Suksesu importa linha {success_count} husi Excel!")

        for row_num, err in error_rows:
            messages.warning(request, f"⚠️ Linha {row_num}: {err}")

        if not success_count and not error_rows:
            messages.info(request, "Arquivo Excel mamuk ka la iha dadus.")

        return redirect('import_kni_excel')

    # GET — tampilkan form upload
    context = {
        'title'     : 'Import Dadus Excel KNI',
        'legend'    : 'Import Dadus Excel KNI',
        'link_antes': [
            {'link_name': 'kni-dash',        'link_text': 'Painel KNI'},
            {'link_name': 'import_kni_excel', 'link_text': 'Import Dadus Excel KNI'},
        ],
    }
    return render(request, 'Dash/form.html', context)