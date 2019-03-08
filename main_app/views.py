from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from mongoengine.queryset.visitor import Q
from .models import Tower, TowerData, DataRaw, MyUser, MySeriesHelper, DataSetMongo, DataSetPG
from .forms import TowerForm, TowerViewForm, RegisterForm, LoginForm
from influxdb import InfluxDBClient
import pytz

from datetime import *
import time, re, io

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


def show_towers_data_mongo(request):
    data = {}

    start_time = time.time()

    towers = DataSetMongo.objects(Q(tower_code="port525") and Q(time_stamp__lte=datetime(2010, 12, 25)))

    end = time.time()
    total_time = (end - start_time)
    print('Query time: ', total_time, ' seconds', towers.count())

    data['towers'] = {}

    return render(request, 'show_towers_data_mongo.html', data)


def add_raw_data_mongo(request):
    total_time_operation = 0
    total_time_insertion = 0
    conta = 0

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
            #firstime = True
            start_time = time.time()
            dataraw = []

            for line in io_file:

                # remove the \n at the end
                line = line.rstrip()

                try:
                    if line.strip()[-1] is ',':
                        line = line.strip()[:-1]
                except IndexError:
                    messages.error(request, 'Error reading a line, check your file -> ' + str(
                        file) + '. No values was entered on the DB')
                    return HttpResponseRedirect(reverse("show_towers_data_mongo"))

                # Isnt necessary as we will store each time serie per line in mongo - Array is inefficient
                # if firstime:
                #     firstime = False
                #     tower_code = line.split(',', 1)[0]
                #     tower_code = tower_code.lower()
                #     try:
                #         tower_data = TowerData.objects.get(tower_code=tower_code)
                #     except TowerData.DoesNotExist:
                #         tower_data = TowerData(tower_code=tower_code, raw_datas=[])

                mylist = line.split(",", 3)

                str_timedate = time.time()
                # 3 to 4 times faster than using strptime
                year = int(mylist[1][0:4])
                month = int(mylist[1][4:6])
                day = int(mylist[1][6:8])
                hour = int(mylist[2][0:2])
                minute = int(mylist[2][3:5])
                second = 0
                values = mylist[3]

                if hour is 24:
                    hour = 23
                    minute = 50
                    time_value = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)
                else:
                    time_value = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC) - timedelta(minutes=10)

                # Other way to split data, but takes more time
                # values = mylist[3]
                # if int(mylist[2][0:2]) is 24:
                #     mydate = str(mylist[1]) + " 23:50"
                #     time_value = datetime.datetime.strptime(mydate, '%Y%m%d %H:%M')
                # else:
                #     mydate = str(mylist[1]) + " " + str(mylist[2])
                #     time_value = datetime.datetime.strptime(mydate, '%Y%m%d %H:%M') - datetime.timedelta(minutes=10)

                tower_code = line.split(',', 1)[0]
                tower_code = tower_code.lower()

                # Check if have a tower_code and a time_stamp and replace the value
                check_Replicated = DataSetMongo.objects(Q(tower_code=tower_code) and Q(time_stamp=time_value))
                if check_Replicated.count() >= 1:
                    check_Replicated.update(value=values)
                else:
                    tower_data = DataSetMongo(tower_code=tower_code, time_stamp=time_value, value=values)
                    dataraw.append(tower_data)

                # raw = DataRaw(time=time_value, data=values)
                # dataraw.append(raw)

            end_time = time.time()
            total_time = (end_time - start_time)
            total_time_operation += total_time
            print(str(file), '\ntime of operation: ', total_time, ' seconds')

            # To check if have a date and update the value, but takes so long!!!
            # for raw in dataraw:
            #     found = False
            #     for raw2 in tower_data.raw_datas:
            #         if str(raw2.time) == (str(raw.time)):
            #             found = True
            #             raw2.data = raw.data
            #             break
            #
            #     if found is False:
            #         tower_data.raw_datas.append(raw)

            start_time = time.time()

            # tower_data.raw_datas +=(dataraw)
            # tower_data.save()

            if dataraw:
                DataSetMongo.objects.insert(dataraw)

            end_time = time.time()
            total_time = (end_time - start_time)
            total_time_insertion += total_time
            print('time to insert in database: ', total_time, ' seconds')

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    return HttpResponseRedirect(reverse("show_towers_data_mongo"))


def show_towers_data_influx(request):
    start_time = time.time()

    result = myclient.query("select time, value from port525")

    end = time.time()
    total_time = (end - start_time)
    print('Query time: ', total_time, ' seconds')

    # print("Result: {0}".format(result))

    # print(json.dumps(list(result)[0]))

    # for obj in list(result)[0]:
    #     print(obj)
    if result:
        result = list(result)[0]
    result = {}
    # print(result)
    return render(request, "show_towers_data_influx.html", {'data': result}, content_type="text/html")


