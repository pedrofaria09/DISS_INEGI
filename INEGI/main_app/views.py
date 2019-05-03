from django.shortcuts import render, get_object_or_404, redirect, render_to_response
from django.http import HttpResponseRedirect, Http404, HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from mongoengine.queryset.visitor import Q as QM
from django.db.models import Q as QD
from .models import *
from .forms import *
from datetime import *
from django.db import IntegrityError
from .aux_functions import parsedate, check_if_period_is_valid, check_if_period_is_valid_2, get_date
from formtools.wizard.views import SessionWizardView
from dal import autocomplete

from django_pandas.io import *
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart
from graphos.renderers.morris import LineChart as LineChartMorris
from graphos.renderers.highcharts import LineChart as LineChartHIGH

from graphos.sources.model import ModelDataSource
from graphos.sources.csv_file import CSVDataSource

from django.utils.html import format_html

import time, re, io, json, pytz, random

# Create your views here.


def get_obj_or_404_2(klass, *args, **kwargs):
    try:
        return klass.objects.get(*args, **kwargs)
    except klass.DoesNotExist:
        raise Http404


def dt2epoch(value):
    epoch = int(time.mktime(value.timetuple()) * 1000)
    return epoch


def chart_nvd3(request):
    qs = DataSetPG.objects.all().order_by('id')
    df = read_frame(qs)
    print(df.head())

    xdata = df['time_stamp'].apply(dt2epoch).tolist()
    new_df = df.value.apply(lambda x: pd.Series(str(x).split(",")))
    del df['value']
    df = pd.concat([df, new_df], axis=1, sort=False)
    del df['id']
    del df['tower_code']

    # Convert all other columns rather than time_stamp to float
    for d in df:
        if df[d].name is not 'time_stamp':
            df[d] = df[d].astype(float).tolist()

    # Replace all NaN with None
    df = df.where((pd.notnull(df)), None)

    ydata = []
    for d in df:
        if df[d].name is not 'time_stamp':
            ydata.append(df[d])

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie = {"tooltip": {"y_start": "value: ", "y_end": " "},
                   "date_format": tooltip_date}
    chartdata = {'x': xdata}
    for idx, item in enumerate(ydata):
        chartdata = {**chartdata, **{'name': item.name, 'y'+str(idx): item, 'extra'+str(idx): extra_serie}}

    # chartdata = {
    #     'x': xdata,
    #     'name': 'series 1', 'y1': ydata[0], 'extra1': extra_serie,
    # }

    # charttype = "lineChart"
    # chartcontainer = 'lineChart_container'
    charttype = "lineWithFocusChart"
    chartcontainer = 'linewithfocuschart_container'
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'chartcontainer': chartcontainer,
        'extra': {
            'x_is_date': True,
            'x_axis_format': '%d %b %Y %H',
            'tag_script_js': True,
            'jquery_on_ready': False,
            'focus_enable': True,
        }
    }
    return render(request, 'chart_nvd3.html', data)


def chart_graphos(request):
    qs = DataSetPG.objects.all().order_by('id')
    df = read_frame(qs)

    new_df = df.value.apply(lambda x: pd.Series(str(x).split(",")))
    del df['value']
    df = pd.concat([df, new_df], axis=1, sort=False)

    # df = read_frame(qs)
    #
    # all_list = df.value.str.split(',').to_list()
    # del df['value']
    # new_df = pd.DataFrame(all_list)
    # df = pd.concat([df, new_df], axis=1, sort=False)
    del df['id']
    del df['tower_code']

    # print(df)
    # df.fillna(0, inplace=True)
    # print(df)

    # for x in df:
    #     if df[x].name is not 'time_stamp':
    #         df[x].astype(float)

    # df.to_csv(path_or_buf='test.csv', float_format='%.2f', index=False, encoding='utf-8')
    df.to_csv(path_or_buf='test.csv', index=False)

    data = [
        ['Year', 'Sales', 'Expenses'],
        ["2004", 1000, 400],
        ["2005", 1170, 460],
        ["2006", 660, 1120],
        ["2007", 1030, 540]
    ]

    # data_source = SimpleDataSource(data=data)
    csv_file = open('test.csv')
    # data_source = CSVDataSource(csv_file)
    data_source = MyCSVDataSource(csv_file)

    # data_source = ModelDataSource(qs, fields=['time_stamp', 'value'])
    # data_source = MyModelDataSource(qs, fields=['time_stamp', 'value'])

    # print(pd.DataFrame.to_csv(self=df , sep=';', float_format='%.2f', index=True, decimal=","))
    chart = LineChart(data_source)
    chart1 = LineChartMorris(data_source, options={'xLabels': 'day', 'continuousLine': 'false'})
    chart2 = LineChartHIGH(data_source, width=1200, height=600, options={'title': 'Data Visualization', 'chart': {'zoomType': 'xy'}, 'series': {'events': {'click': "function(event) {alert(this.yAxis.toValue(event.x, false));}"}}})

    context = {'chart': chart, 'chart1': chart1, 'chart2': chart2}

    return render(request, 'chart_graphos.html', context)


def index(request):

    if request.user.id is None:
        form = LoginForm()
        return render(request, 'home.html', {'form': form})
    else:
        context = {}
        return render(request, 'home.html', context)


class MyCSVDataSource(CSVDataSource):
    def get_data(self):
        data = super(MyCSVDataSource, self).get_data()
        header = data[0]
        data_without_header = data[1:]
        for row in data_without_header:
            for x in range(1, len(row)):
                try:
                    row[x] = float(row[x])
                except (ValueError, TypeError):
                    row[x] = None
        data_without_header.insert(0, header)
        return data_without_header


class MyModelDataSource(ModelDataSource):
    def get_data(self):
        data = super(MyModelDataSource, self).get_data()
        header = data[0]
        data_without_header = data[1:]
        for row in data_without_header:
            for x in range(1, len(row)):
                try:
                    row[x] = float(row[x])
                except (ValueError, TypeError):
                    row[x] = None
        data_without_header.insert(0, header)
        return data_without_header


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            try:
                user = MyUser.objects.get(username=username)
            except MyUser.DoesNotExist:
                user = None

            if user is not None:
                raw_password = form.cleaned_data.get('password')
                user = authenticate(username=username, password=raw_password)
                if user is not None:
                    if user.is_active:
                        messages.success(request, 'Login done!')
                        login(request, user)
                else:
                    messages.error(request, 'Error in the values')
            else:
                messages.error(request, 'This user is not registered!!!')
        return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('/')


def search(request):
    if request.method == 'POST' and request.POST['value']:
        value = request.POST['value']

        clusters = Cluster.objects.filter(name__icontains=value)

        towers = Tower.objects.filter(QD(code_inegi__icontains=value)| QD(client__name__icontains=value) | QD(designation__icontains=value))

        calibrations = Calibration.objects.filter(QD(offset__icontains=value) | QD(slope__icontains=value) | QD(ref__icontains=value))

        equipments = Equipment.objects.filter(sn__icontains=value)
        if equipments:
            equipments.calibrations = Calibration.objects.filter(equipment__in=equipments)

        return render(request, 'search.html', {'clusters': clusters, 'towers': towers, 'calibrations': calibrations, 'equipments': equipments})
    else:
        return HttpResponseRedirect(reverse("index"))


# ========================================= USERS =========================================


def add_user(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)

        if form.is_valid():

            bool_client = form.cleaned_data.get('is_client')
            bool_staff = form.cleaned_data.get('is_staff')
            bool_manager = form.cleaned_data.get('is_manager')

            if bool_client and bool_manager:
                form._errors['is_manager'] = ['You cant be a client and a manager']
            elif bool_client and bool_staff:
                form._errors['is_staff'] = ['You cant be a client and a administrator']
            elif form.is_valid():
                form.save()
                messages.success(request, 'User added!')
                return HttpResponseRedirect(reverse("list_users"))
            else:
                messages.warning(request, 'User not added!!!')
        else:
            messages.warning(request, 'User not added!!!')
    else:
        form = RegisterForm()

    return render(request, 'add_user.html', {'form': form})


