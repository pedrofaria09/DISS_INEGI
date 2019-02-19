from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.contrib import messages
from datetime import datetime

from .models import Tower, TowerData, DataRaw, InfluxData, Meta
from .forms import TowerForm


# Create your views here.


def get_obj_or_404_2(klass, *args, **kwargs):
    try:
        return klass.objects.get(*args, **kwargs)
    except klass.DoesNotExist:
        raise Http404


def index(request):
    data ={}
    return render(request, 'home.html', data)


def add_tower(request):

    if request.method == 'POST':
        form = TowerForm(request.POST)
        if form.is_valid():
            form.save()

            messages.success(request, 'Torre criada com sucesso!')
            return HttpResponseRedirect(reverse("show_towers"))
        else:
            messages.warning(request, 'A Torre não foi adicionada')
    else:
        form = TowerForm()

    return render(request, 'add_tower.html', {'form': form})


def show_towers(request):
    towers = Tower.objects.all()

    return render(request, 'show_towers.html', {'towers': towers})


def delete_tower(request, tower_id):
    tower = get_object_or_404(Tower, pk=tower_id)
    tower.delete()
    messages.success(request, 'Torre apagada com sucesso!')

    return HttpResponseRedirect(reverse("show_towers"))


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

        if hour is 24:
            hour = 23
            minute = 59
            second = 59

        time = datetime(year, month, day, hour, minute, second)

        raw = DataRaw(time=time, data=mylist[3])

        tower_data.raw_datas += [raw]
        tower_data.save()

    f.close()

    # TODO - abrir vários .row dentro de uma pasta e adicionar à DB

    return HttpResponseRedirect(reverse("show_towers_data"))


def show_towers_data_influx(request):
    data = InfluxData.objects.all()

    for das in data:
        print(das)

    return render(request, 'show_towers_data_influx.html', {'data': data})
