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
from .aux_functions import parsedate, check_if_period_is_valid, check_if_period_is_valid_2, get_date, get_date_secs, get_color_index
from formtools.wizard.views import SessionWizardView
from dal import autocomplete

from django_pandas.io import *
from graphos.sources.simple import SimpleDataSource
from graphos.renderers.gchart import LineChart
from graphos.renderers.morris import LineChart as LineChartMorris
from graphos.renderers.highcharts import LineChart as LineChartHIGH

from graphos.sources.model import ModelDataSource
from graphos.sources.csv_file import CSVDataSource
from chartjs.views.lines import BaseLineChartView, HighchartPlotLineChartView
from pymongo import ASCENDING as PYASCENDING
from pymongo import DESCENDING as PYDESCENDING
from django.core import serializers

import time, re, io, json, pytz, random, csv, os, glob, gc
import numpy as np
from faker import Faker
from django.views.generic import View
from .utils import render_to_pdf
from django.template import loader


class GeneratePdf(View):
    def get(self, request, *args, **kwargs):
        data = {
            "invoice_id": 123,
            "customer_name": "John Cooper",
            "amount": 1399.99,
            "today": "Today",
        }
        # template = loader.get_template('pdf/pdf.html')
        # return HttpResponse(template.render(data, request))
        pdf = render_to_pdf('pdf/pdf.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

    # def get(self, request, *args, **kwargs):
    #     template = loader.get_template('pdf/pdf.html')
    #     context = {
    #         "invoice_id": 123,
    #         "customer_name": "John Cooper",
    #         "amount": 1399.99,
    #         "today": "Today",
    #     }
    #     html = template.render(context)
    #     pdf = render_to_pdf('pdf/pdf.html', context)
    #     if pdf:
    #         response = HttpResponse(pdf, content_type='application/pdf')
    #         filename = "Invoice_%s.pdf" % ("12341231")
    #         content = "inline; filename='%s'" % (filename)
    #         download = request.GET.get("download")
    #         if download:
    #             content = "attachment; filename='%s'" % (filename)
    #         response['Content-Disposition'] = content
    #         return response
    #     return HttpResponse("Not found")

# ========================================= MAGIC =========================================


def get_obj_or_404_2(klass, *args, **kwargs):
    try:
        return klass.objects.get(*args, **kwargs)
    except klass.DoesNotExist:
        raise Http404


def index(request):

    if request.user.id is None:
        form = LoginForm()
        return render(request, 'home.html', {'form': form})
    else:
        users = MyUser.objects.all().order_by('-id')[:5]

        if request.user.is_client or (request.user.is_manager and not request.user.is_staff):
            now = datetime.now(pytz.utc)
            user_towers = UserTowerDates.objects.filter(user__pk=request.user.pk, begin_date__lte=now,
                                                        end_date__gte=now).values_list('tower', flat=True)
            stations = Tower.objects.filter(pk__in=user_towers).distinct()[:5]
        else:
            stations = Tower.objects.all().order_by('-id')[:5]

        context = {'users': users, 'stations': stations}
        return render(request, 'home.html', context)


def import_raw_data(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))
    context = {}
    return render(request, 'import_raw_data.html', context)


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
    if not request.user.is_staff:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if not request.user.is_staff:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if not request.user.is_staff:
        messages.error(request, 'You dont have access to this page')
        return HttpResponse("not ok")

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
    if not request.user.is_staff:
        messages.error(request, 'You dont have access to this page')
        return HttpResponse("not ok")

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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client or (request.user.is_manager and not request.user.is_staff):
        now = datetime.now(pytz.utc)
        user_towers = UserTowerDates.objects.filter(user__pk=request.user.pk, begin_date__lte=now,
                                                    end_date__gte=now).values_list('tower', flat=True)
        towers = Tower.objects.filter(pk__in=user_towers).distinct()
    else:
        towers = Tower.objects.all().order_by('-id')

    # towers = Tower.objects.all()

    return render(request, 'list_towers.html', {'towers': towers})


def view_tower(request, tower_id):
    try:
        tower = Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    if request.user.is_client or (request.user.is_manager and not request.user.is_staff):
        now = datetime.now(pytz.utc)
        to_check = UserTowerDates.objects.filter(user__pk=request.user.pk, begin_date__lte=now, end_date__gte=now, tower=tower)
        if not to_check:
            messages.error(request, 'You dont have access to this page')
            return HttpResponseRedirect(reverse("list_towers"))

    if request.method == 'GET':
        form = TowerForm(instance=tower)
    elif request.method == 'POST':

        if request.user.is_client:
            messages.error(request, 'You dont have access to this page')
            return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    equipments = Equipment.objects.all()

    return render(request, 'list_equipments.html', {'equipments': equipments})


def add_equipment(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))
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


def add_calib_equip(request):
    data = dict()

    if request.method == 'POST':
        form_eq = EquipmentForm(request.POST)
        form_calib = CalibrationForm(request.POST)
        if form_eq.is_valid() and form_calib.is_valid():
            equipment = form_eq.save(commit=False)
            equipment.save()
            calib = form_calib.save(commit=False)
            calib.equipment = equipment
            calib.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form_eq = EquipmentForm()
        form_calib = CalibrationForm()

    context = {'form_eq': form_eq, 'form_calib': form_calib}
    data['html_form'] = render_to_string('add_calib_equip.html', context, request=request)
    return JsonResponse(data)


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
        form = MetricTypeForm(request.POST)
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
        else:
            data['form_is_valid'] = False
    else:
        form = MetricTypeForm()

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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


# ========================================= CONFIGURATION OF PERIODS TO TOWERS =========================================


def add_conf_period(request, tower_id):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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

    return render(request, 'add_conf_period.html', {'form': form, 'tower': tower, 'tower_id': tower_id})