def list_users(request):
    users = MyUser.objects.all()

    return render(request, 'list_users.html', {'users': users})


def view_user(request, user_id):

    if not request.user.is_staff and not str(request.user.id) == str(user_id):
        messages.error(request, 'You dont have permissions to do this!!!')
        return HttpResponseRedirect(reverse("list_users"))

    try:
        user = MyUser.objects.get(id=user_id)
    except MyUser.DoesNotExist:
        return HttpResponseRedirect(reverse("list_users"))

    if request.method == 'GET':
        if str(request.user.id) == str(user_id):
            password_form = PasswordChangeForm(request.user)
        form = UserForm(instance=user)
    elif request.method == 'POST':
        if str(request.user.id) == str(user_id):
            password_form = PasswordChangeForm(request.user, request.POST)
        form = UserForm(request.POST, instance=user)

        if form.is_valid():
            form.save()
            messages.success(request, 'User information updated successfully')
            return HttpResponseRedirect(reverse("list_users"))
        else:
            user_invalid = True

        if str(request.user.id) == str(user_id) and password_form.is_valid():
            user = password_form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password updated successfully!')
            return HttpResponseRedirect(reverse("list_users"))
        else:
            password_invalid = True

        if password_invalid and not user_invalid:
            messages.error(request, "Password wasn't updated!")
        elif user_invalid:
            messages.error(request, "User information wasn't updated!")

    if str(request.user.id) == str(user_id):
        password_form.fields['old_password'].widget.attrs = {'class': 'form-control'}
        password_form.fields['new_password1'].widget.attrs = {'class': 'form-control'}
        password_form.fields['new_password2'].widget.attrs = {'class': 'form-control'}

        return render(request, 'view_user.html', {'password_form': password_form, 'form': form, 'user': user})

    else:
        return render(request, 'view_user.html', {'form': form, 'user': user})


def delete_user(request):
    if request.is_ajax and request.method == 'POST':
        user = MyUser.objects.get(id=request.POST["id"])
        try:
            user.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")
        messages.success(request, 'User was deleted!')
        return HttpResponse('ok')
    messages.error(request, 'A problem happen when removing the user!!!')
    return HttpResponse("not ok")


def ban_user(request):
    if request.is_ajax and request.method == 'POST':
        user = MyUser.objects.get(id=request.POST["id"])
        actual_info = user.is_active
        user.is_active = not user.is_active
        user.save()

        if actual_info != user.is_active:
            messages.success(request, 'User was modified successfully')
        return HttpResponse('ok')
    messages.error(request, 'A problem happen when removing the user!!!')
    return HttpResponse("not ok")


# ========================================= TOWERS =========================================


def add_tower(request):
    if request.method == 'POST':
        form = TowerForm(request.POST)
        if form.is_valid():
            tower = form.save()

            # Associate the tower created to the user (that isn't an admin?)
            # if not request.user.is_staff:
            # MyUser.objects.get(id=request.user.id).towers.add(tower)

            messages.success(request, 'Tower created successfully!')
            return HttpResponseRedirect(reverse("list_towers"))
        else:
            messages.warning(request, 'Tower not added!!!')
    else:
        form = TowerForm()

    return render(request, 'add_tower.html', {'form': form})


def create_tower_if_doesnt_exists(request, tower_code):
    try:
        Tower.objects.get(pk=tower_code)
    except Tower.DoesNotExist:
        tower = Tower(pk=tower_code, name=tower_code)
        tower.save()
        message = "Tower with code: " + tower.code + " created. Please update the meta-information on the Towers page"
        messages.warning(request, message)


def list_towers(request):
    towers = Tower.objects.all()

    return render(request, 'list_towers.html', {'towers': towers})


def view_tower(request, tower_id):
    try:
        tower = Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    if request.method == 'GET':
        form = TowerForm(instance=tower)
    elif request.method == 'POST':
        form = TowerForm(request.POST, instance=tower)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tower was edited successfully')
            return HttpResponseRedirect(reverse("list_towers"))
        else:
            messages.warning(request, 'Tower wasnt edited successfully!!!')

    periods = PeriodConfiguration.objects.filter(tower=tower_id).order_by('-begin_date')

    # To get comments on each classification period for this tower
    equipment_configuration = EquipmentConfig.objects.filter(conf_period__in=periods)
    classifications = ClassificationPeriod.objects.filter(equipment_configuration__in=equipment_configuration)
    comments_classification = CommentClassification.objects.filter(classification__in=classifications).order_by('-begin_date')

    comments_tower = CommentTower.objects.filter(tower=tower)

    # get_query = request.GET.copy()
    # if 'tower' not in get_query:
    #     get_query['tower'] = tower_id
    # if 'classifications' not in get_query:
    #     get_query['classifications'] = comments_classification

    filter = DateTowerFilter(request.GET, queryset=comments_tower)
    filter.flag = 0

    if filter.form['begin_date'].value() and filter.form['end_date'].value():
        begin_date = filter.form['begin_date'].value()
        end_date = filter.form['end_date'].value()

        begin_date = get_date(begin_date)
        end_date = get_date(end_date)

        if end_date < begin_date:
            messages.error(request, "Begin date can't be higher than End date")
        # if filter.form['comment_tower'].value() and filter.form['comment_classification'].value():
        #     comments_tower = CommentTower.objects.filter(pk__in=filter.form['comment_tower'].value())
        #     comments_classification = CommentClassification.objects.filter(classification__in=classifications)
        # elif filter.form['comment_tower'].value():
        #     comments_tower = CommentTower.objects.filter(pk__in=filter.form['comment_tower'].value())
        #     comments_classification = None
        # elif filter.form['comment_classification'].value():
        #     comments_tower = None
        #     comments_classification = CommentClassification.objects.filter(classification__in=classifications)
        else:

            comments_tower = CommentTower.objects.filter(QD(tower=tower) & (QD(begin_date__range=(begin_date, end_date)) |
                                                                            QD(end_date__range=(begin_date, end_date))))
            comments_classification = CommentClassification.objects.filter(QD(classification__in=classifications) & (QD(begin_date__range=(begin_date, end_date)) |
                                                                            QD(end_date__range=(begin_date, end_date))))
            filter = DateTowerFilter(request.GET, queryset=comments_tower)

        filter.flag = 1
        # filter.form._errors = ""
    elif filter.form['begin_date'].value() == '' or filter.form['end_date'].value() == '':
        filter.flag = 1
        # filter.form._errors = ""
    else:
        filter.form._errors = ""

    return render(request, 'view_tower.html', {'form': form, 'tower_id': tower_id, 'tower': tower, 'periods': periods, 'comments_classification': comments_classification, 'comments_tower': comments_tower, 'filter': filter})


def delete_tower(request):
    if request.is_ajax and request.method == 'POST':
        tower = Tower.objects.get(pk=request.POST["id"])
        try:
            tower.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")
        messages.success(request, 'Tower was removed successfully!')
        return HttpResponse('ok')
    messages.error(request, 'A problem occurred when deleting the Tower!')
    return HttpResponse("not ok")


# ========================================= TOWERS ASSOCIATION =========================================


def add_associate_towers(request):
    if not request.user.is_staff:
        messages.error(request, 'You dont have permissions to do this!!!')
        return redirect('/')

    if request.method == 'POST':
        form = UserTowersFrom(request.POST)
        if form.is_valid():
            tower = form.cleaned_data['tower']
            user = form.cleaned_data['user']
            begin_date = form.cleaned_data['begin_date']
            end_date = form.cleaned_data['end_date']
            verify = 0
            for t in tower:
                verify = check_if_period_is_valid_2(t, user, begin_date, end_date, 0)
                if verify is not 0:
                    pass
            if verify is 0:
                form.save()
                messages.success(request, 'Towers associated successfully!')
                return HttpResponseRedirect(reverse("list_associate_towers"))
            elif verify is 1:
                messages.error(request, "End date can't be higher or equal to the Begin date!!!")
            elif verify is 2:
                messages.error(request, "There are already a period for that user and towers")
        else:
            messages.warning(request, 'Problem associating towers!!!')
    else:
        form = UserTowersFrom()

    return render(request, 'add_associate_towers.html', {'form': form})


