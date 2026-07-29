#coding:utf-8

from django.shortcuts import render
from django.http import HttpResponse,JsonResponse,StreamingHttpResponse
from _datetime import datetime
from django.core import serializers
import json

from adviser.models import Bookingevent,Room,ExpvstollHung
from adviser.models import Timeset,Emplschedule,Instrument
from baseinfo.models import Vip,Empl
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from datetime import datetime as dt

# ========== 保留旧函数 (禁止删除，banxiaozhu 依赖) ==========
_OLD_VIEWS_MARKER = True

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


def dictfetchall(cursor):
    """将 cursor 结果转成 dict list"""
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def parse_date_str(s):
    """统一日期格式：20260728 → 2026-07-28"""
    if not s:
        return s
    s = str(s).replace('-', '')
    if len(s) == 8:
        return f'{s[:4]}-{s[4:6]}-{s[6:8]}'
    return s

def _get_company_store(request):
    """从 GET 参数或 headers 取公司门店"""
    company = request.GET.get('company') or request.headers.get('X-Company', '')
    storecode = request.GET.get('storecode') or request.headers.get('X-Storecode', '')
    return company, storecode

def _serialize_booking(b):
    """将 Bookingevent ORM 对象序列化"""
    return {
        'id': b.bookingeventid,
        'vip_uuid': str(b.vipuuid_id or ''),
        'vcode': b.vcode or '',
        'vname': b.vname or '',
        'mtcode': b.mtcode or '',
        'employee_code': b.ecode or '',
        'employee_name': '',
        'booking_date': parse_date_str(b.bookingstartdate) if b.bookingstartdate else '',
        'start_time': b.bookingstarttime or '',
        'end_time': b.bookingendtime or '',
        'room_id': b.roomid or '',
        'room_name': '',
        'instrument_id': b.instrumentid or '',
        'instrument_name': '',
        'room_start_time': b.roomstarttime or '',
        'room_end_time': b.roomendtime or '',
        'instrument_start_time': b.instrumentbookingstarttime or '',
        'instrument_end_time': b.instrumentendtime or '',
        'staff_start_time': b.emplstarttime or '',
        'staff_end_time': b.emplendtime or '',
        'status': b.bookingstatus or '100',
        'detail': b.bookingdetail or '',
        'comein_time': b.comeintime or '',
        'leave_time': b.leavetime or '',
    }

def _build_employee_dict(company, storecode):
    """构建 {ecode: ename} 字典"""
    emp = {}
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT ecode, ename FROM empl WHERE company=%s AND storecode=%s AND status='10'", [company, storecode])
            for row in cur.fetchall():
                emp[row[0]] = row[1]
    except:
        pass
    return emp

def _build_room_dict(company, storecode):
    """构建 {roomid: roomname} 字典"""
    rm = {}
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT roomid, roomname FROM room WHERE company=%s AND storecode=%s", [company, storecode])
            for row in cur.fetchall():
                rm[row[0]] = row[1]
    except:
        pass
    return rm

def _build_instrument_dict(company, storecode):
    """构建 {instrumentid: instrumentname} 字典"""
    ins = {}
    try:
        for obj in Instrument.objects.filter(storecode=storecode):
            ins[str(obj.instrumentid)] = obj.instrumentname or ''
    except:
        pass
    return ins