def add_raw_data_influx(request):
    total_time_operation = 0
    total_time_insertion = 0
    conta = 0

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
            firstime = True
            start_time = time.time()
            points = []

            for line in io_file:

                #remove the \n at the end
                line = line.rstrip()

                try:
                    if line.strip()[-1] is ',':
                        line = line.strip()[:-1]
                except IndexError:
                    messages.error(request, 'Error reading a line, check your file -> ' + str(
                        file) + '. No values was entered on the DB')
                    return HttpResponseRedirect(reverse("show_towers_data_influx"))

                if firstime:
                    firstime = False
                    tower_code = line.split(',', 1)[0]
                    tower_code = tower_code.lower()

                mylist = line.split(",", 3)

                year = int(mylist[1][0:4])
                month = int(mylist[1][4:6])
                day = int(mylist[1][6:8])
                hour = int(mylist[2][0:2])
                minute = int(mylist[2][3:5])
                second = 0
                values = mylist[3]

                if hour is 24:
                    hour = 23
                    minute = 50
                    time_value = datetime(year, month, day, hour, minute, second)
                else:
                    time_value = datetime(year, month, day, hour, minute, second) - timedelta(minutes=10)

                # MySeriesHelper(measurement=tower_code, time=time_value, value=values)

                point = {
                        "measurement": tower_code,
                        "time": time_value,
                        "fields": {
                            "value": values
                            }
                        }
                points.append(point)

            end_time = time.time()
            total_time = (end_time - start_time)
            total_time_operation += total_time
            print(str(file), '\ntime of operation: ', total_time, ' seconds')

            start_time = time.time()
            # MySeriesHelper.commit()
            myclient.write_points(points, batch_size=5000)

            end_time = time.time()
            total_time = (end_time - start_time)
            total_time_insertion += total_time
            print('time to insert in database: ', total_time, ' seconds')

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    return HttpResponseRedirect(reverse("show_towers_data_influx"))


def show_towers_data_pg(request):
    data = {}

    start_time = time.time()
    # towers = DataSetPG.objects.filter(Q(tower_code='port525'))

    towers = DataSetPG.objects.filter(tower_code="port525")

    # for t in towers:
    #     print(t.tower_code, "---", t.time_stamp, "---", t.value)

    end = time.time()
    total_time = (end - start_time)
    print('Query time: ', total_time, ' seconds -- size:', len(towers))
    # DataSetPG.objects.all().delete()
    data['towers'] = {}

    return render(request, 'show_towers_data_pg.html', data)


def add_raw_data_pg(request):
    total_time_operation = 0
    total_time_insertion = 0
    conta = 0

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
            start_time = time.time()
            dataraw = []

            for line in io_file:

                # remove the \n at the end
                line = line.rstrip()

                try:
                    if line.strip()[-1] is ',':
                        line = line.strip()[:-1]
                except IndexError:
                    messages.error(request, 'Error reading a line, check your file -> ' + str(
                        file) + '. No values was entered on the DB')
                    return HttpResponseRedirect(reverse("show_towers_data_pg"))

                mylist = line.split(",", 3)

                year = int(mylist[1][0:4])
                month = int(mylist[1][4:6])
                day = int(mylist[1][6:8])
                hour = int(mylist[2][0:2])
                minute = int(mylist[2][3:5])
                second = 0
                values = mylist[3]

                if hour is 24:
                    hour = 23
                    minute = 50
                    time_value = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)
                else:
                    time_value = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC) - timedelta(minutes=10)

                tower_code = line.split(',', 1)[0]
                tower_code = tower_code.lower()

                # Check if have a tower_code and a time_stamp and replace the value
                check_Replicated = DataSetPG.objects.filter(tower_code=tower_code, time_stamp=time_value)
                if check_Replicated.count() >= 1:
                    check_Replicated.update(value=values)
                else:
                    tower_data = DataSetPG(tower_code=tower_code, time_stamp=time_value, value=values)
                    dataraw.append(tower_data)


            end_time = time.time()
            total_time = (end_time - start_time)
            total_time_operation += total_time
            print(str(file), '\ntime of operation: ', total_time, ' seconds')

            start_time = time.time()

            if dataraw:
                DataSetPG.objects.bulk_create(dataraw)

            end_time = time.time()
            total_time = (end_time - start_time)
            total_time_insertion += total_time
            print('time to insert in database: ', total_time, ' seconds')

    print('Total time of operation: ', total_time_operation, ' seconds')
    print('Total time to insert in database: ', total_time_insertion, ' seconds')

    return HttpResponseRedirect(reverse("show_towers_data_pg"))
