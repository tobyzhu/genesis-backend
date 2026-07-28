
from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse,JsonResponse
from datetime import datetime
from django.core import serializers
from django.db.models import Q,Avg,Sum,Count,Max,Min
import uuid

from common.legacy_db import connect_jmj_read, connect_jmj_write

from jmj.models import ReportPeriod,PeriodData,OldData
from baseinfo.models import Goods,Storeinfo,Wharehouse,Vip,Supplier
from cashier.models import Expvstoll,Expense
from goods.models import Goodstranslog,Salehead,Saledtl,Transhead,Transdtl
import common.constants
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def ReadAndWrite(fromdate, todate):
    # for i in range(len(readDB)):
    #     fromdate ='20190101'
    #     todate ='20190102'

        read = connect_jmj_read()
        Rcursor = read.cursor()
        # readsql = "  select sukid,saleatr, vdate,tmount, '1-2' storecode, '1-2' whcode, seqbar,a.gcode gcode, disc, qty1,qty2,qty3, price1, amount1 "\
        #           "  from goodstranslog a, goods b "\
        #           "  where 1=1 "\
        #           "  and a.vdate between "+ fromdate +" and " + todate + "  "\
        #           "  and a.gcode = b.gcode "\
        #           "  and b.brand='900' "


        readsql = "  select sukid,saleatr, vdate,tmount, '1' storecode, '1-2' whcode, seqbar,a.gcode gcode, disc, qty1,qty2,qty3, price1, amount1 " \
                  "  from goodstranslog a, goods b " \
                  "  where 1=1 " \
                  "and  a.saleatr = 'G' and a.vdate between " + fromdate + " and " + todate + "  " \
                                                                           "  and a.gcode = b.gcode " \
                                                                           "  and b.brand='900' and sukid='01_EXPVSTOLL_28504' "

        Rcursor.execute(readsql)
        readResult = Rcursor.fetchall()
        for value in readResult:
            write = connect_jmj_write()
            Wcursor = write.cursor()
            getgcodemirrorsql = "select gcode2011 from gcodemirror where gcode ='" +value[7]+"'"
            print(getgcodemirrorsql)
            Wcursor.execute(getgcodemirrorsql)
            gcode = Wcursor.fetchone()[0]
            print('gcodemirror',value[2],value[7],gcode)
            checkcdr = "select sukid from goodstranslog where sukid='"+value[0]+"' and seqbar='"+ value[6]+"' and saleatr='G' and storecode= '" + value[4] +"' "
            print(checkcdr)
            Wcursor.execute(checkcdr)
            print(Wcursor.fetchone()[0],Wcursor.rownumber,Wcursor.rowcount,Wcursor.connecti)
            cnt = Wcursor.rowcount
            print('cnt,gcode,len',cnt,gcode,len(gcode))
            if cnt == 0 and len(gcode) > 0:
                print('before writesql')
                writeSql = "INSERT INTO goodstranslog(sukid,saleatr,vdate,tmount,storecode,whcode,seqbar,gcode,disc,qty1,qty2,qty3,price1,amount1,company,companyid) " \
                           " VALUES ('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s' , '%s', '%s', '%s', '%s', '%s'  )" %\
                           (value[0], value[1], value[2], value[3], value[4],value[5], value[6], gcode, value[8], value[9],value[10], value[11], value[12], value[13],'JMJ','JMJ' )
                print('after writesq;',writeSql)
                try:
                    Wcursor.execute(writeSql)
                    print('before commit')
                    write.commit()
                    print('1','1-2',value[2],value[5],value[6],'inserted')
                except:
                    write.rollback()
                    print('2','1-2',value[2],value[5],value[6],'rollback')
                print('before close')
                write.close()
                print('after close')
            else:
                print('skip')
        read.close()
        return 0

