from django import forms
from django.forms import ModelForm
from .models import Tower


class TowerForm(ModelForm):
    class Meta:
        model = Tower
        fields = ('code', 'name')
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Introduza o codigo da Torre'}),
            'name': forms.TextInput(attrs={'placeholder': 'Introduza o nome da Torre'}),
        }

    def __init__(self, *args, **kwargs):
        super(TowerForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = "Codigo"
        self.fields['name'].label = "Nome"
