from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Field
from benefisiariu.models import Benefisiariu, AddressTL, AddressOrigin, Photo
from kni.models import Business, LocBussiness, Program, Employee, Finance, BusinessBaseline, BusinessMonitoring
from custom.models import AdministrativePost, Village, Year, Faze


_BTN = """
    <div class="mt-4 d-flex" style="gap: 0.5rem;">
        <button class="btn btn-sm btn-success" type="submit">
            <i class="fa fa-save"></i> Rai
        </button>
        <button class="btn btn-sm btn-secondary" type="button" onclick="history.back()">
            <i class="fa fa-times"></i> Cancela
        </button>
    </div>
"""

_ALERT = """
    <div class="alert alert-info py-2">
        Kampu ho simbolu <strong>(*)</strong> obrigatóriu tenki prienxe!
    </div>
"""


class BusinessKNIForm(forms.ModelForm):
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


class LocBusinessKNIForm(forms.ModelForm):
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


class ProgramKNIForm(forms.ModelForm):
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


class EmployeeKNIForm(forms.ModelForm):
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


class FinanceKNIForm(forms.ModelForm):
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



class BusinessBaselineForm(forms.ModelForm):

    class Meta:
        model = BusinessBaseline

        fields = [
            'business',
            'daily_income_before',
            'monthly_income_before',
            'yearly_income_before',
            'employee_before',
            'asset_before',
            'sales_before',
            'note',
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(

            HTML(_ALERT),

            Row(
                Column('business', css_class='col-md-12'),
            ),

            Row(
                Column('daily_income_before', css_class='col-md-4'),
                Column('monthly_income_before', css_class='col-md-4'),
                Column('yearly_income_before', css_class='col-md-4'),
            ),

            Row(
                Column('employee_before', css_class='col-md-4'),
                Column('asset_before', css_class='col-md-4'),
                Column('sales_before', css_class='col-md-4'),
            ),

            Row(
                Column('note', css_class='col-md-12'),
            ),

            HTML(_BTN),
        )


class BusinessMonitoringForm(forms.ModelForm):
    class Meta:
        model = BusinessMonitoring
        fields = [
            'month',
            'daily_income',
            'monthly_income',
            'yearly_income',
            'total_sales',
            'total_assets',
            'total_employee',
            'source_data',
            'evidence_file',
            'note',
        ]

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('month', css_class='col-md-4'),
                Column('daily_income', css_class='col-md-4'),
                Column('monthly_income', css_class='col-md-4'),
            ),

            Row(
                Column('yearly_income', css_class='col-md-4'),
                Column('total_sales', css_class='col-md-4'),
                Column('total_assets', css_class='col-md-4'),
            ),

            Row(
                Column('total_employee', css_class='col-md-4'),
                Column('source_data', css_class='col-md-4'),
                Column('evidence_file', css_class='col-md-6'),
                
            ),

            Row(
                Column('note', css_class='col-md-12'),
            ),

            HTML(_BTN),
        )
