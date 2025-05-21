# rcm_app/forms.py
from django import forms
from django.core.validators import FileExtensionValidator

class ExcelUploadForm(forms.Form):
    file = forms.FileField(
        label='Select Excel File',
        validators=[FileExtensionValidator(allowed_extensions=['xlsx', 'xls'])],
        widget=forms.FileInput(attrs={
            'accept': '.xlsx, .xls',
            'class': 'file-input'
        })
    )
