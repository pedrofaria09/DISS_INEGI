from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404, HttpResponse
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm
from mongoengine.queryset.visitor import Q as QM
from django.db.models import Q as QD
from .models import *
from .forms import *
from datetime import *
from .aux_functions import *
from formtools.wizard.views import SessionWizardView

import time, re, io, json

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


def associate_towers(request, user_id):
    if not request.user.is_staff:
        messages.error(request, 'You dont have permissions to do this!!!')
        return HttpResponseRedirect(reverse("list_users"))

    try:
        user = MyUser.objects.get(pk=user_id)
    except MyUser.DoesNotExist:
        return HttpResponseRedirect(reverse("list_users"))

    if request.method == 'GET':
        form = UserTowersFrom(instance=user)
    elif request.method == 'POST':
        form = UserTowersFrom(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Towers was been associated correctly')
            return HttpResponseRedirect(reverse("list_users"))
        else:
            messages.warning(request, 'Problem associating Towers!!!')

    return render(request, 'associate_towers.html', {'form': form, 'user': user})


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

    return render(request, 'view_tower.html', {'form': form, 'tower_id': tower_id, 'tower': tower, 'periods': periods})


def delete_tower(request):
    if request.is_ajax and request.method == 'POST':
        tower = Tower.objects.get(pk=request.POST["id"])
        tower.delete()
        messages.success(request, 'Tower was removed successfully!')
        return HttpResponse('ok')
    messages.error(request, 'A problem occurred when deleting the Tower!')
    return HttpResponse("not ok")


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
        machine.delete()
        messages.success(request, 'Machine was successfully removed!')
        return HttpResponse('ok')
    messages.error(request, 'A problem occurred when deleting the Machine!')
    return HttpResponse("not ok")


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
        cluster.delete()
        messages.success(request, 'Cluster was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the cluster!')
    return HttpResponse("not ok")


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
        form.fields['sn'].disabled = True
    elif request.method == 'POST':
        form = EquipmentForm(request.POST, instance=equipment)
        form.fields['sn'].disabled = True
        if form.is_valid():
            form.save()
            messages.success(request, 'Equipment was edited with success')
            return HttpResponseRedirect(reverse("list_equipments"))
        else:
            messages.warning(request, "Equipment wasn't edited!!!")

    return render(request, 'view_equipment.html', {'form': form, 'equipment_id': equipment_id, 'equipment': equipment})


def delete_equipment(request):
    if request.is_ajax and request.method == 'POST':
        equipment = Equipment.objects.get(pk=request.POST["id"])
        equipment.delete()
        messages.success(request, 'Equipment was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the equipment!')
    return HttpResponse("not ok")


def list_type(request, type):
    if type == 'equipment':
        type_obj = EquipmentType.objects.all()
        name = "Equipments"
    elif type == 'user_group':
        type_obj = UserGroupType.objects.all()
        name = "Users Groups"

    return render(request, 'list_type.html', {'type_obj': type_obj, 'type': type, 'name': name})


def add_type(request, type):
    if type == 'equipment':
        name = "Equipment"
    elif type == 'user_group':
        name = "User Group"

    if request.method == 'POST':
        if type == 'equipment':
            form = EquipmentTypeForm(request.POST)
        elif type == 'user_group':
            form = UserGroupTypeForm(request.POST)

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

    return render(request, 'add_type.html', {'form': form, 'type': type, 'name': name})


def view_type(request, equipment_id, type):
    if type == 'equipment':
        name = "Equipment"
        try:
            obj = EquipmentType.objects.get(pk=equipment_id)
        except EquipmentType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))
    elif type == 'user_group':
        name = "User Group"
        try:
            obj = UserGroupType.objects.get(pk=equipment_id)
        except UserGroupType.DoesNotExist:
            return HttpResponseRedirect(reverse("list_type", kwargs={'type': type}))

    if request.method == 'GET':
        if type == 'equipment':
            form = EquipmentTypeForm(instance=obj)
        elif type == 'user_group':
            form = UserGroupTypeForm(instance=obj)

    elif request.method == 'POST':
        if type == 'equipment':
            form = EquipmentTypeForm(request.POST, instance=obj)
        elif type == 'user_group':
            form = UserGroupTypeForm(request.POST, instance=obj)

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
            try:
                obj.delete()
            except TypeError:
                messages.error(request, 'Cant delete this type because have Equipment associated to him!')
                return HttpResponse("not ok")
        elif request.POST["typex"] == 'user_group':
            obj = UserGroupType.objects.get(pk=request.POST["id"])
            try:
                obj.delete()
            except TypeError:
                messages.error(request, 'Cant delete this type because have an User associated to him!')
                return HttpResponse("not ok")

        messages.success(request, 'Type was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the type!')
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


class FormWizardView(SessionWizardView):
    template_name = "wizard.html"

    # towers = Tower.objects.all()
    # ClusterForm.fields['towers'].choices = [(x, x) for x in towers]

    form_list = [ClusterForm, TowerForm]

    def done(self, form_list,  **kwargs):
        return render(self.request, 'home.html', {
            'form_data': [form.cleaned_data for form in form_list],
        })


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
                    messages.error(request, "End date can't be higher than the Begin date!!!")
                elif verify is 2:
                    messages.error(request, "Begin date is invalid!!!")
                elif verify is 3:
                    messages.error(request, "End date is invalid!!!")

            else:
                messages.warning(request, 'Period not added!!!')

        else:
            messages.warning(request, 'Period was not added!!!')
    else:
        form = PeriodConfigForm()

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
                messages.error(request, "End date can't be higher than the Begin date!!!")
            elif verify is 2:
                messages.error(request, "Begin date is invalid!!!")
            elif verify is 3:
                messages.error(request, "End date is invalid!!!")
        else:
            messages.warning(request, 'Period wasnt edited successfully!!!')

    return render(request, 'view_conf_period.html', {'form': form, 'tower_id': tower_id, 'period_id': period_id, 'period': period})


def delete_conf_period(request):
    if request.is_ajax and request.method == 'POST':
        period = PeriodConfiguration.objects.get(pk=request.POST["id"])
        period.delete()
        messages.success(request, 'Period was deleted successfully!')
        return HttpResponse('ok')
    messages.error(request, 'An error occurred when deleting the Period!')
    return HttpResponse("not ok")
