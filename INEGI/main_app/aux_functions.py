from .views import *

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


def check_if_period_is_valid(tower_id, begin_date, end_date, period_id):
    print("VOU VERIFICAR", tower_id, begin_date, end_date, period_id)
    if end_date:
        if begin_date >= end_date:
            return 1
    try:
        tower = Tower.objects.get(pk=tower_id)
    except Tower.DoesNotExist:
        return HttpResponseRedirect(reverse("list_towers"))

    p1 = PeriodConfiguration.objects.filter(tower=tower, begin_date__lte=begin_date, end_date__gte=begin_date).exclude(id=period_id)
    if p1:
        print("Print 1")
        return 2

    p2 = PeriodConfiguration.objects.filter(tower=tower, begin_date__gte=begin_date).exclude(id=period_id)
    if p2:
        print("Print 2")
        return 2

    if end_date:
        p3 = PeriodConfiguration.objects.filter(tower=tower, end_date__lte=end_date, end_date__gte=end_date).exclude(id=period_id)
        if p3:
            print("Print 3")
            return 3
    return 0
