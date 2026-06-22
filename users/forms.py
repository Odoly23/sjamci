from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML
from django.contrib.auth.models import User, Group
from users.models import Emp, EmpPosition, EmpDivision, EmpUser


class EmpForm(forms.ModelForm):
    class Meta:
        model = Emp
        fields = ['name', 'sexo', 'phone','email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML("""
                <div class="alert alert-info" role="alert">
                    Fo hatene katak kampu ho simbolu Asterik <strong>(*)</strong> obrigatóriu tenki prienxe.!
                </div>
            """),
            Row(
                Column('name', css_class='form-group col-md-4 mb-2'),
                Column('sexo', css_class='form-group col-md-3 mb-2'),
                Column('phone', css_class='form-group col-md-2 mb-2'),
                Column('email', css_class='form-group col-md-3 mb-2'),
                css_class="form-row"
            ),
            HTML("""
                <div class="mt-4">
                    <button class="btn btn-sm btn-success" type="submit">
                        <i class="fa fa-save"></i> Save
                    </button>
                    <button class="btn btn-sm btn-secondary" type="button" onclick="history.back()">
                        <i class="fa fa-times"></i> Cancel
                    </button>
                </div>
            """)
        )

class EmpPositionForm(forms.ModelForm):
    class Meta:
        model = EmpPosition
        fields = ['position']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML("""
                <div class="alert alert-info" role="alert">
                    Fo hatene katak kampu ho simbolu Asterik <strong>(*)</strong> obrigatóriu tenki prienxe.!
                </div>
            """),
            Row(
                Column('position', css_class='form-group col-md-6 mb-2'),
            ),
            HTML("""
                <div class="mt-4">
                    <button class="btn btn-sm btn-success" type="submit">
                        <i class="fa fa-save"></i> Save
                    </button>
                    <button class="btn btn-sm btn-secondary" type="button" onclick="history.back()">
                        <i class="fa fa-times"></i> Cancel
                    </button>
                </div>
            """)
        )


class EmpDivisionForm(forms.ModelForm):
    class Meta:
        model = EmpDivision
        fields = ['gabinete','dn', 'department', ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            HTML("""
                <div class="alert alert-info" role="alert">
                    Fo hatene katak kampu ho simbolu Asterik <strong>(*)</strong> obrigatóriu tenki prienxe.!
                </div>
            """),
            Row(
                Column('gabinete', css_class='form-group col-md-4 mb-2'),
                Column('dn', css_class='form-group col-md-4 mb-2'),
                Column('department', css_class='form-group col-md-4 mb-2'),
            ),
            HTML("""
                <div class="mt-4">
                    <button class="btn btn-sm btn-success" type="submit">
                        <i class="fa fa-save"></i> Save
                    </button>
                    <button class="btn btn-sm btn-secondary" type="button" onclick="history.back()">
                        <i class="fa fa-times"></i> Cancel
                    </button>
                </div>
            """)
        )

class UserForm(forms.ModelForm):
    email = forms.EmailField()
    class Meta:
        model = User
        fields = ['username','email']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('username', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('email', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            HTML(""" <button class="btn btn-sm btn-primary" type="submit">Altera <i class="fa fa-save"></i></button> """)
        )

from django.contrib.auth.forms import PasswordChangeForm
class ChangePasswordForm(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'autocomplete': 'current-password', 'autofocus': True}))
    new_password1 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    new_password2 = forms.CharField(max_length=100, widget=forms.PasswordInput())
    class Meta:
        model = User
        fields = ['old_password','new_password1','new_password2']
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('old_password', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('new_password1', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('new_password2', css_class='form-group col-md-12 mb-0'),
                css_class='form-row'
            ),
            HTML(""" <button class="btn btn-sm btn-primary" type="submit">Alterar <i class="fa fa-save"></i></button> """)
        )