# 补传销售单据到goodstranslog
def FillSalesTransToLog(company,storecode,fromdate, todate):
    trans2 = Expvstoll.objects.filter(company=company,storecode=storecode,valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate,exptxserno='yfy04_EXPVSTOLL_8686').order_by('vsdate')

    for tran2 in trans2:
        vip = Vip.objects.get(company=company, flag='Y', uuid=tran2.vipuuid.uuid)
        if vip.vcode ==None:
            vip.vcode=''
        if vip.vname==None:
            vip.vname=''

        try:
            tx = Goodstranslog.objects.get(company=company,storecode=tran2.storecode,sukid=tran2.exptxserno)
            # tx =  Goodstranslog.objects.get(company=company,storecode=tran2.storecode,transuuid=tran2.uuid)
            print(tran2.exptxserno,tran2.vsdate,'skipped')
        except:
            items = Expense.objects.filter(company=company).filter(storecode=tran2.storecode,ttype='G',transuuid=tran2)
            store = Storeinfo.objects.get(company=company,storecode=tran2.storecode)
            for item in items:
                try:
                    # goodstranslog = Goodstranslog.objects.get(company=company,transuuid=item.transuuid,seqbar=item.ditem)
                    goodstranslog = Goodstranslog.objects.get(company=company,exptxserno=item.exptxserno,seqbar=item.ditem)
                    print('1')
                    print('2',str(uuid.uuid4()).replace('-','') )
                    # print('2')
                    goodstranslog.uuid =str(uuid.uuid4()).replace('-','')
                    print('goodstranslog.uuid',goodstranslog.uuid)
                    # goodstranslog.vdate=tran2.vsdate
                    # goodstranslog.sumdisc=tran2.sumdisc
                    # goodstranslog.tmount=tran2.totmount
                    # goodstranslog.ecode=tran2.ecode
                    # goodstranslog.companyid=tran2.company
                    # goodstranslog.storecode=tran2.storecode
                    # goodstranslog.whcode=store.salewhcode
                    # goodstranslog.gcode=item.srvcode
                    # goodstranslog.qty1=item.s_qty
                    # goodstranslog.price1=item.s_price
                    # goodstranslog.amount1=item.s_mount
                    # goodstranslog.company=tran2.company
                    # goodstranslog.creater=tran2.creater
                    # goodstranslog.transuuid=tran2.uuid
                    # goodstranslog.transdesc=vip.vname+'-'+vip.vcode
                    goodstranslog.save()
                    print(goodstranslog.sukid,goodstranslog.gcode,'is skipped!')
                except:
                    goodstranslog = Goodstranslog.objects.create(sukid=tran2.exptxserno,saleatr=item.ttype,vdate=tran2.vsdate,sumdisc=tran2.sumdisc,
                                                 tmount=tran2.totmount,ecode=tran2.ecode,
                                                 companyid=tran2.company,storecode=tran2.storecode,whcode=store.salewhcode,
                                                 seqbar=item.ditem,gcode=item.srvcode,qty1=item.s_qty,price1=item.s_price,amount1=item.s_mount,uuid=str(uuid.uuid4()).replace('-',''),
                                                 company=tran2.company,creater=tran2.creater,transuuid=tran2.uuid,transdesc=vip.vname+'-'+vip.vcode,ioflag='1')
                    goodstranslog.set_qty2()
                    goodstranslog.set_qty3()
                    print(goodstranslog.sukid,goodstranslog.gcode,'is created!')



    return 0

# 从goodstranslog中删除掉作废的商品销售单记录
def DelInvaildTrans(company, fromdate,todate):
    trans2 = Expvstoll.objects.filter(company=company,flag='N').filter(valiflag='N').filter(vsdate__gte=fromdate).filter(
        vsdate__lte=todate)
    print(trans2)

    for tran2 in trans2:
        try:
            txs = Goodstranslog.objects.filter(company=company, storecode=tran2.storecode, sukid=tran2.exptxserno)
            for tx in txs:
                tx.delete()
                # tx.save()
                print(tran2.exptxserno, ' deleted')
        except:
            print(tran2.exptxserno,  'skipped!')

    return 0

# 已经转出确认，但goodstranglog中没有记录，目前yfy总部转出经常出现这个问题
# def FillTransdtl(request):
def FillTransdtl(company, fromdate):
    # try:
    #     fromdate=request.GET['fromdate']
    # except:
    #     fromdate='20190901'

    uuid=''
    saleatr='TO'
    doccode=''
    trans2 = Transhead.objects.filter(flag='Y',company=company,vdate__gte=fromdate,status='20')
    print(fromdate,trans2)

    for tran2 in trans2:
        print(tran2.company,tran2.outstore,tran2.outwhcode,saleatr,tran2.sukid, tran2.doccode)

        logs = Goodstranslog.objects.filter(company=tran2.company,storecode=tran2.outstore,whcode=tran2.outwhcode,sukid=tran2.sukid,saleatr=saleatr).count()
        print('logs exists counts:',logs)
        if logs==0:
            print('create:', tran2.outstore, tran2.outwhcode, tran2.sukid, tran2.doccode)
            items = Transdtl.objects.filter(company=tran2.company).filter(transheadid_id=tran2.uuid)
            for item in items:
                print('create:',tran2.outstore,tran2.outwhcode,tran2.sukid,tran2.doccode,item.seqbar,item.gcode,item.qty)
                goodstranslog = Goodstranslog.objects.create(sukid=tran2.sukid,doccode=tran2.doccode,saleatr=saleatr,vdate=tran2.vdate,sumdisc=tran2.smndisc,
                                             tmount=tran2.tmount,ecode=tran2.ecode,
                                             companyid=tran2.company,storecode=tran2.outstore,whcode=tran2.outwhcode,
                                             seqbar=item.seqbar,gcode=item.gcode,qty1=item.qty,price1=item.price,amount1=item.mount,
                                             company=tran2.company,creater='sys_filler')
                print('created:',goodstranslog.gcode,goodstranslog.saleatr)
                goodstranslog.set_qty2()
                goodstranslog.set_qty3()
                # goodstranslog.save()

    return HttpResponse(0, content_type="application/json")