@csrf_exempt
def events_list(request):
    """GET /booking/events/ — 按日期查预约列表"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    company, storecode = _get_company_store(request)
    date_str = request.GET.get('date', '')
    if not date_str:
        date_str = dt.now().strftime('%Y%m%d')
    else:
        date_str = date_str.replace('-', '')

    if not company or not storecode:
        return JsonResponse({'error': '缺少公司/门店参数'}, status=400)

    emp_map = _build_employee_dict(company, storecode)
    room_map = _build_room_dict(company, storecode)
    ins_map = _build_instrument_dict(company, storecode)

    bookings = Bookingevent.objects.filter(
        companyid=company,
        storecode=storecode,
        bookingstartdate=date_str,
    ).exclude(bookingstatus='390').order_by('bookingstarttime')

    results = []
    for b in bookings:
        item = _serialize_booking(b)
        item['employee_name'] = emp_map.get(b.ecode or '', '')
        item['room_name'] = room_map.get(b.roomid or '', '')
        item['instrument_name'] = ins_map.get(str(b.instrumentid or ''), '')
        results.append(item)

    return JsonResponse({'count': len(results), 'results': results})


@csrf_exempt
def events_detail(request, event_id):
    """GET /booking/events/{id}/ — 单条预约明细"""
    company, storecode = _get_company_store(request)
    try:
        b = Bookingevent.objects.get(companyid=company, bookingeventid=event_id)
    except Bookingevent.DoesNotExist:
        return JsonResponse({'error': '预约不存在'}, status=404)

    emp_map = _build_employee_dict(company, storecode)
    room_map = _build_room_dict(company, storecode)
    ins_map = _build_instrument_dict(company, storecode)

    item = _serialize_booking(b)
    item['employee_name'] = emp_map.get(b.ecode or '', '')
    item['room_name'] = room_map.get(b.roomid or '', '')
    item['instrument_name'] = ins_map.get(str(b.instrumentid or ''), '')
    return JsonResponse(item)


@csrf_exempt
def events_create(request):
    """POST /booking/events/ — 新建预约"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': '无效的 JSON'}, status=400)

    company = data.get('company', request.headers.get('X-Company', ''))
    storecode = data.get('storecode', request.headers.get('X-Storecode', ''))
    if not company or not storecode:
        return JsonResponse({'error': '缺少公司/门店'}, status=400)

    vipuuid = data.get('vip_uuid', '')
    vcode = data.get('vcode', '')
    vname = data.get('vname', '')
    mtcode = data.get('mtcode', '')

    # 查找或创建 Vip
    vip = None
    if vipuuid:
        try:
            vip = Vip.objects.get(company=company, uuid=vipuuid)
        except:
            pass
    if not vip and vcode:
        try:
            vip = Vip.objects.get(company=company, vcode=vcode)
        except:
            pass
    if not vip:
        vip = Vip.objects.get_or_create(company=company, storecode=storecode,
            vname=vname or '散客', mtcode=mtcode or '',
            defaults={'viptype': '30', 'vcode': vcode or ''})[0]

    bookingstartdate = (data.get('booking_date') or '').replace('-', '')
    bookingstarttime = data.get('start_time', '')
    bookingendtime = data.get('end_time', '')

    bookingevent = Bookingevent.objects.create(
        companyid=company,
        storecode=storecode,
        vipuuid=vip,
        vcode=vcode or (vip.vcode if vip else ''),
        vname=vname or (vip.vname if vip else ''),
        mtcode=mtcode or (vip.mtcode if vip else ''),
        bookingstartdate=bookingstartdate,
        bookingstarttime=bookingstarttime,
        bookingendtime=bookingendtime,
        ecode=data.get('employee_code', ''),
        roomid=data.get('room_id', ''),
        roomstarttime=data.get('room_start_time', ''),
        roomendtime=data.get('room_end_time', ''),
        instrumentid=data.get('instrument_id', ''),
        instrumentbookingstarttime=data.get('instrument_start_time', ''),
        instrumentendtime=data.get('instrument_end_time', ''),
        bookingdetail=data.get('detail', ''),
        bookingstatus='100',
        operecode=data.get('operecode', ''),
        bookingflag='Y',
    )

    item = _serialize_booking(bookingevent)
    item['employee_name'] = _build_employee_dict(company, storecode).get(bookingevent.ecode or '', '')
    return JsonResponse(item, status=201)


@csrf_exempt
def events_update(request, event_id):
    """PUT /booking/events/{id}/ — 更新预约"""
    if request.method != 'PUT':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': '无效的 JSON'}, status=400)

    company = data.get('company', request.headers.get('X-Company', ''))
    storecode = data.get('storecode', request.headers.get('X-Storecode', ''))
    if not company:
        company, _ = _get_company_store(request)

    try:
        b = Bookingevent.objects.get(companyid=company, bookingeventid=event_id)
    except Bookingevent.DoesNotExist:
        return JsonResponse({'error': '预约不存在'}, status=404)

    # 更新字段（只更新传了的）
    def _update_if(key, model_field):
        if key in data:
            setattr(b, model_field, data[key])

    _update_if('booking_date', 'bookingstartdate')
    _update_if('start_time', 'bookingstarttime')
    _update_if('end_time', 'bookingendtime')
    _update_if('vcode', 'vcode')
    _update_if('vname', 'vname')
    _update_if('mtcode', 'mtcode')
    _update_if('employee_code', 'ecode')
    _update_if('room_id', 'roomid')
    _update_if('room_start_time', 'roomstarttime')
    _update_if('room_end_time', 'roomendtime')
    _update_if('instrument_id', 'instrumentid')
    _update_if('instrument_start_time', 'instrumentbookingstarttime')
    _update_if('instrument_end_time', 'instrumentendtime')
    _update_if('detail', 'bookingdetail')
    if 'booking_date' in data:
        b.bookingstartdate = data['booking_date'].replace('-', '')

    b.save()
    return JsonResponse({'status': 'ok'})