def list_associate_towers(request):
    if not request.user.is_staff:
        messages.error(request, 'You dont have permissions to do this!!!')
        return redirect('/')

    utd = UserTowerDates.objects.all()

    return render(request, 'list_associate_towers.html', {'utd': utd})


def view_associate_towers(request, association_id):
    if not request.user.is_staff:
        messages.error(request, 'You dont have permissions to do this!!!')
        return redirect('/')

    try:
        utd = UserTowerDates.objects.get(pk=association_id)
    except UserTowerDates.DoesNotExist:
        return HttpResponseRedirect(reverse("list_associate_towers"))

    if request.method == 'POST':
        form = UserTowersFrom(request.POST, instance=utd)
        if form.is_valid():
            tower = form.cleaned_data['tower']
            user = form.cleaned_data['user']
            begin_date = form.cleaned_data['begin_date']
            end_date = form.cleaned_data['end_date']
            verify = 0
            for t in tower:
                verify = check_if_period_is_valid_2(t, user, begin_date, end_date, association_id)
                if verify is not 0:
                    pass
            if verify is 0:
                form.save()
                messages.success(request, 'Towers associated successfully!')
                return HttpResponseRedirect(reverse("list_associate_towers"))
            elif verify is 1:
                messages.error(request, "End date can't be higher or equal to the Begin date!!!")
            elif verify is 2:
                messages.error(request, "There are already a period for that user and towers")
        else:
            messages.warning(request, 'Problem associating towers!!!')
    else:
        form = UserTowersFrom(instance=utd)

    return render(request, 'view_associate_towers.html', {'form': form, 'association_id': association_id, 'utd': utd})


def delete_associate_tower(request):
    if request.is_ajax and request.method == 'POST':
        utd = UserTowerDates.objects.get(pk=request.POST["id"])
        try:
            utd.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")
        messages.success(request, 'Association was removed successfully!')
        return HttpResponse('ok')
    messages.error(request, 'A problem occurred when deleting the Association!')
    return HttpResponse("not ok")

# ========================================= MACHINES =========================================


def add_machine(request):
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Machine created successfully!')
            return HttpResponseRedirect(reverse("list_machines"))
        else:
            messages.warning(request, 'Machine not added!!!')
    else:
        form = MachineForm()

    return render(request, 'add_machine.html', {'form': form})


def list_machines(request):
    machines = Machine.objects.all()

    return render(request, 'list_machines.html', {'machines': machines})


def view_machine(request, machine_id):
    try:
        machine = Machine.objects.get(pk=machine_id)
    except Machine.DoesNotExist:
        return HttpResponseRedirect(reverse("list_machines"))

    if request.method == 'GET':
        form = MachineForm(instance=machine)
    elif request.method == 'POST':
        form = MachineForm(request.POST, instance=machine)
        if form.is_valid():
            form.save()
            messages.success(request, 'Machine was edited successfully')
            return HttpResponseRedirect(reverse("list_machines"))
        else:
            messages.warning(request, 'Machine wasnt edited!!!')

    return render(request, 'view_machine.html', {'form': form, 'machine_id': machine_id, 'machine': machine})


def delete_machine(request):
    if request.is_ajax and request.method == 'POST':
        machine = Machine.objects.get(pk=request.POST["id"])
        try:
            machine.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")
        messages.success(request, 'Machine was successfully removed!')
        return HttpResponse('ok')
    messages.error(request, 'A problem occurred when deleting the Machine!')
    return HttpResponse("not ok")


# ========================================= CLUSTERS =========================================


def add_cluster(request):
    if request.method == 'POST':
        form = ClusterForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, 'Cluster created successfully!')
            return HttpResponseRedirect(reverse("list_clusters"))
        else:
            messages.warning(request, 'Cluster not added!!!')
    else:
        form = ClusterForm()

    return render(request, 'add_cluster.html', {'form': form})


def list_clusters(request):
    clusters = Cluster.objects.all()

    return render(request, 'list_clusters.html', {'clusters': clusters})


def view_cluster(request, cluster_id):
    try:
        cluster = Cluster.objects.get(pk=cluster_id)
    except Cluster.DoesNotExist:
        return HttpResponseRedirect(reverse("list_clusters"))

    if request.method == 'GET':
        form = ClusterForm(instance=cluster)
    elif request.method == 'POST':
        form = ClusterForm(request.POST, instance=cluster)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cluster was edited with success')
            return HttpResponseRedirect(reverse("list_clusters"))
        else:
            messages.warning(request, "Cluster wasn't edited!!!")

    return render(request, 'view_cluster.html', {'form': form, 'cluster_id': cluster_id, 'cluster': cluster})


def delete_cluster(request):
    if request.is_ajax and request.method == 'POST':
        cluster = Cluster.objects.get(pk=request.POST["id"])
        try:
            cluster.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")
        messages.success(request, 'Cluster was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the cluster!')
    return HttpResponse("not ok")


# ========================================= EQUIPMENTS =========================================


def list_equipments(request):
    equipments = Equipment.objects.all()

    return render(request, 'list_equipments.html', {'equipments': equipments})


def add_equipment(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, 'Equipment created successfully!')
            return HttpResponseRedirect(reverse("list_equipments"))
        else:
            messages.warning(request, 'Equipment not added!!!')
    else:
        form = EquipmentForm()

    return render(request, 'add_equipment.html', {'form': form})


def view_equipment(request, equipment_id):
    try:
        equipment = Equipment.objects.get(pk=equipment_id)
    except Equipment.DoesNotExist:
        return HttpResponseRedirect(reverse("list_equipments"))

    if request.method == 'GET':
        form = EquipmentForm(instance=equipment)
    elif request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment was edited with success')
            return HttpResponseRedirect(reverse("list_equipments"))
        else:
            messages.warning(request, "Equipment wasn't edited!!!")

    calibrations = Calibration.objects.filter(equipment=equipment_id).order_by('-calib_date')

    return render(request, 'view_equipment.html', {'form': form, 'equipment_id': equipment_id, 'equipment': equipment, 'calibrations':calibrations})


def delete_equipment(request):
    if request.is_ajax and request.method == 'POST':
        equipment = Equipment.objects.get(pk=request.POST["id"])
        try:
            equipment.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")
        messages.success(request, 'Equipment was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the equipment!')
    return HttpResponse("not ok")


# ========================================= TYPES =========================================


def list_type(request, type):
    if type == 'equipment':
        type_obj = EquipmentType.objects.all()
        name = "Equipments Type"
    elif type == 'user_group':
        type_obj = UserGroupType.objects.all()
        name = "Users Groups Type"
    elif type == 'model':
        type_obj = EquipmentCharacteristic.objects.all()
        name = "Equipment Models"
    elif type == 'unit':
        type_obj = UnitType.objects.all()
        name = "Unit Type"
    elif type == 'statistic':
        type_obj = StatisticType.objects.all()
        name = "Statistic Type"
    elif type == 'metric':
        type_obj = MetricType.objects.all()
        name = "Metric Type"
    elif type == 'component':
        type_obj = ComponentType.objects.all()
        name = "Component Type"
    elif type == 'affiliation':
        type_obj = AffiliationType.objects.all()
        name = "Affiliation Type"

    return render(request, 'list_type.html', {'type_obj': type_obj, 'type': type, 'name': name})


