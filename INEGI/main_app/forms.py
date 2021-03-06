from django import forms
from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm
from bootstrap_datepicker_plus import DatePickerInput
from dal import autocomplete

import django_filters
from django.forms.widgets import HiddenInput


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
        fields = ('username', 'password1', 'password2', 'full_name', 'is_client', 'is_manager', 'is_staff', 'group_type', 'affiliation')

        # widgets = {'birthdate': DatePickerInput(format='%d/%m/%Y'),}

        widgets = {
            'group_type': autocomplete.ModelSelect2(url='group-autocomplete', attrs={'style': 'width:100%'}),
            'affiliation': autocomplete.ModelSelect2(url='affiliation-autocomplete', attrs={'style': 'width:100%'})
        }

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
        # self.fields['group_type'].widget.attrs.update({'class': 'form-control mandatory'})
        #self.fields['is_client'].widget.attrs.update({'class': 'form-check-input'})
        #self.fields['is_manager'].widget.attrs.update({'class': 'form-check-input'})


class UserForm(ModelForm):
    class Meta:
        model = MyUser
        fields = ('username', 'full_name', 'is_client', 'is_manager', 'is_staff', 'group_type', 'affiliation')

        # widgets = {'birthdate': DatePickerInput(format='%d/%m/%Y'),}

        widgets = {
            'group_type': autocomplete.ModelSelect2(url='group-autocomplete', attrs={'style': 'width:100%'}),
            'affiliation': autocomplete.ModelSelect2(url='affiliation-autocomplete', attrs={'style': 'width:100%'})
        }

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
        # self.fields['group_type'].widget.attrs.update({'class': 'form-control mandatory'})
        # self.fields['birthdate'].disabled = True


class UserTowersFrom(ModelForm):
    tower = forms.ModelMultipleChoiceField(
        queryset=Tower.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2Multiple(url='tower-autocomplete', attrs={'style': 'width:100%'})
    )

    user = forms.ModelChoiceField(
        queryset=MyUser.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='user-autocomplete', attrs={'style': 'width:100%'})
    )

    begin_date = forms.DateTimeField(input_formats=["%m/%Y"], widget=DatePickerInput(format="%m/%Y", attrs={'autocomplete': 'off'}))
    end_date = forms.DateTimeField(input_formats=["%m/%Y"], widget=DatePickerInput(format="%m/%Y", attrs={'autocomplete': 'off'}))

    class Meta:
        model = UserTowerDates
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(UserTowersFrom, self).__init__(*args, **kwargs)
        self.fields['tower'].label = "Towers"
        self.fields['user'].label = "User"
        self.fields['begin_date'].label = "Begin Date"
        self.fields['end_date'].label = "End Date"


