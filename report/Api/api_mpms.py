from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from django.db.models import Count, Sum
from mpms.models import  mpmsEmpresa, mpmsLokalizasaun, mpmsLisensamentu,\
                         mpmsKapital, mpmsEmpregador, mpmsMateriaPrima, mpmsAtividade
from benefisiariu.models import Benefisiariu


# ══════════════════════════════════════════════════════════════
#  1. TOTAL EMPRESA TUIR MUNISIPIU
# ══════════════════════════════════════════════════════════════
class APIMpmsPerMunisipiu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes     = [AllowAny]

    def get(self, request, format=None):
        data = (
            mpmsLokalizasaun.objects
            .values('municipality__name')
            .annotate(total=Count('empresa', distinct=True))
            .order_by('-total')
        )
        return Response({
            'label': [d['municipality__name'] or '-' for d in data],
            'obj':   [d['total'] for d in data],
        })


# ══════════════════════════════════════════════════════════════
#  2. TIPU FUNDUS (Ukuran Usaha) TUIR MUNISIPIU — Stacked Bar
# ══════════════════════════════════════════════════════════════
class APIMpmsTipuFundus(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes     = [AllowAny]

    def get(self, request, format=None):
        from mpms.models import TIPU_FUNDUS_CHOICES

        # Ambil semua munisipiu yang ada
        muns = (
            mpmsLokalizasaun.objects
            .values_list('municipality__name', flat=True)
            .distinct()
            .order_by('municipality__name')
        )

        datasets = []
        colors = {
            'home_industria__caseiras': '#e74c3c',
            'mikro':                   '#3498db',
            'pequenas':                '#2ecc71',
            'medias':                  '#f39c12',
            'grandes':                 '#9b59b6',
        }

        for key, label in TIPU_FUNDUS_CHOICES:
            values = []
            for mun in muns:
                total = mpmsKapital.objects.filter(
                    tipu_fundus=key,
                    empresa__lokalizasaun__municipality__name=mun
                ).count()
                values.append(total)

            datasets.append({
                'label':           label,
                'data':            values,
                'backgroundColor': colors.get(key, '#95a5a6'),
            })

        return Response({
            'labels':   list(muns),
            'datasets': datasets,
        })


# ══════════════════════════════════════════════════════════════
#  3. JENERU EMPRESARIU (Mane/Feto) TUIR MUNISIPIU
# ══════════════════════════════════════════════════════════════
class APIMpmsJeneru(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes     = [AllowAny]

    def get(self, request, format=None):
        mane = (
            mpmsEmpresa.objects
            .filter(benefisiariu__sex='Mane')
            .count()
        )
        feto = (
            mpmsEmpresa.objects
            .filter(benefisiariu__sex='Feto')
            .count()
        )
        return Response({
            'label': ['Mane', 'Feto'],
            'obj':   [mane, feto],
        })


# ══════════════════════════════════════════════════════════════
#  4. TIPO ATIVIDADE
# ══════════════════════════════════════════════════════════════
class APIMpmsTipoAtividade(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes     = [AllowAny]

    def get(self, request, format=None):
        data = (
            mpmsEmpresa.objects
            .values('tipo_atividade__name')
            .annotate(total=Count('id'))
            .order_by('-total')
        )
        return Response({
            'label': [d['tipo_atividade__name'] or 'Seluk' for d in data],
            'obj':   [d['total'] for d in data],
        })


# ══════════════════════════════════════════════════════════════
#  5. LISENSAMENTU (Iha/Laiha/Sei iha Prosesu)
# ══════════════════════════════════════════════════════════════
class APIMpmsLisensamentu(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes     = [AllowAny]

    def get(self, request, format=None):
        from mpms.models import LISENSAMENTU_CHOICES

        label, obj = [], []
        for key, display in LISENSAMENTU_CHOICES:
            total = mpmsLisensamentu.objects.filter(lisensamentu=key).count()
            label.append(display)
            obj.append(total)

        return Response({'label': label, 'obj': obj})


# ══════════════════════════════════════════════════════════════
#  6. KAPITAL INVESTIMENTO
# ══════════════════════════════════════════════════════════════
class APIMpmsKapital(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes     = [AllowAny]

    def get(self, request, format=None):
        from mpms.models import KAPITAL_RANGE_CHOICES

        label, obj = [], []
        for key, display in KAPITAL_RANGE_CHOICES:
            total = mpmsKapital.objects.filter(kapital_investimento=key).count()
            label.append(display)
            obj.append(total)

        return Response({'label': label, 'obj': obj})


# ══════════════════════════════════════════════════════════════
#  7. EMPREGADOR — Nasional vs Internasional per Munisipiu
# ══════════════════════════════════════════════════════════════
class APIMpmsEmpregador(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes     = [AllowAny]

    def get(self, request, format=None):
        muns = (
            mpmsLokalizasaun.objects
            .values_list('municipality__name', flat=True)
            .distinct()
            .order_by('municipality__name')
        )

        nasional_mane, nasional_feto = [], []
        inter_mane,    inter_feto    = [], []

        for mun in muns:
            emp = mpmsEmpregador.objects.filter(
                empresa__lokalizasaun__municipality__name=mun
            ).aggregate(
                nm=Sum('nasional_mane'),
                nf=Sum('nasional_feto'),
                im=Sum('internasional_mane'),
                if_=Sum('internasional_feto'),
            )
            nasional_mane.append(emp['nm'] or 0)
            nasional_feto.append(emp['nf'] or 0)
            inter_mane.append(emp['im'] or 0)
            inter_feto.append(emp['if_'] or 0)

        return Response({
            'labels': list(muns),
            'datasets': [
                {'label': 'Nasionál Mane',       'data': nasional_mane, 'backgroundColor': '#3498db'},
                {'label': 'Nasionál Feto',        'data': nasional_feto, 'backgroundColor': '#e74c3c'},
                {'label': 'Internasionál Mane',   'data': inter_mane,   'backgroundColor': '#2ecc71'},
                {'label': 'Internasionál Feto',   'data': inter_feto,   'backgroundColor': '#f39c12'},
            ]
        })


# ══════════════════════════════════════════════════════════════
#  8. MATERIA PRIMA ORIGEM
# ══════════════════════════════════════════════════════════════
class APIMpmsMateria(APIView):
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes     = [AllowAny]

    def get(self, request, format=None):
        from mpms.models import MATERIA_ORIGEM_CHOICES

        label, obj = [], []
        for key, display in MATERIA_ORIGEM_CHOICES:
            total = mpmsMateriaPrima.objects.filter(origem=key).count()
            label.append(display)
            obj.append(total)

        return Response({'label': label, 'obj': obj})