_STATUS_TRANSITIONS = {
    '200': 'comeintime',       # 到店
    '210': 'roomstarttime',    # 进房间
    '220': 'emplstarttime',    # 开始服务
    '224': 'instrumentstarttime',  # 仪器开始
    '227': 'instrumentendtime',    # 仪器结束
    '230': 'emplendtime',      # 服务结束
    '240': 'roomendtime',      # 离房
    '250': 'callcleantime',    # 呼叫清洁
    '260': 'cleanstarttime',   # 开始清洁
    '270': 'cleanendtime',     # 清洁结束
    '290': 'leavetime',        # 离店
    '390': 'canceltime',       # 取消
}

_VALID_NEXT_STATUSES = {
    '100': ['200', '390'],
    '200': ['210', '220', '390'],
    '210': ['220', '390'],
    '220': ['224', '227', '230', '390'],
    '224': ['227', '390'],
    '227': ['230', '390'],
    '230': ['240', '250', '290', '390'],
    '240': ['250', '290'],
    '250': ['260'],
    '260': ['270'],
    '270': ['290'],
}

@csrf_exempt
def events_status(request, event_id):
    """POST /booking/events/{id}/status/ — 状态变更（自由流转，仅记录时间戳）"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    company, storecode = _get_company_store(request)
    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': '无效的 JSON'}, status=400)

    new_status = data.get('status', '')
    try:
        b = Bookingevent.objects.get(companyid=company, bookingeventid=event_id)
    except Bookingevent.DoesNotExist:
        return JsonResponse({'error': '预约不存在'}, status=404)

    # 记录时间戳
    time_field = _STATUS_TRANSITIONS.get(new_status)
    now_str = dt.now().strftime('%H%M%S')
    if time_field:
        setattr(b, time_field, now_str)
    if new_status == '390':
        b.canceltime = now_str

    b.bookingstatus = new_status
    b.save()

    return JsonResponse({
        'status': 'ok',
        'booking_status': new_status,
        'timestamp': now_str,
    })


@csrf_exempt
def events_cancel(request, event_id):
    """POST /booking/events/{id}/cancel/ — 快捷取消"""
    # 直接调用 status 逻辑，避免 body 读取问题
    import types
    body = json.dumps({'status': '390'})
    request._body = body.encode()


@csrf_exempt
def events_check_conflicts(request, event_id):
    """GET /booking/events/{id}/check-conflicts/ — 冲突检测"""
    company, storecode = _get_company_store(request)
    start_time = request.GET.get('start_time')
    end_time = request.GET.get('end_time')
    employee_code = request.GET.get('employee_code', '')
    room_id = request.GET.get('room_id', '')
    instrument_id = request.GET.get('instrument_id', '')

    conflicts = []
    today = request.GET.get('date', '').replace('-', '')
    if not today:
        today = dt.now().strftime('%Y%m%d')

    if employee_code and start_time and end_time:
        overlap = Bookingevent.objects.filter(
            companyid=company, storecode=storecode,
            bookingstartdate=today,
            ecode=employee_code,
            bookingstarttime__lt=end_time,
            bookingendtime__gt=start_time,
        ).exclude(bookingstatus__in=['290', '390']).exclude(bookingeventid=event_id)
        for o in overlap:
            conflicts.append({
                'type': 'employee_time',
                'booking_id': o.bookingeventid,
                'vname': o.vname or '',
                'start': o.bookingstarttime or '',
                'end': o.bookingendtime or '',
            })

    if room_id and start_time and end_time:
        room_overlap = Bookingevent.objects.filter(
            companyid=company, storecode=storecode,
            bookingstartdate=today,
            roomid=room_id,
            bookingstarttime__lt=end_time,
            bookingendtime__gt=start_time,
        ).exclude(bookingstatus__in=['290', '390']).exclude(bookingeventid=event_id)
        for o in room_overlap:
            conflicts.append({
                'type': 'room',
                'booking_id': o.bookingeventid,
                'vname': o.vname or '',
                'start': o.bookingstarttime or '',
                'end': o.bookingendtime or '',
            })

    return JsonResponse({'conflicts': conflicts})


@csrf_exempt
def timesets_list(request):
    """GET /booking/timesets/ — 门店时段模板列表"""
    company, storecode = _get_company_store(request)
    qs = Timeset.objects.all().order_by('timeid')
    results = [{'timeid': t.timeid, 'flag': t.flag} for t in qs]
    return JsonResponse({'results': results})


@csrf_exempt
def schedules_list(request):
    """GET /booking/schedules/ — 员工排班查询"""
    company, storecode = _get_company_store(request)
    date_str = request.GET.get('date', dt.now().strftime('%Y%m%d')).replace('-', '')
    if not company or not storecode:
        return JsonResponse({'results': []})

    qs = Emplschedule.objects.filter(
        company=company, storecode=storecode,
        vsdate=date_str,
    ).order_by('ecode')

    results = []
    for s in qs:
        results.append({
            'ecode': s.ecode or '',
            'scheduleid': s.scheduleid or '',
            'operno': s.operno or '',
            'flag': s.flag or '',
        })
    return JsonResponse({'results': results})


@csrf_exempt
def employees_list(request):
    """GET /booking/employees/ — 可预约员工列表"""
    company, storecode = _get_company_store(request)
    if not company or not storecode:
        return JsonResponse({'results': []})

    with connection.cursor() as cur:
        cur.execute(
            "SELECT a.ecode, a.ename, a.position, b.positiondesc "
            "FROM empl a, position b "
            "WHERE a.company=%s AND a.storecode=%s "
            "and a.company=b.company "
            "AND a.POSITION = b.positioncode "
            "AND a.status='Y' "
            "AND a.flag='Y' "
            "AND b.bookingflag='Y' "
            "AND b.flag='Y'",
            [company, storecode]
        )
        rows = dictfetchall(cur)

    return JsonResponse({'results': rows})


@csrf_exempt
def rooms_list(request):
    """GET /booking/rooms/ — 门店房间列表"""
    company, storecode = _get_company_store(request)
    qs = Room.objects.filter(storecode=storecode)
    results = [{'roomid': r.roomid, 'roomname': r.roomname} for r in qs]
    return JsonResponse({'results': results})


@csrf_exempt
def instruments_list(request):
    """GET /booking/instruments/ — 门店仪器列表"""
    company, storecode = _get_company_store(request)
    qs = Instrument.objects.filter(storecode=storecode)
    results = [{'instrumentid': str(r.instrumentid), 'instrumentname': r.instrumentname} for r in qs]
    return JsonResponse({'results': results})

@csrf_exempt
def schedules_save(request):
    """POST /booking/schedules/save/ — 批量保存排班"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    company, storecode = _get_company_store(request)
    if not company or not storecode:
        return JsonResponse({'error': '缺少公司/门店'}, status=400)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({'error': '无效的 JSON'}, status=400)

    items = data.get('schedules', [])
    if not items:
        return JsonResponse({'error': '排班数据为空'}, status=400)

    saved = 0
    for item in items:
        ecode = item.get('ecode', '')
        vsdate = str(item.get('vsdate', '')).replace('-', '')
        scheduleid = item.get('scheduleid', '')
        if not ecode or not vsdate:
            continue

        obj, created = Emplschedule.objects.update_or_create(
            company=company,
            storecode=storecode,
            vsdate=vsdate,
            ecode=ecode,
            defaults={'scheduleid': scheduleid if scheduleid else None}
        )
        saved += 1

    return JsonResponse({'status': 'ok', 'saved': saved})


@csrf_exempt
def shift_list(request):
    """GET /booking/schedules/shift-list/ — 班次列表"""
    from common.constants import SCHEDULELIST
    results = [{'value': v, 'label': l} for v, l in SCHEDULELIST]
    return JsonResponse({'results': results})
