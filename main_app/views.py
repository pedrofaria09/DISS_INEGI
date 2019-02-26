from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
import datetime, json

from .models import Tower, TowerData, DataRaw, MyUser, InfluxData, Meta, InfluxDBClient, MySeriesHelper
from .forms import TowerForm, TowerViewForm, RegisterForm, LoginForm
from collections import namedtuple
from django.core import serializers

myclient = InfluxDBClient(host='localhost', port=8086, database='INEGI_INFLUX')


# Create your views here.


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
        return render(request, 'home.html', {})


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
    try:
        user = MyUser.objects.get(id=user_id)
    except MyUser.DoesNotExist:
        return HttpResponseRedirect(reverse("list_users"))

    if request.method == 'GET':
        form = RegisterForm(instance=user)
    elif request.method == 'POST':
        form = RegisterForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'User was edited successfully')
            return HttpResponseRedirect(reverse("list_users"))
        else:
            messages.warning(request, 'User was not edited!!!')

    return render(request, 'view_user.html', {'form': form, 'user': user})


def delete_user(request):
    if request.is_ajax and request.method == 'POST':
        user = MyUser.objects.get(id=request.POST["id"])
        user.delete()
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


def add_tower(request):
    if request.method == 'POST':
        form = TowerForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, 'Tower created successfully!')
            return HttpResponseRedirect(reverse("list_towers"))
        else:
            messages.warning(request, 'Tower not added!!!')
    else:
        form = TowerForm()

    return render(request, 'add_tower.html', {'form': form})


def list_towers(request):
    towers = Tower.objects.all()

    return render(request, 'list_towers.html', {'towers': towers})


def view_tower(request, tower_id):
    try:
        tower = Tower.objects.get(id=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    if request.method == 'GET':
        form = TowerViewForm(instance=tower)
    elif request.method == 'POST':
        form = TowerViewForm(request.POST, instance=tower)
        if form.is_valid():
            form.save()
            messages.success(request, 'A torre foi editada com sucesso')
            return HttpResponseRedirect(reverse("list_towers"))
        else:
            messages.warning(request, 'A torre não foi editada')

    return render(request, 'view_tower.html', {'form': form, 'tower_id': tower_id})


def delete_tower(request):
    if request.is_ajax and request.method == 'POST':
        tower = Tower.objects.get(id=request.POST["id"])
        tower.delete()
        messages.success(request, 'A Torre foi removida com sucesso!')
        return HttpResponse('ok')
    messages.error(request, 'Aconteceu um problema na remoção da Torre!')
    return HttpResponse("not ok")


def create_tower_data(request, tower_id):
    get_object_or_404(Tower, pk=tower_id)

    try:
        tower = TowerData.objects.get(tower_code=tower_id)
    except TowerData.DoesNotExist:
        tower = None

    if tower is None:
        print("ALOOOO")

    tower_data = TowerData(tower_code=tower_id, raw_datas=[])
    tower_data.save()

    return redirect('/')


def show_towers_data(request):
    data = {}
    towers = TowerData.objects.all()
    data['towers'] = towers

    return render(request, 'show_towers_data.html', data)


def add_raw_data(request):
    with open('files/2018_10_01_0000.row') as f:
        first_line = f.readline()

    tower_code = first_line.split(',', 1)[0]

    try:
        tower_data = TowerData.objects.get(tower_code=tower_code)
    except TowerData.DoesNotExist:
        tower_data = TowerData(tower_code=tower_code, raw_datas=[])

    f = open("files/2018_10_01_0000.row", "r")
    for line in f:
        mylist = line.split(",", 3)

        year = int(mylist[1][0:4])
        month = int(mylist[1][4:6])
        day = int(mylist[1][6:8])
        hour = int(mylist[2][0:2])
        minute = int(mylist[2][3:5])
        second = 0
        values = mylist[3][:-2]

        if hour is 24:
            hour = 23
            minute = 59
            second = 59

        time = datetime.datetime(year, month, day, hour, minute, second)

        raw = DataRaw(time=time, data=values)

        tower_data.raw_datas += [raw]
        tower_data.save()

    f.close()

    # TODO - abrir vários .row dentro de uma pasta e adicionar à DB

    return HttpResponseRedirect(reverse("show_towers_data"))


def show_towers_data_influx(request):


    result = myclient.query("select time, value from PORT1000")

    # print("Result: {0}".format(result))

    # print(json.dumps(list(result)[0]))

    # for obj in list(result)[0]:
    #     print(obj)
    if result:
        result = list(result)[0]

    # print(result)
    return render(request, "show_towers_data_influx.html", {'data': result}, content_type="text/html")


def add_raw_data_influx(request):
    with open('files/2018_10_01_0000.row') as f:
        first_line = f.readline()

    tower_code = first_line.split(',', 1)[0]

    # MySeriesHelper(measurement='test', time=datetime.datetime.now(), value=111)
    # MySeriesHelper(measurement='test', value=222)
    # MySeriesHelper.commit()

    f = open("files/2018_10_01_0000.row", "r")
    points = []
    for line in f:
        print(line)
        mylist = line.split(",", 3)

        year = int(mylist[1][0:4])
        month = int(mylist[1][4:6])
        day = int(mylist[1][6:8])
        hour = int(mylist[2][0:2])
        minute = int(mylist[2][3:5])
        second = 0

        if hour is 24:
            hour = 23
            minute = 59
            second = 59

        time = datetime.datetime(year, month, day, hour, minute, second)

        point = {
            "measurement": tower_code,
            "time": time,
            "fields": {
                "value": mylist[3][:-2]
            }
        }
        points.append(point)

    f.close()
    # for p in points:
    #     print(p)
    myclient.write_points(points)

    return HttpResponseRedirect(reverse("show_towers_data_influx"))
