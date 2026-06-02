from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Field
from monitoring.models import (
    BusinessImpactMonitoring,
    FundUsage,
    BusinessAsset,
    CashFlow,
    FinancialBook,
)

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

class BusinessImpactMonitoringForm(forms.ModelForm):
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
            'monitoring_date': forms.DateInput(attrs={'type': 'date'}),
            'credit_source': forms.TextInput(attrs={'placeholder': 'Ex: BNCTL, Caixa Geral, Microfinance...'}),
            'new_business_idea': forms.Textarea(attrs={'rows': 2}),
            'observation': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            HTML(_ALERT),
            Row(
                Column('fund_received', css_class='col-md-4'),
                Column('fund_used', css_class='col-md-4'),
                Column('fund_balance', css_class='col-md-4'),
            ),
            Row(
                Column('monthly_income', css_class='col-md-4'),
                Column('monthly_expense', css_class='col-md-4'),
                Column('monthly_profit', css_class='col-md-4'),
            ),
            Row(
                Column('use_accounting_book', css_class='col-md-3'),
                Column('has_income', css_class='col-md-3'),
                Column('paid_tax', css_class='col-md-3'),
                Column('tax_amount', css_class='col-md-3'),
            ),
            Row(
                Column('plan_credit', css_class='col-md-6'),
                Column('credit_source', css_class='col-md-6'),
            ),
            Row(
                Column('plan_new_business', css_class='col-md-6'),
                Column('new_business_idea', css_class='col-md-6'),
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
        fields = ['transaction_date', 'transaction_type', 'description', 'amount']
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
                Column('transaction_date', css_class='col-md-3'),
                Column('transaction_type', css_class='col-md-3'),
                Column('amount', css_class='col-md-3'),
                Column('description', css_class='col-md-3'),
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