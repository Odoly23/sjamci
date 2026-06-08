from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Field
from monitoring.models import BusinessImpactMonitoring, FundUsage, BusinessAsset, CashFlow, FinancialBook
from django_summernote.widgets import SummernoteWidget

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

_CSS = """
<style>
    .conditional-field {
        transition: all 0.3s ease;
    }
    .conditional-field.hidden {
        display: none;
    }
</style>
"""


class BusinessImpactMonitoringForm(forms.ModelForm):
    observation = forms.CharField(label="Observasaun", required=False, widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '200px'}}))
    class Meta:
        model = BusinessImpactMonitoring
        fields = [
            'fund_received',
            'fund_used',
            'monthly_income',
            'monthly_expense',
            'use_accounting_book',
            'has_income',
            'paid_tax',
            'tax_amount',
            'plan_credit',
            'credit_source',
            'plan_new_business',
            'new_business_idea',
            'observation',
        ]
        widgets = {
            'fund_received': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'fund_used': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'monthly_income': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'monthly_expense': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'credit_source': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: BNCTL, Caixa Geral, Microfinance...'}),
            'new_business_idea': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Deskrisaun ideia negosiu foun...'}),
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Observasaun seluk...'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': '0.00'}),
            'use_accounting_book': forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-toggle': 'accounting-book'}),
            'has_income': forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-toggle': 'income-fields'}),
            'paid_tax': forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-toggle': 'tax-field'}),
            'plan_credit': forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-toggle': 'credit-field'}),
            'plan_new_business': forms.CheckboxInput(attrs={'class': 'form-check-input', 'data-toggle': 'newbusiness-field'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_tag = True
        self.helper.attrs = {'id': 'impact-monitoring-form'}
        
        self.helper.layout = Layout(
            HTML(_CSS),
            HTML(_ALERT),
            Row(
                Column('fund_received', css_class='col-md-4'),
                Column('fund_used', css_class='col-md-4'),
                HTML('<div class="col-md-4"><div class="form-control-plaintext"><strong>Saldo: </strong><span id="balance-display">0.00</span></div></div>'),
            ),
            Row(
                HTML('<div class="col-12"><hr><strong>Rendimentu no Despeza</strong></div>'),
            ),
            Row(
                Column('monthly_income', css_class='col-md-4 income-field'),
                Column('monthly_expense', css_class='col-md-4 expense-field'),
                HTML('<div class="col-md-4"><div class="form-control-plaintext"><strong>Lukru: </strong><span id="profit-display">0.00</span></div></div>'),
            ),
            Row(
                HTML('<div class="col-12"><hr><strong>Informasaun Adisionál</strong></div>'),
            ),
            Row(
                Column('use_accounting_book', css_class='col-md-3'),
                Column('has_income', css_class='col-md-3'),
                Column('paid_tax', css_class='col-md-3'),
                Column('tax_amount', css_class='col-md-3 conditional-field tax-field',),
            ),
            Row(
                Column('plan_credit', css_class='col-md-4'),
                Column('credit_source', css_class='col-md-8 conditional-field credit-field'),
            ),
            Row(
                Column('plan_new_business', css_class='col-md-4'),
                Column('new_business_idea', css_class='col-md-8 conditional-field newbusiness-field'),
            ),
            Row(
                Column('observation', css_class='col-md-12'),
            ),
            HTML(_BTN),
        )


class FundUsageForm(forms.ModelForm):
    class Meta:
        model = FundUsage
        fields = ['item_name', 'amount', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('item_name', css_class='col-md-6'),
                Column('amount', css_class='col-md-6'),
            ),
            Row(
                Column('description', css_class='col-md-12'),
            ),
            HTML(_BTN),
        )


class BusinessAssetForm(forms.ModelForm):
    class Meta:
        model = BusinessAsset
        fields = ['asset_name', 'quantity', 'value', 'condition']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('asset_name', css_class='col-md-6'),
                Column('quantity', css_class='col-md-2'),
                Column('value', css_class='col-md-2'),
                Column('condition', css_class='col-md-2'),
            ),
            HTML(_BTN),
        )


class CashFlowForm(forms.ModelForm):
    class Meta:
        model = CashFlow
        fields = ['quarter','transaction_date', 'transaction_type', 'description', 'amount']
        widgets = {
            'transaction_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('quarter', css_class='col-md-6'),
                Column('transaction_date', css_class='col-md-6'),
            ),
            Row(
                Column('transaction_type', css_class='col-md-4'),
                Column('amount', css_class='col-md-4'),
                Column('description', css_class='col-md-4'),
            ),
            HTML(_BTN),
        )


class FinancialBookForm(forms.ModelForm):
    class Meta:
        model = FinancialBook
        fields = ['title', 'file', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('title', css_class='col-md-6'),
                Column('file', css_class='col-md-6'),
            ),
            Row(
                Column('description', css_class='col-md-12'),
            ),
            HTML(_BTN),
        )