def add_type(request, type):
    if type == 'equipment':
        name = "Equipment Type"
    elif type == 'user_group':
        name = "User Group Type"
    elif type == 'model':
        name = "Equipment Models"
    elif type == 'unit':
        name = "Unit Type"
    elif type == 'statistic':
        name = "Statistic Type"
    elif type == 'metric':
        name = "Metric Type"
    elif type == 'component':
        name = "Component Type"
    elif type == 'affiliation':
        name = "Affiliation Type"

    if request.method == 'POST':
        if type == 'equipment':
            form = EquipmentTypeForm(request.POST)
        elif type == 'user_group':
            form = UserGroupTypeForm(request.POST)
        elif type == 'model':
            form = EquipmentCharacteristicForm(request.POST)
        elif type == 'unit':
            form = UnitTypeForm(request.POST)
        elif type == 'statistic':
            form = StatisticTypeForm(request.POST)
        elif type == 'metric':
            form = MetricTypeForm(request.POST)
        elif type == 'component':
            form = ComponentTypeForm(request.POST)
        elif type == 'affiliation':
            form = AffiliationTypeForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'New Type created successfully!')
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
        else:
            messages.warning(request, 'Type not added!!!')
    else:
        if type == 'equipment':
            form = EquipmentTypeForm()
        elif type == 'user_group':
            form = UserGroupTypeForm()
        elif type == 'model':
            form = EquipmentCharacteristicForm()
        elif type == 'unit':
            form = UnitTypeForm()
        elif type == 'statistic':
            form = StatisticTypeForm()
        elif type == 'metric':
            form = MetricTypeForm()
        elif type == 'component':
            form = ComponentTypeForm()
        elif type == 'affiliation':
            form = AffiliationTypeForm()

    return render(request, 'add_type.html', {'form': form, 'type': type, 'name': name})


def add_type_equipment(request):
    data = dict()

    if request.method == 'POST':
        form = EquipmentTypeForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = EquipmentTypeForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_equipment.html', context, request=request)
    return JsonResponse(data)


def add_type_user_group(request):
    data = dict()

    if request.method == 'POST':
        form = UserGroupTypeForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = UserGroupTypeForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_user_group.html', context, request=request)
    return JsonResponse(data)


def add_type_model(request):
    data = dict()

    if request.method == 'POST':
        form = EquipmentCharacteristicForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = EquipmentCharacteristicForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_model.html', context, request=request)
    return JsonResponse(data)


def add_type_unit(request):
    data = dict()

    if request.method == 'POST':
        form = UnitTypeForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = UnitTypeForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_unit.html', context, request=request)
    return JsonResponse(data)


def add_type_statistic(request):
    data = dict()

    if request.method == 'POST':
        form = StatisticTypeForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = StatisticTypeForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_statistic.html', context, request=request)
    return JsonResponse(data)


def add_type_metric(request):
    data = dict()

    if request.method == 'POST':
        form = MetricType(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = MetricType()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_metric.html', context, request=request)
    return JsonResponse(data)


def add_type_component(request):
    data = dict()

    if request.method == 'POST':
        form = ComponentTypeForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = ComponentTypeForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_component.html', context, request=request)
    return JsonResponse(data)


def add_type_affiliation(request):
    data = dict()

    if request.method == 'POST':
        form = AffiliationTypeForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = AffiliationTypeForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_affiliation.html', context, request=request)
    return JsonResponse(data)


def add_equipment_json(request):
    data = dict()

    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = EquipmentForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_equipment_json.html', context, request=request)
    return JsonResponse(data)


def view_type(request, equipment_id, type):
    if type == 'equipment':
        name = "Equipment Type"
        try:
            obj = EquipmentType.objects.get(pk=equipment_id)
        except EquipmentType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
    elif type == 'user_group':
        name = "User Group Type"
        try:
            obj = UserGroupType.objects.get(pk=equipment_id)
        except UserGroupType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
    elif type == 'model':
        name = "Equipment Models"
        try:
            obj = EquipmentCharacteristic.objects.get(pk=equipment_id)
        except EquipmentCharacteristic.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
    elif type == 'unit':
        name = "Unit Type"
        try:
            obj = UnitType.objects.get(pk=equipment_id)
        except UnitType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
    elif type == 'statistic':
        name = "Statistic Type"
        try:
            obj = StatisticType.objects.get(pk=equipment_id)
        except StatisticType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
    elif type == 'metric':
        name = "Metric Type"
        try:
            obj = MetricType.objects.get(pk=equipment_id)
        except MetricType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
    elif type == 'component':
        name = "Component Type"
        try:
            obj = ComponentType.objects.get(pk=equipment_id)
        except ComponentType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
    elif type == 'affiliation':
        name = "Affiliation Type"
        try:
            obj = AffiliationType.objects.get(pk=equipment_id)
        except AffiliationType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))

    if request.method == 'GET':
        if type == 'equipment':
            form = EquipmentTypeForm(instance=obj)
        elif type == 'user_group':
            form = UserGroupTypeForm(instance=obj)
        elif type == 'model':
            form = EquipmentCharacteristicForm(instance=obj)
        elif type == 'unit':
            form = UnitTypeForm(instance=obj)
        elif type == 'statistic':
            form = StatisticTypeForm(instance=obj)
        elif type == 'metric':
            form = MetricTypeForm(instance=obj)
        elif type == 'component':
            form = ComponentTypeForm(instance=obj)
        elif type == 'affiliation':
            form = AffiliationTypeForm(instance=obj)

    elif request.method == 'POST':
        if type == 'equipment':
            form = EquipmentTypeForm(request.POST, instance=obj)
        elif type == 'user_group':
            form = UserGroupTypeForm(request.POST, instance=obj)
        elif type == 'model':
            form = EquipmentCharacteristicForm(request.POST, instance=obj)
        elif type == 'unit':
            form = UnitTypeForm(request.POST, instance=obj)
        elif type == 'statistic':
            form = StatisticTypeForm(request.POST, instance=obj)
        elif type == 'metric':
            form = MetricTypeForm(request.POST, instance=obj)
        elif type == 'component':
            form = ComponentTypeForm(request.POST, instance=obj)
        elif type == 'affiliation':
            form = AffiliationTypeForm(request.POST, instance=obj)

        if form.is_valid():
            form.save()
            messages.success(request, 'Type was edited with success')
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
        else:
            messages.warning(request, "Type wasn't edited!!!")

    return render(request, 'view_type.html', {'form': form, 'obj_id': equipment_id, 'obj': obj, 'type': type, 'name': name})


def delete_type(request):
    if request.is_ajax and request.method == 'POST':
        if request.POST["typex"] == 'equipment':
            obj = EquipmentType.objects.get(pk=request.POST["id"])
        elif request.POST["typex"] == 'user_group':
            obj = UserGroupType.objects.get(pk=request.POST["id"])
        elif request.POST["typex"] == 'model':
            obj = EquipmentCharacteristic.objects.get(pk=request.POST["id"])
        elif request.POST["typex"] == 'unit':
            obj = UnitType.objects.get(pk=request.POST["id"])
        elif request.POST["typex"] == 'statistic':
            obj = StatisticType.objects.get(pk=request.POST["id"])
        elif request.POST["typex"] == 'metric':
            obj = MetricType.objects.get(pk=request.POST["id"])
        elif request.POST["typex"] == 'component':
            obj = ComponentType.objects.get(pk=request.POST["id"])
        elif request.POST["typex"] == 'affiliation':
            obj = AffiliationType.objects.get(pk=request.POST["id"])

        try:
            obj.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Type was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the type!')
    return HttpResponse("not ok")


# ========================================= DATASETS =========================================


def show_towers_data_mongo(request):
    data = {}

    DataSetMongo.objects.all().delete()

    start_time = time.time()
    towers = DataSetMongo.objects(QM(tower_code="port525") and QM(time_stamp__lte=datetime(2010, 12, 25)))
    end = time.time()
    total_time = (end - start_time)
    print('Query time: ', total_time, ' seconds', towers.count())

    data['towers'] = {}

    return render(request, 'show_towers_data_mongo.html', data)


