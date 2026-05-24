from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Field

from custom.models import AdministrativePost, Village, Year
from .models import (
    mpmsEmpresa,
    mpmsLokalizasaun,
    mpmsLisensamentu,
    mpmsKapital,
    mpmsEmpregador,
    mpmsMateriaPrima,
    mpmsAtividade
)

# =========================================================
# SHARED UI
# =========================================================

_BTN = """
<div class="mt-4 d-flex" style="gap:0.5rem;">
    <button class="btn btn-sm btn-success" type="submit">
        <i class="fa fa-save"></i> Rai
    </button>

    <button class="btn btn-sm btn-secondary"
            type="button"
            onclick="history.back()">

        <i class="fa fa-times"></i> Kansela
    </button>
</div>
"""

_ALERT = """
<div class="alert alert-info py-2">
    Kampu ho simbolu <strong>(*)</strong>
    obrigatóriu tenki prienxe.
</div>
"""

# =========================================================
# EMPRESA
# =========================================================

class MpmsEmpresaForm(forms.ModelForm):

    class Meta:
        model = mpmsEmpresa

        fields = [
            'benefisiariu',
            'business',
            'company_name',
            'tipo_atividade',
            'tinan_hari',
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(

            HTML(_ALERT),

            Row(
                Column('benefisiariu', css_class='col-md-6'),
                Column('business', css_class='col-md-6'),
            ),

            Row(
                Column('company_name', css_class='col-md-8'),
                Column('tinan_hari', css_class='col-md-4'),
            ),

            Row(
                Column('tipo_atividade', css_class='col-md-12'),
            ),

            HTML(_BTN),
        )


# =========================================================
# LOKALIZASAUN
# =========================================================

class MpmsLokalizasaunForm(forms.ModelForm):

    class Meta:
        model = mpmsLokalizasaun

        fields = [
            'municipality',
            'administrativepost',
            'village',
            'aldeia',
            'rua_avenida',
            'latitude',
            'longitude',
            'area_polygon',
        ]

        widgets = {
            'area_polygon': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        self.fields['village'].queryset = Village.objects.none()

        if 'municipality' in self.data:

            try:
                mun_id = int(self.data.get('municipality'))

                self.fields['administrativepost'].queryset = (
                    AdministrativePost.objects.filter(
                        municipality_id=mun_id
                    ).order_by('name')
                )

            except:
                pass

        if 'administrativepost' in self.data:

            try:
                post_id = int(self.data.get('administrativepost'))

                self.fields['village'].queryset = (
                    Village.objects.filter(
                        administrativepost_id=post_id
                    ).order_by('name')
                )

            except:
                pass

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(

            HTML(_ALERT),

            Row(
                Column('municipality', css_class='col-md-4'),
                Column('administrativepost', css_class='col-md-4'),
                Column('village', css_class='col-md-4'),
            ),

            Row(
                Column('aldeia', css_class='col-md-4'),
                Column('latitude', css_class='col-md-4'),
                Column('longitude', css_class='col-md-4'),
            ),

            Row(
                Column('rua_avenida', css_class='col-md-12'),
            ),

            Field('area_polygon'),

            HTML(_BTN),
        )


# =========================================================
# LISENSAMENTU
# =========================================================

class MpmsLisensamentuForm(forms.ModelForm):

    class Meta:
        model = mpmsLisensamentu

        fields = [
            'lisensamentu',
            'lisensamentu_status',
            'tipo_rai',
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(

            HTML(_ALERT),

            Row(
                Column('lisensamentu', css_class='col-md-4'),
                Column('lisensamentu_status', css_class='col-md-4'),
                Column('tipo_rai', css_class='col-md-4'),
            ),

            HTML(_BTN),
        )


# =========================================================
# KAPITAL
# =========================================================

class MpmsKapitalForm(forms.ModelForm):

    class Meta:
        model = mpmsKapital

        fields = [
            'kapital_investimento',
            'tipu_fundus',
            'total_fundus',
            'lukru_brutu_mes',
            'lukru_brutu_ano',
            'lukru_likidu_mes',
            'lukru_likidu_ano',
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(

            HTML(_ALERT),

            HTML('<hr><p class="font-weight-bold text-muted">Kapital</p>'),

            Row(
                Column('kapital_investimento', css_class='col-md-4'),
                Column('tipu_fundus', css_class='col-md-4'),
                Column('total_fundus', css_class='col-md-4'),
            ),

            HTML('<hr><p class="font-weight-bold text-muted">Lukru Brutu</p>'),

            Row(
                Column('lukru_brutu_mes', css_class='col-md-6'),
                Column('lukru_brutu_ano', css_class='col-md-6'),
            ),

            HTML('<hr><p class="font-weight-bold text-muted">Lukru Likidu</p>'),

            Row(
                Column('lukru_likidu_mes', css_class='col-md-6'),
                Column('lukru_likidu_ano', css_class='col-md-6'),
            ),

            HTML(_BTN),
        )


# =========================================================
# EMPREGADOR
# =========================================================

class MpmsEmpregadorForm(forms.ModelForm):

    class Meta:
        model = mpmsEmpregador

        fields = [
            'nasional_mane',
            'nasional_feto',
            'internasional_mane',
            'internasional_feto',
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(

            HTML(_ALERT),

            HTML('<hr><p class="font-weight-bold text-muted">Nasionál</p>'),

            Row(
                Column('nasional_mane', css_class='col-md-6'),
                Column('nasional_feto', css_class='col-md-6'),
            ),

            HTML('<hr><p class="font-weight-bold text-muted">Internasionál</p>'),

            Row(
                Column('internasional_mane', css_class='col-md-6'),
                Column('internasional_feto', css_class='col-md-6'),
            ),

            HTML(_BTN),
        )


# =========================================================
# MATERIA PRIMA
# =========================================================

class MpmsMateriaPrimaForm(forms.ModelForm):

    class Meta:
        model = mpmsMateriaPrima

        fields = [
            'kustu',
            'origem',
            'deskrisaun',
        ]

        widgets = {
            'deskrisaun': forms.Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(

            HTML(_ALERT),

            Row(
                Column('kustu', css_class='col-md-6'),
                Column('origem', css_class='col-md-6'),
            ),

            Row(
                Column('deskrisaun', css_class='col-md-12'),
            ),

            HTML(_BTN),
        )


# =========================================================
# ATIVIDADE
# =========================================================

class MpmsAtividadeForm(forms.ModelForm):

    class Meta:
        model = mpmsAtividade

        fields = [
            'program',
            'tipu_apoio',
            'year',
            'amount',
            'status',
            'observasaun',
        ]

        widgets = {
            'observasaun': forms.Textarea(attrs={'rows': 3})
        }

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.fields['year'].queryset = (
            Year.active_objects.all().order_by('-year')
        )

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(

            HTML(_ALERT),

            Row(
                Column('program', css_class='col-md-6'),
                Column('tipu_apoio', css_class='col-md-6'),
            ),

            Row(
                Column('year', css_class='col-md-4'),
                Column('amount', css_class='col-md-4'),
                Column('status', css_class='col-md-4'),
            ),

            Row(
                Column('observasaun', css_class='col-md-12'),
            ),

            HTML(_BTN),
        )