def ProcessDupGoodstranslog(request):
    company=request.GET['company']
    presukid=''
    preseqbar=''
    cnt=0
    saleatr='G'
    # sukid='00_salehead_72'
    trans = Goodstranslog.objects.filter(company=company,saleatr=saleatr,create_time__gte='2021-03-19').order_by('sukid','seqbar')
    for tran in trans:
        # print(tran.sukid,tran.seqbar)
        thissukid=tran.sukid
        thistransuuid = tran.transuuid
        thisseqbar=tran.seqbar
        trans2= Goodstranslog.objects.filter(company=company,saleatr=saleatr,transuuid=tran.transuuid,seqbar=tran.seqbar).order_by('gtranukid')
        cnt=1
        for tran2 in trans2:
            if cnt >1:
                tran2.areacode='N'
                print(tran2.sukid,tran2.seqbar,tran2.gcode,tran2.gtranukid,'is dup!')
                tran2.save()
            cnt =cnt+1

    return HttpResponse(0, content_type="application/json")

def RecalcuteGoodsTransLog(company, storecode, fromdate,todate):
    whcodes = Wharehouse.objects.filter(flag='Y',company=company,storecode=storecode)
    # print(whcodes)
    for whcode in whcodes:
        print(whcode)

        goodstranslogs = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode,vdate__gte=fromdate,vdate__lte=todate).order_by('gtranukid')
        for goodstranslog in goodstranslogs:
            goodstranslog.set_goodsuuid()
            goodstranslog.set_qty2()
            goodstranslog.set_qty3()


    return HttpResponse(0, content_type="application/json")

# 按门店重新计算goodstranslog的库存数据
def RecalcuteGoodsTransLogByStorecode(request):
    try:
        company=request.GET['company']
    except:
        company='demo'

    try:
        storecode=request.GET['storecode']
    except:
        storecode='00'

    try:
        fromdate= request.GET['fromdate']
    except:
        fromdate= datetime.strftime(datetime.today(),'%Y%m%d')
        print(datetime.strftime(datetime.today(),'%Y%m%d'))

    try:
        todate= request.GET['todate']
    except:
        todate= datetime.strftime(datetime.today(),'%Y%m%d')
        print(datetime.strftime(datetime.today(),'%Y%m%d'))

    whcodes = Wharehouse.objects.filter(flag='Y',company=company,storecode=storecode)
    for whcode in whcodes:
        print(whcode)
        goodstranslogs = Goodstranslog.objects.filter(company=company,whcode=whcode.wharehousecode,vdate__gte=fromdate,vdate__lte=todate).order_by('gtranukid')
        for goodstranslog in goodstranslogs:
            goodstranslog.set_goodsuuid()
            goodstranslog.set_qty2()
            goodstranslog.set_qty3()
    return HttpResponse(0, content_type="application/json")

def daily():
    company='yiren'
    fromdate = ( datetime.date.today() + datetime.timedelta(days=-1) ).strftime('%Y%m%d')
    todate = datetime.date.today().strftime('%Y%m%d')

    trans = Expvstoll.objects.filter(company=company, flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)
    for tran in trans:
        tran.set_oldcustflag()

    return 0

def ProcessGoods(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    try:
        storelist = request.GET['storelist']
    except:
        storelist = ['00','01','02','03','04']

    fromdate = request.GET['fromdate']
    todate = request.GET['todate']

    # trans = Expvstoll.objects.filter(company=company, flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)

    # for tran in trans:
    #     tran.set_oldcustflag()
    print(company,fromdate,todate)

    if company=='JMJ':
        # 从营业部取吉祥物销售数据 到JMJ系统
        ReadAndWrite(fromdate,todate)
        #
        # 把JMJ作废的交易，从GOODSTRANSLOG中取消

        DelInvaildTrans(company,fromdate,todate)

    # 把未记录goodstranslog的销售记录，补充进去
    # FillSalesTransToLog(company,'04',fromdate,todate)


    # 作废的交易，从GOODSTRANSLOG中取消
    # DelInvaildTrans(company,fromdate,todate)

    #重新计算GOODSTRANSLOG中qty2, qty3
    for storecode in storelist:
        # FillSalesTransToLog(company,storecode,fromdate,todate)
        RecalcuteGoodsTransLog(company,storecode,fromdate,todate)
        print(storecode)
    return HttpResponse("完成！", content_type="application/json")

def tmp_f(request):
    company='yiren'
    storelist =('01','02','03','04')
    fromdate = '20200510'
    todate = '20200612'
    goodstrans = Goodstranslog.objects.filter(company=company,storecode__in=storelist,saleatr='G',vdate__gte=fromdate,vdate__lte=todate,qty2__lt=0)
    for goodstx in goodstrans:
        tranx = Expvstoll.objects.get(company=company,uuid=goodstrans.transuuid)
        gcodetransdetail = Goodstranslog.objects.filter(company=company,storecode=goodstx.storecode,vdate__gte=fromdate)
        # if

def get_goodstockqty(request):
    company = request.GET['company']
    storecode = request.GET['storecode']
    gcode = request.GET['gcode']
    stockdate = datetime.strftime( datetime.now()  ,'%Y%m%d')
    try:
        salewhcode = Storeinfo.objects.get(flag='Y',company=company,storecode=storecode).salewhcode
        stockqty = Goodstranslog.objects.filter(company=company,whcode=salewhcode,gcode=gcode).order_by('-create_time').first().qty2
        print('stockqty',company,salewhcode,gcode,stockqty)
    except Exception as e:
        print(e)
        stockqty=0
        print('stockqty error',e,company,salewhcode,gcode,stockqty)

    return HttpResponse(stockqty, content_type="application/json")

class GoodsReport_yfy(object):
    def __init__(self, **kwargs):
        self.company = kwargs.get('company', 'yiren')
        self.storelist = kwargs.get('storecode', '01,02,03,04').split(',')
        self.fromdate = '20210101'
        self.todate = '20211231'

    def get_basedate(self):
        # inqty = Goodstranslog.objects.filter(company=self.company,vdate__gte=self.fromdate,vdate__lte=self.todate,saleatr='I').\
        #     values('goodsuuid__brand').annotate(inqty=Sum('qty1'))
        # outqty = Goodstranslog.objects.filter(company=self.company,vdate__gte=self.fromdate,vdate__lte=self.todate,saleatr__in=('G','F','U')).\
        #     values('goodsuuid__brand').annotate(inqty=Sum('qty1'))
        lastqty = Goodstranslog.objects.filter(company=self.company,vdate__lte=self.todate).values('gcode').annotate(gtranukid=Max('gtranukid'))
        # stockqty = Goodstranslog.objects.filter(company=self.company,vdate__lte=self.todate).order_by('-create_time').first().qty2
        print('goodstranslog',lastqty)

# .values('vipuuid__ecode2').annotate(trans_vip_cnt=Count('vipuuid', distinct=True),trans_vip_times=Count(Concat('vipuuid','vsdate'), distinct=True))

def yfy_goodsreport(request):
    param = {
        'company': 'yiren',
        'storelist': '01,02,03,04',
        'fromdate': '20211201',
        'todate': '20211231'
    }
    print('param',param)
    goodsreport = GoodsReport_yfy(**param)
    # 计算每个美疗师，每个个月份所分配到的护理师的数量
    # emplcnt_df = emplreport.get_empl_vip_cnt_by_month()

    # 取某月的报表，统计前几个月的数据
    total_df = goodsreport.get_basedate()

    return  HttpResponse('200')
# ===== 商品进出货管理 API =====

@csrf_exempt
def wharehouse_list(request):
    """GET 仓库列表 /goods/wharehouses/"""
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '')
    filters = {'company': company, 'flag': 'Y'}
    if storecode:
        filters['storecode'] = storecode
    whs = Wharehouse.objects.filter(**filters).values('wharehousecode', 'wharehousename', 'storecode')
    return JsonResponse(list(whs), safe=False)


