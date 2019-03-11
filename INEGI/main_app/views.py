from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from mongoengine.queryset.visitor import Q as QM
from django.db.models import Q as QD
from .models import *
from .forms import *
from influxdb import InfluxDBClient
from datetime import *
from .aux_functions import *

import time, re, io, json

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
        tower = Tower.objects.get(pk=tower_id)
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
        tower = Tower.objects.get(pk=request.POST["id"])
        tower.delete()
        messages.success(request, 'A Torre foi removida com sucesso!')
        return HttpResponse('ok')
    messages.error(request, 'Aconteceu um problema na remoção da Torre!')
    return HttpResponse("not ok")


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
                if firstime:
                    create_tower_if_doesnt_exists(request, tower_code)
                    firstime = False

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

    result = myclient.query("select time, value from ort542")
    result2 = myclient.query("select time, value from ort542_b")

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
                if firstime:
                    create_tower_if_doesnt_exists(request, tower_code)
                    firstime = False

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
                myclient.write_points(points, batch_size=5000)
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

    DataSetPG.objects.all().delete()

    start_time = time.time()
    dataset = DataSetPG.objects.filter(QD(tower_code='port525'))

    # for t in dataset:
    #     print(t.tower_code, "---", t.time_stamp, "---", t.value)

    end = time.time()
    total_time = (end - start_time)
    print('Query time: ', total_time, ' seconds -- size:', len(dataset))
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
                if firstime:
                    create_tower_if_doesnt_exists(request, tower_code)
                    firstime = False

                # Check if have a tower_code and a time_stamp and replace the value - VERY Heavy operation
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

            total_time = (time.time() - op_time)
            total_time_operation += total_time
            print('time of operation: ', total_time, ' seconds')

            db_time = time.time()
            if dataraw:
                DataSetPG.objects.bulk_create(dataraw)
            total_time = (time.time() - db_time)
            total_time_insertion += total_time
            print('time to insert in database: ', total_time, ' seconds')

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    if not flag_problem:
        messages.success(request, "All files was entered successfully")

    return HttpResponseRedirect(reverse("show_towers_data_pg"))