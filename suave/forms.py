from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Field
from suave.models import  EkipaMember, ProductService, MainCustomer,Competitor, FixedAsset, MarketAssessment, FinancialAssessment, CreditInfo
from kni.models import  Business, LocBussiness, Program, Employee, Finance
from custom.models import AdministrativePost, Village, TIpu_Programa, Year, Faze


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

class BusinessKSForm(forms.ModelForm):
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
                Column('size', css_class='col-md-4'),
            ),
            HTML(_BTN),
        )


class LocBusinessKSForm(forms.ModelForm):
    class Meta:
        model  = LocBussiness
        fields = [
            'address','municipality', 'administrativepost', 'village',
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


class ProgramKSForm2(forms.ModelForm):
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


class EmployeeKSForm(forms.ModelForm):
    class Meta:
        model  = Employee
        fields = ['business', 'male', 'female']

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
                Column('male',   css_class='col-md-6'),
                Column('female', css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


class FinanceKSForm(forms.ModelForm):
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

class EkipaMemberForm(forms.ModelForm):
    class Meta:
        model  = EkipaMember
        fields = ['name', 'phone', 'role', 'is_active']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('name',  css_class='col-md-6'),
                Column('phone', css_class='col-md-6'),
            ),
            Row(
                Column('role',      css_class='col-md-6'),
                Column('is_active', css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


class ProductServiceForm(forms.ModelForm):
    class Meta:
        model  = ProductService
        fields = [
            'business', 'name',
            'production_volume', 'production_frequency',
            'sales_volume', 'sales_frequency', 'sales_amount',
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('business', css_class='col-md-6'),
                Column('name',     css_class='col-md-6'),
            ),
            Row(
                Column('production_volume',    css_class='col-md-6'),
                Column('production_frequency', css_class='col-md-6'),
            ),
            Row(
                Column('sales_volume',    css_class='col-md-4'),
                Column('sales_frequency', css_class='col-md-4'),
                Column('sales_amount',    css_class='col-md-4'),
            ),
            HTML(_BTN),
        )


class MainCustomerForm(forms.ModelForm):
    class Meta:
        model  = MainCustomer
        fields = ['business', 'name', 'demand_volume', 'frequency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('business', css_class='col-md-6'),
                Column('name',     css_class='col-md-6'),
            ),
            Row(
                Column('demand_volume', css_class='col-md-6'),
                Column('frequency',     css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


class CompetitorForm(forms.ModelForm):
    class Meta:
        model  = Competitor
        fields = ['business', 'name', 'demand_volume', 'frequency']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('business', css_class='col-md-6'),
                Column('name',     css_class='col-md-6'),
            ),
            Row(
                Column('demand_volume', css_class='col-md-6'),
                Column('frequency',     css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


class MarketAssessmentForm(forms.ModelForm):
    class Meta:
        model  = MarketAssessment
        fields = [
            'business',
            'promotion_strategy', 'current_challenges',
            'long_term_challenges', 'priority', 'response_strategy',
        ]
        widgets = {
            'promotion_strategy':   forms.Textarea(attrs={'rows': 3}),
            'current_challenges':   forms.Textarea(attrs={'rows': 3}),
            'long_term_challenges': forms.Textarea(attrs={'rows': 3}),
            'response_strategy':    forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('business', css_class='col-md-6'),
                Column('priority', css_class='col-md-6'),
            ),
            Row(
                Column('promotion_strategy', css_class='col-md-12'),
            ),
            Row(
                Column('current_challenges',   css_class='col-md-6'),
                Column('long_term_challenges', css_class='col-md-6'),
            ),
            Row(
                Column('response_strategy', css_class='col-md-12'),
            ),
            HTML(_BTN),
        )


class ProgramKSForm(forms.ModelForm):
    class Meta:
        model  = Program
        fields = ['program_type', 'faze', 'year', 'approved_amount', 'amount']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.fields['program_type'].queryset = TIpu_Programa.active_objects.filter(id=2) 
        self.fields['year'].queryset = Year.active_objects.filter(is_active=True)
        self.fields['faze'].queryset = Faze.active_objects.filter(id=6)
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('program_type', css_class='col-md-4'),
                Column('faze',         css_class='col-md-4'),
                Column('year',         css_class='col-md-4'),
            ),
            Row(
                Column('approved_amount', css_class='col-md-6'),
                Column('amount',          css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


class FinancialAssessmentForm(forms.ModelForm):
    class Meta:
        model  = FinancialAssessment
        fields = [
            'business',
            'accounting_book', 'inventory_method', 'inventory_frequency',
            'monthly_revenue', 'annual_revenue', 'projected_revenue',
            'pays_tax', 'monthly_tax', 'total_assets',
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
            HTML('<hr><p class="text-muted font-weight-bold">Kontabilidade &amp; Inventariu</p>'),
            Row(
                Column('accounting_book',     css_class='col-md-4'),
                Column('inventory_method',    css_class='col-md-4'),
                Column('inventory_frequency', css_class='col-md-4'),
            ),
            HTML('<hr><p class="text-muted font-weight-bold">Rendimento</p>'),
            Row(
                Column('monthly_revenue',   css_class='col-md-4'),
                Column('annual_revenue',    css_class='col-md-4'),
                Column('projected_revenue', css_class='col-md-4'),
            ),
            HTML('<hr><p class="text-muted font-weight-bold">Impostu &amp; Assets</p>'),
            Row(
                Column('pays_tax',     css_class='col-md-4'),
                Column('monthly_tax',  css_class='col-md-4'),
                Column('total_assets', css_class='col-md-4'),
            ),
            HTML(_BTN),
        )


class FixedAssetForm(forms.ModelForm):
    class Meta:
        model  = FixedAsset
        fields = ['financial', 'name', 'value']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('financial', css_class='col-md-12'),
            ),
            Row(
                Column('name',  css_class='col-md-6'),
                Column('value', css_class='col-md-6'),
            ),
            HTML(_BTN),
        )


class CreditInfoForm(forms.ModelForm):
    class Meta:
        model  = CreditInfo
        fields = [
            'business',
            'took_credit', 'provider', 'amount',
            'satisfied', 'wants_more',
            'preferred_institution', 'reason_preference',
            'repayment_status', 'repayment_notes', 'recommendation',
            'collateral_amount', 'approved_by_bank',
            'has_repayment_problem', 'program_continuation',
        ]
        widgets = {
            'reason_preference': forms.Textarea(attrs={'rows': 2}),
            'repayment_notes':   forms.Textarea(attrs={'rows': 2}),
            'recommendation':    forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('business', css_class='col-md-12'),
            ),
            HTML('<hr><p class="text-muted font-weight-bold">Kreditu Foun</p>'),
            Row(
                Column('took_credit', css_class='col-md-4'),
                Column('provider',    css_class='col-md-4'),
                Column('amount',      css_class='col-md-4'),
            ),
            HTML('<hr><p class="text-muted font-weight-bold">Preferensia &amp; Espetativa</p>'),
            Row(
                Column('satisfied',             css_class='col-md-4'),
                Column('wants_more',            css_class='col-md-4'),
                Column('preferred_institution', css_class='col-md-4'),
            ),
            Row(
                Column('reason_preference', css_class='col-md-12'),
            ),
            HTML('<hr><p class="text-muted font-weight-bold">Situasaun Pagamentu</p>'),
            Row(
                Column('repayment_status', css_class='col-md-6'),
                Column('repayment_notes',  css_class='col-md-6'),
            ),
            Row(
                Column('recommendation', css_class='col-md-12'),
            ),
            HTML('<hr><p class="text-muted font-weight-bold">Kolateral &amp; Banku</p>'),
            Row(
                Column('collateral_amount',     css_class='col-md-4'),
                Column('approved_by_bank',      css_class='col-md-4'),
                Column('has_repayment_problem', css_class='col-md-4'),
            ),
            Row(
                Column('program_continuation', css_class='col-md-4'),
            ),
            HTML(_BTN),
        )