def add_raw_data_mongo(request):
    total_time_operation = 0
    total_time_insertion = 0
    conta = 0
    flag_problem = False

    for file in request.FILES.getlist('document'):
        conta = conta + 1

    if conta > 150:
        messages.error(request, "Please select at max. 150 files")
        return HttpResponseRedirect(reverse("show_towers_data_mongo"))

    for file in request.FILES.getlist('document'):
        decoded_file = file.read().decode('utf-8')
        io_file = io.StringIO(decoded_file)

        file = re.findall('[0-9]{4}_[0-9]{2}.row', str(file))

        if file:
            print(str(file))
            firstime = True
            op_time = time.time()
            dataraw = []

            for i, line in enumerate(io_file):

                # remove the \n at the end
                line = line.rstrip()

                try:
                    if line.strip()[-1] is ',':
                        line = line.strip()[:-1]
                except IndexError:
                    flag_problem = True
                    messages.error(request, 'Error reading a line, check your file -> ' + str(
                        file) + '. No values was entered on the DB for this file')
                    return HttpResponseRedirect(reverse("show_towers_data_mongo"))

                mylist = line.split(",", 3)

                time_value, flag_date = parsedate(request, file, mylist, i)

                if flag_date:
                    return HttpResponseRedirect(reverse("show_towers_data_mongo"))

                try:
                    mylist[3]
                except IndexError:
                    flag_problem = True
                    messages.warning(request, 'Warning!!! reading a line, check your file -> ' + str(
                        file) + ' at line: ' + str(i + 1) + '. No values was entered on the DB for time stamp: ' + str(
                        time_value))
                    continue

                values = mylist[3]
                tower_code = mylist[0]
                tower_code = tower_code.lower()

                # Check for if tower exists or not, if not create.
                # if firstime:
                #     create_tower_if_doesnt_exists(request, tower_code)
                #     firstime = False

                # Check if have a tower_code and a time_stamp and replace the value - Heavy Operation
                try:
                    check_replicated = DataSetMongo.objects(QM(tower_code=tower_code) and QM(time_stamp=time_value))
                except DataSetMongo.DoesNotExist:
                    check_replicated = None

                if check_replicated.count() >= 1:
                    check_replicated.update(value=values)
                else:
                    tower_data = DataSetMongo(tower_code=tower_code, time_stamp=time_value, value=values)
                    dataraw.append(tower_data)

            total_time = (time.time() - op_time)
            total_time_operation += total_time
            print('time of operation: ', total_time, ' seconds')

            db_time = time.time()
            if dataraw:
                DataSetMongo.objects.insert(dataraw)
            total_time = (time.time() - db_time)
            total_time_insertion += total_time
            print('time to insert in database: ', total_time, ' seconds')

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_mongo"))


def show_towers_data_influx(request):
    start_time = time.time()

    result = INFLUXCLIENT.query("select time, value from ort542")
    result2 = INFLUXCLIENT.query("select time, value from ort542_b")

    end = time.time()
    total_time = (end - start_time)
    print('Query time: ', total_time, ' seconds')

    # print("Result: {0}".format(result))

    # print(json.dumps(list(result)[0]))

    # for obj in list(result)[0]:
    #     print(obj)

    if result:
        result = list(result)[0]
    if result2:
        result += list(result2)[0]

    result = {}
    # print(len(result))
    return render(request, "show_towers_data_influx.html", {'data': result}, content_type="text/html")


def add_raw_data_influx(request):
    total_time_operation = 0
    total_time_insertion = 0
    conta = 0
    flag_problem = False

    for file in request.FILES.getlist('document'):
        conta = conta + 1

    if conta > 150:
        messages.error(request, "Please select at max. 150 files")
        return HttpResponseRedirect(reverse("show_towers_data_influx"))

    for file in request.FILES.getlist('document'):
        decoded_file = file.read().decode('utf-8')
        io_file = io.StringIO(decoded_file)

        file = re.findall('[0-9]{4}_[0-9]{2}.row', str(file))

        if file:
            print(str(file))
            firstime = True
            op_time = time.time()
            points = []
            tt_date = 0

            for i, line in enumerate(io_file):
                #remove the \n at the end
                line = line.rstrip()

                try:
                    if line.strip()[-1] is ',':
                        line = line.strip()[:-1]
                except IndexError:
                    flag_problem = True
                    messages.error(request, 'Error!!! Reading a line, check your file -> ' + str(
                        file) + '. No values was entered on the DB for this file')
                    return HttpResponseRedirect(reverse("show_towers_data_influx"))

                mylist = line.split(",", 3)

                timefordate = time.time()
                time_value, flag_date = parsedate(request, file, mylist, i)
                tt_date += time.time() - timefordate

                if flag_date:
                    return HttpResponseRedirect(reverse("show_towers_data_influx"))

                try:
                    mylist[3]
                except IndexError:
                    flag_problem = True
                    messages.warning(request, 'Warning!!! reading a line, check your file -> ' + str(
                        file) + ' at line: ' + str(i+1) + '. No values was entered on the DB for time stamp: ' + str(time_value))
                    continue

                values = mylist[3]
                tower_code = mylist[0]
                tower_code = tower_code.lower()

                # Check for if tower exists or not, if not create.
                # if firstime:
                #     create_tower_if_doesnt_exists(request, tower_code)
                #     firstime = False

                # MySeriesHelper(measurement=tower_code, time=time_value, value=values)
                point = {
                        "measurement": tower_code,
                        "time": time_value,
                        "fields": {
                            "value": values
                            }
                        }
                points.append(point)

            print('time of parse time: ', tt_date, ' seconds')

            total_time = (time.time() - op_time)
            total_time_operation += total_time
            print('time of operation: ', total_time, ' seconds')

            db_time = time.time()
            # MySeriesHelper.commit()
            if points:
                INFLUXCLIENT.write_points(points, batch_size=5000)
            total_time = (time.time() - db_time)
            total_time_insertion += total_time
            print('time to insert in database: ', total_time, ' seconds')

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_influx"))


def show_towers_data_pg(request):
    data = {}

    # DataSetPG.objects.all().delete()

    start_time = time.time()
    # dataset = DataSetPG.objects.filter(QD(tower_code='port525'))
    dataset = DataSetPG.objects.all()

    # for t in dataset:
    #     print(t.tower_code, "---", t.time_stamp, "---", t.value)

    end = time.time()
    total_time = (end - start_time)
    print('\nQuery time: ', total_time, ' seconds -- size:', len(dataset))
    data['towers'] = {}

    return render(request, 'show_towers_data_pg.html', data)


def add_raw_data_pg(request):
    total_time_operation = 0
    total_time_insertion = 0
    conta = 0
    flag_problem = False

    for file in request.FILES.getlist('document'):
        conta = conta + 1

    if conta > 150:
        messages.error(request, "Please select at max. 150 files")
        return HttpResponseRedirect(reverse("show_towers_data_pg"))

    for file in request.FILES.getlist('document'):
        decoded_file = file.read().decode('utf-8')
        io_file = io.StringIO(decoded_file)

        file = re.findall('[0-9]{4}_[0-9]{2}.row', str(file))

        if file:
            print(str(file))
            op_time = time.time()
            db_time = 0
            dataraw = []
            firstime = True

            for i, line in enumerate(io_file):
                # remove the \n at the end
                line = line.rstrip()

                try:
                    if line.strip()[-1] is ',':
                        line = line.strip()[:-1]
                except IndexError:
                    flag_problem = True
                    messages.error(request, 'Error reading a line, check your file -> ' + str(
                        file) + '. No values was entered on the DB')
                    return HttpResponseRedirect(reverse("show_towers_data_pg"))

                mylist = line.split(",", 3)

                time_value, flag_date = parsedate(request, file, mylist, i)

                if flag_date:
                    return HttpResponseRedirect(reverse("show_towers_data_pg"))

                try:
                    mylist[3]
                except IndexError:
                    flag_problem = True
                    messages.warning(request, 'Warning!!! reading a line, check your file -> ' + str(
                        file) + ' at line: ' + str(i + 1) + '. No values was entered on the DB for time stamp: ' + str(
                        time_value))
                    continue

                values = mylist[3]
                tower_code = mylist[0]
                tower_code = tower_code.lower()

                # Check for if tower exists or not, if not create.
                # if firstime:
                #     create_tower_if_doesnt_exists(request, tower_code)
                #     firstime = False

                # Check if have a tower_code and a time_stamp and replace the value - VERY Heavy operation
                db_time_start = time.time()
                try:
                    check_replicated = DataSetPG.objects.get(QD(tower_code=tower_code) and QD(time_stamp=time_value))
                except DataSetPG.DoesNotExist:
                    check_replicated = None

                if check_replicated:
                    check_replicated.value = values
                    check_replicated.save()
                else:
                    tower_data = DataSetPG(tower_code=tower_code, time_stamp=time_value, value=values)
                    dataraw.append(tower_data)
                db_time += (time.time() - db_time_start)

                # Heavier!!!!! - Maybe because takes care one by one! - Takes 1 to 2 seconds more in 6000 lines
                # db_time_start = time.time()
                # DataSetPG.objects.update_or_create(tower_code=tower_code, time_stamp=time_value, defaults={'value': values})
                # db_time += (time.time() - db_time_start)

            total_time_insertion += db_time
            print('Database time inside: ', db_time, ' seconds')

            op_time = (time.time() - op_time)
            total_time_operation += op_time
            print('Operation time: ', op_time, ' seconds')

            # Takes normally 0.3 secs
            db_time2 = time.time()
            if dataraw:
                DataSetPG.objects.bulk_create(dataraw)
            db_time2 = (time.time() - db_time2)
            total_time_insertion += db_time2

    print('Total time to insert in database: ', total_time_insertion, ' seconds')
    print('Total time of operation: ', total_time_operation, ' seconds')

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_pg"))


