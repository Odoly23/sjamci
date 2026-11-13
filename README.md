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
main/               # Main application
manufatureira/      # Gestão manufatureira
monitoring/         # Monitorizasaun impaktu negósiu
mpms/               # Modulu MPMS
notif/              # Sistema notifikasaun
report/             # Relatóriu no dashboard
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
