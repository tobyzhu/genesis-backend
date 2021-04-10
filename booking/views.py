
from django.shortcuts import render
from django.http import HttpResponse,StreamingHttpResponse
from _datetime import datetime
from django.core import serializers
import json

from adviser.models import Bookingevent,Room,ExpvstollHung

# Create your views here.

def test(request):
    data = [
        {
            'cash01':'500',
            'cash02':'500.98'
         },
    ]
    return HttpResponse(data, content_type="application/json")

def checkpwd(request):
    userid = request.GET['userid']
    pwd = request.GET['pwd']

    data1=[
        {
            'sys_userstatus': 1
        }
    ]
    data =json.dumps(list(data1))
    return HttpResponse(data, content_type="application/json")

def querybooking(request):
    # company=request.GET['comany']
    # storecode=request.GET['storecode']
    params = request.GET['roomid']

    # roomid = request.GET['roomid']
    company = params.split(',')[0]
    storecode = params.split(',')[1]
    roomid = params.split(',')[2]
    print(company,storecode,roomid)

    thisdate = datetime.strftime(datetime.now(),'%Y%m%d')
    print(thisdate)
    booking_objs = Bookingevent.objects.filter(companyid=company,storecode=storecode,roomid=roomid,bookingstartdate=thisdate).values('bookingeventid','vcode','instrumentid','bookingstarttime','bookingendtime','ecode')

    data = json.dumps(list(booking_objs))
    return HttpResponse(data, content_type="application/json")
    # return HttpResponse(json.dumps(resp), content_type="application/json")

def queryroom(request):
    room_set = Room.objects.all().values('roomid','roomname')
    room_list =room_set[:]
    data = json.dumps(list(room_list))
    print(datetime.strftime(datetime.now(),'%H%M%S'))
    return  HttpResponse(data, content_type="application/json")

def QueryBookingStatus(request):
    # company=request.GET['comany']
    # storecode=request.GET['storecode']
    bookingeventid = request.GET['bookingeventid']
    bookingstatus = Bookingevent.objects.filter(bookingeventid=bookingeventid).values('bookingstatus')
    data = json.dumps(list(bookingstatus))
    return HttpResponse(data, content_type="application/json")

def changestatus(request):
    # company=request.GET['comany']
    # storecode=request.GET['storecode']
    # roomid = request.GET['roomid']

    params = request.GET['roomid']

    # roomid = request.GET['roomid']
    company = params.split(',')[0]
    storecode = params.split(',')[1]
    roomid = params.split(',')[2]
    print(company,storecode,roomid)

    bookingevnentid = request.GET['bookingeventid']
    status = request.GET['status']

    if status =='10':
        print('10')


    if status =='200':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus=status
        bookingevent.comeintime = datetime.strftime(datetime.now(),'%H%M%S')

    if status =='210':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus=status
        bookingevent.roomstarttime = datetime.strftime(datetime.now(),'%H%M%S')

    if status =='220':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus=status
        bookingevent.emplstarttime = datetime.strftime(datetime.now(),'%H%M%S')

    if status =='224':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus=status
        bookingevent.instrumentstarttime = datetime.strftime(datetime.now(),'%H%M%S')

    if status =='227':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus=status
        bookingevent.instrumentendtime = datetime.strftime(datetime.now(),'%H%M%S')

    if status =='230':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus=status
        bookingevent.emplendtime = datetime.strftime(datetime.now(),'%H%M%S')

    if status == '240':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.roomendtime = datetime.strftime(datetime.now(), '%H%M%S')

    if status == '250':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.callcleantime = datetime.strftime(datetime.now(), '%H%M%S')

    if status == '260':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.cleanstarttime = datetime.strftime(datetime.now(), '%H%M%S')

    if status == '270':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.cleanendtime = datetime.strftime(datetime.now(), '%H%M%S')

    if status == '290':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.leavetime = datetime.strftime(datetime.now(), '%H%M%S')



    if status == '300':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.roomstarttime = ''
        bookingevent.roomendtime = ''
        bookingevent.emplstarttime = ''
        bookingevent.emplendtime = ''
        bookingevent.callcleantime = ''
        bookingevent.cleanstarttime = ''
        bookingevent.cleanendtime = ''
        bookingevent.instrumentstarttime = ''
        bookingevent.instrumentendtime = ''
        bookingevent.canceltime = ''

    if status == '310':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.instrumentstarttime = datetime.strftime(datetime.now(), '%H%M%S')

    if status == '320':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.instrumentendtime = datetime.strftime(datetime.now(), '%H%M%S')

    if status == '390':
        bookingevent = Bookingevent.objects.get(companyid=company,storecode=storecode,bookingeventid=bookingevnentid)
        bookingevent.bookingstatus = status
        bookingevent.canceltime = datetime.strftime(datetime.now(), '%H%M%S')

    bookingevent.save()

    return  HttpResponse(200, content_type="application/json")




