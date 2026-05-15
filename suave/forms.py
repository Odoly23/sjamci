from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Field
from benefisiariu.models import (
    Program, EkipaMember, ProductService, MainCustomer,
    Competitor, FixedAsset, MarketAssessment, FinancialAssessment, CreditInfo,
)
from custom.models import AdministrativePost, Village


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
        fields = ['program_type', 'faze', 'year', 'approved_amount', 'amount', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('program_type', css_class='col-md-4'),
                Column('faze',         css_class='col-md-4'),
                Column('year',         css_class='col-md-4'),
            ),
            Row(
                Column('approved_amount', css_class='col-md-4'),
                Column('amount',          css_class='col-md-4'),
                Column('status',          css_class='col-md-4'),
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