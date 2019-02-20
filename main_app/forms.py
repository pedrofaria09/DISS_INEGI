from django import forms
from django.forms import ModelForm
from .models import Tower, MyUser
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'password1', 'password2', 'full_name', 'is_client', 'is_manager')

    # def clean_username(self):
    #     username = self.cleaned_data.get('username')
    #     if username and MyUser.objects.filter(username=username).exists():
    #         raise forms.ValidationError(u'Username already in use!')
    #     return username

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm password"
        self.fields['full_name'].label = "Full name"
        self.fields['is_client'].label = "Is this a client?"
        self.fields['is_manager'].label = "Is this a manager?"

        self.fields['username'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control mandatory'})
        #self.fields['is_client'].widget.attrs.update({'class': 'form-check-input'})
        #self.fields['is_manager'].widget.attrs.update({'class': 'form-check-input'})



class TowerForm(ModelForm):
    class Meta:
        model = Tower
        fields = ('code', 'name')
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Introduza o codigo da Torre', 'style': 'width:100%'}),
            'name': forms.TextInput(attrs={'placeholder': 'Introduza o nome da Torre', 'style': 'width:100%'}),
        }

    def __init__(self, *args, **kwargs):
        super(TowerForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = "Codigo"
        self.fields['name'].label = "Nome"


class TowerViewForm(ModelForm):
    class Meta:
        model = Tower
        fields = ('code', 'name')
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Introduza o codigo da Torre', 'style': 'width:100%'}),
            'name': forms.TextInput(attrs={'placeholder': 'Introduza o nome da Torre', 'style': 'width:100%'}),
        }

    def __init__(self, *args, **kwargs):
        super(TowerViewForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = "Codigo"
        self.fields['name'].label = "Nome"
        self.fields['code'].disabled = True