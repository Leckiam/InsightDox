from django import forms

class InformeCostosUploadForm(forms.Form):
    archivo = forms.FileField(label="Archivo de informe de costos", allow_empty_file=False)