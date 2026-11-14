# sjamci
# SJAMCI - Sistema Jestaun no Monitorizasaun

SJAMCI mak sistema Django ida ne'ebé dezenvolve atu ajuda prosesu jestaun, monitorizasaun, no administrasaun dadus benefisiáriu, utilizador, relatoriu, no atividade organizasional sira.

## 🚀 Teknologia

Project ida ne'e uza:

- Python 3
- Django
- SQLite3
- Bootstrap
- HTML/CSS/JavaScript
- Git & GitHub

---

## 📁 Estrutura Projetu

```bash
Asja/               # Django project configuration
benefisiariu/       # Gestão benefisiáriu
config/             # Utility, decorators, auth utils
custom/             # Custom configurations/models
kni/                # Modulu KNI
website/            # Pajina públiku (landing page: lian 4, mapa, gráfiku)
main/               # Main application
manufatureira/      # Gestão manufatureira
monitoring/         # Monitorizasaun impaktu negósiu
mpms/               # Modulu MPMS
notif/              # Sistema notifikasaun
offline/            # Rejistu offline (PWA) ba KNI, KS, MPMS
report/             # Relatóriu no dashboard
seguransa/          # 2FA, troka password, auditoria, backup
suave/              # Modulu suave
users/              # Gestão utilizador
manage.py
```

---

## ⚙️ Instalasaun

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # prenxe valór sira
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Grupu utilizador ne'ebé sistema uza: `admin`, `staff`, `XFD`, `KNI`, `KS`, `dnim`, `mpms`, `Cliente`.

## 🧪 Teste

```bash
python manage.py test
```

Teste sira verifika: template hotu kompila, naran URL no template ne'ebé refere eziste,
la iha rota duplikadu, API relatóriu presiza login, kontrolu asesu tuir grupu,
blokeiu login hafoin tentativa sala, no la iha password default iha kodigu.

## 🔐 Seguransa

- **HTTPS obrigatóriu** bainhira `DEBUG=False` (HSTS, cookie `Secure`/`HttpOnly`). Servidór proxy tenke haruka header `X-Forwarded-Proto`.
- **Blokeiu login**: tentativa sala dala 5 → konta blokeia minutu 15 (`LOGIN_FAILURE_LIMIT`, `LOGIN_COOLOFF_HOURS`).
- **Password**: mínimu karakter 10. Konta foun no reset simu password temporáriu aleatóriu ne'ebé hatudu dala ida de'it; la iha password default.
- **API relatóriu** (`/Api/sumario/...`) presiza sesaun login.
- **Kontrolu asesu** tuir grupu; asesu la autorizadu simu pajina 403.
- **Audit**: login/logout rejista iha *Master Data → Audit Login*; eventu seguransa hakerek ba `logs/security.log`.
- **Segredu** (SECRET_KEY, password baze-dadus, email) rai iha `.env` de'it — nunka iha Git.

## 🛡️ Funsionalidade seguransa no operasaun

| Funsionalidade | Oinsá uza |
|---|---|
| **Troka password obrigatóriu** | Konta foun ka reset tenke troka password temporáriu iha login dahuluk. Obriga konta hotu: `python manage.py force_password_change --all` |
| **Verifikasaun pasu-2 (2FA)** | Kada utilizador ativa iha menu *2FA* ho aplikasaun autentikadór (TOTP). Se lakon telemovel, admin reset iha painel admin → *Seguransa Konta* |
| **Rejistu atividade (auditoria)** | Kada kria/altera/hamoos dadus rejista ho utilizador, IP no valór uluk → foun. Haree iha *Master Data → Rejistu Atividade* (filtra, esporta CSV) |
| **Backup** | `python manage.py backup_data --keep 30` (rai iha `backups/`; restaura ho `loaddata`). Rekomenda halo ho cron loron-loron |
| **Health check** | `GET /healthz/` fó `200` se aplikasaun no baze-dadus la'o — ba monitorizasaun servidór |

Ezemplu cron (backup kalan-kalan tuku 02:00):

```bash
0 2 * * * cd /srv/sjamci && venv/bin/python manage.py backup_data --keep 30
```

## 🌐 Pajina públiku (landing page)