@csrf_exempt
def stock_query(request):
    """GET 库存查询 /goods/stock-query/"""
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '')
    whcode = request.GET.get('whcode', '')
    search = request.GET.get('search', '')

    params = [company]
    where_extra = ''
    if storecode:
        where_extra += ' AND t.storecode = %s'
        params.append(storecode)
    if whcode:
        where_extra += ' AND t.whcode = %s'
        params.append(whcode)

    sql = """
        SELECT t.storecode, t.whcode, t.gcode, t.qty2, t.vdate,
               g.gname, g.spec, g.brand, g.unit, g.minivalues, g.maxvalues,
               g.uuid
        FROM goodstranslog t
        JOIN (
            SELECT storecode, whcode, gcode, MAX(gtranukid) as max_id
            FROM goodstranslog
            WHERE company = %s
            GROUP BY storecode, whcode, gcode
        ) latest ON t.storecode = latest.storecode
                 AND t.whcode = latest.whcode
                 AND t.gcode = latest.gcode
                 AND t.gtranukid = latest.max_id
        LEFT JOIN goods g ON t.gcode = g.gcode AND t.company = g.company
        WHERE 1=1
    """ + where_extra

    if search:
        sql += ' AND (t.gcode LIKE %s OR g.gname LIKE %s)'
        params.extend(['%' + search + '%', '%' + search + '%'])

    sql += ' ORDER BY t.gcode'

    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        rows = cursor.fetchall()

    result = []
    for row in rows:
        stock_qty = float(row[3] or 0)
        minv = float(row[9] or 0)
        maxv = float(row[10] or 0)
        alert = 'normal'
        if minv > 0 and stock_qty <= minv:
            alert = 'low'
        elif maxv > 0 and stock_qty >= maxv:
            alert = 'high'
        result.append({
            'storecode': row[0],
            'whcode': row[1],
            'gcode': row[2],
            'qty': stock_qty,
            'vdate': row[4] or '',
            'gname': row[5] or '',
            'spec': row[6] or '',
            'brand': row[7] or '',
            'unit': row[8] or '',
            'minivalues': minv,
            'maxvalues': maxv,
            'goodsuuid': row[11] or '',
            'alert': alert,
        })

    return JsonResponse(result, safe=False)


def _next_sukid(prefix='ST'):
    """生成单据号 ST + YYYYMMDD + 4位序号"""
    today = datetime.now().strftime('%Y%m%d')
    key = prefix + today
    seq = str(uuid.uuid4().int)[-4:]
    return key + seq

@csrf_exempt

