from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Field

from manufatureira.models import Manufatur, Lokalizasaun, Membro, Aktividade
from custom.models import Municipality, AdministrativePost, Village, Year, Status, IndustryType, Tipu_Apoio
from kni.models import Program, Business, LocBussiness, Employee, Finance


_BTN = """
<div class="mt-4 d-flex" style="gap:0.5rem;">
    <button type="submit" class="btn btn-sm btn-success">
        <i class="fa fa-save"></i> Rai
    </button>
    <button type="button" class="btn btn-sm btn-secondary" onclick="history.back()">
        <i class="fa fa-times"></i> Cancel
    </button>
</div>
"""

_ALERT = """
<div class="alert alert-info py-2">
    Kampu ho simbolu <strong>(*)</strong> obrigatóriu tenki prienxe!
</div>
"""



class BusinessDNIMForm(forms.ModelForm):
    class Meta:
        model  = Business
        fields = ['name', 'idea', 'sector', 'category','size']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('name', css_class='col-md-6'),
                Column('idea', css_class='col-md-6'),
            ),
            Row(
                Column('sector',   css_class='col-md-4'),
                Column('category', css_class='col-md-4'),
                Column('size', css_class='col-md-4')
            ),
            HTML(_BTN),
        )


class LocBusinessDNIMForm(forms.ModelForm):
    class Meta:
        model  = LocBussiness
        fields = [
            'municipality', 'administrativepost', 'village','address',
            'aldeia', 'latitude', 'longitude', 'area_polygon',
        ]
        widgets = {'area_polygon': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['area_polygon'].required       = False
        self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        self.fields['village'].queryset            = Village.objects.none()

        if 'municipality' in self.data:
            try:
                mun_id = int(self.data.get('municipality'))
                self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(
                    municipality_id=mun_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.municipality:
            self.fields['administrativepost'].queryset = \
                self.instance.municipality.administrativepost_set.order_by('name')

        if 'administrativepost' in self.data:
            try:
                ap_id = int(self.data.get('administrativepost'))
                self.fields['village'].queryset = Village.objects.filter(
                    administrativepost_id=ap_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.administrativepost:
            self.fields['village'].queryset = \
                self.instance.administrativepost.village_set.order_by('name')

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('municipality',       css_class='col-md-4'),
                Column('administrativepost', css_class='col-md-4'),
                Column('village',            css_class='col-md-4'),
            ),
            Row(
                Column('aldeia',    css_class='col-md-4'),
                Column('latitude',  css_class='col-md-4'),
                Column('longitude', css_class='col-md-4'),
            ),
            Field('area_polygon'),
            HTML(_BTN),
        )


class ProgramDNIMForm(forms.ModelForm):
    class Meta:
        model  = Program
        fields = ['faze', 'year', 'approved_amount', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['year'].queryset = Year.active_objects.all().order_by('-year')
        self.fields['faze'].queryset = Faze.active_objects.exclude(name="KREDITU")
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('year', css_class='col-md-6'),
                Column('faze', css_class='col-md-6')
            ),
            Row(
                Column('approved_amount', css_class='col-md-6'),
                Column('amount',          css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


class EmployeeDNIMForm(forms.ModelForm):
    class Meta:
        model  = Employee
        fields = ['business', 'male', 'female']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('business', css_class='col-md-12'),
            ),
            Row(
                Column('male',   css_class='col-md-6'),
                Column('female', css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


class FinanceDNIMForm(forms.ModelForm):
    class Meta:
        model  = Finance
        fields = ['business', 'budget']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('business', css_class='col-md-6'),
                Column('budget',   css_class='col-md-6'),
            ),
            HTML(_BTN),
        )
# =========================
# MANUFATUR FORM
# =========================
class ManufaturForm(forms.ModelForm):
    class Meta:
        model = Manufatur
        fields = [
            'name',
            'benefisiariu',
            'business',
            'leader_name',
            'phone',
            'status'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('name', css_class='col-md-6'),
                Column('leader_name', css_class='col-md-6'),
            ),
            Row(
                Column('benefisiariu', css_class='col-md-4'),
                Column('business', css_class='col-md-4'),
                Column('phone', css_class='col-md-4'),
            ),
            Row(
                Column('status', css_class='col-md-12'),
            ),
            HTML(_BTN),
        )


# =========================
# LOKALIZASAUN FORM
# =========================
class LokalizasaunForm(forms.ModelForm):
    class Meta:
        model = Lokalizasaun
        fields = [
            'municipality',
            'administrativepost',
            'village',
            'aldeia',
            'latitude',
            'longitude',
            'area_polygon',
        ]
        widgets = {
            'area_polygon': forms.HiddenInput()
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['area_polygon'].required = False

        self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        self.fields['village'].queryset = Village.objects.none()

        if 'municipality' in self.data:
            try:
                mun = int(self.data.get('municipality'))
                self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(
                    municipality_id=mun
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.municipality:
            self.fields['administrativepost'].queryset = self.instance.municipality.administrativepost_set.all()

        if 'administrativepost' in self.data:
            try:
                ap = int(self.data.get('administrativepost'))
                self.fields['village'].queryset = Village.objects.filter(
                    administrativepost_id=ap
                )
            except (ValueError, TypeError):
                pass

        elif self.instance.pk and self.instance.administrativepost:
            self.fields['village'].queryset = self.instance.administrativepost.village_set.all()

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
            Field('area_polygon'),
            HTML(_BTN),
        )


# =========================
# MEMBRO FORM
# =========================
class MembroForm(forms.ModelForm):
    class Meta:
        model = Membro
        fields = ['manufatur', 'male', 'female']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('manufatur', css_class='col-md-12'),
            ),
            Row(
                Column('male', css_class='col-md-6'),
                Column('female', css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


# =========================
# AKTIVIDADE FORM
# =========================
class AktividadeForm(forms.ModelForm):
    class Meta:
        model = Aktividade
        fields = [
            'manufatur',
            'program',
            'industry_type',
            'support_type',
            'year',
            'amount',
            'status',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.fields['year'].queryset = Year.objects.all().order_by('-year')

        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('manufatur', css_class='col-md-6'),
                Column('program', css_class='col-md-6'),
            ),
            Row(
                Column('industry_type', css_class='col-md-4'),
                Column('support_type', css_class='col-md-4'),
                Column('year', css_class='col-md-4'),
            ),
            Row(
                Column('amount', css_class='col-md-6'),
                Column('status', css_class='col-md-6'),
            ),
            HTML(_BTN),
        )