# ========================================= WIZARD =========================================


class FormWizardView(SessionWizardView):
    template_name = "wizard.html"

    # towers = Tower.objects.all()
    # ClusterForm.fields['towers'].choices = [(x, x) for x in towers]

    form_list = [ClusterForm, TowerForm]

    def done(self, form_list,  **kwargs):
        return render(self.request, 'home.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })


# ========================================= CONFIGURATION OF PERIODS TO TOWERS =========================================


def add_conf_period(request, tower_id):

    try:
        tower = Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    if request.method == 'POST':
        form = PeriodConfigForm(request.POST)

        if form.is_valid():
            bool_wind = form.cleaned_data.get('wind_rss')
            bool_rss = form.cleaned_data.get('solar_rss')

            if bool_wind and bool_rss:
                form._errors['wind_rss'] = ['Tower cant be wind and solar']
            elif form.is_valid():
                verify = check_if_period_is_valid(tower_id, form.cleaned_data.get('begin_date'), form.cleaned_data.get('end_date'), 0)

                if verify is 0:
                    period = PeriodConfiguration(begin_date=form.cleaned_data.get('begin_date'),
                                                 end_date=form.cleaned_data.get('end_date'),
                                                 wind_rss=form.cleaned_data.get('wind_rss'),
                                                 solar_rss=form.cleaned_data.get('solar_rss'),
                                                 raw_freq=form.cleaned_data.get('raw_freq'),
                                                 time_zone=form.cleaned_data.get('time_zone'),
                                                 tower=tower)
                    period.save()
                    messages.success(request, 'Period was created successfully!')
                    return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))
                elif verify is 1:
                    messages.error(request, "End date can't be higher or equal to the Begin date!!!")
                elif verify is 2:
                    messages.error(request, "Begin date is invalid!!!")
                elif verify is 3 or verify is 4:
                    messages.error(request, "End date is invalid!!!")
                elif verify is 5:
                    messages.error(request, "Have an open period")

            else:
                messages.warning(request, 'Period not added!!!')

        else:
            messages.warning(request, 'Period was not added!!!')
    else:
        form = PeriodConfigForm()
    print(form.as_p())

    return render(request, 'add_conf_period.html', {'form': form, 'tower': tower, 'tower_id': tower_id})