def inbound_create(request):
    """POST 入库单(草稿) /goods/inbound/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    company = data.get('company', '')
    storecode = data.get('storecode', '')
    whcode = data.get('whcode', '')
    vdate = data.get('vdate', datetime.now().strftime('%Y%m%d'))
    note = data.get('note', '')
    supplierid = data.get('supplierid', '')
    items = data.get('items', [])
    supplierid = data.get('supplierid', '')
    ecode = data.get('ecode', '')

    if not all([company, storecode, whcode, items]):
        return JsonResponse({'error': '缺少必要参数'}, status=400)

    sukid = _next_sukid('IN')
    doccode = sukid

    # 创建 Salehead 草稿
    head = Salehead.objects.create(
        company=company, storecode=storecode,
        sukid=sukid, doccode=doccode, saleatr='I',
        vdate=vdate, inwhcode=whcode, instorecode=storecode,
        supplierid=supplierid,
        ecode=ecode, gnote=note,
        status='10', creater='pc_stock',
    )

    created = []
    for idx, item in enumerate(items):
        gcode = item.get('gcode', '')
        qty = float(item.get('qty', 0))
        price = float(item.get('price', 0))
        amount = qty * price
        goodsvaldate = item.get('goodsvaldate', '')
        seqbar = f'{idx+1:04d}'
        if qty <= 0:
            continue
        Saledtl.objects.create(
            company=company, storecode=storecode,
            saleheadid=head, sukid=sukid, seqbar=seqbar,
            gcode=gcode, qty=qty, price=price, mount=amount,
            goodsvaldate=goodsvaldate,
            creater='pc_stock',
        )
        created.append({'seqbar': seqbar, 'gcode': gcode, 'qty': qty})

    return JsonResponse({'success': True, 'sukid': sukid, 'status': '10', 'items': created})


@csrf_exempt
def outbound_create(request):
    """POST 出库单(草稿) /goods/outbound/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    company = data.get('company', '')
    storecode = data.get('storecode', '')
    whcode = data.get('whcode', '')
    vdate = data.get('vdate', datetime.now().strftime('%Y%m%d'))
    note = data.get('note', '')
    supplierid = data.get('supplierid', '')
    out_type = data.get('out_type', 'O')
    items = data.get('items', [])
    ecode = data.get('ecode', '')

    if not all([company, storecode, whcode, items]):
        return JsonResponse({'error': '缺少必要参数'}, status=400)
    if out_type not in ('O', 'U', 'F'):
        return JsonResponse({'error': '出库类型无效'}, status=400)

    sukid = _next_sukid('OUT')
    doccode = sukid

    head = Salehead.objects.create(
        company=company, storecode=storecode,
        sukid=sukid, doccode=doccode, saleatr=out_type,
        vdate=vdate, outwhcode=whcode,
        ecode=ecode, gnote=note,
        supplierid=supplierid,        status='10', creater='pc_stock',
    )

    created = []
    for idx, item in enumerate(items):
        gcode = item.get('gcode', '')
        qty = float(item.get('qty', 0))
        price = float(item.get('price', 0))
        amount = qty * price
        seqbar = f'{idx+1:04d}'
        if qty <= 0:
            continue
        Saledtl.objects.create(
            company=company, storecode=storecode,
            saleheadid=head, sukid=sukid, seqbar=seqbar,
            gcode=gcode, qty=qty, price=price, mount=amount,
            creater='pc_stock',
        )
        created.append({'seqbar': seqbar, 'gcode': gcode, 'qty': qty})

    return JsonResponse({'success': True, 'sukid': sukid, 'status': '10', 'items': created})


