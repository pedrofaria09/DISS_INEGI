import re, pytz
from django.contrib import messages
from datetime import *
from .models import *

def parsedate(request, file, mylist, i):

    flag = False

    if re.findall('[0-9]{8}', str(mylist[1])):
        year = int(mylist[1][0:4])
        month = int(mylist[1][4:6])
        day = int(mylist[1][6:8])
        if re.findall('[0-9]{2}:[0-9]{2}', str(mylist[2])):
            hour = int(mylist[2][0:2])
            minute = int(mylist[2][3:5])
            second = 0
        elif re.findall('[0-9]:[0-9]{2}', str(mylist[2])):
            hour = int(mylist[2][0:1])
            minute = int(mylist[2][2:4])
            second = 0
        elif re.findall('[0-9]{4}', str(mylist[2])):
            hour = int(mylist[2][0:2])
            minute = int(mylist[2][2:4])
            second = 0
        else:
            flag = True
            messages.error(request, 'Error 1 reading a line, check your file -> ' + str(
                file) + 'at line: ' + str(i + 1) + '. No values was entered on the DB for this file')

    elif re.findall('[0-9]{2}-[0-9]{2}-[0-9]{4}', str(mylist[1])):
        day = int(mylist[1][0:2])
        month = int(mylist[1][3:5])
        year = int(mylist[1][6:10])
        if re.findall('[0-9]{2}:[0-9]{2}:[0-9]{2}', str(mylist[2])):
            hour = int(mylist[2][0:2])
            minute = int(mylist[2][3:5])
            second = int(mylist[2][6:8])
        elif re.findall('[0-9]:[0-9]{2}:[0-9]{2}', str(mylist[2])):
            hour = int(mylist[2][0:1])
            minute = int(mylist[2][2:4])
            second = int(mylist[2][5:7])
        elif re.findall('[0-9]{4}:[0-9]{2}', str(mylist[2])):
            hour = int(mylist[2][0:2])
            minute = int(mylist[2][2:4])
            second = int(mylist[2][5:7])
        else:
            flag = True
            messages.error(request, 'Error 2 reading a line, check your file -> ' + str(
                file) + 'at line: ' + str(i + 1) + '. No values was entered on the DB for this file')
    else:
        flag = True
        messages.error(request, 'Error 3 reading a line, check your file -> ' + str(
            file) + 'at line: ' + str(i + 1) + '. No values was entered on the DB for this file')

    if not flag:
        if hour is 24:
            hour = 23
            minute = 50
            time_value = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC)
        else:
            time_value = datetime(year, month, day, hour, minute, second, tzinfo=pytz.UTC) - timedelta(minutes=10)
    else:
        time_value = 0

    # Other way to split data, but takes more time - Old version - doesnt check DD-MM-YYYY,H/HH:MM:SS
    # values = mylist[3]
    # if int(mylist[2][0:2]) is 24:
    #     mydate = str(mylist[1]) + " 23:50"
    #     time_value = datetime.datetime.strptime(mydate, '%Y%m%d %H:%M')
    # else:
    #     mydate = str(mylist[1]) + " " + str(mylist[2])
    #     time_value = datetime.datetime.strptime(mydate, '%Y%m%d %H:%M') - datetime.timedelta(minutes=10)

    return time_value, flag


def create_tower_if_doesnt_exists(request, tower_code):
    try:
        Tower.objects.get(pk=tower_code)
    except Tower.DoesNotExist:
        tower = Tower(pk=tower_code, name=tower_code)
        tower.save()
        message = "Tower with code: " + tower.code + " created. Please update the meta-information on the Towers page"
        messages.warning(request, message)
