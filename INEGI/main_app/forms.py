from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from bootstrap_datepicker_plus import DatePickerInput


class LoginForm(forms.Form):
    username = forms.CharField(label='User Name', max_length=64)
    password = forms.CharField(widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['username'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['password'].widget.attrs.update({'class': 'form-control mandatory'})


class RegisterForm(UserCreationForm):
    class Meta:
        model = MyUser
        fields = ('username', 'password1', 'password2', 'full_name', 'is_client', 'is_manager', 'is_staff', 'group_type')

        # widgets = {'birthdate': DatePickerInput(format='%d/%m/%Y'),}

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and MyUser.objects.filter(username=username).exists():
            raise forms.ValidationError(u'Username already in use!')
        return username

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['password1'].label = "Password"
        self.fields['password2'].label = "Confirm password"
        self.fields['full_name'].label = "Full name"
        # self.fields['birthdate'].label = "Date of birth"

        self.fields['is_client'].label = "Is this a Client?"
        self.fields['is_manager'].label = "Is this a Manager?"
        self.fields['is_staff'].label = "Is this a Administrator?"

        self.fields['group_type'].label = "Type of Group"

        self.fields['username'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['group_type'].widget.attrs.update({'class': 'form-control mandatory'})
        #self.fields['is_client'].widget.attrs.update({'class': 'form-check-input'})
        #self.fields['is_manager'].widget.attrs.update({'class': 'form-check-input'})


class UserForm(ModelForm):
    class Meta:
        model = MyUser
        fields = ('username', 'full_name', 'is_client', 'is_manager', 'is_staff', 'group_type')

        # widgets = {'birthdate': DatePickerInput(format='%d/%m/%Y'),}

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['username'].label = "Username"
        self.fields['full_name'].label = "Full name"
        # self.fields['birthdate'].label = "Date of birth"

        self.fields['is_client'].label = "Is this a Client?"
        self.fields['is_manager'].label = "Is this a Manager?"
        self.fields['is_staff'].label = "Is this a Administrator?"

        self.fields['group_type'].label = "Type of Group"

        self.fields['username'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['group_type'].widget.attrs.update({'class': 'form-control mandatory'})
        # self.fields['birthdate'].disabled = True


class UserTowersFrom(ModelForm):
    class Meta:
        model = MyUser
        fields = ['towers']
        # towers = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=Tower.objects.all())

    def __init__(self, *args, **kwargs):
        super(UserTowersFrom, self).__init__(*args, **kwargs)
        self.fields["towers"].widget = forms.CheckboxSelectMultiple()
        self.fields["towers"].queryset = Tower.objects.all()
        # self.fields['towers'].widget.attrs['size'] = 20


class TowerForm(ModelForm):
    class Meta:
        model = Tower
        fields = ('code', 'name')
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Please enter the Tower code', 'style': 'width:100%'}),
            'name': forms.TextInput(attrs={'placeholder': 'Please enter the Tower name', 'style': 'width:100%'}),
        }

    def __init__(self, *args, **kwargs):
        super(TowerForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = "Code"
        self.fields['name'].label = "Name"


class MachineForm(ModelForm):
    class Meta:
        model = Machine
        fields = ('code', 'name')
        widgets = {
            'code': forms.TextInput(attrs={'placeholder': 'Please enter the Machine code', 'style': 'width:100%'}),
            'name': forms.TextInput(attrs={'placeholder': 'Please enter the Machine name', 'style': 'width:100%'}),
        }

    def __init__(self, *args, **kwargs):
        super(MachineForm, self).__init__(*args, **kwargs)
        self.fields['code'].label = "Code"
        self.fields['name'].label = "Name"


class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
        fields = ('name', 'towers')
        # towers = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=Tower.objects.all())

    def __init__(self, *args, **kwargs):
        super(ClusterForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory'})

        self.fields["towers"].widget = forms.CheckboxSelectMultiple()
        self.fields["towers"].queryset = Tower.objects.all()
        # self.fields['towers'].widget.attrs['size'] = 20


class EquipmentForm(ModelForm):
    class Meta:
        model = Equipment
        fields = ('sn', 'manufacturer', 'model', 'version', 'designation', 'status', 'type')

    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)
        self.fields['sn'].label = "Serial Number"
        self.fields['manufacturer'].label = "Manufacturer"
        self.fields['model'].label = "Model"
        self.fields['version'].label = "Version"
        self.fields['designation'].label = "Designation"
        self.fields['status'].label = "Active?"
        self.fields['type'].label = "Equipment Type"

        self.fields['sn'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['manufacturer'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['model'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['version'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['designation'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['type'].widget.attrs.update({'class': 'form-control mandatory'})


class TypeForm(ModelForm):
    class Meta:
        model = EquipmentType
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(TypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Equipment Type Name"

        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory'})