class TowerForm(ModelForm):
    installation_date = forms.DateTimeField(required=False, input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off', 'placeholder': 'Installation Date'}))

    class Meta:
        model = Tower
        fields = '__all__'
        widgets = {
            'code_inegi': forms.TextInput(attrs={'placeholder': 'Please enter the INEGI code', 'style': 'width:100%'}),
            'code_aux_1': forms.TextInput(attrs={'placeholder': 'Auxiliar code 1', 'style': 'width:100%'}),
            'code_aux_2': forms.TextInput(attrs={'placeholder': 'Auxiliar code 2', 'style': 'width:100%'}),
            'code_client': forms.TextInput(attrs={'placeholder': 'Client code', 'style': 'width:100%'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Designation', 'style': 'width:100%'}),
            'utm_zone': forms.TextInput(attrs={'placeholder': 'UTM Zone', 'style': 'width:100%'}),
            'project': forms.TextInput(attrs={'placeholder': 'Project designation', 'style': 'width:100%'}),
            'client': autocomplete.ModelSelect2(url='affiliation-autocomplete', attrs={'style': 'width:100%'}),
            'parish': forms.TextInput(attrs={'placeholder': 'Parish', 'style': 'width:100%'}),
            'district': forms.TextInput(attrs={'placeholder': 'District', 'style': 'width:100%'}),
            'gsm_number': forms.TextInput(attrs={'placeholder': 'GSM Number', 'style': 'width:100%'}),
        }

    def __init__(self, *args, **kwargs):
        super(TowerForm, self).__init__(*args, **kwargs)
        self.fields['code_inegi'].label = "INEGI Code"

        self.fields['code_inegi'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['code_aux_1'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['code_aux_2'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['code_client'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['designation'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['position_x'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['position_y'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['coords_system'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['utm_zone'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['project'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['parish'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['district'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['country'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['gsm_number'].widget.attrs.update({'class': 'form-control mandatory'})


class MachineForm(ModelForm):
    installation_date = forms.DateTimeField(required=False, input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off',  'placeholder': 'Installation Date'}))

    class Meta:
        model = Machine
        fields = '__all__'
        widgets = {
            'code_inegi': forms.TextInput(attrs={'placeholder': 'Please enter the INEGI code', 'style': 'width:100%'}),
            'code_aux_1': forms.TextInput(attrs={'placeholder': 'Auxiliar code 1', 'style': 'width:100%'}),
            'code_aux_2': forms.TextInput(attrs={'placeholder': 'Auxiliar code 2', 'style': 'width:100%'}),
            'code_client': forms.TextInput(attrs={'placeholder': 'Client code', 'style': 'width:100%'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Designation', 'style': 'width:100%'}),
            'utm_zone': forms.TextInput(attrs={'placeholder': 'UTM Zone', 'style': 'width:100%'}),
            'project': forms.TextInput(attrs={'placeholder': 'Project designation', 'style': 'width:100%'}),
            'client': autocomplete.ModelSelect2(url='affiliation-autocomplete', attrs={'style': 'width:100%'}),
            'parish': forms.TextInput(attrs={'placeholder': 'Parish', 'style': 'width:100%'}),
            'district': forms.TextInput(attrs={'placeholder': 'District', 'style': 'width:100%'}),
            'gsm_number': forms.TextInput(attrs={'placeholder': 'GSM Number', 'style': 'width:100%'}),
        }

    def __init__(self, *args, **kwargs):
        super(MachineForm, self).__init__(*args, **kwargs)
        self.fields['code_inegi'].label = "INEGI Code"


class ClusterForm(ModelForm):
    class Meta:
        model = Cluster
        fields = ('name', 'towers')
        # towers = forms.ModelMultipleChoiceField(widget=forms.CheckboxSelectMultiple(), queryset=Tower.objects.all())
        widgets = {
            'towers': autocomplete.ModelSelect2Multiple(url='tower-autocomplete', attrs={'style': 'width:100%'})
        }

    def __init__(self, *args, **kwargs):
        super(ClusterForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory'})
        # self.fields["towers"].widget = forms.CheckboxSelectMultiple()
        # self.fields["towers"].queryset = Tower.objects.all()
        # self.fields['towers'].widget.attrs['size'] = 20


class EquipmentForm(ModelForm):
    type = forms.ModelChoiceField(
        queryset=EquipmentType.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url='equipment-type-autocomplete', attrs={'style': 'width:100%'})
    )

    class Meta:
        model = Equipment
        fields = ('__all__')

        widgets = {
            'model': autocomplete.ModelSelect2(url='model-autocomplete', forward=['type'], attrs={'style': 'width:100%'})
        }

    def __init__(self, *args, **kwargs):
        super(EquipmentForm, self).__init__(*args, **kwargs)
        self.fields['sn'].label = "Serial Number"
        self.fields['type'].label = "Equipment Type"
        self.fields['model'].label = "Model"

        self.fields['sn'].widget.attrs.update({'class': 'form-control mandatory'})
    field_order = ['sn', 'type', 'model']


class EquipmentCharacteristicForm(ModelForm):
    type = forms.ModelChoiceField(
        queryset=EquipmentType.objects.all(),
        widget=autocomplete.ModelSelect2(url='equipment-type-autocomplete', attrs={'style': 'width:100%'})
    )

    class Meta:
        model = EquipmentCharacteristic
        fields = ('__all__')

    def __init__(self, *args, **kwargs):
        super(EquipmentCharacteristicForm, self).__init__(*args, **kwargs)
        self.fields['manufacturer'].label = "Manufacturer"
        self.fields['model'].label = "Model"
        self.fields['version'].label = "Version"
        self.fields['designation'].label = "Designation"
        self.fields['slope_stn'].label = "Standard Slope"
        self.fields['offset_stn'].label = "Standard Offset"
        self.fields['output'].label = "Output"
        self.fields['gama'].label = "Gama"
        self.fields['error'].label = "Error"
        self.fields['sep_field'].label = "Separator Field - Dataset"
        self.fields['sep_dec'].label = "Separator Decimal - Dataset"
        self.fields['sep_thousand'].label = "Separator Thousand - Dataset"

        self.fields['manufacturer'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['model'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['version'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['designation'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['slope_stn'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['offset_stn'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['output'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['gama'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['error'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['sep_field'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['sep_dec'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['sep_thousand'].widget.attrs.update({'class': 'form-control mandatory'})


class CalibrationForm(ModelForm):
    dimension_type = forms.ModelChoiceField(
        queryset=DimensionType.objects.all().order_by('-id'),
        widget=autocomplete.ModelSelect2(url='dimension-type-autocomplete', attrs={'style': 'width:100%'})
    )

    calib_date = forms.DateTimeField(required=False, input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))

    class Meta:
        model = Calibration
        fields = ('__all__')
        exclude = ('equipment',)

    def __init__(self, *args, **kwargs):
        super(CalibrationForm, self).__init__(*args, **kwargs)
        self.fields['calib_date'].label = "Date of calibration"
        self.fields['ref'].label = "Reference"
        self.fields['slope'].label = "Calibration Slope"
        self.fields['offset'].label = "Calibration Offset"

        self.fields['offset'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['slope'].widget.attrs.update({'class': 'form-control mandatory'})
        self.fields['ref'].widget.attrs.update({'class': 'form-control mandatory'})


class EquipmentTypeForm(ModelForm):
    class Meta:
        model = EquipmentType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(EquipmentTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Equipment Type Name"
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory', 'placeholder': 'Ex. Anemometer'})
        self.fields['initials'].label = "Equipment Type Initials"
        self.fields['initials'].widget.attrs.update({'class': 'form-control mandatory', 'placeholder': 'Ex. AN'})


class UserGroupTypeForm(ModelForm):
    class Meta:
        model = UserGroupType
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(UserGroupTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "User Group Type Name"
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory', 'placeholder': 'Ex. Field Team'})


class UnitTypeForm(ModelForm):
    class Meta:
        model = UnitType
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(UnitTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Unit Type Name"
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory', 'placeholder': 'Ex. m/s'})


class StatisticTypeForm(ModelForm):
    class Meta:
        model = StatisticType
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(StatisticTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Statistic Type Name"
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory', 'placeholder': 'Ex. Average'})


class MetricTypeForm(ModelForm):
    class Meta:
        model = MetricType
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(MetricTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Metric Type Name"
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory', 'placeholder': 'Ex. Speed'})


class ComponentTypeForm(ModelForm):
    class Meta:
        model = ComponentType
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(ComponentTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Component Type Name"
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory', 'placeholder': 'Ex. Vertical'})


class AffiliationTypeForm(ModelForm):
    class Meta:
        model = AffiliationType
        fields = ('name',)

    def __init__(self, *args, **kwargs):
        super(AffiliationTypeForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Affiliation Type Name"
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory', 'placeholder': 'Ex. EDP'})


class PeriodConfigForm(ModelForm):
    begin_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))
    end_date = forms.DateTimeField(required=False, input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))

    class Meta:
        model = PeriodConfiguration
        fields = ('begin_date', 'end_date', 'active', 'wind_rss', 'solar_rss', 'raw_freq', 'time_zone')

        # widgets = {'begin_date': DatePickerInput(format='%Y/%m/%d %H:%M'),
        #            'end_date': DatePickerInput(format='%Y/%m/%d %H:%M'), }

    def __init__(self, *args, **kwargs):
        super(PeriodConfigForm, self).__init__(*args, **kwargs)
        self.fields['begin_date'].label = "Start Date"
        self.fields['end_date'].label = "End Date"
        self.fields['active'].label = "Is this a Tower active?"
        self.fields['wind_rss'].label = "Is this a Wind RSS Tower Period?"
        self.fields['solar_rss'].label = "Is this a Solar RSS Tower Period?"
        self.fields['raw_freq'].label = "Raw Frequency"
        self.fields['time_zone'].label = "Time Zone"

        self.fields['raw_freq'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%'})
        self.fields['time_zone'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%'})


class EquipmentConfigForm(ModelForm):
    calibration = forms.ModelChoiceField(
        queryset=Calibration.objects.all().order_by('-id'),
        widget=autocomplete.ModelSelect2(url='calibration-autocomplete', attrs={'style': 'width:100%'})
    )

    class Meta:
        model = EquipmentConfig
        fields = '__all__'
        exclude = ('conf_period',)

    def __init__(self, *args, **kwargs):
        super(EquipmentConfigForm, self).__init__(*args, **kwargs)
        self.fields['calibration'].label = "Equipment/Calibration"
        self.fields['boom_var_height'].label = "Boom vertical height"
        self.fields['slope_dl'].label = "Data Logger Slope"
        self.fields['offset_dl'].label = "Data Logger Offset"
        self.fields['slope_dl'].required = True
        self.fields['offset_dl'].required = True

        self.fields['height'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%', 'autocomplete': 'off'})
        self.fields['height_label'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%', 'autocomplete': 'off'})
        self.fields['orientation'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%'})
        self.fields['boom_length'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%'})
        self.fields['slope_dl'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%'})
        self.fields['offset_dl'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%'})
        self.fields['boom_var_height'].widget.attrs.update({'class': 'form-control mandatory', 'style': 'width:25%'})


class StatusForm(ModelForm):
    class Meta:
        model = Status
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(StatusForm, self).__init__(*args, **kwargs)
        self.fields['code'].widget.attrs.update({'class': 'form-control mandatory', 'autocomplete': 'off'})
        self.fields['name'].widget.attrs.update({'class': 'form-control mandatory', 'autocomplete': 'off'})


class ClassificationPeriodForm(ModelForm):
    begin_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))
    end_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))

    status = forms.ModelChoiceField(
        queryset=Status.objects.all().order_by('-id'),
        widget=autocomplete.ModelSelect2(url='status-autocomplete', attrs={'style': 'width:100%'})
    )

    class Meta:
        model = ClassificationPeriod
        fields = '__all__'
        exclude = ('user', 'equipment_configuration', )

    def __init__(self, *args, **kwargs):
        super(ClassificationPeriodForm, self).__init__(*args, **kwargs)


class DimensionTypeForm(ModelForm):
    unit = forms.ModelChoiceField(
        queryset=UnitType.objects.all().order_by('-id'),
        widget=autocomplete.ModelSelect2(url='unit-autocomplete', attrs={'style': 'width:100%'})
    )

    statistic = forms.ModelChoiceField(
        queryset=StatisticType.objects.all().order_by('-id'),
        widget=autocomplete.ModelSelect2(url='statistic-autocomplete', attrs={'style': 'width:100%'})
    )

    metric = forms.ModelChoiceField(
        queryset=MetricType.objects.all().order_by('-id'),
        widget=autocomplete.ModelSelect2(url='metric-autocomplete', attrs={'style': 'width:100%'})
    )

    component = forms.ModelChoiceField(
        queryset=ComponentType.objects.all().order_by('-id'),
        widget=autocomplete.ModelSelect2(url='component-autocomplete', attrs={'style': 'width:100%'})
    )

    class Meta:
        model = DimensionType
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(DimensionTypeForm, self).__init__(*args, **kwargs)


class DimensionForm(ModelForm):
    dimension_type = forms.ModelChoiceField(
        queryset=DimensionType.objects.all().order_by('-id'),
        widget=autocomplete.ModelSelect2(url='dimension-type-autocomplete', attrs={'style': 'width:100%'})
    )

    class Meta:
        model = Dimension
        fields = '__all__'
        exclude = ('equipment_configuration', )

    def __init__(self, *args, **kwargs):
        super(DimensionForm, self).__init__(*args, **kwargs)
        self.fields['column'].widget.attrs.update({'class': 'form-control mandatory', 'autocomplete': 'off'})


class CommentClassificationForm(ModelForm):
    begin_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))
    end_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))

    class Meta:
        model = CommentClassification
        fields = '__all__'
        exclude = ('comment_date', 'user', 'classification',)

    def __init__(self, *args, **kwargs):
        super(CommentClassificationForm, self).__init__(*args, **kwargs)
        self.fields['internal_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 4})
        self.fields['compact_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 4})
        self.fields['detailed_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 4})

    field_order = ['begin_date', 'end_date', 'internal_comment', 'compact_comment', 'detailed_comment']


class CommentTowerForm(ModelForm):
    begin_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))
    end_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))

    class Meta:
        model = CommentTower
        fields = '__all__'
        exclude = ('comment_date', 'user', 'tower',)

    def __init__(self, *args, **kwargs):
        super(CommentTowerForm, self).__init__(*args, **kwargs)
        self.fields['internal_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 4})
        self.fields['compact_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 4})
        self.fields['detailed_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 4})

    field_order = ['begin_date', 'end_date', 'internal_comment', 'compact_comment', 'detailed_comment']


class DateTowerFilter(django_filters.FilterSet):
    begin_date = django_filters.DateFilter(input_formats=["%Y-%m-%d %H:%M"], widget=DatePickerInput(format="%Y-%m-%d %H:%M"))
    end_date = django_filters.DateFilter(input_formats=["%Y-%m-%d %H:%M"], widget=DatePickerInput(format="%Y-%m-%d %H:%M"))

    # tower = django_filters.ModelChoiceFilter(required=False, queryset=None, widget=HiddenInput())
    # classifications = django_filters.ModelChoiceFilter(required=False, queryset=None, widget=HiddenInput())
    #
    # comment_tower = django_filters.ModelMultipleChoiceFilter(
    #     required=False,
    #     queryset=CommentTower.objects.all().order_by('-id'),
    #     widget=autocomplete.ModelSelect2Multiple(url='comment-tower-autocomplete', forward=['begin_date', 'end_date', 'tower'], attrs={'style': 'width:100%'})
    # )
    #
    # comment_classification = django_filters.ModelMultipleChoiceFilter(
    #     required=False,
    #     queryset=CommentClassification.objects.all().order_by('-id'),
    #     widget=autocomplete.ModelSelect2Multiple(url='comment-classification-autocomplete', forward=['begin_date', 'end_date', 'tower', 'classifications'],
    #                                      attrs={'style': 'width:100%'})
    # )

    class Meta:
        model = CommentTower
        fields = ['begin_date', 'end_date', ]

    # def __init__(self, *args, **kwargs):
    #     super(DateTowerFilter, self).__init__(*args, **kwargs)
    #     self.filters['comment_tower'].label = "Comments Tower Selection"
    #     self.filters['comment_classification'].label = "Comments Classification Selection"


class DateRangeChooseForm(forms.Form):
    begin_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))
    end_date = forms.DateTimeField(input_formats=["%d/%m/%Y %H:%M"], widget=DatePickerInput(format="%d/%m/%Y %H:%M", attrs={'autocomplete': 'off'}))


class TowersDataVForm(forms.Form):
    tower = forms.ModelChoiceField(
        queryset=Tower.objects.all(),
        required=False,
        widget=autocomplete.ModelSelect2(url='tower-autocomplete', attrs={'style': 'width:100%'})
    )

    begin_date_search = forms.DateTimeField(input_formats=["%Y-%m-%d %H:%M"], widget=DatePickerInput(format="%Y-%m-%d %H:%M", attrs={'autocomplete': 'off'}))
    end_date_search = forms.DateTimeField(input_formats=["%Y-%m-%d %H:%M"], widget=DatePickerInput(format="%Y-%m-%d %H:%M", attrs={'autocomplete': 'off'}))

    begin_date = forms.DateTimeField(input_formats=["%Y-%m-%d %H:%M:%S"], widget=DatePickerInput(format="%Y-%m-%d %H:%M:%S", attrs={'autocomplete': 'off'}))
    end_date = forms.DateTimeField(input_formats=["%Y-%m-%d %H:%M:%S"], widget=DatePickerInput(format="%Y-%m-%d %H:%M:%S", attrs={'autocomplete': 'off'}))

    equipments = forms.ModelMultipleChoiceField(
        queryset=PeriodConfiguration.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2Multiple(url='tower-conf_periods-autocomplete', forward=['tower', 'begin_date', 'end_date'], attrs={'style': 'width:100%'})
    )

    status = forms.ModelChoiceField(
        queryset=Status.objects.all(),
        required=True,
        widget=autocomplete.ModelSelect2(url='status-autocomplete', attrs={'style': 'width:100%'})
    )


class CommentClassificationChartForm(ModelForm):
    class Meta:
        model = CommentClassification
        fields = ('internal_comment', 'compact_comment', 'detailed_comment',)

    def __init__(self, *args, **kwargs):
        super(CommentClassificationChartForm, self).__init__(*args, **kwargs)
        self.fields['internal_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 2})
        self.fields['compact_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 2})
        self.fields['detailed_comment'].widget.attrs.update({'class': 'form-control mandatory', 'rows': 2})