def view_conf_period(request, period_id, tower_id):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("view_tower", kwargs={'tower_id': tower_id}))

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

    for c in configurations:
        dimension = Dimension.objects.filter(equipment_configuration=c)
        c.dimension = dimension
        if not c.slope_dl:
            c.slope_dl = 1
        slope_f = c.calibration.slope/c.slope_dl
        c.slope_f = slope_f
        if not c.offset_dl:
            c.offset_dl = 1
        offset_f = c.calibration.offset-(c.offset_dl*slope_f)
        c.offset_f = offset_f

    return render(request, 'view_conf_period.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'period': period, 'configurations': configurations})


def delete_conf_period(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
                                                   offset_dl=form.cleaned_data.get('offset_dl'),
                                                   slope_dl=form.cleaned_data.get('slope_dl'),
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    status = Status.objects.all()

    return render(request, 'list_status.html', {'status': status})


def view_status(request, status_id):

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    dimensions = DimensionType.objects.all()

    return render(request, 'list_dimensions_type.html', {'dimensions': dimensions})


def view_dimension_type(request, dimension_type_id):

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
            return HttpResponseRedirect(reverse("list_dimensions_type"))
        else:
            messages.warning(request, 'Dimension type wasnt edited!!! Maybe there is already a Dimension type with that values')

    return render(request, 'view_dimension_type.html', {'form': form, 'dimension_type_id': dimension_type_id, 'dimension_type': dimension_type})


def delete_dimension_type(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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

    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

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
    if request.user.is_client:
        messages.error(request, 'You dont have access to that action')
        return HttpResponse("not ok")
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
            qs = qs.filter(QD(sn__icontains=self.q) | QD(model__type__name__icontains=self.q))

        return qs


class TowerAutocomplete(autocomplete.Select2QuerySetView):

    def get_queryset(self):
        if self.request.user.is_client or (self.request.user.is_manager and not self.request.user.is_staff):
            now = datetime.now(pytz.utc)
            user_towers = UserTowerDates.objects.filter(user__pk=self.request.user.pk, begin_date__lte=now,
                                                        end_date__gte=now).values_list('tower', flat=True)
            qs = Tower.objects.filter(pk__in=user_towers).distinct().order_by('-id')
        else:
            qs = Tower.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(code_inegi__icontains=self.q)

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
            qs = qs.filter(QD(username__icontains=self.q) | QD(full_name__icontains=self.q))

        return qs


class ModelAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = EquipmentCharacteristic.objects.all().order_by('-id')

        type = self.forwarded.get('type', None)

        if type:
            qs = qs.filter(type=type)

        if self.q:
            qs = qs.filter(QD(type__name__icontains=self.q) | QD(manufacturer__icontains=self.q) | QD(model__icontains=self.q) | QD(version__icontains=self.q))

        return qs


class CalibrationAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Calibration.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(QD(ref__icontains=self.q) | QD(equipment__sn__icontains=self.q))

        return qs


class StatusAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Status.objects.all().order_by('-id')

        if self.q:
            qs = qs.filter(QD(name__icontains=self.q) | QD(code__icontains=self.q))

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


class TowerConfPeriodsAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = PeriodConfiguration.objects.none()
        tower = self.forwarded.get('tower', None)
        begin_date = self.forwarded.get('begin_date', None)
        end_date = self.forwarded.get('end_date', None)

        if tower and begin_date and end_date:
            begin_date = get_date_secs(begin_date)
            end_date = get_date_secs(end_date)

            # qs = PeriodConfiguration.objects.filter((QD(begin_date__range=(begin_date, end_date)) | QD(end_date__range=(begin_date, end_date)))).order_by('-id')
            qs = PeriodConfiguration.objects.filter((QD(begin_date__lte=begin_date) & QD(end_date__gte=begin_date)) | (QD(begin_date__lte=end_date) & QD(end_date__gte=end_date))).order_by('-id')
            qs = qs.filter(tower=tower).distinct()
            if qs:
                qs = EquipmentConfig.objects.filter(conf_period__in=qs).order_by('calibration').distinct('calibration')
                # qs = EquipmentConfig.objects.filter(conf_period__in=qs).values_list('calibration', flat=True)
                # qs = Calibration.objects.filter(pk__in=qs).distinct().values_list('equipment', flat=True)
                # qs = Equipment.objects.filter(pk__in=qs).distinct()
                # print(qs)

        if self.q:
            qs = qs.filter(QD(calibration__equipment__model__type__name__icontains=self.q) | QD(height_label__icontains=self.q))

        return qs


# ========================================= CHARTS =========================================


def dt2epoch(value):
    epoch = int(time.mktime(value.timetuple()) * 1000)
    return epoch


def data_visualization(request):
    form_tower = TowersDataVForm()
    form_comment = CommentClassificationChartForm()
    context = {'form_tower': form_tower, 'form_comment': form_comment}
    return render(request, 'data_visualization.html', context)


class LineChartJson(BaseLineChartView):
    def get_labels(self):
        """Return 7 labels for the x-axis."""
        return ["January", "February", "March", "April", "May", "June", "July"]

    def get_providers(self):
        """Return names of datasets."""
        return ["Central", "Eastside", "Westside"]

    def get_data(self):
        """Return 3 datasets to plot."""

        return [[75, 44, 92, 11, 44, 95, 35],
                [41, 92, 18, 3, 73, 87, 92],
                [87, 21, 94, 3, 90, 13, 65]]


class LineHighchartRawData(HighchartPlotLineChartView):

    def __init__(self):
        self.xdata = []
        self.ydata = []
        self.indexs = []

    def get(self, request, *args, **kwargs):
        tower_id = self.request.GET.get('tower_id', '')
        begin_date = self.request.GET.get('begin_date', '')
        end_date = self.request.GET.get('end_date', '')
        print("GET - tower_id: ", tower_id)

        tower = Tower.objects.get(pk=tower_id)

        if not (begin_date and end_date):
            end_date = datetime.now(pytz.utc)
            begin_date = end_date - timedelta(days=30)
        else:
            begin_date = get_date(begin_date)
            end_date = get_date(end_date)

        # qs = DataSetPG.objects.filter(QD(tower_code=tower)).order_by('time_stamp')

        qs = DataSetPG.objects.filter(QD(tower_code=tower) & QD(time_stamp__range=(begin_date, end_date))).values('time_stamp', 'value').order_by('time_stamp')

        conf_periods = PeriodConfiguration.objects.filter(QD(tower=tower) & QD(begin_date__gte=begin_date, end_date__lte=end_date)).order_by('begin_date')
        # print(conf_periods)
        df = read_frame(qs)

        new_df = df.value.apply(lambda x: pd.Series(str(x).split(",")))
        if not new_df.empty:
            new_cols = ["Undefined"+str(x+1) for x in list(new_df.columns)]
            new_df.columns = new_cols
        df = pd.concat([df, new_df], axis=1, sort=False)
        del df['value']

        new_df = pd.DataFrame()
        # new_df = []

        # Need to change columns name and get the correct order from the columns to read in each period in Dimensions
        for i, cf in enumerate(conf_periods):
            if i == 0:
                new_df = pd.concat([new_df, df[(df['time_stamp'] < cf.begin_date)]], sort=False)
                # new_df.append(df[(df['time_stamp'] < cf.begin_date)])

            temp_df = df[(df['time_stamp'] >= cf.begin_date) & (df['time_stamp'] <= cf.end_date)]

            equipments_conf = EquipmentConfig.objects.filter(conf_period=cf)
            for eq in equipments_conf:
                dim = Dimension.objects.filter(equipment_configuration=eq)
                for d in dim:
                    # String to show in df header
                    name = eq.calibration.equipment.model.type.initials + '@' + str(eq.height_label) + d.dimension_type.statistic.name
                    column = d.column
                    temp_df = temp_df.rename(columns={"Undefined"+str(column): name})
                    if not temp_df.empty:
                        temp_df[name] = temp_df[name].astype(float)
                        # We need to get the original value back (raw_data-OffLogger)-SloLogger
                        default = (temp_df[name] - (float(eq.offset_dl)))/float(eq.slope_dl)
                        # Then multiply default by SloCalib and sum OffCalib
                        final = (default*(float(eq.calibration.slope)))+float(eq.calibration.offset)
                        temp_df[name] = final
            if not temp_df.empty:
                # new_df.append(temp_df)
                new_df = pd.concat([new_df, temp_df], sort=False)

            if i == len(conf_periods)-1:
                new_df = pd.concat([new_df, df[(df['time_stamp'] > cf.end_date)]], sort=False)
                # new_df.append(df[(df['time_stamp'] > cf.end_date)])

        # replace the new_df to the df, if new_df empty, means no periods and dimensions was configured yet.
        if not df.empty and len(new_df) > 0:
            # df = pd.concat(new_df, axis=0, sort=False)
            df = new_df
        # Delete columns with empty values - Columns that had periods and dimensions
        df.dropna(axis=1, how='all', inplace=True)

        # Convert all other columns rather than time_stamp to float
        for d in df:
            if df[d].name is not 'time_stamp':
                df[d] = df[d].astype(float).tolist()

        # Fill open spaces with a freq of 10min with NaN's
        if not df.empty:
            df = df.set_index('time_stamp')
            i = df.index[0]
            f = df.index[-1]
            continuousrange = pd.date_range(i, f, freq=('10T'))
            df = df.reindex(index=continuousrange)

        # Replace all NaN with None
        df = df.where((pd.notnull(df)), None)

        # Convert data to unix_time
        eixo_x = df.index.astype(np.int64)//10**6
        self.xdata = eixo_x.tolist()

        for d in df:
            if df[d].name is not 'time_stamp':
                self.ydata.append(df[d].values.tolist())
                self.indexs.append(df[d].name)

        self.title = 'Data Visualization'
        self.y_axis_title = 'Values'

        # special - line charts credits are personalized
        self.credits = {
            'enabled': True,
            'href': 'http://google.com',
            'text': 'INEGI Team',
        }

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_labels(self):
        """Return labels."""
        return self.xdata

    def get_providers(self):
        """Return names of datasets."""
        return self.indexs

    def get_data(self):
        """Return dataset to plot."""
        return self.ydata


class LineHighchartJsonTESTS(HighchartPlotLineChartView):

    def __init__(self):
        self.xdata = []
        self.ydata = []
        self.indexs = []

    def get(self, request, *args, **kwargs):
        tower_id = self.request.GET.get('tower_id', '')
        begin_date = self.request.GET.get('begin_date', '')
        end_date = self.request.GET.get('end_date', '')
        typeX = self.request.GET.get('typeX', '')
        print("GET - tower_id: ", tower_id)

        tower = Tower.objects.get(pk=tower_id)

        if not (begin_date and end_date):
            end_date = datetime.now(pytz.utc)
            begin_date = end_date - timedelta(days=30)
        else:
            begin_date = get_date(begin_date)
            end_date = get_date(end_date)

        df = pd.DataFrame()
        if typeX == 'pg':
            # qs = DataSetPG.objects.filter(QD(tower_code=tower)).order_by('time_stamp')

            qs = DataSetPG.objects.filter(QD(tower_code=tower.code_inegi) & QD(time_stamp__range=(begin_date, end_date))).order_by('time_stamp').values('time_stamp', 'value')

            df = read_frame(qs)

        elif typeX == 'mo':
            qs = DataSetMongoPyMod.objects.raw({'tower_code': tower.code_inegi, 'time_stamp': {'$gte': begin_date, '$lte': end_date}})
            qs = qs.order_by([('time_stamp', PYASCENDING)])

            rows_list = []
            for ds in qs:
                dict1 = {'time_stamp': str(ds.time_stamp), 'value': str(ds.value)}
                rows_list.append(dict1)

            df = pd.DataFrame(rows_list, columns=['time_stamp', 'value'])
            # df = df.sort_values(by='time_stamp')
            # df = df.reset_index(drop=True)
            df['time_stamp'] = pd.to_datetime(df['time_stamp'])

        elif typeX == 'in':
            begin_date = begin_date.strftime("%Y-%m-%dT%H:%M:%SZ")
            end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

            qs = INFLUXCLIENT.query("select * FROM '"+tower.code_inegi+"'where time >= '"+begin_date+"' and time <= '"+end_date+"' order by time")
            qs = list(qs)[0]

            rows_list = []
            for el in qs:
                dict1 = {'time_stamp': el.get('time'), 'value': el.get('value')}
                rows_list.append(dict1)

            df = pd.DataFrame(rows_list, columns=['time_stamp', 'value'])
            # df = df.sort_values(by='time_stamp')
            # df = df.reset_index(drop=True)
            df['time_stamp'] = pd.to_datetime(df['time_stamp'])

        elif typeX == 'files':
            rows_list = []
            path = "./files/raw_data/" + tower.code_inegi + "/"
            for filename in glob.glob(os.path.join(path, '*.row')):
                with open(filename, 'r') as f:
                    for i, line in enumerate(f):
                        line = line.rstrip()
                        try:
                            if line.strip()[-1] is ',':
                                line = line.strip()[:-1]
                        except IndexError:
                            print("Problem with file")
                            pass

                        mylist = line.split(",", 3)

                        time_value, flag_date = parsedate(request, f, mylist, i)

                        if flag_date:
                            print("Problem with date at :" + str(i))
                        values = mylist[3]
                        tower_code = mylist[0]
                        tower_code = tower_code.lower()
                        if begin_date <= time_value and end_date >= time_value:
                            dict1 = {'time_stamp': str(time_value), 'value': str(values)}
                            rows_list.append(dict1)

            df = pd.DataFrame(rows_list, columns=['time_stamp', 'value'])
            df = df.sort_values(by='time_stamp')
            df = df.reset_index(drop=True)
            df['time_stamp'] = pd.to_datetime(df['time_stamp'])

        if not df.empty:
            new_df = df.value.apply(lambda x: pd.Series(str(x).split(",")))
            del df['value']
            df = pd.concat([df, new_df], axis=1, sort=False)

        # Convert all other columns rather than time_stamp to float
        for d in df:
            if df[d].name != 'time_stamp':
                df[d] = df[d].astype(float).tolist()

        # Fill open spaces with a freq of 10min with NaN's
        if not df.empty:
            df = df.set_index('time_stamp')
            i = df.index[0]
            f = df.index[-1]
            continuousrange = pd.date_range(i, f, freq=('10T'))
            df = df.reindex(index=continuousrange)

        # Replace all NaN with None
        df = df.where((pd.notnull(df)), None)

        # Convert data to unix_time
        eixo_x = df.index.astype(np.int64) // 10 ** 6
        self.xdata = eixo_x.tolist()

        # print(df)
        for d in df:
            if df[d].name != 'time_stamp':
                self.ydata.append(df[d].values.tolist())
                self.indexs.append(df[d].name)

        self.title = 'Data Visualization'
        self.y_axis_title = 'Values'

        # special - line charts credits are personalized
        self.credits = {
            'enabled': True,
            'href': 'http://google.com',
            'text': 'INEGI Team',
        }

        context = self.get_context_data(**kwargs)
        return self.render_to_response(context)

    def get_labels(self):
        """Return labels."""
        return self.xdata

    def get_providers(self):
        """Return names of datasets."""
        return self.indexs

    def get_data(self):
        """Return dataset to plot."""
        return self.ydata


def classify_from_charts(request):
    begin_date = get_date_secs(request.GET.get('begin_date', ''))
    end_date = get_date_secs(request.GET.get('end_date', ''))
    tower_id = request.GET.get('tower_id', '')
    equipments_config = request.GET.getlist('equipments', '')
    status = request.GET.get('status', '')
    status = Status.objects.get(pk=status)
    internal_comment = request.GET.get('internal_comment', '')
    compact_comment = request.GET.get('compact_comment', '')
    detailed_comment = request.GET.get('detailed_comment', '')

    print("GET - Begin: ", begin_date)
    print("GET - End: ", end_date)
    print("GET - tower_id: ", tower_id)
    print("GET - equipments_config: ", equipments_config)
    print("GET - status: ", status)
    print("GET - internal_comment: ", internal_comment)
    print("GET - compact_comment: ", compact_comment)
    print("GET - detailed_comment: ", detailed_comment)

    eq_to_class = EquipmentConfig.objects.filter(pk__in=equipments_config).values_list('calibration', flat=True)
    eq_to_class = Calibration.objects.filter(pk__in=eq_to_class).distinct().values_list('equipment', flat=True)
    eq_to_class = Equipment.objects.filter(pk__in=eq_to_class).distinct()
    # print("\n", eq_to_class, "\n")

    # configuration_periods = PeriodConfiguration.objects.filter((QD(begin_date__range=(begin_date, end_date)) | QD(end_date__range=(begin_date, end_date))))
    configuration_periods = PeriodConfiguration.objects.filter(QD(tower=tower_id) & ((QD(begin_date__lte=begin_date) & QD(end_date__gte=begin_date)) | (QD(begin_date__lte=end_date) & QD(end_date__gte=end_date))))
    flag_comment = 0
    flag_class = 0
    for cp in configuration_periods:
        # print("PERIODS DATES:", cp.begin_date, cp.end_date)
        equipments_conf = EquipmentConfig.objects.filter(conf_period=cp)
        # print(equipments_conf)
        for eq in equipments_conf:
            if eq.calibration.equipment in eq_to_class:
                # print("Vou classificar", eq)
                if begin_date > cp.begin_date:
                    begin_date_to_class = begin_date
                else:
                    begin_date_to_class = cp.begin_date

                if end_date < cp.end_date:
                    end_date_to_class = end_date
                else:
                    end_date_to_class = cp.end_date

                # print("DATE TO CLASS: ", begin_date_to_class, end_date_to_class, "\n")

                classification = ClassificationPeriod(begin_date=begin_date_to_class,
                                                      end_date=end_date_to_class,
                                                      equipment_configuration=eq,
                                                      status=status,
                                                      user=request.user)
                try:
                    classification.save()
                    flag_class = 1
                except IntegrityError:
                    data = {}
                    data['is_taken'] = True
                    data['error'] = "There are already a Classification equal for that Equipment with same Begin and End Date"
                    return JsonResponse(data)

                if internal_comment or compact_comment or detailed_comment:
                    now = datetime.now(pytz.utc)
                    comment_classification = CommentClassification(begin_date=begin_date_to_class,
                                                                   end_date=end_date_to_class,
                                                                   comment_date=now,
                                                                   classification=classification,
                                                                   user=request.user,
                                                                   internal_comment=internal_comment,
                                                                   compact_comment=compact_comment,
                                                                   detailed_comment=detailed_comment)
                    try:
                        comment_classification.save()
                        flag_comment = 1
                    except IntegrityError:
                        data = {}
                        data['is_taken'] = True
                        data['error'] = "There are already an Comment equal to that - Same Begin and End Date, and Classification."
                        return JsonResponse(data)

    if flag_comment:
        data = {'message': "Classification and Comments entered successfully."}
    elif flag_class:
        data = {'message': "Classification entered successfully."}
    else:
        data = {'message': "Nothing to do!!!"}
    return JsonResponse(data)


def XChartClassifications(request):

    begin_date = request.GET.get('begin_date', '')
    end_date = request.GET.get('end_date', '')
    tower_id = request.GET.get('tower_id', '')

    # print("GETX - Begin: ", begin_date)
    # print("GETX - End: ", end_date)
    # print("GETX - tower_id: ", tower_id)

    if not (begin_date and end_date):
        end_date = datetime.now(pytz.utc)
        begin_date = end_date - timedelta(days=30)
    else:
        begin_date = get_date(begin_date)
        end_date = get_date(end_date)

    data = []
    categories = []

    # period_conf = PeriodConfiguration.objects.filter(QD(tower=tower_id) & ((QD(begin_date__lte=begin_date) & QD(end_date__gte=begin_date)) | (QD(begin_date__lte=end_date) & QD(end_date__gte=end_date))))
    # period_conf = PeriodConfiguration.objects.filter(QD(tower=tower_id) & QD(begin_date__gte=begin_date, end_date__lte=end_date))
    period_conf = PeriodConfiguration.objects.filter(QD(tower=tower_id) & ((QD(begin_date__range=(begin_date, end_date)) | QD(end_date__range=(begin_date, end_date)))))
    # print(period_conf)
    # print(period_conf)
    # tower = Tower.objects.get(pk=10)
    # period_conf = PeriodConfiguration.objects.filter(tower=tower).order_by('id')
    eq_config = EquipmentConfig.objects.filter(conf_period__in=period_conf).order_by('id')

    # Fill categories 1st
    for eq in eq_config:
        name = eq.calibration.equipment.model.type.initials + '@' + str(eq.height_label)
        if name not in categories:
            categories.append(name)

    # Fill data
    for eq in eq_config:
        name = eq.calibration.equipment.model.type.initials + '@' + str(eq.height_label)
        classifications = ClassificationPeriod.objects.filter(equipment_configuration=eq).order_by('id')
        for cl in classifications:
            data.append({'x': dt2epoch(cl.begin_date),
                         'x2': dt2epoch(cl.end_date),
                         'y': categories.index(name),
                         'name': cl.status.name,
                         'colorIndex': get_color_index(cl.status.code)})

    dataToReturn = {}
    dataToReturn['data'] = data
    dataToReturn['categories'] = categories
    return JsonResponse(dataToReturn)


# ============ Tests of some more charts ============


def chart_chartjs(request):
    date_form = DateRangeChooseForm()
    return render(request, 'chart_chartjs.html', {'date_form': date_form})


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
    chart2 = LineChartHIGH(data_source, width=1200, height=600, options={'title': 'Data Visualization', 'chart': {'zoomType': 'xy'}})

    context = {'chart': chart, 'chart1': chart1, 'chart2': chart2}

    return render(request, 'chart_graphos.html', context)


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


# ========================================= DATASETS =========================================


def show_towers_data_mongo(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    data = {}

    # start_time = time.time()
    # towers = DataSetMongoPyMod.objects(QM(tower_code="port525") and QM(time_stamp__lte=datetime(2010, 12, 25)))
    # end = time.time()
    # total_time = (end - start_time)
    # print('Query time: ', total_time, ' seconds', towers.count())
    #
    # data['towers'] = {}

    return render(request, 'show_towers_data_mongo.html', data)


def dropdb_mongo(request):
    # dt = DataSetMongoPyMod.objects.all().count()
    # data = {'size': dt}
    DataSetMongoPyMod.objects.all().delete()
    return JsonResponse({})


def add_raw_data_mongo(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    total_time_operation = 0
    total_time_insertion = 0
    flag_problem = False

    conta = len(request.FILES.getlist('document'))

    if conta is 0:
        messages.error(request, "Please select one file")
        return HttpResponseRedirect(reverse("show_towers_data_mongo"))

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
                # try:
                #     check_replicated = DataSetMongoPyMod.objects(QM(tower_code=tower_code) and QM(time_stamp=time_value))
                # except DataSetMongoPyMod.DoesNotExist:
                #     check_replicated = None
                #
                # if check_replicated.count() >= 1:
                #     check_replicated.update(value=values)
                # else:
                #     tower_data = DataSetMongoPyMod(tower_code=tower_code, time_stamp=time_value, value=values)
                #     dataraw.append(tower_data)

                tower_data = DataSetMongoPyMod(tower_code=tower_code, time_stamp=time_value, value=values)
                dataraw.append(tower_data)

            total_time = (time.time() - op_time)
            total_time_operation += total_time
            print('time of operation: ', total_time, ' seconds')

            db_time = time.time()
            if dataraw:
                DataSetMongoPyMod.objects.bulk_create(dataraw)
            total_time = (time.time() - db_time)
            total_time_insertion += total_time
            print('time to insert in database: ', total_time, ' seconds')

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_mongo"))


def show_towers_data_influx(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    # start_time = time.time()
    #
    # result = INFLUXCLIENT.query("select time, value from port525")
    #
    # end = time.time()
    # total_time = (end - start_time)
    # print('Query time: ', total_time, ' seconds')

    # print("Result: {0}".format(result))

    # print(json.dumps(list(result)[0]))

    # for obj in list(result)[0]:
    #     print(obj)

    # if result:
    #     result = list(result)[0]

    result = {}
    # print(len(result))
    return render(request, "show_towers_data_influx.html", {'data': result}, content_type="text/html")


def dropdb_influx(request):
    INFLUXCLIENT.query("DROP SERIES FROM /.*/")
    data = {'message': "Dropped"}
    return JsonResponse(data)


def add_raw_data_influx(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    total_time_operation = 0
    total_time_insertion = 0
    flag_problem = False

    conta = len(request.FILES.getlist('document'))

    if conta is 0:
        messages.error(request, "Please select one file")
        return HttpResponseRedirect(reverse("show_towers_data_influx"))

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
                INFLUXCLIENT.write_points(points, batch_size=100000)
            total_time = (time.time() - db_time)
            total_time_insertion += total_time
            print('time to insert in database: ', total_time, ' seconds')

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_influx"))


def show_towers_data_pg(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    form_tower = TowersDataVForm()
    data = {'form_tower': form_tower}

    # start_time = time.time()
    # # dataset = DataSetPG.objects.filter(QD(tower_code='port525'))
    # dataset = DataSetPG.objects.all()
    #
    # # for t in dataset:
    # #     print(t.tower_code, "---", t.time_stamp, "---", t.value)
    #
    # end = time.time()
    # total_time = (end - start_time)
    # print('\nQuery time: ', total_time, ' seconds -- size:', len(dataset))
    # data['towers'] = {}

    return render(request, 'show_towers_data_pg.html', data)


def dropdb_pg(request):
    # dt = DataSetPG.objects.all().count()
    # data = {'size': dt}
    DataSetPG.objects.all().delete()
    return JsonResponse({})


def add_raw_data_pg(request):
    if request.user.is_client:
        messages.error(request, 'You dont have access to this page')
        return HttpResponseRedirect(reverse("index"))

    total_time_operation = 0
    total_time_insertion = 0
    flag_problem = False

    conta = len(request.FILES.getlist('document'))

    if conta is 0:
        messages.error(request, "Please select one file")
        return HttpResponseRedirect(reverse("show_towers_data_pg"))

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
                # db_time_start = time.time()
                # try:
                #     check_replicated = DataSetPG.objects.get(QD(tower_code=tower_code) and QD(time_stamp=time_value))
                # except DataSetPG.DoesNotExist:
                #     check_replicated = None
                #
                # if check_replicated:
                #     check_replicated.value = values
                #     check_replicated.save()
                # else:
                #     tower_data = DataSetPG(tower_code=tower_code, time_stamp=time_value, value=values)
                #     dataraw.append(tower_data)
                tower_data = DataSetPG(tower_code=tower_code, time_stamp=time_value, value=values)
                dataraw.append(tower_data)
                # db_time += (time.time() - db_time_start)

                # Heavier!!!!! - Maybe because takes care one by one! - Takes 1 to 2 seconds more in 6000 lines
                # db_time_start = time.time()
                # DataSetPG.objects.update_or_create(tower_code=tower_code, time_stamp=time_value, defaults={'value': values})
                # db_time += (time.time() - db_time_start)

            # total_time_insertion += db_time
            # print('Database time inside: ', db_time, ' seconds')

            op_time = (time.time() - op_time)
            total_time_operation += op_time
            print('Operation time: ', op_time, ' seconds')

            db_time2 = time.time()
            if dataraw:
                DataSetPG.objects.bulk_create(dataraw, batch_size=100000)
            db_time2 = (time.time() - db_time2)
            total_time_insertion += db_time2

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_pg"))


# ===============================================================================================
# ========================================= TESTES!!!!! =========================================
# ===============================================================================================


FILE_PATH_TO_UPLOAD = "./files/raw_data/100000.row"
ITIMES = 1
BATCHS = 1
# SIZE_FOR_IT = 100000
FILE_TEST_PG = './files/tests_insert_pg_ci.csv'
FILE_TEST_IN = './files/tests_insert_in_ci.csv'
FILE_TEST_MG = './files/tests_insert_mg_ci.csv'

ITIMES_QR = 5
ITIMES_QR_PAR = 10
FILE_QR_PG = './files/tests_query_pg_ci.csv'
FILE_QR_MG = './files/tests_query_mg_ci.csv'
FILE_QR_IN = './files/tests_query_in_par.csv'


def queryset_iterator(queryset, chunksize=1000):
    try:
        pk = 0
        last_pk = queryset.order_by('-id')[0].pk
        queryset = queryset.order_by('pk')
        while pk < last_pk:
            for row in queryset.filter(pk__gt=pk)[:chunksize]:
                pk = row.pk
                yield row
            gc.collect()
    except IndexError:
        pass


def query_pg(request):
    file_to_write = csv.writer(open(FILE_QR_PG, 'a+'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    tt = 0

    # PARCIAL
    end_date = datetime(2019, 4, 5, 4, 10, tzinfo=pytz.UTC)
    begin_date = end_date - timedelta(days=90)
    conta = DataSetPG.objects.filter(tower_code="port1", time_stamp__gte=begin_date, time_stamp__lte=end_date).count()
    print(conta)
    print(DataSetPG.objects.filter(tower_code="port1", time_stamp__gte=begin_date, time_stamp__lte=end_date).explain(ANALYZE=True))
    for it in range(1, ITIMES_QR_PAR + 1):
        start_time = time.time()
        dt = DataSetPG.objects.filter(tower_code="port1", time_stamp__gte=begin_date, time_stamp__lte=end_date)
        for d in dt:
            pass
        end = time.time()
        total_time = (end - start_time)
        print(it, total_time)
        tt += total_time
        if it is 1:
            file_to_write.writerow(["SIZE: " + str(conta) + " de X Query PARCIAL"])
            file_to_write.writerow(['Iteration', 'Query Time'])
        file_to_write.writerow([str(it), str(total_time)])

    file_to_write.writerow([])

    # tt = 0
    # # TOTAL C chunks
    # conta = DataSetPG.objects.all().count()
    # print(conta)
    # for it in range(1, ITIMES_QR+1):
    #     start_time = time.time()
    #     dt = DataSetPG.objects.all().iterator(chunk_size=100000)
    #     for d in dt:
    #         pass
    #     end = time.time()
    #     total_time = (end - start_time)
    #     print(it, total_time)
    #     tt += total_time
    #     if it is 1:
    #         file_to_write.writerow(["SIZE: " + str(conta) + " Query TOTAL C/C"])
    #         file_to_write.writerow(['Iteration', 'Query Time'])
    #     file_to_write.writerow([str(it), str(total_time)])
    #
    # file_to_write.writerow([])

    # tt = 0
    # # TOTAL S chunks
    # conta = DataSetPG.objects.all().count()
    # print(conta)
    # for it in range(1, ITIMES_QR + 1):
    #     start_time = time.time()
    #     dt = DataSetPG.objects.all()
    #     for d in dt:
    #         pass
    #     end = time.time()
    #     total_time = (end - start_time)
    #     print(it, total_time)
    #     tt += total_time
    #     if it is 1:
    #         file_to_write.writerow(["SIZE: " + str(conta) + " Query TOTAL S/C"])
    #         file_to_write.writerow(['Iteration', 'Query Time'])
    #     file_to_write.writerow([str(it), str(total_time)])
    #
    # file_to_write.writerow([])

    data = {}
    data['time'] = tt
    data['size'] = conta
    return JsonResponse(data)


def query_in(request):
    file_to_write = csv.writer(open(FILE_QR_IN, 'a+'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    tt = 0
    conta = 0
    print(ITIMES_QR)

    # Parcial
    end_date = datetime(2019, 4, 5, 4, 10, tzinfo=pytz.UTC)
    begin_date = end_date - timedelta(days=90)
    begin_date = begin_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_date = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")
    for it in range(1, ITIMES_QR_PAR + 1):
        start_time = time.time()
        dt = INFLUXCLIENT.query("select * FROM port1 where time >= '" + begin_date + "' and time <= '" + end_date + "' order by time")
        end = time.time()
        total_time = (end - start_time)
        print(it, total_time)
        tt += total_time
        if it is 1:
            for d in dt:
                conta += len(d)
            file_to_write.writerow(["SIZE: " + str(conta) + " de X Query PARCIAL"])
            file_to_write.writerow(['Iteration', 'Query Time'])
        file_to_write.writerow([str(it), str(total_time)])

    # tt = 0
    # conta = 0
    # # Total
    # for it in range(1, ITIMES_QR + 1):
    #     start_time = time.time()
    #     dt = INFLUXCLIENT.query("select * FROM /.*/")
    #     end = time.time()
    #     total_time = (end - start_time)
    #     print(it, total_time)
    #     tt += total_time
    #     if it is 1:
    #         for d in dt:
    #             conta += len(d)
    #         file_to_write.writerow(["SIZE: " + str(conta) + " Query TOTAL"])
    #         file_to_write.writerow(['Iteration', 'Query Time'])
    #     file_to_write.writerow([str(it), str(total_time)])

    file_to_write.writerow([])

    data = {}
    data['time'] = tt
    data['size'] = conta
    return JsonResponse(data)


def query_mg(request):
    file_to_write = csv.writer(open(FILE_QR_MG, 'a+'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    tt = 0

    # PARCIAL
    end_date = datetime(2019, 4, 5, 4, 10, tzinfo=pytz.UTC)
    begin_date = end_date - timedelta(days=90)
    conta = DataSetMongoPyMod.objects.raw({'tower_code': 'port1', 'time_stamp': {'$gte': begin_date, '$lte': end_date}}).count()
    print(conta)
    for it in range(1, ITIMES_QR_PAR + 1):
        start_time = time.time()
        dt = DataSetMongoPyMod.objects.raw({'tower_code': 'port1', 'time_stamp': {'$gte': begin_date, '$lte': end_date}})
        for d in dt:
            pass
        end = time.time()
        total_time = (end - start_time)
        print(it, total_time)
        tt += total_time
        if it is 1:
            file_to_write.writerow(["SIZE: " + str(conta) + " of X Query PARCIAL"])
            file_to_write.writerow(['Iteration', 'Query Time'])
        file_to_write.writerow([str(it), str(total_time)])

    file_to_write.writerow([])

    tt = 0
    # TOTAL C chunks
    conta = DataSetMongoPyMod.objects.values().all().count()
    print(conta)
    for it in range(1, ITIMES_QR + 1):
        start_time = time.time()
        dt = DataSetMongoPyMod.objects.all().aggregate(batchSize=100000)
        for d in dt:
            pass
        end = time.time()
        total_time = (end - start_time)
        print(it, total_time)
        tt += total_time
        if it is 1:
            file_to_write.writerow(["SIZE: " + str(conta) + " Query TOTAL C/C"])
            file_to_write.writerow(['Iteration', 'Query Time'])
        file_to_write.writerow([str(it), str(total_time)])

    file_to_write.writerow([])

    tt = 0
    # TOTAL S chunks
    conta = DataSetMongoPyMod.objects.values().all().count()
    print(conta)
    for it in range(1, ITIMES_QR + 1):
        start_time = time.time()
        dt = DataSetMongoPyMod.objects.all()
        for d in dt:
            pass
        end = time.time()
        total_time = (end - start_time)
        print(it, total_time)
        tt += total_time
        if it is 1:
            file_to_write.writerow(["SIZE: " + str(conta) + " Query TOTAL S/C"])
            file_to_write.writerow(['Iteration', 'Query Time'])
        file_to_write.writerow([str(it), str(total_time)])

    file_to_write.writerow([])

    data = {}
    data['time'] = tt
    data['size'] = conta
    return JsonResponse(data)


def count_pg(request):

    # start_time = time.time()
    # # dt = DataSetPG.objects.all()
    # # print(DataSetPG.objects.all().explain())
    # # dt = DataSetPG.objects.filter(QD(tower_code="port5") & QD(time_stamp__lte=datetime(2010, 12, 25, tzinfo=pytz.UTC)) & QD(time_stamp__gte=datetime(1990, 12, 25, tzinfo=pytz.UTC)))
    # conta = len(DataSetPG.objects.filter(QD(tower_code="port1")).order_by('-time_stamp'))
    # print(DataSetPG.objects.filter(QD(tower_code="port1")).order_by('-time_stamp').explain())
    # end = time.time()
    # total_time = (end - start_time)
    # print(total_time)

    start_time = time.time()
    # conta = len(DataSetPG.objects.filter(QD(tower_code="port1") & QD(time_stamp__gte=datetime(2009, 4, 8, 18, 20, tzinfo=pytz.UTC)) & QD(time_stamp__lte=datetime(2019, 4, 5, 4, 10, tzinfo=pytz.UTC))).order_by('-time_stamp'))
    # dt = queryset_iterator(DataSetPG.objects.all(), chunksize=100000)
    dt = DataSetPG.objects.all().iterator(chunk_size=100000)
    for d in dt:
        pass
    end = time.time()
    total_time = (end - start_time)

    conta = DataSetPG.objects.all().count()

    data = {}
    data['time'] = total_time
    data['size'] = conta

    return JsonResponse(data)


def count_influx(request):
    start_time = time.time()
    dt = INFLUXCLIENT.query(query="select * FROM /.*/")
    # dt = INFLUXCLIENT.query("select * FROM port1")
    end = time.time()
    total_time = (end - start_time)

    result = 0
    for d in dt:
        result += len(d)

    data = {}
    data['time'] = total_time
    data['size'] = result
    return JsonResponse(data)


def count_mongo(request):
    # start_time = time.time()
    # # dt = DataSetMongoPyMod.objects.all()
    # # dt = DataSetMongoPyMod.objects.raw({'tower_code': tower.code_inegi, 'time_stamp': {'$gte': begin_date, '$lte': end_date}})
    # dt = DataSetMongoPyMod.objects.raw({'tower_code': 'port1'})
    # conta = dt.count()  # REAL OPERATION!!!!
    # end = time.time()
    # total_time = (end - start_time)

    start_time = time.time()
    # dt = queryset_iterator_mongo(DataSetMongoPyMod.objects.all(batch_size=5), chunksize=5)
    dt = DataSetMongoPyMod.objects.all().aggregate(batchSize=100000)
    # dt = DataSetMongoPyMod.objects.raw({'tower_code': 'port1', 'time_stamp': {'$gte': datetime(2009, 4, 8, 18, 20, tzinfo=pytz.UTC), '$lte': datetime(2019, 4, 5, 4, 10, tzinfo=pytz.UTC)}})
    # dt = DataSetMongoPyMod.objects.raw({'tower_code': 'port1'})
    for d in dt:
        pass
    end = time.time()
    total_time = (end - start_time)

    conta = DataSetMongoPyMod.objects.all().count()

    data = {}
    data['time'] = total_time
    data['size'] = conta
    return JsonResponse(data)


def add_raw_data_pg2(request):
    flag_problem = False
    file = open(FILE_PATH_TO_UPLOAD, "r")
    file_to_write = csv.writer(open(FILE_TEST_PG, 'a+'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    print(ITIMES, BATCHS)

    if file:
        file_to_write.writerow(["SIZE: "+str(BATCHS)+str(file)])
        file_to_write.writerow(['Iteration', 'Operation Time', 'Insertion Time'])
        # print(str(file))

        for t in range(0, ITIMES):
            print("Iteration: ", t)
            if t is not 0:
                file = open(FILE_PATH_TO_UPLOAD, "r")

            # fake = Faker()
            #
            # for i in range(0, SIZE_FOR_IT):
            #     rndm_date = fake.date_time_between(start_date='-100y', end_date='now', tzinfo=pytz.UTC)
            #     tower_code = "port"+str(random.randint(0, 100))
            #     # tower_code = "port525"
            #     values = "49,67,28,8,49,66,31,8,49,76,29,10,268,11,255,12,45,2961,1000,138,91,93"
            #     tower_data = DataSetPG(tower_code=tower_code, time_stamp=rndm_date, value=values)
            #     dataraw.append(tower_data)

            total_time_operation = 0
            total_time_insertion = 0

            for b in range(0, BATCHS):
                print("PG Batch: ", b)
                if b is not 0:
                    file = open(FILE_PATH_TO_UPLOAD, "r")

                op_time = time.time()
                dataraw = []

                for i, line in enumerate(file):
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
                    batch = b + 1
                    tower_code = "port" + str(batch)

                    tower_data = DataSetPG(tower_code=tower_code, time_stamp=time_value, value=values)
                    dataraw.append(tower_data)

                op_time = (time.time() - op_time)
                total_time_operation += op_time
                print('Operation time: ', op_time, ' seconds')

                db_time2 = time.time()
                if dataraw:
                    DataSetPG.objects.bulk_create(dataraw, batch_size=100000)
                db_time2 = (time.time() - db_time2)
                print('Inserition time: ', db_time2, ' seconds')
                total_time_insertion += db_time2
                file.close()

            print('Total time of operation: ', total_time_operation, ' seconds')
            print('Total time to insert in database: ', total_time_insertion, ' seconds')

            iteration = t + 1
            file_to_write.writerow([str(iteration), str(total_time_operation), str(total_time_insertion)])

            if t is not ITIMES - 1:
                DataSetPG.objects.all().delete()
            # else:
            #     file_to_write.writerow([str(total_time_operation), str(total_time_insertion)])

    file.close()

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_pg"))


def add_raw_data_influx2(request):
    flag_problem = False
    file = open(FILE_PATH_TO_UPLOAD, "r")
    file_to_write = csv.writer(open(FILE_TEST_IN, 'a+'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    print(ITIMES, BATCHS)

    if file:
        file_to_write.writerow(["SIZE: "+str(BATCHS)+str(file)])
        file_to_write.writerow(['Iteration', 'Operation Time', 'Insertion Time'])
        # print(str(file))

        for t in range(0, ITIMES):
            print("Iteration: ", t)
            if t is not 0:
                file = open(FILE_PATH_TO_UPLOAD, "r")

            # fake = Faker()
            #
            # for i in range(0, SIZE_FOR_IT):
            #     rndm_date = fake.date_time_between(start_date='-100y', end_date='now')
            #     # tower_code = "port"+str(random.randint(0, 100))
            #     tower_code = "port525"
            #     values = "49,67,28,8,49,66,31,8,49,76,29,10,268,11,255,12,45,2961,1000,138,91,93"
            #     point = {
            #         "measurement": tower_code,
            #         "time": rndm_date,
            #         "fields": {
            #             "value": values
            #         }
            #     }
            #     points.append(point)

            total_time_operation = 0
            total_time_insertion = 0

            for b in range(0, BATCHS):
                print("Influx Batch: ", b)
                if b is not 0:
                    file = open(FILE_PATH_TO_UPLOAD, "r")

                op_time = time.time()
                points = []

                for i, line in enumerate(file):
                    # # remove the \n at the end
                    line = line.rstrip()

                    try:
                        if line.strip()[-1] is ',':
                            line = line.strip()[:-1]
                    except IndexError:
                        flag_problem = True
                        messages.error(request, 'Error reading a line, check your file -> ' + str(
                            file) + '. No values was entered on the DB')
                        return HttpResponseRedirect(reverse("show_towers_data_influx"))

                    mylist = line.split(",", 3)

                    time_value, flag_date = parsedate(request, file, mylist, i)

                    if flag_date:
                        return HttpResponseRedirect(reverse("show_towers_data_influx"))

                    try:
                        mylist[3]
                    except IndexError:
                        flag_problem = True
                        messages.warning(request, 'Warning!!! reading a line, check your file -> ' + str(
                            file) + ' at line: ' + str(i + 1) + '. No values was entered on the DB for time stamp: ' + str(
                            time_value))
                        continue

                    values = mylist[3]
                    batch = b+1
                    tower_code = "port"+str(batch)

                    point = {
                        "measurement": tower_code,
                        "time": time_value,
                        "fields": {
                            "value": values
                        }
                    }
                    points.append(point)

                op_time = (time.time() - op_time)
                total_time_operation += op_time
                print('Operation time: ', op_time, ' seconds')

                db_time2 = time.time()
                if points:
                    INFLUXCLIENT.write_points(points, batch_size=100000)
                db_time2 = (time.time() - db_time2)
                print('Inserition time: ', db_time2, ' seconds')
                total_time_insertion += db_time2
                file.close()

            print('Total time of operation: ', total_time_operation, ' seconds')
            print('Total time to insert in database: ', total_time_insertion, ' seconds')

            iteration = t + 1
            file_to_write.writerow([str(iteration), str(total_time_operation), str(total_time_insertion)])

            if t is not ITIMES - 1:
                INFLUXCLIENT.query("DROP SERIES FROM /.*/")
            # else:
            #     file_to_write.writerow([str(total_time_operation), str(total_time_insertion)])

    file.close()

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_influx"))


def add_raw_data_mongo2(request):
    flag_problem = False
    file = open(FILE_PATH_TO_UPLOAD, "r")
    file_to_write = csv.writer(open(FILE_TEST_MG, 'a+'), delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    print(ITIMES, BATCHS)
    if file:
        file_to_write.writerow(["SIZE: "+str(BATCHS)+str(file)])
        file_to_write.writerow(['Iteration', 'Operation Time', 'Insertion Time'])
        # print(str(file))

        for t in range(0, ITIMES):
            print("Iteration: ", t)
            if t is not 0:
                file = open(FILE_PATH_TO_UPLOAD, "r")

            # fake = Faker()
            #
            # for i in range(0, SIZE_FOR_IT):
            #     rndm_date = fake.date_time_between(start_date='-100y', end_date='now', tzinfo=pytz.UTC)
            #     # tower_code = "port"+str(random.randint(0, 100))
            #     tower_code = "port525"
            #     values = "49,67,28,8,49,66,31,8,49,76,29,10,268,11,255,12,45,2961,1000,138,91,93"
            #
            #     tower_data = DataSetMongoPyMod(tower_code=tower_code, time_stamp=rndm_date, value=values)
            #     dataraw.append(tower_data)

            total_time_insertion = 0
            total_time_operation = 0

            for b in range(0, BATCHS):
                print("Mongo Batch: ", b)
                if b is not 0:
                    file = open(FILE_PATH_TO_UPLOAD, "r")

                dataraw = []
                op_time = time.time()

                for i, line in enumerate(file):
                    # # remove the \n at the end
                    line = line.rstrip()

                    try:
                        if line.strip()[-1] is ',':
                            line = line.strip()[:-1]
                    except IndexError:
                        flag_problem = True
                        messages.error(request, 'Error reading a line, check your file -> ' + str(
                            file) + '. No values was entered on the DB')
                        return HttpResponseRedirect(reverse("show_towers_data_mongo"))

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
                    batch = b+1
                    tower_code = "port"+str(batch)

                    tower_data = DataSetMongoPyMod(tower_code=tower_code, time_stamp=time_value, value=values)
                    dataraw.append(tower_data)

                op_time = (time.time() - op_time)
                total_time_operation += op_time
                print('Operation time: ', op_time, ' seconds')

                db_time2 = time.time()
                if dataraw:
                    DataSetMongoPyMod.objects.bulk_create(dataraw)
                db_time2 = (time.time() - db_time2)
                print('Inserition time: ', db_time2, ' seconds')
                total_time_insertion += db_time2
                file.close()

            print('Total time of operation: ', total_time_operation, ' seconds')
            print('Total time to insert in database: ', total_time_insertion, ' seconds')

            iteration = t + 1
            file_to_write.writerow([str(iteration), str(total_time_operation), str(total_time_insertion)])

            if t is not ITIMES-1:
                DataSetMongoPyMod.objects.all().delete()
            # else:
            #     file_to_write.writerow([str(total_time_operation), str(total_time_insertion)])

    file.close()

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_mongo"))