def view_conf_period(request, period_id, tower_id):
    try:
        period = PeriodConfiguration.objects.get(pk=period_id)
    except PeriodConfiguration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    if request.method == 'GET':
        form = PeriodConfigForm(instance=period)
    elif request.method == 'POST':
        form = PeriodConfigForm(request.POST, instance=period)
        if form.is_valid():
            verify = check_if_period_is_valid(tower_id, form.cleaned_data.get('begin_date'), form.cleaned_data.get('end_date'), period_id)

            if verify is 0:
                form.save()
                messages.success(request, 'Period was edited successfully')
                return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))
            elif verify is 1:
                messages.error(request, "End date can't be higher or equal to the Begin date!!!")
            elif verify is 2:
                messages.error(request, "Begin date is invalid!!!")
            elif verify is 3 or verify is 4 or verify is 5:
                messages.error(request, "End date is invalid!!!")
        else:
            messages.warning(request, 'Period wasnt edited successfully!!!')

    configurations = EquipmentConfig.objects.filter(conf_period=period_id).order_by('-id')

    return render(request, 'view_conf_period.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'period': period, 'configurations': configurations})


def delete_conf_period(request):
    if request.is_ajax and request.method == 'POST':
        period = PeriodConfiguration.objects.get(pk=request.POST["id"])
        try:
            period.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Period was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Period!')
    return HttpResponse("not ok")


# ========================================= CALIBRATIONS =========================================


def add_calibration(request, equipment_id):

    try:
        equipment = Equipment.objects.get(pk=equipment_id)
    except Equipment.DoesNotExist:
        return HttpResponseRedirect(reverse("view_equipment", kwargs={'equipment_id': equipment_id}))

    if request.method == 'POST':
        form = CalibrationForm(request.POST)

        if form.is_valid():
            calibration = Calibration(offset=form.cleaned_data.get('offset'),
                                      slope=form.cleaned_data.get('slope'),
                                      calib_date=form.cleaned_data.get('calib_date'),
                                      ref=form.cleaned_data.get('ref'),
                                      equipment=equipment,
                                      dimension_type=form.cleaned_data.get('dimension_type'))
            calibration.save()
            messages.success(request, 'Calibration was added successfully')
            return HttpResponseRedirect(reverse("view_equipment", kwargs={'equipment_id': equipment_id}))
        else:
            messages.warning(request, 'Calibration was not added!!!')
    else:
        form = CalibrationForm()

    return render(request, 'add_calibration.html', {'form': form, 'equipment': equipment, 'equipment_id': equipment_id})


def view_calibration(request, equipment_id, calib_id):
    try:
        calibration = Calibration.objects.get(pk=calib_id)
    except Calibration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_equipment", kwargs={'equipment_id': equipment_id}))

    if request.method == 'GET':
        form = CalibrationForm(instance=calibration)
    elif request.method == 'POST':
        form = CalibrationForm(request.POST, instance=calibration)
        if form.is_valid():
            form.save()
            messages.success(request, 'Calibration was added successfully')
            return HttpResponseRedirect(reverse("view_equipment", kwargs={'equipment_id': equipment_id}))
        else:
            messages.warning(request, 'Calibration wasnt edited successfully!!!')

    return render(request, 'view_calibration.html', {'form': form, 'equipment_id': equipment_id, 'calib_id': calib_id, 'calibration': calibration})


def delete_calibration(request):
    if request.is_ajax and request.method == 'POST':
        calib = Calibration.objects.get(pk=request.POST["id"])
        try:
            calib.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Calibration was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Calibration!')
    return HttpResponse("not ok")


# ==================================== CONFIGURATION OF EQUIPMENTS TO CONF PERIODS ====================================


def add_equipment_config(request, tower_id, period_id):

    try:
        Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    try:
        conf_period = PeriodConfiguration.objects.get(pk=period_id)
    except PeriodConfiguration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    if request.method == 'POST':
        form = EquipmentConfigForm(request.POST)

        if form.is_valid():
            if EquipmentConfig.objects.filter(conf_period=period_id, calibration=form.cleaned_data.get('calibration')):
                messages.error(request, 'This Period Configuration already have that Equipment/Calibration!!!')
            else:
                equipment_config = EquipmentConfig(height=form.cleaned_data.get('height'),
                                                   height_label=form.cleaned_data.get('height_label'),
                                                   orientation=form.cleaned_data.get('orientation'),
                                                   boom_length=form.cleaned_data.get('boom_length'),
                                                   boom_var_height=form.cleaned_data.get('boom_var_height'),
                                                   calibration=form.cleaned_data.get('calibration'),
                                                   conf_period=conf_period)
                equipment_config.save()
                messages.success(request, 'Equipment Configuration was added successfully')
                return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))
        else:
            messages.warning(request, 'Equipment Configuration was not added!!!')
    else:
        form = EquipmentConfigForm()

    return render(request, 'add_equipment_config.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'conf_period': conf_period})


def view_equipment_config(request, tower_id, period_id, equi_conf_id):

    try:
        Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    try:
        PeriodConfiguration.objects.get(pk=period_id)
    except PeriodConfiguration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    try:
        equipment_config = EquipmentConfig.objects.get(pk=equi_conf_id)
    except EquipmentConfig.DoesNotExist:
        return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))

    if request.method == 'GET':
        form = EquipmentConfigForm(instance=equipment_config)
    else:
        form = EquipmentConfigForm(request.POST, instance=equipment_config)
        if form.is_valid():
            if EquipmentConfig.objects.filter(conf_period=period_id, calibration=form.cleaned_data.get('calibration')).exclude(pk=equi_conf_id):
                messages.error(request, 'This Period Configuration already have that Equipment/Calibration!!!')
            else:
                form.save()
                messages.success(request, 'Equipment Configuration was edited successfully')
                return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))
        else:
            messages.warning(request, 'Equipment Configuration wasnt edited successfully!!!')

    classification = ClassificationPeriod.objects.filter(equipment_configuration=equipment_config)
    dimension = Dimension.objects.filter(equipment_configuration=equipment_config)

    return render(request, 'view_equipment_config.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id, 'equipment_config': equipment_config, 'classification': classification, 'dimension': dimension})


def delete_equipment_config(request):
    if request.is_ajax and request.method == 'POST':
        equipment_config = EquipmentConfig.objects.get(pk=request.POST["id"])
        try:
            equipment_config.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Equipment Configuration was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Equipment Configuration!')
    return HttpResponse("not ok")


# ========================================= STATUS =========================================


def add_status(request):
    if request.method == 'POST':
        form = StatusForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Status added!')
            return HttpResponseRedirect(reverse("list_status"))
        else:
            messages.warning(request, 'Status not added!!!')
    else:
        form = StatusForm()

    return render(request, 'add_status.html', {'form': form})


def add_type_status(request):
    data = dict()

    if request.method == 'POST':
        form = StatusForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = StatusForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_status.html', context, request=request)
    return JsonResponse(data)


def list_status(request):
    status = Status.objects.all()

    return render(request, 'list_status.html', {'status': status})


def view_status(request, status_id):
    try:
        status = Status.objects.get(pk=status_id)
    except Status.DoesNotExist:
        return HttpResponseRedirect(reverse("list_status"))

    if request.method == 'GET':
        form = StatusForm(instance=status)
    else:
        form = StatusForm(request.POST, instance=status)
        if form.is_valid():
            form.save()
            messages.success(request, 'Status was edited successfully')
            return HttpResponseRedirect(reverse("list_status"))
        else:
            messages.warning(request, 'Status wasnt edited!!!')

    return render(request, 'view_status.html', {'form': form, 'status_id': status_id, 'status': status})


def delete_status(request):
    if request.is_ajax and request.method == 'POST':
        status = Status.objects.get(pk=request.POST["id"])
        try:
            status.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Status was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Status!')
    return HttpResponse("not ok")


# ========================================= CLASSIFICATION PERIODS =========================================


def add_classification_period(request, tower_id, period_id, equi_conf_id):
    try:
        Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    try:
        period = PeriodConfiguration.objects.get(pk=period_id)
    except PeriodConfiguration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    try:
        equipment_config = EquipmentConfig.objects.get(pk=equi_conf_id)
    except EquipmentConfig.DoesNotExist:
        return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))

    if request.method == 'POST':
        form = ClassificationPeriodForm(request.POST)

        if form.is_valid():
            if form.cleaned_data.get('begin_date') < period.begin_date or form.cleaned_data.get('end_date') > period.end_date:
                messages.error(request, 'Data must be between the Period Configuration')
            else:
                classification = form.save(commit=False)
                classification.user = request.user
                classification.equipment_configuration = equipment_config
                classification.save()
                messages.success(request, 'Classification added!')
                return HttpResponseRedirect(reverse("view_equipment_config", kwargs={'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id}))
        else:
            messages.warning(request, 'Classification not added!!!')
    else:
        cla = ClassificationPeriod(begin_date=period.begin_date, end_date=period.end_date)
        form = ClassificationPeriodForm(instance=cla)

    return render(request, 'add_classification_period.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id, 'period': period, 'equipment_config': equipment_config})


def view_classification_period(request, tower_id, period_id, equi_conf_id, classification_id):
    try:
        Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    try:
        period = PeriodConfiguration.objects.get(pk=period_id)
    except PeriodConfiguration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    try:
        equipment_config = EquipmentConfig.objects.get(pk=equi_conf_id)
    except EquipmentConfig.DoesNotExist:
        return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))

    try:
        classification = ClassificationPeriod.objects.get(pk=classification_id)
    except ClassificationPeriod.DoesNotExist:
        return HttpResponseRedirect(reverse("view_equipment_config", kwargs={'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id}))

    if request.method == 'GET':
        form = ClassificationPeriodForm(instance=classification)
    else:
        form = ClassificationPeriodForm(request.POST, instance=classification)
        if form.is_valid():
            if form.cleaned_data.get('begin_date') < period.begin_date or form.cleaned_data.get('end_date') > period.end_date:
                messages.error(request, 'Data must be between the Period Configuration')
            else:
                classification = form.save(commit=False)
                classification.user = request.user
                classification.equipment_configuration = equipment_config
                classification.save()
                messages.success(request, 'Classification was edited successfully')
                return HttpResponseRedirect(reverse("view_equipment_config", kwargs={'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id}))
        else:
            messages.warning(request, 'Classification wasnt edited successfully!!!')

    return render(request, 'view_classification_period.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id, 'classification_id': classification_id, 'classification': classification})


def delete_classification_period(request):
    if request.is_ajax and request.method == 'POST':
        classification = ClassificationPeriod.objects.get(pk=request.POST["id"])
        try:
            classification.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Classification Period was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Classification Period!')
    return HttpResponse("not ok")


# ========================================= DIMENSIONS TYPES =========================================


def add_dimension_type(request):
    if request.method == 'POST':
        form = DimensionTypeForm(request.POST)

        if form.is_valid():
            form.save()
            messages.success(request, 'Dimension type added!')
            return HttpResponseRedirect(reverse("list_dimensions_type"))
        else:
            messages.warning(request, 'There is already a Dimension type with that values')
    else:
        form = DimensionTypeForm()

    return render(request, 'add_dimension_type.html', {'form': form})


def add_type_dimension(request):
    data = dict()

    if request.method == 'POST':
        form = DimensionTypeForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = DimensionTypeForm()

    context = {'form': form}
    data['html_form'] = render_to_string('add_type_dimension.html', context, request=request)
    return JsonResponse(data)


def list_dimensions_type(request):
    dimensions = DimensionType.objects.all()

    return render(request, 'list_dimensions_type.html', {'dimensions': dimensions})


def view_dimension_type(request, dimension_type_id):
    try:
        dimension_type = DimensionType.objects.get(pk=dimension_type_id)
    except DimensionType.DoesNotExist:
        return HttpResponseRedirect(reverse("list_dimensions_type"))

    if request.method == 'GET':
        form = DimensionTypeForm(instance=dimension_type)
    else:
        form = DimensionTypeForm(request.POST, instance=dimension_type)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dimension type was edited successfully')
            return HttpResponseRedirect(reverse("list_status"))
        else:
            messages.warning(request, 'Dimension type wasnt edited!!! Maybe there is already a Dimension type with that values')

    return render(request, 'view_dimension_type.html', {'form': form, 'dimension_type_id': dimension_type_id, 'dimension_type': dimension_type})


def delete_dimension_type(request):
    if request.is_ajax and request.method == 'POST':
        status = DimensionType.objects.get(pk=request.POST["id"])
        try:
            status.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Dimension Type was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Dimension Type!')
    return HttpResponse("not ok")


# ========================================= DIMENSION =========================================


def add_dimension(request, tower_id, period_id, equi_conf_id):
    try:
        Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    try:
        period = PeriodConfiguration.objects.get(pk=period_id)
    except PeriodConfiguration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    try:
        equipment_config = EquipmentConfig.objects.get(pk=equi_conf_id)
    except EquipmentConfig.DoesNotExist:
        return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))

    if request.method == 'POST':
        form = DimensionForm(request.POST)

        if form.is_valid():
            dimension = form.save(commit=False)
            dimension.equipment_configuration = equipment_config
            dimension.save()
            messages.success(request, 'Dimension added!')
            return HttpResponseRedirect(reverse("view_equipment_config", kwargs={'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id}))
        else:
            messages.warning(request, 'Dimension not added!!!')
    else:
        form = DimensionForm()

    return render(request, 'add_dimension.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id, 'period': period, 'equipment_config': equipment_config})


def view_dimension(request, tower_id, period_id, equi_conf_id, dimension_id):
    try:
        Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    try:
        PeriodConfiguration.objects.get(pk=period_id)
    except PeriodConfiguration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    try:
        equipment_config = EquipmentConfig.objects.get(pk=equi_conf_id)
    except EquipmentConfig.DoesNotExist:
        return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))

    try:
        dimension = Dimension.objects.get(pk=dimension_id)
    except Dimension.DoesNotExist:
        return HttpResponseRedirect(reverse("view_equipment_config", kwargs={'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id}))

    if request.method == 'GET':
        form = DimensionForm(instance=dimension)
    else:
        form = DimensionForm(request.POST, instance=dimension)
        if form.is_valid():
            dimension = form.save(commit=False)
            dimension.equipment_configuration = equipment_config
            dimension.save()
            messages.success(request, 'Dimension was edited successfully')
            return HttpResponseRedirect(reverse("view_equipment_config", kwargs={'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id}))
        else:
            messages.warning(request, 'Dimension wasnt edited successfully!!!')

    return render(request, 'view_dimension.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id, 'dimension_id': dimension_id, 'dimension': dimension})


def delete_dimension(request):
    if request.is_ajax and request.method == 'POST':
        dimension = Dimension.objects.get(pk=request.POST["id"])
        try:
            dimension.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Dimension was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Dimension!')
    return HttpResponse("not ok")


# ========================================= COMMENT =========================================


def add_comment_classification(request, tower_id, period_id, equi_conf_id, classification_id):
    try:
        Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    try:
        period = PeriodConfiguration.objects.get(pk=period_id)
    except PeriodConfiguration.DoesNotExist:
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    try:
        equipment_config = EquipmentConfig.objects.get(pk=equi_conf_id)
    except EquipmentConfig.DoesNotExist:
        return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))

    try:
        classification = ClassificationPeriod.objects.get(pk=classification_id)
    except EquipmentConfig.DoesNotExist:
        return HttpResponseRedirect(reverse("view_conf_period", kwargs={'tower_id': tower_id, 'period_id': period_id}))

    if request.method == 'POST':
        form = CommentClassificationForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.classification = classification
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return HttpResponseRedirect(reverse("view_equipment_config", kwargs={'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id}))
        else:
            messages.warning(request, 'Comment not added!!!')
    else:
        comment = CommentClassification(begin_date=period.begin_date, end_date=period.end_date)
        form = CommentClassificationForm(instance=comment)

    return render(request, 'add_comment_classification.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'equi_conf_id': equi_conf_id, 'classification_id': classification_id, 'classification': classification})


def add_comment_tower(request, tower_id):
    try:
        tower = Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    if request.method == 'POST':
        form = CommentTowerForm(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.tower = tower
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment added!')
            return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))
        else:
            messages.warning(request, 'Comment not added!!!')
    else:
        form = CommentTowerForm()

    return render(request, 'add_comment_tower.html', {'form': form, 'tower_id': tower_id, 'tower': tower})


def view_comment(request, tower_id, comment_id, type):

    if type == 'classification':
        try:
            comment = CommentClassification.objects.get(pk=comment_id)
        except CommentClassification.DoesNotExist:
            return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))
    elif type == 'tower':
        try:
            comment = CommentTower.objects.get(pk=comment_id)
        except CommentTower.DoesNotExist:
            return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

    if request.method == 'GET':
        if type == 'classification':
            form = CommentClassificationForm(instance=comment)
        elif type == 'tower':
            form = CommentTowerForm(instance=comment)
    else:
        if type == 'classification':
            form = CommentClassificationForm(request.POST, instance=comment)
        elif type == 'tower':
            form = CommentTowerForm(request.POST, instance=comment)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.save()
            messages.success(request, 'Comment was edited successfully')
            return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))
        else:
            messages.warning(request, 'Comment wasnt edited successfully!!!')

    return render(request, 'view_comment.html', {'form': form, 'tower_id': tower_id, 'comment_id': comment_id, 'type': type})


def delete_comment(request):
    if request.is_ajax and request.method == 'POST':
        if request.POST["typex"] == 'classification':
            obj = CommentClassification.objects.get(pk=request.POST["id"])
        elif request.POST["typex"] == 'tower':
            obj = CommentTower.objects.get(pk=request.POST["id"])
        try:
            obj.delete()
        except (TypeError, IntegrityError) as e:
            messages.error(request, e.__cause__)
            return HttpResponse("not ok")

        messages.success(request, 'Comment was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Comment!')
    return HttpResponse("not ok")

# ========================================= AUTOCOMPLETES =========================================


class EquipmentTypeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = EquipmentType.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class EquipmentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Equipment.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(sn__icontains=self.q)

        return qs


class TowerAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Tower.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(code__icontains=self.q)

        return qs


class GroupAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = UserGroupType.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class UserAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = MyUser.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(full_name__icontains=self.q)

        return qs


class ModelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = EquipmentCharacteristic.objects.all().order_by('-id')

        type = self.forwarded.get('type', None)

        if type:
            qs = qs.filter(type=type)

        if self.q:
            qs = qs.filter(QD(type__name__icontains=self.q) | QD(model__icontains=self.q) | QD(version__icontains=self.q))

        return qs


class CalibrationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Calibration.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(equipment__sn__icontains=self.q)

        return qs


class StatusAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Status.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(code__icontains=self.q)

        return qs


class UnitAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = UnitType.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class StatisticAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = StatisticType.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class MetricAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = MetricType.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class ComponentAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = ComponentType.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs


class DimensionTypeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = DimensionType.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(QD(unit__name__icontains=self.q) | QD(statistic__name__icontains=self.q) | QD(metric__name__icontains=self.q) | QD(component__name__icontains=self.q))

        return qs


class CommentTowerTypeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):

        qs = CommentTower.objects.all().order_by('-id')

        begin_date = self.forwarded.get('begin_date', None)
        end_date = self.forwarded.get('end_date', None)
        tower_id = self.forwarded.get('tower', None)

        if begin_date and end_date:
            begin_date = get_date(begin_date)
            end_date = get_date(end_date)
            qs = qs.filter(QD(tower__pk=tower_id) & (QD(begin_date__range=(begin_date, end_date)) | QD(end_date__range=(begin_date, end_date))))
        if self.q:
            qs = qs.filter(tower__icontains=self.q)

        return qs


class CommentClassificationTypeAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        tower_id = self.forwarded.get('tower', None)

        periods = PeriodConfiguration.objects.filter(tower=tower_id).order_by('-begin_date')

        # To get comments on each classification period for this tower
        equipment_configuration = EquipmentConfig.objects.filter(conf_period__in=periods)
        classifications = ClassificationPeriod.objects.filter(equipment_configuration__in=equipment_configuration)
        comments_classification = CommentClassification.objects.filter(classification__in=classifications).order_by('-begin_date')

        qs = comments_classification

        begin_date = self.forwarded.get('begin_date', None)
        end_date = self.forwarded.get('end_date', None)
        classifications = self.forwarded.get('classifications', None)

        if begin_date and end_date:
            begin_date = get_date(begin_date)
            end_date = get_date(end_date)
            qs = qs.filter((QD(begin_date__range=(begin_date, end_date)) | QD(end_date__range=(begin_date, end_date))))
        if self.q:
            qs = qs.filter(tower__icontains=self.q)

        return qs


class AffiliationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = AffiliationType.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
