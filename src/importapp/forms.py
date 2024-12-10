from django import forms


class JSONImportForm(forms.Form):
    email = forms.EmailField()
    json_file = forms.FileField()