@csrf_exempt
def transfer_create(request):
    """POST 调拨单(草稿) /goods/transfer/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    company = data.get('company', '')
    out_storecode = data.get('out_storecode', '')
    out_whcode = data.get('out_whcode', '')
    in_storecode = data.get('in_storecode', '')
    in_whcode = data.get('in_whcode', '')
    vdate = data.get('vdate', datetime.now().strftime('%Y%m%d'))
    note = data.get('note', '')
    supplierid = data.get('supplierid', '')
    items = data.get('items', [])
    ecode = data.get('ecode', '')

    if not all([company, out_storecode, out_whcode, in_storecode, in_whcode, items]):
        return JsonResponse({'error': '缺少必要参数'}, status=400)

    sukid = _next_sukid('TR')
    doccode = sukid

    head = Transhead.objects.create(
        company=company,
        sukid=sukid, doccode=doccode, saleatr='20',
        vdate=vdate,
        outstore=out_storecode, outwhcode=out_whcode,
        instore=in_storecode, towhcode=in_whcode,
        ecode=ecode, gnote=note,
        status='10', creater='pc_stock',
    )

    created = []
    for idx, item in enumerate(items):
        gcode = item.get('gcode', '')
        qty = float(item.get('qty', 0))
        price = float(item.get('price', 0))
        amount = qty * price
        seqbar = f'{idx+1:04d}'
        if qty <= 0:
            continue
        Transdtl.objects.create(
            company=company,
            transheadid=head, sukid=sukid, seqbar=seqbar,
            gcode=gcode, qty=qty, price=price, mount=amount,
        )
        created.append({'seqbar': seqbar, 'gcode': gcode, 'qty': qty})

    return JsonResponse({'success': True, 'sukid': sukid, 'status': '10', 'items': created})


# ===== 确认 / 作废 / 列表 =====

def _confirm_salehead_translog(head):
    """确认 Salehead 时写入 Goodstranslog"""
    items = Saledtl.objects.filter(company=head.company, sukid=head.sukid)
    for item in items:
        is_in = head.saleatr == 'I'
        saleatr_val = head.saleatr if is_in else head.saleatr
        wh = head.inwhcode if is_in else head.outwhcode
        ioflag = '1' if is_in else '0'
        log = Goodstranslog.objects.create(
            sukid=head.sukid, doccode=head.doccode or '',
            saleatr=saleatr_val, vdate=head.vdate or '',
            storecode=head.storecode or '', whcode=wh or '',
            gcode=item.gcode, qty1=item.qty, price1=item.price,
            amount1=item.mount, goodsvaldate=item.goodsvaldate or '',
            batch=item.batch or '', gnote=head.gnote or '',
            ecode=head.ecode or '',
            company=head.company, companyid=head.company,
            ioflag=ioflag, creater='pc_confirm',
            uuid=str(uuid.uuid4()).replace('-', ''),
        )
        log.set_qty2()
        if item.goodsvaldate:
            log.set_qty3()


@csrf_exempt
def confirm_document(request):
    """POST 确认单据 /goods/confirm/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    company = data.get('company', '')
    sukid = data.get('sukid', '')
    ecode = data.get('ecode', '')

    if not company or not sukid:
        return JsonResponse({'error': '缺少参数 company/sukid'}, status=400)

    # 尝试 Salehead（入库/出库）
    try:
        head = Salehead.objects.get(company=company, sukid=sukid, status='10')
    except Salehead.DoesNotExist:
        head = None

    if head:
        # 出库验库存
        if head.saleatr in ('O', 'U', 'F'):
            items = Saledtl.objects.filter(company=company, sukid=sukid)
            for item in items:
                wh = head.outwhcode or ''
                try:
                    latest = Goodstranslog.objects.filter(
                        company=company, storecode=head.storecode,
                        whcode=wh, gcode=item.gcode
                    ).latest()
                    stock_qty = float(latest.qty2 or 0)
                except Goodstranslog.DoesNotExist:
                    stock_qty = 0
                if stock_qty < float(item.qty or 0):
                    return JsonResponse({
                        'error': '库存不足', 'gcode': item.gcode,
                        'stock': stock_qty, 'required': float(item.qty or 0),
                    }, status=400)

        # 写入 Goodstranslog
        _confirm_salehead_translog(head)
        head.status = '20'
        head.emp_ecode = ecode
        head.save()
        return JsonResponse({'success': True, 'type': 'salehead', 'sukid': sukid, 'status': '20'})

    # 尝试 Transhead（调拨）
    try:
        head = Transhead.objects.get(company=company, sukid=sukid, status='10')
    except Transhead.DoesNotExist:
        return JsonResponse({'error': '单据不存在或不是草稿状态'}, status=404)

    # 调拨验调出库存
    items = Transdtl.objects.filter(company=company, sukid=sukid)
    for item in items:
        try:
            latest = Goodstranslog.objects.filter(
                company=company, storecode=head.outstore,
                whcode=head.outwhcode, gcode=item.gcode
            ).latest()
            stock_qty = float(latest.qty2 or 0)
        except Goodstranslog.DoesNotExist:
            stock_qty = 0
        if stock_qty < float(item.qty or 0):
            return JsonResponse({
                'error': '调出库存不足', 'gcode': item.gcode,
                'stock': stock_qty, 'required': float(item.qty or 0),
            }, status=400)

    # 调现成的 set_goodstranslog()
    head.ecode = ecode
    head.set_goodstranslog()
    head.status = '20'
    head.save()
    return JsonResponse({'success': True, 'type': 'transhead', 'sukid': sukid, 'status': '20'})