Pajina inisiál `/` loke ba públiku (utilizador ne'ebé login ona ba direta `/painel/`):

- **Barra leten**: telefone, lokalizasaun no email (karuk); bandeira 4 (loos) atu troka lian — Tetun, Português, English, Bahasa Indonesia.
- **Navbar no menu**, **slider**, kartaun númeru, programa, informasaun importante, funsionalidade, pergunta no kontaktu.
- **Mapa Timor-Leste** ho totál benefisiáriu tuir munisípiu, filtru **tinan**, tabela no **gráfiku** (tuir tinan, programa, seksu), no download CSV.
- Estatístika públiku hatudu de'it númeru agregadu (la iha naran, telefone ka dadus pesoál) no rai iha cache minutu 10.

**Troka lian iha sistema no painel admin**: bandeira 4 hanesan mós iha navbar sistema (hafoin login) no iha painel admin Django. Lian rai iha cookie ida de'it (`django_language`), entaun eskolla iha pajina públiku la'o ba fatin hotu.
- Sistema: menu, navbar, rodapé no pajina inisiu tradús (`website/ui_strings.py`); konteúdu pajina (formuláriu, tabela) sei iha Tetun.
- Painel admin Django: Português, English no Indonesia uza tradusaun Django nian; Tetun uza Português tanba Django la iha tradusaun Tetun.

Konfigurasaun:
- Kontaktu: `LANDING_PHONE`, `LANDING_EMAIL`, `LANDING_ADDRESS` iha `.env`.
- Slide no informasaun importante: painel admin → *Pajina Públiku* (ho tradusaun opsionál; se la iha slide, sistema uza slide default).
- Tradusaun testu fixu: `website/i18n.py`.
- Limite munisípiu: geoBoundaries / © OpenStreetMap contributors (ODbL 1.0), iha `website/static/website/tl-adm1.geojson`.

## 📱 Rejistu offline (PWA)

Ofisiál KNI, Kreditu Suave no MPMS bele rejista benefisiáriu iha kampu maski la iha internet.

1. Bainhira **online**, login no loke menu **Rejistu Offline** (dala ida, atu dispozitivu rai formuláriu). Bele *Instala iha dispozitivu* hanesan aplikasaun.
2. Iha kampu (**offline**), loke aplikasaun → *Benefisiáriu KNI / Kreditu Suave / MPMS* → prienxe dadus benefisiáriu, negósiu, lokalizasaun (ho botaun GPS) no programa → *Rai rejistu*.
3. Bainhira iha internet fali, rejistu haruka automátiku (ka *Sinkroniza agora*). Se sesaun remata, login fali — dadus iha dispozitivu la lakon.

Regra:
- Sinkronizasaun uza form no view online nian rasik, entaun validasaun no regra (ezemplu duplikadu naran/telefone, kria konta kliente KNI) hanesan.
- Kada rejistu iha UUID; haruka dala rua la kria duplikadu. Se pasu ida falla, la iha dadus balun de'it mak rai.
- Rejistu ne'ebé servidór rekuza hela iha dispozitivu ho razaun, no bele *Hadia*.
- Dadus hein sinkroniza rai **iha dispozitivu** (la enkripta) — uza dispozitivu ofisiál ho xave ekran. Hafoin sinkroniza, dadus pesoál hasai husi dispozitivu.
- PWA presiza **HTTPS** iha produsaun. Bainhira troka ficheiru iha `offline/static/`, aumenta `OFFLINE_CACHE_VERSION` iha `settings.py`.
- DNDI seidauk iha formuláriu (módulu seidauk iha modelu dadus).

## 🚀 Produsaun

```bash
export DJANGO_SETTINGS_MODULE=Asja.settings_prod
python manage.py check --deploy
python manage.py migrate
python manage.py collectstatic --noinput
gunicorn Asja.wsgi:application --bind 127.0.0.1:8000 --workers 3
```

`Asja.settings_prod` rekuza hahú se `ALLOWED_HOSTS` mamuk ka `*`, `SECRET_KEY` badak, ka baze-dadus SQLite.
Halo backup baze-dadus no pasta `media/` loron-loron.
