from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, HTML, Field
from benefisiariu.models import Benefisiariu, AddressTL, Photo, AddressOrigin, BeneficiariuEvaluation
from custom.models import Municipality, AdministrativePost, Village
from django_summernote.widgets import SummernoteWidget

class DateInput(forms.DateInput):
    input_type = 'date'

class BeneficiariuEvaluationForm(forms.ModelForm):
    description = forms.CharField(label="Deskrisaun/Razaun", required=False, widget=SummernoteWidget(attrs={'summernote': {'width': '100%', 'height': '200px'}}))
    class Meta:
        model = BeneficiariuEvaluation
        fields = ['status', 'description']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_method = 'post'

        self.helper.layout = Layout(
            Row(
                Column('status', css_class='col-md-6'),
            ),

            Row(
                Column('description', css_class='col-md-12'),
            ),

            HTML("""
                <div class="mt-4 d-flex" style="gap: 0.5rem;">
                    <button class="btn btn-sm btn-success" type="submit">
                        <i class="fa fa-save"></i> Save
                    </button>
                    <button class="btn btn-sm btn-secondary" type="button" onclick="history.back()">
                        <i class="fa fa-times"></i> Cancel
                    </button>
                </div>
            """)
        )

class UploadExcelForm(forms.Form):
    file = forms.FileField(label="Upload File Excel")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data'
        self.helper.layout = Layout(
            Field('file'),
            HTML("""
                <div class="mt-4 d-flex" style="gap: 0.5rem;">
                    <button class="btn btn-sm btn-success" type="submit">
                        <i class="fa fa-save"></i> Save
                    </button>
                    <button class="btn btn-sm btn-secondary" type="button" onclick="history.back()">
                        <i class="fa fa-times"></i> Cancel
                    </button>
                </div>
            """)
        )

class BenefisiariuForm(forms.ModelForm):
    dob = forms.DateField(label='Data Moris', required=False, widget=DateInput())

    class Meta:
        model = Benefisiariu
        fields = ['name', 'pob', 'dob', 'sex', 'nivel_edukasaun',
                  'marital', 'status', 'phone', 'email_website', 'file']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_enctype = 'multipart/form-data' # fix: form_enctype
        self.helper.layout = Layout(
            HTML("""
                <div class="alert alert-info">
                    Fo hatene katak kampu ho simbolu Asterik <strong>(*)</strong> obrigatóriu tenki prienxe!
                </div>
            """),
            Row(
                Column('name', css_class='col-md-6'),
                Column('pob', css_class='col-md-6'),
            ),
            Row(
                Column('sex', css_class='col-md-3'),
                Column('marital', css_class='col-md-3'),
                Column('dob', css_class='col-md-3'),
                Column('nivel_edukasaun', css_class='col-md-3'),
            ),
            Row(
                Column('phone', css_class='col-md-4'),
                Column('file', css_class='col-md-4'),
                Column('email_website', css_class='col-md-4'),
            ),
            HTML("""
                <div class="mt-4 d-flex" style="gap: 0.5rem;">
                    <button class="btn btn-sm btn-success" type="submit">
                        <i class="fa fa-save"></i> Save
                    </button>
                    <button class="btn btn-sm btn-secondary" type="button" onclick="history.back()">
                        <i class="fa fa-times"></i> Cancel
                    </button>
                </div>
            """)
        )

class AddressTLForm(forms.ModelForm):
    class Meta:
        model = AddressTL
        fields = ['address', 'municipality', 'administrativepost', 'village']
        widgets = {'area_polygon': forms.HiddenInput()}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['administrativepost'].queryset = AdministrativePost.objects.none()
        self.fields['village'].queryset = Village.objects.none()

        # Logic queryset tetap sama
        if 'municipality' in self.data:
            try:
                municipality_id = int(self.data.get('municipality'))
                self.fields['administrativepost'].queryset = AdministrativePost.objects.filter(
                    municipality_id=municipality_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.municipality:
            self.fields['administrativepost'].queryset = self.instance.municipality.administrativepost_set.order_by('name')

        if 'administrativepost' in self.data:
            try:
                administrativepost_id = int(self.data.get('administrativepost'))
                self.fields['village'].queryset = Village.objects.filter(
                    administrativepost_id=administrativepost_id
                ).order_by('name')
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.administrativepost:
            self.fields['village'].queryset = self.instance.administrativepost.village_set.order_by('name')
        
        self.helper = FormHelper()
        self.helper.form_tag = False  

class AddressOriginForm(forms.ModelForm):
    class Meta:
        model = AddressOrigin
        fields = ['city', 'address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('city', css_class='col-md-6'),
                Column('address', css_class='col-md-6'),
            ),
            HTML("""
                <div class="mt-3 d-flex" style="gap: 0.5rem;">
                    <button class="btn btn-primary btn-sm" type="submit">
                        <i class="fa fa-save"></i> Rai
                    </button>
                    <a class="btn btn-secondary btn-sm" href="{% url 'benef-detail-kni' hashid=hashid %}">
                        <i class="fa fa-close"></i> Cancela
                    </a>
                </div>
            """)
        )

class PhotoUploadForm(forms.ModelForm):
    image = forms.FileField(label="Upload Photo", required=False)

    class Meta:
        model = Photo
        fields = ['image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_tag = False