@csrf_exempt
def cancel_document(request):
    """POST 作废单据 /goods/cancel/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)
    company = data.get('company', '')
    sukid = data.get('sukid', '')
    if not company or not sukid:
        return JsonResponse({'error': '缺少参数'}, status=400)

    for model_cls in (Salehead, Transhead):
        try:
            head = model_cls.objects.get(company=company, sukid=sukid)
            if head.status == '90':
                return JsonResponse({'error': '单据已作废'}, status=400)
            head.status = '90'
            head.save()
            return JsonResponse({'success': True, 'sukid': sukid, 'status': '90'})
        except model_cls.DoesNotExist:
            continue
    return JsonResponse({'error': '单据不存在'}, status=404)


def document_list(request):
    """GET 单据列表 /goods/documents/"""
    company = request.GET.get('company', '')
    status_filter = request.GET.get('status', '')
    doc_type = request.GET.get('doc_type', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))

    base_filters = {'company': company}

    # ── Salehead count & query ──
    sh_filters = dict(base_filters)
    if status_filter:
        sh_filters['status'] = status_filter
    if doc_type in ('I', 'O', 'U', 'F'):
        sh_filters['saleatr'] = doc_type
    if date_from:
        sh_filters['vdate__gte'] = date_from
    if date_to:
        sh_filters['vdate__lte'] = date_to
    sh_total = Salehead.objects.filter(**sh_filters).count()
    sh_qs = Salehead.objects.filter(**sh_filters).order_by('-vdate')[:page_size + 50]

    # ── Transhead count & query ──
    th_filters = dict(base_filters)
    if status_filter:
        th_filters['status'] = status_filter
    if doc_type == 'TO':
        th_filters['saleatr'] = '20'
    if date_from:
        th_filters['vdate__gte'] = date_from
    if date_to:
        th_filters['vdate__lte'] = date_to
    th_total = Transhead.objects.filter(**th_filters).count()
    th_qs = Transhead.objects.filter(**th_filters).order_by('-vdate')[:page_size + 50]

    # ── Combine & sort ──
    combined = []

    for h in sh_qs:
        item_count = Saledtl.objects.filter(company=company, sukid=h.sukid).count()
        combined.append({
            'doc_type': h.saleatr or '',
            'sukid': h.sukid or '',
            'doccode': h.doccode or '',
            'vdate': h.vdate or '',
            'storecode': h.storecode or '',
            'whcode': h.inwhcode or h.outwhcode or '',
            'other_storecode': '', 'other_whcode': '',
            'ecode': h.ecode or '', 'note': h.gnote or '',
            'supplierid': h.supplierid or '',
            'status': h.status or '10', 'model': 'salehead',
            'item_count': item_count,
            'tmount': float(h.tmount or 0),
        })

    for h in th_qs:
        item_count = Transdtl.objects.filter(company=company, sukid=h.sukid).count()
        combined.append({
            'doc_type': 'TO',
            'sukid': h.sukid or '', 'doccode': h.doccode or '',
            'vdate': h.vdate or '',
            'storecode': h.outstore or '', 'whcode': h.outwhcode or '',
            'other_storecode': h.instore or '', 'other_whcode': h.towhcode or '',
            'ecode': h.ecode or '', 'note': h.gnote or '',
            'supplierid': '',
            'status': h.status or '10', 'model': 'transhead',
            'item_count': item_count,
            'tmount': float(h.tmount or 0),
        })

    total = sh_total + th_total
    combined.sort(key=lambda x: x['vdate'], reverse=True)
    offset = (page - 1) * page_size
    page_results = combined[offset:offset + page_size]

    return JsonResponse({'count': total, 'page': page, 'page_size': page_size, 'results': page_results})


@csrf_exempt
def document_detail(request):
    """GET 单据明细 /goods/document-detail/?sukid=xxx"""
    company = request.GET.get('company', '')
    sukid = request.GET.get('sukid', '')
    if not company or not sukid:
        return JsonResponse({'error': '缺少参数'}, status=400)

    # 尝试 Salehead + Saledtl
    items = Saledtl.objects.filter(company=company, sukid=sukid).values('gcode', 'qty', 'price', 'mount', 'goodsvaldate', 'seqbar')
    if items.exists():
        head = Salehead.objects.get(company=company, sukid=sukid)
        result_items = []
        for it in items:
            gname = ''
            try:
                g = Goods.objects.get(company=company, gcode=it['gcode'])
                gname = g.gname or ''
            except Goods.DoesNotExist:
                pass
            result_items.append({
                'gcode': it['gcode'], 'gname': gname,
                'qty': float(it['qty'] or 0), 'price': float(it['price'] or 0),
                'amount': float(it['mount'] or 0),
                'goodsvaldate': it['goodsvaldate'] or '',
                'seqbar': it['seqbar'] or '',
            })
        return JsonResponse({
            'sukid': sukid, 'model': 'salehead',
            'header': {
                'storecode': head.storecode or '',
                'whcode': head.inwhcode or head.outwhcode or '',
                'vdate': head.vdate or '',
                'note': head.gnote or '',
                'status': head.status or '10',
                'doc_type': head.saleatr or '',
                'supplierid': head.supplierid or '',
                'ecode': head.ecode or '',
            },
            'items': result_items,
        })

    # 尝试 Transhead + Transdtl
    items = Transdtl.objects.filter(company=company, sukid=sukid).values('gcode', 'qty', 'price', 'mount', 'goodsvaldate', 'seqbar')
    if items.exists():
        head = Transhead.objects.get(company=company, sukid=sukid)
        result_items = []
        for it in items:
            gname = ''
            try:
                g = Goods.objects.get(company=company, gcode=it['gcode'])
                gname = g.gname or ''
            except Goods.DoesNotExist:
                pass
            result_items.append({
                'gcode': it['gcode'], 'gname': gname,
                'qty': float(it['qty'] or 0), 'price': float(it['price'] or 0),
                'amount': float(it['mount'] or 0),
                'goodsvaldate': it['goodsvaldate'] or '',
                'seqbar': it['seqbar'] or '',
            })
        return JsonResponse({
            'sukid': sukid, 'model': 'transhead',
            'header': {
                'storecode': head.outstore or '',
                'whcode': head.outwhcode or '',
                'vdate': head.vdate or '',
                'note': head.gnote or '',
                'status': head.status or '10',
                'doc_type': 'TO',
                'supplierid': '',
                'ecode': head.ecode or '',
                'in_storecode': head.instore or '',
                'in_whcode': head.towhcode or '',
            },
            'items': result_items,
        })

    return JsonResponse({'error': '单据不存在'}, status=404)



@csrf_exempt
def document_update(request):
    """POST 更新草稿单据 /goods/document-update/"""
    if request.method != 'POST':
        return JsonResponse({'error': 'method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'invalid JSON'}, status=400)

    company = data.get('company', '')
    sukid = data.get('sukid', '')
    note = data.get('note', '')
    items = data.get('items', [])
    ecode = data.get('ecode', '')

    if not company or not sukid:
        return JsonResponse({'error': '缺少参数'}, status=400)

    # Try Salehead
    try:
        head = Salehead.objects.get(company=company, sukid=sukid)
        if head.status != '10':
            return JsonResponse({'error': '只有草稿状态才能修改'}, status=400)
        if note:
            head.gnote = note
        if ecode:
            head.ecode = ecode
        head.save()
        # Delete old items and recreate
        Saledtl.objects.filter(company=company, sukid=sukid).delete()
        for idx, it in enumerate(items):
            seqbar = it.get('seqbar', f'{idx+1:04d}')
            Saledtl.objects.create(
                company=company, storecode=head.storecode or '',
                saleheadid=head, sukid=sukid, seqbar=seqbar,
                gcode=it.get('gcode', ''), qty=float(it.get('qty', 0)),
                price=float(it.get('price', 0)), mount=float(it.get('qty', 0)) * float(it.get('price', 0)),
                goodsvaldate=it.get('goodsvaldate', ''),
                creater='pc_edit',
            )
        return JsonResponse({'success': True, 'sukid': sukid})
    except Salehead.DoesNotExist:
        pass

    # Try Transhead
    try:
        head = Transhead.objects.get(company=company, sukid=sukid)
        if head.status != '10':
            return JsonResponse({'error': '只有草稿状态才能修改'}, status=400)
        if note:
            head.gnote = note
        head.save()
        Transdtl.objects.filter(company=company, sukid=sukid).delete()
        for idx, it in enumerate(items):
            seqbar = it.get('seqbar', f'{idx+1:04d}')
            Transdtl.objects.create(
                company=company, transheadid=head, sukid=sukid, seqbar=seqbar,
                gcode=it.get('gcode', ''), qty=float(it.get('qty', 0)),
                price=float(it.get('price', 0)), mount=float(it.get('qty', 0)) * float(it.get('price', 0)),
                goodsvaldate=it.get('goodsvaldate', ''),
            )
        return JsonResponse({'success': True, 'sukid': sukid})
    except Transhead.DoesNotExist:
        pass

    return JsonResponse({'error': '单据不存在'}, status=404)
@csrf_exempt
def translog_list(request):
    """GET 库存流水 /goods/translog/"""
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '')
    whcode = request.GET.get('whcode', '')
    gcode = request.GET.get('gcode', '')
    saleatr = request.GET.get('saleatr', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 50))

    filters = {'company': company}
    if storecode:
        filters['storecode'] = storecode
    if whcode:
        filters['whcode'] = whcode
    if gcode:
        filters['gcode'] = gcode
    if saleatr:
        filters['saleatr'] = saleatr
    if date_from:
        filters['vdate__gte'] = date_from
    if date_to:
        filters['vdate__lte'] = date_to

    qs = Goodstranslog.objects.filter(**filters).order_by('-gtranukid')
    total = qs.count()
    offset = (page - 1) * page_size
    qs = qs[offset:offset + page_size]

    # SALEATR 类型映射
    atr_map = dict(common.constants.SALEATR)

    result = []
    for log in qs:
        gname = ''
        if log.goodsuuid:
            gname = log.goodsuuid.gname
        result.append({
            'gtranukid': log.gtranukid,
            'sukid': log.sukid or '',
            'saleatr': log.saleatr or '',
            'saleatr_name': atr_map.get(log.saleatr, ''),
            'vdate': log.vdate or '',
            'doccode': log.doccode or '',
            'storecode': log.storecode or '',
            'whcode': log.whcode or '',
            'gcode': log.gcode or '',
            'gname': gname,
            'qty': float(log.qty1 or 0),
            'price': float(log.price1 or 0),
            'amount': float(log.amount1 or 0),
            'qty2': float(log.qty2 or 0),
            'batch': log.batch or '',
            'goodsvaldate': log.goodsvaldate or '',
            'gnote': log.gnote or '',
            'create_time': log.create_time.strftime('%Y-%m-%d %H:%M') if log.create_time else '',
        })

    return JsonResponse({
        'count': total,
        'page': page,
        'page_size': page_size,
        'results': result,
    })


@csrf_exempt
def store_list(request):
    """GET 门店列表 /goods/stores/"""
    company = request.GET.get('company', '')
    stores = Storeinfo.objects.filter(company=company, flag='Y').values('storecode', 'storename')
    return JsonResponse(list(stores), safe=False)
@csrf_exempt
def supplier_list(request):
    """GET 供应商列表 /goods/suppliers/"""
    company = request.GET.get("company", "")
    suppliers = Supplier.objects.filter(company=company, flag="Y").values("supplierid", "suppliername").order_by("supplierid")
    return JsonResponse(list(suppliers), safe=False)

