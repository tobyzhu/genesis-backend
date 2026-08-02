#coding = utf-8

from django.shortcuts import render
import datetime,time
from django.db.models import Avg,Count,Sum,F,Max
import json
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.db.models import Q,F
import uuid
import numpy as np
import pandas as pd
import os
import genesis.settings as settings
from django.db.models.functions import Concat,Substr

# Create your views here.
from .models import DailyReportNo1,ReportClassData
from cashier.models import Expvstoll,Expense,Toll,Cardhistory
from adviser.models import Cardinfo
from adviser.views import *
from baseinfo.models import *  #Appoption,Storeinfo,Vip,Cardtype,Serviece,Goods,Paymode,Empl
from goods.models import Goodstranslog
from baseinfo.models import BRAND,MARKETCLASS1,MARKETCLASS2,MARKETCLASS3,MARKETCLASS4,FINANCECLASS1,FINANCECLASS2,ARCHIVEMENTCLASS1,ARCHIVEMENTCLASS2
from common.models import *
from wechat.models import WechatUser
import common.constants
from matplotlib import pyplot as plt

# from report.common_report import CardinfoData

# COMPANY='yiren'
TODAY=datetime.now().strftime('%Y%m%d')

def strtodate(str):
    if str == None:
        str='2020-01-01'

    if len(str)==8:
        return str[0:3]+'-'+str[4:5]+'-'+str[6:7]

    str='2020-01-01'
    return str

class BaseInfo_df(object):
    def __init__(self,company):
        self.company=company

    # def get_srvname(self,company,ttype,itemcode):

    def get_baseinfo(self,segname):
        data= Appoption.objects.filter(company=self.company,flag='Y',seg=segname).values_list('itemname','itemvalues')
        data_df = pd.DataFrame(list(data),columns=['itemname','分类'])
        # print('data_df',data_df)
        return data_df

    def get_brand(self):
        data= Appoption.objects.filter(company=self.company,flag='Y',seg='brand').values_list('itemname','itemvalues')
        data_df = pd.DataFrame(list(data),columns=['brand','品牌'])
        # print('data_df',data_df)
        return data_df

    def get_displayclass1(self):
        # displayclass1= Appoption.objects.filter(company=self.company,flag='Y',seg='displayclass1').values_list('itemname','itemvalues')
        data= Appoption.objects.filter(company=self.company,flag='Y',seg='displayclass1').values_list('itemname','itemvalues')
        data_df = pd.DataFrame(list(data),columns=['displayclass1','显示分类一'])
        print('data_df',data_df)
        return data_df

    def get_displayclass2(self):
        # displayclass1= Appoption.objects.filter(company=self.company,flag='Y',seg='displayclass1').values_list('itemname','itemvalues')
        data= Appoption.objects.filter(company=self.company,flag='Y',seg='displayclass2').values_list('itemname','itemvalues')
        data_df = pd.DataFrame(list(data),columns=['displayclass2','显示分类二'])
        print('data_df',data_df)
        return data_df

    def get_itemname_df(self):
            brand_df = self.get_brand()
            print('brand_df',brand_df)

            sitems = Serviece.objects.filter(company=self.company,flag='Y').values_list('svrcdoe','svrname','brand')
            sitems_df = pd.DataFrame(list(sitems),columns=['itemcode','项目名称','brand'])
            sitems_df['ttype']= sitems_df.apply(lambda x: 'S',axis=1)
            print('sitem_df',sitems_df)

            gitems = Goods.objects.filter(company=self.company,flag='Y').values_list('gcode','gname','brand')
            gitems_df = pd.DataFrame(list(gitems),columns=['itemcode','项目名称','brand'])
            gitems_df['ttype']= gitems_df.apply(lambda x: 'G',axis=1)
            print('gitem_df',gitems_df)
            #
            citems = Cardinfo.objects.filter(company=self.company,flag='Y').values_list('ccode','cardtypeuuid__cardname','cardtypeuuid__brand')
            citems_df = pd.DataFrame(list(citems),columns=['itemcode','项目名称','brand'])
            citems_df['ttype'] = citems_df.apply(lambda x: 'C', axis=1)

            items_df = pd.DataFrame.append(sitems_df,gitems_df)
            items_df = pd.DataFrame.append(items_df,citems_df)
            items_df = pd.DataFrame.merge(items_df,brand_df,on='brand')
            print('items_df',items_df)
            return items_df

# 1.03 读取图片demo
def read_img(request):
    """
    : 读取图片
    :param request:
    :return:
    """
    try:
        data = request.GET
        filename = data.get("filename")
        print('MEDIA_ROOT',settings.MEDIA_ROOT,filename)
        imagepath = os.path.join(settings.MEDIA_ROOT, "{}".format(filename))  # 图片路径
        # imagepath = "c:\python35\genesis\images\" + filename
        print('imagepath',imagepath)

        # imagepath = settings.MEDIA_ROOT
        with open(imagepath, 'rb') as f:
            image_data = f.read()
        return HttpResponse(image_data, content_type="image/jpg")
    except Exception as e:
        print(e)
        return HttpResponse(str(e))

def ensure_float(x):
    if isinstance(x,np.float):
        return x
    else :
        return 0

def SetDailyReportNo1(request):
    company=request.GET['company']
    fromdate ='20191101'
    todate ='20191214'
    storelist = Storeinfo.objects.filter(company=company,flag='Y').exclude(storecode='88').exclude(storecode='00').order_by('storecode')
    vsdate = '20191210'

    CARD_PAYMODE_LIST = Paymode.objects.filter(company=company, flag='Y', iscash='0').values_list('pcode', flat=True)
    CASH_PAYMODE_LIST = list(Paymode.objects.filter(company=company, flag='Y', iscash='1').values_list('pcode', flat=True))
    SEND_PAYMODE_LIST = Paymode.objects.filter(company=company, flag='Y', iscash='2').values_list('pcode', flat=True)

    print('cash_paymode_list',CASH_PAYMODE_LIST,CARD_PAYMODE_LIST,list(SEND_PAYMODE_LIST))
    for store in storelist:
        # 客次
        # reportdatas1 = Expvstoll.objects.filter(company=company,storecode=store.storecode,vsdate__gte=fromdate,vsdate__lte=vsdate,valiflag='Y',flag='Y').\
        #     values('storecode','vsdate').annotate(vipcnt=Count('vipuuid',distinct=True))
        # print('reportdatas1',reportdatas1)
        # for reportdata in reportdatas:
        #     print('reportdata',reportdata,company ,reportdata['storecode'],reportdata['vsdate'],reportdata['vipcnt'])
        #     # print('viptimes sql',viptimes.query)
        #     dailyreportno1 = DailyReportNo1.objects.get_or_create(company=company,storecode=store.storecode,reportdate=reportdata['vsdate'])
        #     vipcnt = reportdata['vipcnt']
        #     print('vipcnt',vipcnt)
        #     dailyreportno1[0].vipcnt= vipcnt
        #     dailyreportno1[0].save()


        # 新客数
        # newviplists = Vip.objects.filter(company=company,storecode=store.storecode, create_date__gte=fromdate, create_date__lte=todate ).\
        #         values('storecode','create_date').annotate(newvipcnt=Count('uuid',distinct=True))
        # print('newviplists',newviplists,newviplists.query)
        # for newviplist in newviplists:
        #     print('newviplist',newviplist,company ,newviplist['storecode'],newviplist['vsdate'],newviplist['newvipcnt'])
        #     # print('viptimes sql',viptimes.query)
        #     dailyreportno1 = DailyReportNo1.objects.get_or_create(company=company,storecode=store.storecode,reportdate=newviplist['vsdate'])
        #     dailyreportno1[0].newvipcnt= newviplist['newvipcnt']
        #     dailyreportno1[0].save()

        newviplists = Expvstoll.objects.filter(company=company,storecode=store.storecode,vsdate__gte=fromdate,vsdate__lte=todate,oldcustflag='1').\
            values('storecode','vsdate').\
            annotate(newvipcnt=Count('vipuuid',distinct=True))
        for newviplist in newviplists:
            print('newviplist',newviplist,company ,newviplist['storecode'],newviplist['vsdate'],newviplist['newvipcnt'])
            # print('viptimes sql',viptimes.query)
            dailyreportno1 = DailyReportNo1.objects.get_or_create(company=company,storecode=store.storecode,reportdate=newviplist['vsdate'])
            dailyreportno1[0].newvipcnt= newviplist['newvipcnt']
            dailyreportno1[0].save()
        # print('newvips：', newvipcnts,newvipcnts.query)

        # 新客消费金额
        newvipamounts = Toll.objects.filter(company=company,storecode=store.storecode,flag='Y',transuuid__oldcustflag='1',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate,pcode__in=CASH_PAYMODE_LIST).\
            values('storecode','transuuid__vsdate').annotate(newvipamount=Sum('totmount'))
        print('newvipamount：', newvipamounts,newvipamounts.query)
        for item in newvipamounts:
            print('item',item,company ,item['storecode'],item['transuuid__vsdate'],item['newvipamount'])
            # print('viptimes sql',viptimes.query)
            dailyreportno1 = DailyReportNo1.objects.get_or_create(company=company,storecode=store.storecode,reportdate=item['transuuid__vsdate'])
            dailyreportno1[0].newvipamount= item['newvipamount']
            dailyreportno1[0].save()
        # newvipamount =0
        # 新客入会人数
        # newvipwithcardcnt=0

        # 服务/商品收入
        #     非赠送类的服务 和商品
        # transdatas2 = Expense.objects.filter(company=company,storecode=store.storecode,flag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate,transuuid__valiflag='Y',transuuid__flag='Y').\
        #     values('storecode','transuuid__vsdate','ttype','stype').annotate(totamount=Sum('s_mount'))
        # print('reportdatas2',transdatas2)
        # print('after union',reportdatas1.union(transdatas2))S
        # print('transdata sql', transdatas.query)
        # for transdata in transdatas:
        #     print('transdata',transdata, transdata['transuuid__vsdate'],transdata['totamount'])
        #     dailyreportno1 = DailyReportNo1.objects.get_or_create(company=company,storecode=store.storecode,reportdate=transdata['transuuid__vsdate'])
        #     if transdata['ttype']=='S':
        #         if transdata['stype']=='N':
        #             dailyreportno1[0].shouru_samount = transdata['totamount']
        #
        #     if transdata['ttype'] == 'G':
        #         if transdata['stype'] == 'N':
        #             dailyreportno1[0].shouru_gamount = transdata['totamount']
        #
        #     if transdata['ttype'] == 'C':
        #         if transdata['stype'] == 'N':
        #             dailyreportno1[0].shouru_camount = transdata['totamount']
        #
        #     dailyreportno1[0].save()

        #       现金  /卡付 /赠送
        # 服务
        # 商品
        # 卡
        # transdatas = Expense.objects.filter(company=company,storecode=store.storecode,flag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate,transuuid__valiflag='Y',transuuid__flag='Y',ttype__in=('S','G')).\
        #     values('storecode','transuuid__vsdate','ttype').annotate( cashamount=Sum(F('s_mount') * F('cashratio')), cardamount= Sum(F('s_mount') * F('cardratio')), sendamount=Sum(F('s_mount') * F('sendratio')))\
        #     .order_by('storecode','transuuid__vsdate','ttype')
        # print('transdata:', transdatas,transdatas.query)
        # for transdata in transdatas:
        #     print('transdata',transdata, transdata['transuuid__vsdate'],transdata['cashamount'])
        #     dailyreportno1 = DailyReportNo1.objects.get_or_create(company=company,storecode=store.storecode,reportdate=transdata['transuuid__vsdate'])
        #
        #     if transdata['ttype']=='S':
        #         dailyreportno1[0].cash_samount = transdata['cashamount']
        #         dailyreportno1[0].card_samount = transdata['cardamount']
        #         dailyreportno1[0].send_samount = transdata['sendamount']
        #
        #     if transdata['ttype'] == 'G':
        #         dailyreportno1[0].cash_gamount = transdata['cashamount']
        #         dailyreportno1[0].card_gamount = transdata['cardamount']
        #         dailyreportno1[0].send_gamount = transdata['sendamount']
        #
        # transdatas = Expense.objects.\
        #             filter(company=company, storecode=store.storecode, flag='Y',transuuid__vsdate__gte=fromdate, transuuid__vsdate__lte=todate,transuuid__valiflag='Y', transuuid__flag='Y', ttype__in=('C', 'I')). \
        #             values('storecode', 'transuuid__vsdate').\
        #             annotate(cashamount=Sum(F('s_mount') * F('cashratio')), cardamount=Sum(F('s_mount') * F('cardratio')),sendamount=Sum(F('s_mount') * F('sendratio'))) \
        #             .order_by('storecode', 'transuuid__vsdate')
        # print('transdata:', transdatas, transdatas.query)
        # for transdata in transdatas:
        #     print('transdata', transdata, transdata['transuuid__vsdate'], transdata['cashamount'])
        #     dailyreportno1 = DailyReportNo1.objects.get_or_create(company=company, storecode=store.storecode,
        #                                                           reportdate=transdata['transuuid__vsdate'])
        #     dailyreportno1[0].cash_camount = transdata['cashamount']
        #     dailyreportno1[0].card_camount = transdata['cardamount']
        #     dailyreportno1[0].send_camount = transdata['sendamount']
        #     dailyreportno1[0].save()

        #
        # paymodes = Paymode.objects.filter(company=company,flag='Y',iscash__exact='1').values_list('pcode')
        # paydata = Toll.objects.filter(company=company,storecode=store.storecode,flag='Y',transuuid__vsdate=vsdate,transuuid__valiflag='Y',transuuid__flag='Y',pcode__in=paymodes).\
        #     values('storecode').annotate(cashamount=Sum('totmount')).values('storecode','cashamount').values('storecode','cashamount')
        # print('paydata',paydata)
        # print('paydata sql',paydata.query)


        # vipcnt = Vip.objects.filter(company=company,storecode=store.storecode).annotate(vipcnt=Count('expvstoll__vipuuid',distinct=True)).values('storecode','vipcnt')
        # print('vipcnt',vipcnt)

        # vipcnt = Expvstoll.objects.filter(company=common.constants.COMPANYID).filter(storecode=store.storecode,vsdate=vsdate).values('storecode','vsdate').annotate(vipcnt=Count('vipuuid')).distinct().values('storecode','vsdate','vipcnt')
        #
        # print(store.storecode,viptimes,vipcnt)



        # print('store=',store.storecode,'vsdate=',vsdate, viptimes,vipcnt)
    return HttpResponse("完成！", content_type="application/json")

def SetReportData(request):
    try:
        company=request.GET['company']
    except:
        company=common.constants.COMPANYID

    # try:
    #     storecode=request.GET['storecode']
    # except:
    #     storecode='00'

    fromdate ='20191301'
    todate='20191215'
    vsdate='20191201'

    storelist = Storeinfo.objects.filter(company=company, flag='M').exclude(storecode='88').exclude(storecode='00').order_by('storecode')
    vsdate = '20191210'

    # exams = Paymode.objects.all().values('company','pcode','pname').order_by('company','pcode')
    # print('exams',exams)
    # transposed = {}
    #
    # for exam in exams:
    #     transposed.setdefault(exam['company'], {}).update(
    #         {'pcode%s' % exam['pcode']: exam['pname']})
    #     print(transposed)
    #
    # print('transposed',transposed)

    DISPLAYCLASS1 = Appoption.objects.filter(company=company, flag='Y',seg='displayclass1').values_list('itemname', 'itemvalues').order_by('itemname')
    DISPLAYCLASS1_CODE  = Appoption.objects.filter(company=company, flag='Y',seg='displayclass1').values_list('itemname',flat=True).order_by('itemname')

    DISPLAYCLASS2 = Appoption.objects.filter(company=company, flag='Y',seg='displayclass2').values_list('itemname', 'itemvalues').order_by('itemname')
    DISPLAYCLASS2_CODE  = Appoption.objects.filter(company=company, flag='Y',seg='displayclass2').values_list('itemname',flat=True).order_by('itemname')

    MARKETCLASS1 = Appoption.objects.filter(company=company, flag='Y',seg='marketclass1').values_list('itemname', 'itemvalues').order_by('itemname')
    MARKETCLASS2 = Appoption.objects.filter(company=company, flag='Y', seg='marketclass2').values_list('itemname', 'itemvalues').order_by('itemname')
    MARKETCLASS3 = Appoption.objects.filter(company=company, flag='Y', seg='marketclass3').values_list('itemname', 'itemvalues').order_by('itemname')
    MARKETCLASS4 = Appoption.objects.filter(company=company, flag='Y', seg='marketclass4').values_list('itemname', 'itemvalues').order_by('itemname')
    FINANCECLASS1 = Appoption.objects.filter(company=company, flag='Y',seg='financeclass1').values_list('itemname', 'itemvalues').order_by('itemname')
    FINANCECLASS2 = Appoption.objects.filter(company=company, flag='Y',seg='financeclass2').values_list('itemname', 'itemvalues').order_by('itemname')
    ARCHIVEMENTCLASS1 = Appoption.objects.filter(company=company, flag='Y',seg='archivementclass1').values_list('itemname', 'itemvalues').order_by('itemname')
    ARCHIVEMENTCLASS2 = Appoption.objects.filter(company=company, flag='Y', seg='archivementclass2').values_list('itemname', 'itemvalues').order_by('itemname')

    CARD_PAYMODE_LIST = Paymode.objects.filter(company=company, flag='Y', iscash='0').values_list('pcode', flat=True).order_by('pcode')
    CASH_PAYMODE_LIST = list(Paymode.objects.filter(company=company, flag='Y', iscash='1').values_list('pcode', flat=True).order_by('pcode'))
    SEND_PAYMODE_LIST = Paymode.objects.filter(company=company, flag='Y', iscash='2').values_list('pcode', flat=True).order_by('pcode')

    # print('cash_paymode_list', CASH_PAYMODE_LIST, CARD_PAYMODE_LIST, list(SEND_PAYMODE_LIST))
    for store in storelist:
        storecode=store.storecode
        report_type='vip'
        # vips = Expvstoll.objects.filter(company=company,storecode=storecode,flag='Y',valiflag='Y',vsdate=vsdate).values('','vipuuid').distinct()
        # print(len(vips))

        print('DISPLAYCLASS1_CODE',DISPLAYCLASS1_CODE)
        for item in DISPLAYCLASS1_CODE:
            print('item',item)
            srvs = Serviece.objects.filter(company=company, flag='Y',displayclass1=item).values_list('svrcdoe',flat=True)
            transitems = Expense.objects.filter(company=company,storecode=storecode,transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate,transuuid__valiflag='Y',srvcode__in=srvs). \
                values('storecode', 'transuuid__vsdate','transuuid__vipuuid','ttype').annotate(qty=Sum('s_qty'),amount=Sum(F('s_mount')*(F('cashratio')+F('cardratio'))))
            print('transitems',transitems,transitems.query)
            for transitem in transitems:
                print('transitem',transitem)
                print('transuuid__vipuuid',str(transitem['transuuid__vipuuid']))
                vip = Vip.objects.get(uuid=transitem['transuuid__vipuuid'])
                reportclassdata = ReportClassData.objects.get_or_create(company=company,storecode=storecode,report_type=report_type,vip=vip,datarang='daily',
                                                                        reportdate=transitem['transuuid__vsdate'],report_class_type='DISPLAYCLASS1',
                                                                        report_class_code=item,ttype=transitem['ttype'])[0]
                reportclassdata.qty=transitem['qty']
                reportclassdata.amount=transitem['amount']
                reportclassdata.save()
                print('reportclassdata',reportclassdata)

        print('DISPLAYCLASS2_CODE',DISPLAYCLASS2_CODE)
        for item in DISPLAYCLASS2_CODE:
            print('item',item)
            srvs = Serviece.objects.filter(company=company, flag='Y',displayclass1=item).values_list('svrcdoe',flat=True)
            transitems = Expense.objects.filter(company=company,storecode=storecode,transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate,transuuid__valiflag='Y',srvcode__in=srvs). \
                values('storecode', 'transuuid__vsdate','transuuid__vipuuid','ttype').annotate(qty=Sum('s_qty'),amount=Sum(F('s_mount')*(F('cashratio')+F('cardratio'))))
            print('transitems',transitems,transitems.query)
            for transitem in transitems:
                print('transitem',transitem)
                print('transuuid__vipuuid',str(transitem['transuuid__vipuuid']))
                vip = Vip.objects.get(uuid=transitem['transuuid__vipuuid'])
                reportclassdata = ReportClassData.objects.get_or_create(company=company,storecode=storecode,report_type=report_type,vip=vip,datarang='daily',
                                                                        reportdate=transitem['transuuid__vsdate'],report_class_type='DISPLAYCLASS1',
                                                                        report_class_code=item,ttype=transitem['ttype'])[0]
                reportclassdata.vcode=vip.vcode
                reportclassdata.qty=transitem['qty']
                reportclassdata.amount=transitem['amount']
                reportclassdata.save()
                print('reportclassdata',reportclassdata)


    return HttpResponse("完成！", content_type="application/json")

def makePlanByVip(request):
    company='yiren'
    storelist = ('01','02','03','04')
    fromdate='20191201'
    todate='20191231'
    classes1 = Appoption.objects.filter(company=company,flag='Y',seg='displayclass1').values_list('itemname','itemvalues').order_by('itemname').distinct()
    classes2 = Appoption.objects.filter(company=company,flag='Y',seg='displayclass2').order_by('itemname')
    # print('calsses1',classes1,'classes2',classes2)
    vipdate=[]

    # cardtypeclasses1 = Cardtype.objects.filter(company=company,flag='Y',displayclass1__contains=classes1.itemname)
    # print('cardtypeclasses1',cardtypeclasses1)
    # cardtypeclasses2 = Cardtype.objects.filter(company=company,flag='Y',displayclass2__contains=classes2.itemname)
    # print('cardtypeclasses2',cardtypeclasses2)
    # serviececlasses1 = Serviece.objects.filter(company=company,flag='Y',displayclass1=classes1)
    # print('serviececlasses1',serviececlasses1)
    # serviececlasses2 = Serviece.objects.filter(company=company,flag='Y',displayclass2=classes2)
    # print('serviececlasses2',serviececlasses2)

    cardinfos = Cardinfo.objects.filter(company=company,status='O',flag='Y',storecode__in=storelist).exclude(cardtypeuuid__displayclass1__isnull=True).\
        values_list('vipuuid__uuid','vcode','vipuuid__vname','cardtypeuuid__displayclass1','cardtypeuuid__cardname').annotate(leftamount=Sum('leftmoney')).\
        order_by('vcode','cardtypeuuid__displayclass1','cardtypeuuid__cardtype').distinct()
    vips = list(Cardinfo.objects.filter(company=company,status='O',flag='Y',storecode__in=storelist).\
        values_list('vipuuid__uuid','vcode','vipuuid__vname').distinct())
    # print('vips',vips)
    vipindex = pd.MultiIndex.from_tuples(vips,names=['vipuuid','vcode','vname'])
    print('vipindex',vipindex)

    cardtypes = list(Cardtype.objects.filter(company=company,flag='Y').values_list('displayclass1','cardname').distinct())
    # print('cardtypes',cardtypes)
    class1index = pd.MultiIndex.from_tuples(cardtypes,names=['class1','cardname'])

    cardinfo_df = pd.DataFrame(list(cardinfos),columns=['vipuuid','vcode','vname','classname','cardname','leftamount'])
    cardinfo_df = cardinfo_df.fillna(0)
    print(cardinfo_df)
    #
    # print('index',index)
    df = pd.pivot_table(cardinfo_df,index=['vipuuid','vcode','vname'],columns=['classname','cardname'],values='leftamount',aggfunc=np.sum).reset_index()  #to_string(na_rep='')  #.reset_index()
    # df.fillna(0)
    print(df)

    consumedata = Expense.objects.filter(company=company,transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate).\
        values_list('transuuid__vipuuid','transuuid__vcode','transuuid__vipuuid__vname','srvcode').annotate(consumeqty=Sum('s_qty'),consumeamount=Sum(F('s_mount')*(F('cashratio')+F('cardratio'))))

    print('consumedata',consumedata)
    consumedata_df = pd.DataFrame(list(consumedata),columns=['vipuuid','vcode','vname','srvcode','consumeqty','consumeamount'])
    print('consumedata_df',consumedata_df)
    # df.to_excel('c:/tmp/t1.xlsx','sheet5')


    # vips = Vip.objects.filter(company=company,storecode='01',flag='Y',viptype='10')
    # for vip in vips:
    #     print('vip',vip.vcode,vip.vname, vip)
    #     classes1 = Cardtype.objects.filter(company=company,flag='Y',displayclass1__isnull=False).order_by('displayclass1').values_list('displayclass1',flat=True).distinct()
    #     print('classes1',classes1)
    #     for class1 in classes1:
    #         print('class1',class1)
    #         cardtypes = Cardtype.objects.filter(company=company, flag='Y', displayclass1=class1)
    #         leftmoney=0
    #         leftqty =0
    #         for cardtype in cardtypes:
    #             cardinfos = Cardinfo.objects.filter(company=company,flag='Y',status='O',vipuuid=vip, cardtype=cardtype.cardtype)
    #             for cardinfo in cardinfos:
    #                 leftmoney = leftmoney + cardinfo.leftmoney
    #                 leftqty = leftqty + cardinfo.leftqty
    #         print(vip.vcode,vip.vname,class1,leftmoney,leftqty)

    return HttpResponse("完成！", content_type="application/json")


def getNewVipInfo(request):
    company='yiren'
    fromdate='20191022'
    todate='20191130'

    newviplist = Expvstoll.objects.filter(company=company,flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate,oldcustflag='1').\
        values_list('storecode','vipuuid','vipuuid__source','vipuuid__vcode','vipuuid__vname','vipuuid__viptype').order_by('storecode','vcode').distinct()
    newvip_df = pd.DataFrame(list(newviplist),columns=['storecode','vipuuid','source','vcode','vname','viptype'])
    print('newvip_df',newvip_df)
    newvipamount = Expense.objects.filter(company=company,flag='Y',transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate).\
        values_list('transuuid__vipuuid').annotate(cashamount=Sum(F('s_mount')*F('cashratio')))
    newvipamount_df=pd.DataFrame(list(newvipamount),columns=['vipuuid','cashamount'])
    print('newvipamount_df',newvipamount_df)
    print('od2',pd.merge(newvip_df, newvipamount_df, on='vipuuid'))

    vipcard = Cardinfo.objects.filter(company=company,flag='Y',status='O').values_list('vipuuid','cardtypeuuid__displayclass1','cardtypeuuid__cardname').\
        annotate(leftmoney=Sum('leftmoney'),leftqty=Sum('leftqty')).distinct()
    print('vipcard')
    print(list(vipcard))
    vipcard_df = pd.DataFrame(list(vipcard),columns=['vipuuid','class1','cardname','leftmoney','leftqty'])
    print('vipcard_df')
    print(vipcard_df)
    newvipdata_df = pd.merge(newvip_df, newvipamount_df, on='vipuuid')
    print('newvipdata_df')
    print(newvipdata_df)
    newvipdata_df2 = pd.merge(newvipdata_df, vipcard_df, on='vipuuid')
    print('newvipdata_df2')
    print(newvipdata_df2)
    # df = pd.pivot_table(newvipdata_df2,index=['storecode','vipuuid','source','vcode','vname','viptype','cashamount'],columns=['class1','cardname'],values=['leftmoney','leftqty'],aggfunc=[np.sum],fill_value=0,margins=False).reset_index()
    df = pd.pivot_table(newvipdata_df2,index=['storecode','source','vcode','vname','viptype','cashamount'],columns=['class1','cardname'],values=['leftmoney','leftqty'],aggfunc=[np.sum],fill_value=0,margins=1).reset_index()

    print(df)
    # df.to_excel('c:/tmp/t2.xlsx','sheet1')
    json_data= df.to_json(orient='records')
    print('newvip json_data',json_data)
    return HttpResponse(json_data, content_type="application/json")

# 生成门店报表，包含以下数据：现金类、卡付类、赠送类等各种收款方式数据。
# 到店客数，到店客次，新客数量，新客金额，
# 非赠送服务、商品、疗程卡数据及金额，
# 入卡现金
# 按照各种分类，进行统计的正常/赠送 数量，金额。

def get_amount(amount,ratio):
    if amount ==None:
        amount=0

    if ratio ==None:
        ratio =0
    # print('params',amount,ratio)
    return round(amount * ratio,2)


def get_dailydesc(x):
    desc = '客数:'+ str(x.vipcnt) +' 新客:'+str(x.newvipcnt) + ' 新客金额:'+str(round(x.newvipamount,2)) + ' 总资金收入：'+str(round(x.s_cashamount+x.g_cashamount+x.c_cashamount,2)) + \
            ' 其中卡金:'+str(round(x.c_cashamount,2)) +' 总消耗:'+str(round(x.s_cashamount+x.s_cardamount+x.g_cashamount+x.g_cardamount,2))  +'  其中耗卡:'+str(round(x.s_cardamount+x.g_cardamount,2))

    return desc

def get_DailyStoreData(company, storelist,fromdate,todate):

    company=company
    storelist = storelist
    fromdate=fromdate
    todate=todate

    CARD_PAYMODE_LIST = Paymode.objects.filter(company=company, flag='Y', iscash='0').values_list('pcode', flat=True)
    CASH_PAYMODE_LIST = list(Paymode.objects.filter(company=company, flag='Y', iscash='1').values_list('pcode', flat=True))
    SEND_PAYMODE_LIST = Paymode.objects.filter(company=company, flag='Y', iscash='2').values_list('pcode', flat=True)

    TRANXS =Expvstoll.objects.filter(company=company,storecode__in=storelist,flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)
    # 客次
    vipcnt = Expvstoll.objects.filter(company=company,storecode__in=storelist,vsdate__gte=fromdate,vsdate__lte=todate,valiflag='Y',flag='Y').\
        values('storecode','vsdate').annotate(vipcnt=Count('vipuuid',distinct=True)).distinct().order_by('storecode','-vsdate')
    # print('vipcnt',list(vipcnt))
    vipcnt_df = pd.DataFrame(vipcnt,columns=['storecode','vsdate','vipcnt'])

    # vipcnt_df2=vipcnt_df.cumsum()
    # print('vipcnt_df',vipcnt_df,len(vipcnt_df) ,vipcnt_df2)

    # vipcnt_plt =vipcnt_df.plot.line(x='vsdate',y='vipcnt')
    # type(vipcnt_plt)
    # plt.savefig("abc.jpg")
    # plt.show()

    # 新客数
    # newvipcnt = Vip.objects.filter(company=company,create_time__gte=datetime.date(fromdate), create_time__lte=datetime.date(todate) ).\
    #         values('storecode','create_time').annotate(newvipcnt=Count('uuid',distinct=True))
    newvipcnt = Expvstoll.objects.filter(company=company, storecode__in=storelist,vsdate__gte=fromdate,vsdate__lte=todate, oldcustflag='1'). \
                values('storecode','vsdate'). \
                annotate(newvipcnt=Count('vipuuid', distinct=True)).distinct()
    # print('newvipcnt',list(newvipcnt))
    newvipcnt_df = pd.DataFrame(list(newvipcnt),columns=['storecode','vsdate','newvipcnt'])
    print('newvipcnt_df',newvipcnt_df, len(newvipcnt_df))

    # 新客消费金额
    newvipamount = Toll.objects.filter(company=company, storecode__in=storelist,flag='Y',transuuid__oldcustflag='1', transuuid__vsdate__gte=fromdate,
                                        transuuid__vsdate__lte=todate, pcode__in=CASH_PAYMODE_LIST). \
        values('storecode','transuuid__vsdate' ).annotate(newvipamount=Sum('totmount')).distinct()
    newvipamount_df = pd.DataFrame(list(newvipamount),columns=['storecode','transuuid__vsdate','newvipamount'])
    newvipamount_df = newvipamount_df.fillna(0)
    newvipamount_df2=newvipamount_df.rename(columns={"transuuid__vsdate": "vsdate"}, inplace=True)
    print('newvipamount_df2',newvipamount_df,len(newvipamount_df))

    s_amountdata = Expense.objects.filter(company=company,flag='Y',ttype='S',transuuid__in=TRANXS).values('storecode','transuuid__vsdate').\
        annotate(s_cashamount=Sum(F('s_mount')*F('cashratio')), s_cardamount=Sum(F('s_mount')*F('cardratio')), s_sendamount=Sum(F('s_mount')*F('sendratio'))  )
    s_amount_df = pd.DataFrame(list(s_amountdata),columns=['storecode','transuuid__vsdate','s_cashamount','s_cardamount','s_sendamount'])

    print('s_amount_df 1',s_amount_df)
    s_amount_df2=s_amount_df.rename(columns={"transuuid__vsdate": "vsdate"}, inplace=True)
    s_amount_df2 = s_amount_df.fillna(0)
    print('s_amount_df 1, 2',s_amount_df,s_amount_df2)

    g_amountdata = Expense.objects.filter(company=company,flag='Y',ttype='G',transuuid__in=TRANXS).values('storecode','transuuid__vsdate').\
        annotate(g_cashamount=Sum(F('s_mount')*F('cashratio')), g_cardamount=Sum(F('s_mount')*F('cardratio')), g_sendamount=Sum(F('s_mount')*F('sendratio'))  )
    g_amount_df = pd.DataFrame(list(g_amountdata),columns=['storecode','transuuid__vsdate','g_cashamount','g_cardamount','g_sendamount'])

    print('g_amount_df 1',g_amount_df)
    g_amount_df2=g_amount_df.rename(columns={"transuuid__vsdate": "vsdate"}, inplace=True)
    g_amount_df2 = g_amount_df.fillna(0)
    print('g_amount_df 1, 2',g_amount_df,g_amount_df2)

    c_amountdata = Expense.objects.filter(company=company,flag='Y',ttype__in=['C','I'],transuuid__in=TRANXS).values('storecode','transuuid__vsdate').\
        annotate(c_cashamount=Sum(F('s_mount')*F('cashratio')), c_cardamount=Sum(F('s_mount')*F('cardratio')), c_sendamount=Sum(F('s_mount')*F('sendratio'))  )
    c_amount_df = pd.DataFrame(list(c_amountdata),columns=['storecode','transuuid__vsdate','c_cashamount','c_cardamount','c_sendamount'])

    print('c_amount_df 1',c_amount_df)
    c_amount_df2=c_amount_df.rename(columns={"transuuid__vsdate": "vsdate"}, inplace=True)
    c_amount_df2 = c_amount_df.fillna(0)
    print('c_amount_df 1, 2',c_amount_df,c_amount_df2)

    storedata_df = pd.merge(vipcnt_df,newvipcnt_df,how='left',on=['storecode','vsdate'])
    print('storedata_df 1',storedata_df,len(storedata_df))
    storedata_df = pd.merge(storedata_df, newvipamount_df,how='left',on=['storecode','vsdate'])
    print('storedata_df 2',storedata_df)
    storedata_df = pd.merge(storedata_df,s_amount_df2 ,how='left',on=['storecode','vsdate'])
    storedata_df = pd.merge(storedata_df,g_amount_df2 ,how='left',on=['storecode','vsdate'])
    storedata_df = pd.merge(storedata_df,c_amount_df2 ,how='left',on=['storecode','vsdate'])
    storedata_df = storedata_df.fillna(0)
    storedata_df['desc1'] = storedata_df.apply(lambda x : get_dailydesc(x),axis = 1)

    print('storedata_df 3',storedata_df,len(storedata_df))

    # columnsrrename={"(cardamount, C)":"C_cardamount","(cardamount, G)":"G_cardamount","(cardamount, I)":"I_amount","(cardamount, S) ":"S_amount"}
    # storedata_df.rename(columns=columnsrrename, inplace=True)
    # print('storedata_df 4',storedata_df)
    json_data= storedata_df.to_json(orient='records')
    # print('storedata json_data',json_data)

    return json_data
    # return HttpResponse(json_data, content_type="application/json")
    # return HttpResponse("完成！", content_type="application/json")


# 生成门店报表，包含以下数据：现金类、卡付类、赠送类等各种收款方式数据。
# 到店客数，到店客次，新客数量，新客金额，
# 非赠送服务、商品、疗程卡数据及金额，
# 入卡现金
# 按照各种分类，进行统计的正常/赠送 数量，金额。
def get_StoreData(request):
    company='yiren'
    fromdate='20191022'
    todate='20191130'

    CARD_PAYMODE_LIST = Paymode.objects.filter(company=company, flag='Y', iscash='0').values_list('pcode', flat=True)
    CASH_PAYMODE_LIST = list(Paymode.objects.filter(company=company, flag='Y', iscash='1').values_list('pcode', flat=True))
    SEND_PAYMODE_LIST = Paymode.objects.filter(company=company, flag='Y', iscash='2').values_list('pcode', flat=True)


    # 客次
    vipcnt = Expvstoll.objects.filter(company=company,vsdate__gte=fromdate,vsdate__lte=todate,valiflag='Y',flag='Y').\
        values('storecode').annotate(vipcnt=Count('vipuuid',distinct=True)).distinct()
    # print('vipcnt',list(vipcnt))
    vipcnt_df = pd.DataFrame(vipcnt,columns=['storecode','vipcnt'])
    print('vipcnt_df',vipcnt_df)

    # 新客数
    # newvipcnt = Vip.objects.filter(company=company,create_time__gte=datetime.date(fromdate), create_time__lte=datetime.date(todate) ).\
    #         values('storecode','create_time').annotate(newvipcnt=Count('uuid',distinct=True))
    newvipcnt = Expvstoll.objects.filter(company=company, vsdate__gte=fromdate,vsdate__lte=todate, oldcustflag='1'). \
                values('storecode'). \
                annotate(newvipcnt=Count('vipuuid', distinct=True)).distinct()
    # print('newvipcnt',list(newvipcnt))
    newvipcnt_df = pd.DataFrame(list(newvipcnt),columns=['storecode','newvipcnt'])
    print('newvipcnt_df',newvipcnt_df)

    # 新客消费金额
    newvipamount = Toll.objects.filter(company=company, flag='Y',transuuid__oldcustflag='1', transuuid__vsdate__gte=fromdate,
                                        transuuid__vsdate__lte=todate, pcode__in=CASH_PAYMODE_LIST). \
        values('storecode', ).annotate(newvipamount=Sum('totmount')).distinct()
    # print('newvipamount',newvipamount)
    newvipamount_df = pd.DataFrame(list(newvipamount),columns=['storecode','newvipamount'])

    print('newvipamount_df 1',newvipamount_df)



    storedata_df = pd.merge(vipcnt_df,newvipcnt_df,on=['storecode'])
    print('storedata_df 1',storedata_df)
    storedata_df = pd.merge(storedata_df,newvipamount_df,on=['storecode'])
    print('storedata_df 2',storedata_df)
    json_data= storedata_df.to_json(orient='records')
    print('storedata_df',json_data)

    return HttpResponse(json_data, content_type="application/json")
    # return HttpResponse("完成！", content_type="application/json")

def get_CostByBrand(request):
    company='yfy'
    fromdate='20190610'
    todate='20191231'

    BRANDLIST = Appoption.objects.filter(company=company, flag='Y', seg='brand').values_list('itemname', 'itemvalues')
    brand_df = pd.DataFrame(list(BRANDLIST),columns=['brand','brandname'])
    print('brand_df',brand_df)

    goods = Goods.objects.filter(company=company,flag='Y',valiflag='Y').values_list('gcode','gname','brand','buyprc')
    goods_df = pd.DataFrame(list(goods),columns=['gcode','gname','brand','buyprc'])
    print('goods_df',goods_df)
    goods_df2 = pd.merge(goods_df,brand_df,on='brand')
    print('goods_df2',goods_df2)
    goodstranslogs = Goodstranslog.objects.filter(company=company,vdate__gte=fromdate,vdate__lte=todate,saleatr='U').values_list('storecode','gcode','saleatr',).annotate(sumqty=Sum('qty1'))
    # print('goodstranslogs_list:',list(goodstranslogs))
    goodstranslogs_df = pd.DataFrame(list(goodstranslogs),columns=['storecode','gcode','saleatr','qty'])
    print('goodstranslogs_df',goodstranslogs_df)

    data_df = pd.merge(goods_df2,goodstranslogs_df,on='gcode')
    print('data_df',data_df)
    data_df['amount']=data_df['qty']*data_df['buyprc']
    print('data_df wial amount',data_df)
    df= pd.pivot_table(data_df,index=['storecode','gcode','gname'],columns=['brandname'],values=['qty','amount'],aggfunc=[np.sum],fill_value=0,margins=1).reset_index()
    print('df',df)
    df.to_excel('c:/tmp/明细.xlsx','sheet1')
    df2= pd.pivot_table(data_df,index=['storecode'],columns=['brandname'],values=['qty','amount'],aggfunc=[np.sum],fill_value=0,margins=1).reset_index()
    print('df2',df2)
    df2.to_excel('c:/tmp/汇总.xlsx','sheet1')
    return HttpResponse("完成！", content_type="application/json")

def get_VipBase_Yiren(company,storelist,fromdate,todate):
    # company = 'yiren'
    # fromdate = '20191022'
    # todate = '20210123'
    viptypelist=['10','20','30']
    timescardtypelist=['210121','210134','210331','210334','210375','110258','110260','110262','110264']

    empl =Empl.objects.filter(company=company).values_list('ecode','ename')
    empl_df = pd.DataFrame(list(empl),columns=['ecode','准店长姓名'])
    empl_df2 = pd.DataFrame(list(empl),columns=['ecode2','专属护理师姓名'])

    vips = Vip.objects.filter(company=company,viptype__in=viptypelist,flag='Y',status='Y').\
        values_list('uuid','storecode','viptype','vcode','vname','mtcode','vipcode','ecode','ecode2','indate','birth')
    vips_df = pd.DataFrame(list(vips),columns=['vipuuid','门店','客户类型','会员号','会员姓名','手机','档号案','ecode','ecode2','入会日期','生日'])
    # vips_df['入会日期']=vips_df.apply(lambda x :  datetime.strptime(x.indate,'%Y-%m-%d').date(),axis = 1)
    # vips_df['生日']=vips_df.apply(lambda x : strtodate(x.birth), axis = 1)
    vips_df = pd.merge(vips_df,empl_df,how='left',on='ecode')
    vips_df = pd.merge(vips_df,empl_df2,how='left',on='ecode2')
    print('vips_df2',vips_df)

    vipindate =Expvstoll.objects.filter(company=company,flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate).values_list('vipuuid').\
        annotate(vipintimes=Count('vsdate',distinct=True)).annotate(lastindate=Max('vsdate'))
    print('vipindate.query',vipindate.query,vipindate)
    vipindate_df = pd.DataFrame(list(vipindate),columns=['vipuuid','最近到店次数','最后到店日期'])
    # vipindate_df['最后到店日期']=vipindate_df.apply(lambda x : strtodate(x.lastindate), axis = 1)
    print('vipindata_df',vipindate_df)

    # vip10cards = Cardinfo.objects.filter(company=company,flag='Y',status='O',cardtypeuuid__suptype='10').values_list('vipuuid','cardtypeuuid__cardname','leftmoney')
    # vip10cards_df = pd.DataFrame(list(vip10cards),columns=['vipuuid','主卡名称','主卡余额'])
    # print('vip10cards_df',vip10cards_df)
    #
    # viptimescards = Cardinfo.objects.filter(company=company,flag='Y',status='O',cardtype__in=timescardtypelist,leftqty__gt=0).values_list('vipuuid','cardtypeuuid__cardname','s_price','leftqty','leftmoney')
    # viptimescards_df =pd.DataFrame(list(viptimescards),columns=['vipuuid','疗程卡名称','单次价','疗程余次','疗程余额'])
    # print('viptimescards_df',viptimescards_df)

    vipdata_df = pd.merge(vips_df, vipindate_df,how='left',on='vipuuid')
    print('vipdata_df',vipdata_df)

    # vipdata_df2 = pd.merge(vipdata_df,vip10cards_df,on='vipuuid')
    # print('vipdata_df2',vipdata_df2)
    # vipdata_df3 = pd.merge(vipdata_df2,viptimescards_df,on='vipuuid')
    # print('vipdata_df3',vipdata_df3)
    #
    # # vipdata_df3.to_excel('c:/tmp/yiren_speccard_list.xlsx','sheet1')
    # json_data= vipdata_df.to_json(orient='records')
    # print('vipdata_df',vipdata_df)

    return vipdata_df
    # return HttpResponse(json_data, content_type="application/json")

def get_Vip10Card(company):
    company='yiren'
    vip10cards = Cardinfo.objects.filter(company=company,flag='Y',status='O',cardtypeuuid__suptype='10').values_list('vipuuid','cardtypeuuid__cardname','leftmoney')
    vip10cards_df = pd.DataFrame(list(vip10cards),columns=['vipuuid','主卡名称','主卡余额'])
    # print('vip10cards_df',vip10cards_df)
    return vip10cards_df

def get_Vip20Card(company):
    company='yiren'
    # timescardtypelist=['210121','210134','210331','210334','210375','110258','110260','110262','110264']
    viptimescards = Cardinfo.objects.filter(company=company,flag='Y',status='O', cardtypeuuid__suptype='20',leftqty__gt=0).values_list('vipuuid','cardtypeuuid__cardname','s_price','leftqty','leftmoney')
    viptimescards_df =pd.DataFrame(list(viptimescards),columns=['vipuuid','疗程卡名称','单次价','疗程余次','疗程余额'])
    print('viptimescards_df',viptimescards_df)
    return viptimescards_df

def get_Vip30Card(company):
    company='yiren'
    # timescardtypelist=['210121','210134','210331','210334','210375','110258','110260','110262','110264']
    vip30cards = Cardinfo.objects.filter(company=company,flag='Y',status='O',cardtypeuuid__suptype='30').values_list('vipuuid','cardtypeuuid__cardname','leftmoney')
    vip30cards_df = pd.DataFrame(list(vip30cards),columns=['vipuuid','赠送卡卡名称','卡余额'])
    print('vip30cards_df',vip30cards_df)
    return vip30cards_df

def get_VipCTrans(ps_company,storelist,fromdate,todate):
    # company = ps_company
    # fromdate = '20191105'
    # todate = '20200123'
    # storelist = ['01','02','03','04']
    # trans = Expvstoll.objects.filter(company=ps_company,storecode__in=storelist,valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)

    c_expense = Expense.objects.filter(company=ps_company,storecode__in=storelist,transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate,ttype__in=['C','I']).\
        values('transuuid__vipuuid').annotate(cashamount=Sum(F('s_mount')*F('cashratio')),cardamount = Sum(F('s_mount')*F('cardratio')) ,sendamount = Sum(F('s_mount')*F('sendratio')))
    print('c_expense',c_expense.query)
    c_expense_df = pd.DataFrame(list(c_expense))
    # c_expense_df = pd.DataFrame(list(c_expense),columns=['transuuid__vipuuid','入卡-现金流水','入卡-卡付流水','入卡-赠送流水'])

    c_expense_df2 = c_expense_df.rename(columns={"transuuid__vipuuid": "vipuuid","cashamount":"入卡-现金流水","cardamount":"入卡-卡付流水","sendamount":"入卡-赠送流水"}, inplace=True)
    # print('c_expense_df',c_expense_df)
    # c_expense_df.to_excel('c:/tmp/tt.xlsx','sheet1')

    return c_expense_df

def get_VipGTrans(company,storelist,fromdate,todate):
    # company = company
    # fromdate = '20191105'
    # todate = '20200123'
    # storelist = ['01','02','03','04']
    trans = Expvstoll.objects.filter(company=company,storecode__in=storelist,valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)

    g_expense = Expense.objects.filter(transuuid__in=trans,ttype='G').values('transuuid__vipuuid').annotate(cashamount=Sum(F('s_mount')*F('cashratio')),cardamount = Sum(F('s_mount')*F('cardratio')) ,sendamount = Sum(F('s_mount')*F('sendratio')) )
    g_expense_df = pd.DataFrame(list(g_expense))
    #  g_expense_df = pd.DataFrame(list(g_expense),columns=['transuuid__vipuuid','商品-现金流水','商品-卡付流水','商品-赠送流水'])
    # g_expense_df2 =g_expense_df.rename(columns={"transuuid__vipuuid": "vipuuid"}, inplace=True)

    g_expense_df2 = g_expense_df.rename(columns={"transuuid__vipuuid": "vipuuid","cashamount":"商品-现金流水","cardamount":"商品-卡付流水","sendamount":"商品-赠送流水"}, inplace=True)
    print('g_expense_df',g_expense_df)
    return g_expense_df

def get_VipTransDetail(company,storelist,fromdate,todate):
    company = 'yiren'
    fromdate = '20191105'
    todate = '20200123'
    storelist = ['01','02','03','04']
    base_df = BaseInfo_df('yiren')

    trans = Expvstoll.objects.filter(company=company,storecode__in=storelist,valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)
    goods = Goods.objects.filter(company=company,saleflag='Y').values_list('gcode','gname','brand')
    goods_df = pd.DataFrame(list(goods),columns=['itemcode','商品名称','brand'])
    print('goods_df',goods_df)
    brand_df = base_df.get_brand()
    print('brand_df2',brand_df)
    goods_df = pd.DataFrame.merge(goods_df,brand_df,on='brand')
    print('goods_df',goods_df)

    # g_expense = Expense.objects.filter(transuuid__in=trans,ttype='G').values('transuuid__vipuuid','transuuid__vsdate','srvcode').annotate(cashamount=Sum(F('s_mount')*F('cashratio')),cardamount = Sum(F('s_mount')*F('cardratio')) ,sendamount = Sum(F('s_mount')*F('sendratio')) )
    g_expense = Expense.objects.filter(transuuid__in=trans,).values('transuuid__vipuuid','transuuid__vsdate','ttype','srvcode','s_qty','s_mount','cashratio','cardratio' ,'sendratio' )
    print(g_expense.query)
    g_expense_df = pd.DataFrame(list(g_expense))
    g_expense_df.fillna(0)
    g_expense_df['现金流水']=  g_expense_df.apply(lambda x : get_amount(x.s_mount,x.cashratio),axis = 1)
    g_expense_df['划卡流水']=  g_expense_df.apply(lambda x : get_amount(x.s_mount,x.cardratio),axis = 1)
    g_expense_df['赠送流水']=  g_expense_df.apply(lambda x : get_amount(x.s_mount,x.sendratio),axis = 1)
    print('g_expense_df 2',g_expense_df)
    # g_expense_df = pd.DataFrame(list(g_expense),columns=['transuuid__vipuuid','购买日期','srvcode','现金流水','卡付流水','赠送流水'])
    g_expense_df2=g_expense_df.rename(columns={"transuuid__vipuuid": "vipuuid","transuuid__vsdate":"交易日期","srvcode":"itemcode","s_qty":"数量","s_mount":"金额"}, inplace=True)
    g_expense_df2 = pd.DataFrame.merge(g_expense_df,base_df.get_itemname_df(),on=["itemcode",'ttype'])

    print('g_expense_df',g_expense_df,g_expense_df2)
    return g_expense_df2

def get_VipSTrans(company,storelist,fromdate,todate):
    # company = 'yiren'
    # fromdate = '20191105'
    # todate = '20200123'
    # storelist = ['01','02','03','04']
    trans = Expvstoll.objects.filter(company=company,storecode__in=storelist,valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)

    s_expense = Expense.objects.filter(transuuid__in=trans,ttype='S').values('transuuid__vipuuid').annotate(cashamount=Sum(F('s_mount')*F('cashratio')),cardamount = Sum(F('s_mount')*F('cardratio')) ,sendamount = Sum(F('s_mount')*F('sendratio')) )
    s_expense_df = pd.DataFrame(list(s_expense))
    s_expense_df2 = s_expense_df.rename(columns={"transuuid__vipuuid": "vipuuid","cashamount":"服务-现金流水","cardamount":"服务-卡付流水","sendamount":"服务-赠送流水"}, inplace=True)
    print('s_expense_df',s_expense_df)

    # s_expense_df = pd.DataFrame(list(s_expense),columns=['transuuid__vipuuid','服务-现金流水','服务-卡付流水','服务-赠送流水'])
    # s_expense_df2=s_expense_df.rename(columns={"transuuid__vipuuid": "vipuuid"}, inplace=True)
    # print('s_expense_df',s_expense_df)
    return s_expense_df

def get_vipdata_yiren(request):
    company = request.GET['company']
    # company = 'yiren'
    storelist=['01','02','03','04','05']
    fromdate = '20190610'
    todate = '20200526'

    print('company',company)

    vipbase_df=get_VipBase_Yiren(company,storelist,fromdate,todate)
    print('vipbase_df',vipbase_df)
    vip10cards_df = get_Vip10Card(company)
    # # vip20scards_df = get_Vip20Card
    # vip30cards_df = get_Vip30Card(company)

    vipdata_df = pd.DataFrame.merge(vipbase_df,vip10cards_df,how='left',on='vipuuid')
    # vipdata_df = pd.DataFrame.merge(vipbase_df,vip30cards_df,how='left',on='vipuuid')
    # vipdata_df = vipbase_df
    vip_gtrans_df = get_VipGTrans(company,storelist,fromdate,todate)

    vip_strans_df = get_VipSTrans(company, storelist, fromdate, todate)


    # 含入卡金额
    vip_ctrans_df = get_VipCTrans(company,storelist,fromdate,todate)
    vipdata_df = pd.DataFrame.merge(vipdata_df,vip_ctrans_df,how='left',on='vipuuid')
    vipdata_df = pd.DataFrame.merge(vipdata_df,vip_strans_df,how='left',on='vipuuid')
    vipdata_df = pd.DataFrame.merge(vipdata_df,vip_gtrans_df,how='left',on='vipuuid')
    vipdata_df.fillna(0)
    # vipdata_df = pd.DataFrame(vipdata_df,columns=['门店','客户类型','会员号','会员姓名','手机','入会日期','生日','交易日期','ttype','项目名称','品牌','数量','金额','现金流水','划卡流水','赠送流水'])
    print(vipdata_df)
    outputfile = "c:/tmp/"+company+"_vipdate_"+fromdate+"_"+todate+".xlsx"
    # vipdata_df.to_excel('c:/tmp/yiren_vipdata_consume_20191022_20200524.xlsx','sheet1')
    vipbase_df.to_excel(outputfile,'sheet1')

    # 各项简易明细
    # vip_transdetal_df = get_VipTransDetail(company,storelist,fromdate,todate)
    # vipdata_df = pd.DataFrame.merge(vipdata_df,vip_transdetal_df,on='vipuuid')
    # vipdata_df.fillna(0)
    # vipdata_df = pd.DataFrame(vipdata_df,columns=['门店','客户类型','会员号','会员姓名','手机','入会日期','生日','交易日期','ttype','项目名称','品牌','数量','金额','现金流水','划卡流水','赠送流水'])
    # print(vipdata_df)
    # vipdata_df.to_excel('c:/tmp/yiren_transdetail.xlsx','sheet1')

    # json_data= vipdata_df.to_json(orient='records')
    return HttpResponse('', content_type="application/json")

class Manage_Data(object):
    def __init__(self, **kwargs):
        self.appcode = kwargs.get('appcode','100')
        self.company=kwargs.get('company','demo')
        self.storecode = kwargs.get('storecode','88')
        self.ecode= kwargs.get('ecode','888')
        self.openid  = kwargs.get('openid','12345')
        self.fromdate = kwargs.get('fromdate','20200101')
        self.todate = kwargs.get('todate',datetime.today().strftime('%Y%m%d'))

        # wechatuser = WechatUser.objects.get(appcode=self.appcode,openid=self.openid)
        # sysuser = Hdsysuser.objects.get(uuid= wechatuser.useruuid)
        # companylist=sysuser.company
        # # storelist="'"+ "','".join(empl.storelist)
        # self.storelist=",".join(sysuser.storelist)
        self.storelist = ('01','02','03','04')

    def vipcnt(self,**kwargs):
        trans = Expvstoll.objects.filter(flag='Y', valiflag='Y', company=self.company, storecode=self.storecode,vsdate__gte=self.fromdate,
                                         vsdate__lte=self.todate)
        self.vipcnt = trans.values('vipuuid').order_by('vipuuid').distinct().count()

        # self.vipcnt_daily = trans.values('storecode','vsdate').annotate(vipcnts=Count('vipuuid',distinct=True))
        # print(self.vipcnt_daily.query)
        # print('self.vipcnt_daily:',self.vipcnt_daily)

        self.viptimes = trans.values('vsdate','vipuuid').distinct().count()
        # self.viptimes_daily = trans.values('storecode','vsdate')..count()
        print('self.vipcnt',self.vipcnt,self.vipcnt_daily,self.viptimes)

    def vipcnt_daily(self):
        trans = Expvstoll.objects.filter(flag='Y', valiflag='Y', company=self.company, storecode=self.storecode,vsdate__gte=self.fromdate,
                                         vsdate__lte=self.todate)
        self.vipcnt_daily = trans.values('storecode','vsdate').annotate(vipcnts=Count('vipuuid',distinct=True))
        print(self.vipcnt_daily.query)

    def newvip(self):
        newviptrans = Expvstoll.objects.filter(flag='Y', valiflag='Y', company=self.company, storecode=self.storecode,
                                         vsdate__gte=self.fromdate,vsdate__lte=self.todate,oldcustflag='1')
        self.newvipcnt = newviptrans.values('vipuuid').order_by('vipuuid').distinct().count()
        newvip_amount = Expense.objects.values('s_mount','cashratio','cardratio','sendratio').\
            filter(company=self.company,storecode=self.storecode,transuuid__valiflag='Y',transuuid__vsdate__gte=self.fromdate,transuuid__vsdate__lte=self.todate).\
            aggregate(cashamount=Sum(F('s_mount')*F('cashratio')),cardamount=Sum(F('s_mount')*F('cardratio')))
        self.newvip_cashamount = newvip_amount['cashamount']

        newvip_amount = Expense.objects.values('s_mount','cashratio','cardratio','sendratio').\
            filter(company=self.company,storecode=self.storecode,ttype__in=['C','I'],transuuid__valiflag='Y',transuuid__vsdate__gte=self.fromdate,transuuid__vsdate__lte=self.todate).\
            aggregate(cardamount=Sum(F('s_mount')*F('cashratio')))
        self.newvip_cardamount = newvip_amount['cardamount']
        # print('newvip_cardamount',self.newvip_cardamount )
        print('newvip:',self.newvipcnt,self.newvip_cashamount,self.newvip_cardamount)

    def newvip_daily(self):
        newviptrans = Expvstoll.objects.filter(flag='Y', valiflag='Y', company=self.company, storecode=self.storecode,
                                         vsdate__gte=self.fromdate,vsdate__lte=self.todate,oldcustflag='1')
        self.newvipcnt_daily = newviptrans.values('storecode','vsdate').annotate(newvipcnt=Count('vipuuid',distinct=True))
        print(self.newvipcnt_daily)
        newvip_amount = Expense.objects.values('s_mount','cashratio','cardratio','sendratio').\
            filter(company=self.company,storecode=self.storecode,transuuid__valiflag='Y',transuuid__vsdate__gte=self.fromdate,transuuid__vsdate__lte=self.todate).\
            aggregate(cashamount=Sum(F('s_mount')*F('cashratio')),cardamount=Sum(F('s_mount')*F('cardratio')))
        self.newvip_cashamount = newvip_amount['cashamount']

        newvip_amount = Expense.objects.values('s_mount','cashratio','cardratio','sendratio').\
            filter(company=self.company,storecode=self.storecode,ttype__in=['C','I'],transuuid__valiflag='Y',transuuid__vsdate__gte=self.fromdate,transuuid__vsdate__lte=self.todate).\
            aggregate(cardamount=Sum(F('s_mount')*F('cashratio')))
        self.newvip_cardamount = newvip_amount['cardamount']
        # print('newvip_cardamount',self.newvip_cardamount )
        print('newvip:',self.newvipcnt_daily)

    def amount(self):
        amount = Expense.objects.values('s_mount','cashratio','cardratio','sendratio').\
            filter(company=self.company,storecode=self.storecode,transuuid__valiflag='Y',transuuid__vsdate__gte=self.fromdate,transuuid__vsdate__lte=self.todate)

        self.s_amount = amount.filter(ttype='S').aggregate(s_amount=Sum('s_mount'),s_cashamount=Sum(F('s_mount')*F('cashratio')),s_cardamount=Sum(F('s_mount')*F('cardratio')),s_sendamount=Sum(F('s_mount')*F('sendratio')) )
        print('self.s_amount', self.s_amount)
        self.g_amount = amount.filter(ttype='G').aggregate(g_amount=Sum('s_mount'),g_cashamount=Sum(F('s_mount')*F('cashratio')),g_cardamount=Sum(F('s_mount')*F('cardratio')),g_sendamount=Sum(F('s_mount')*F('sendratio')) )
        print('self.g_amount', self.g_amount)
        self.c_amount = amount.filter(ttype__in=['C','I']).aggregate(c_amount=Sum('s_mount'),c_cashamount=Sum(F('s_mount')*F('cashratio')),c_cardamount=Sum(F('s_mount')*F('cardratio')),c_sendamount=Sum(F('s_mount')*F('sendratio')) )
        print('self.c_amount',self.c_amount)

    def s_item(self):
        s_item = Expense.objects.filter(company=self.company,storecode__in=self.storelist,transuuid__valiflag='Y', transuuid__vsdate__gte=self.fromdate,transuuid__vsdate__lte=self.todate)
        self.s_item_data = s_item.filter(ttype='S').values('srvcode').annotate(s_qty=Sum('s_qty'),s_amount=Sum('s_mount'),
                                                            s_cashamount=Sum(F('s_mount')*F('cashratio')),
                                                            s_cardamount=Sum(F('s_mount')*F('cardratio')),
                                                            s_sendamount=Sum(F('s_mount')*F('sendratio')) ).order_by('srvcode')
        self.s_item_data_df = pd.DataFrame(list(self.s_item_data),columns=('itemcode','s_qty','s_cashamount','s_cardamount','s_sengamount'))
        print('self.s_item_data', self.s_item_data)

    def g_item(self):
        g_item = Expense.objects.filter(company=self.company,storecode__in=self.storelist,transuuid__valiflag='Y', transuuid__vsdate__gte=self.fromdate,transuuid__vsdate__lte=self.todate)
        self.g_item_data = g_item.filter(ttype='G').values('srvcode').annotate(g_qty=Sum('s_qty'), g_amount=Sum('s_mount'),
                                                             g_cashamount=Sum(F('s_mount') * F('cashratio')),
                                                             g_cardamount=Sum(F('s_mount') * F('cardratio')),
                                                             g_sendamount=Sum(F('s_mount') * F('sendratio'))).order_by('srvcode')
        self.g_item_data_df = pd.DataFrame(list(self.g_item_data),columns=('itemcode','g_qty','g_cashamount','g_cardamount','g_sengamount'))
        print('self.g_item_data', self.g_item_data)

    def c_item(self):
        c_item = Expense.objects.filter(company=self.company,storecode__in=self.storelist,transuuid__valiflag='Y', transuuid__vsdate__gte=self.fromdate,transuuid__vsdate__lte=self.todate)
        self.c_item_data = c_item.filter(ttype__in=('C','I')).values_list('newcardtype').annotate(c_qty=Sum('s_qty'),c_amount=Sum('s_mount'),
                                                            c_cashamount=Sum(F('s_mount')*F('cashratio')),
                                                            c_cardamount=Sum(F('s_mount')*F('cardratio')),
                                                            c_sendamount=Sum(F('s_mount')*F('sendratio')) ).order_by('newcardtype')
        print('self.c_item_data', self.c_item_data)
        self.c_item_data_df = pd.DataFrame(list(self.c_item_data),columns=['itemcode','c_qty','c_amount','c_cashamount','c_cardamount','c_sendamount'])
        print('self.c_item_data_df',self.c_item_data_df)

    def cardleft(self):
        self.cardleft = Cardinfo.objects.filter(company=self.company, storecode__in=self.storelist,status='O').\
            values_list('cardtype','cardtypeuuid','cardtypeuuid__cardname','cardtypeuuid__suptype').annotate(sum_leftqty=Sum('leftqty'),sum_leftmoney=Sum('leftmoney')).order_by('cardtype')
        print('cardleftmoney',self.cardleft)
        self.cardleft_times =  Cardinfo.objects.filter(company=self.company, storecode__in=self.storelist,status='O',cardtypeuuid__comptype='times').\
            values_list('cardtype','cardtypeuuid','cardtypeuuid__cardname','cardtypeuuid__suptype').\
            annotate(sum_leftqty=Sum('leftqty'),sum_leftmoney=Sum('leftmoney')).order_by('cardtype')
        self.cardleft_amount = Cardinfo.objects.filter(company=self.company, storecode__in=self.storelist, status='O',cardtypeuuid__comptype='amount'). \
            values_list('cardtype', 'cardtypeuuid', 'cardtypeuuid__cardname', 'cardtypeuuid__suptype').\
            annotate(sum_leftqty=Sum('leftqty'), sum_leftmoney=Sum('leftmoney')).order_by('cardtype')

        self.cardleft_df = pd.DataFrame(list(self.cardleft),columns=['itemcode','cardtypeuuid','itemname','suptype','sum_leftqty','sum_leftmoney'])
        self.cardleft_times_df = pd.DataFrame(list(self.cardleft_times),columns=['itemcode','cardtypeuuid','itemname','suptype','sum_leftqty','sum_leftmoney'])
        self.cardleft_amount_df = pd.DataFrame(list(self.cardleft_amount),columns=['itemcode','cardtypeuuid','itemname','suptype','sum_leftqty','sum_leftmoney'])

        print('cardleftmoney_df',self.cardleft_df )

    def compose_card(self):
        self.c_item()
        self.cardleft()
        self.compose_card_df = pd.merge(self.c_item_data_df,self.cardleft_times_df,how='right',on='itemcode')
        print('self.compose_card_df:',self.compose_card_df )


    def get_invipcnt(request,**kwargs):
        appcode = request.GET['appcode']
        openid = request.GET['openid']

        try:
            month = request.GET['month']
        except:
            month =datetime.today().strftime('%Y%m')

        try:
            fromdate = request.GET['fromdate']
        except:
            fromdate='20190101'

        try:
            todate = request.GET['todate']
        except:
            todate = datetime.today().strftime('%Y%m%d')

        sql =   "   select company,storecode, vsdate, count(distinct vipuuid) vipcnt" \
                "   from expvstoll" \
                "   where 1=1 and flag='Y' and valiflag='Y' " \
                "   and company in (%s)"\
                "   and find_in_set(storecode , %s )   "\
                "   and substring(vsdate,1,6) =  %s"\
                "   group by company,storecode,vsdate "\
                "   order by company,storecode,vsdate desc"
        params= (companylist +' '+ storelist +'  '+ month ).split()
        # params = (company + ' ' + vipuuid + ' ' + comptype).split()
        print(sql, params)
        json_data = sql_to_json(sql,params)
        return HttpResponse( json_data, content_type="application/json")

    def get_inviptimes(request):
        baseinfo= BaseInfo_df('yiren')
        baseinfo.get_itemname_df()
        return HttpResponse( 'get_inviptimes', content_type="application/json")


    def get_dailystoredata(request):
        company=request.GET['company']
        appcode = request.GET['appcode']
        openid = request.GET['openid']

        try:
            storecode = request.GET['storecode']
        except:
            storecode='88'
        storelist = list(storecode)

        try:
            month = request.GET['month']
        except:
            month =datetime.today().strftime('%Y%m')

        try:
            fromdate = request.GET['fromdate'].replace('-','')
        except:
            fromdate='20200401'

        try:
            todate = request.GET['todate'].replace('-','')
        except:
            todate = datetime.today().strftime('%Y%m%d')

        # wechatuser = WechatUser.objects.get(appcode=appcode,openid=openid)
        # sysuser = Hdsysuser.objects.get(uuid= wechatuser.useruuid)
        # companylist=sysuser.company
        # # storelist="'"+ "','".join(empl.storelist)+"'"
        # storelist=",".join(sysuser.storelist)
        # print('storelist 1',storelist)
        # storelist=['01','02','03','04']
        # print('storelist 2',storelist)
        # print('complist',companylist,storelist, fromdate,todate)
        companylist=[]
        companylist.insert(0, company)
        storelist=[]
        storelist.insert(0,storecode)
        print('companylist,storelist',company,storecode,companylist,storelist,fromdate,todate)

        json_data = get_DailyStoreData(company,storelist,fromdate,todate)

        return HttpResponse( json_data, content_type="application/json")

def get_base_data(request):
    company=request.GET['company']
    storecode = request.GET['storecode']
    try:
        month = request.GET['month']
    except:
        month = datetime.today().strftime('%Y%m')

    try:
        fromdate = request.GET['fromdate']
    except:
        fromdate = '20200101'

    try:
        todate = request.GET['todate']
    except:
        todate = datetime.today().strftime('%Y%m%d')

    params={
        'company':company,
        'storecode':storecode,
        'fromdate':fromdate,
        'todate':todate
    }
    basedata = Manage_Data(**params)
    # basedata.vipcnt()
    # basedata.newvip()
    # basedata.newvip_daily()
    # basedata.amount()
    # basedata.c_item()
    # basedata.cardleft()
    basedata.compose_card()

    # print('basedata.__dict__:',basedata.__dict__)
    #
    # t1 = Expense.objects.values('s_mount', 'cashratio', 'cardratio', 'sendratio').annotate(
    #     sumamount=Sum(F('s_mount') * F('cashratio'))).filter(company='yiren', storecode='01',
    #                                                          transuuid__vsdate__gte='20200101', transuuid__valiflag='Y')

    return  HttpResponse('200')

def get_coredata_bystore(request,**kwargs):
    print('**kwargs',kwargs)
    try:
        company = request.GET['company']
    except:
        company='demo'
    storecode = request.GET['storecode']
    try:
        month = request.GET['month']
    except:
        month = datetime.today().strftime('%Y%m')

    try:
        fromdate = request.GET['fromdate'].replace('-','')
    except:
        fromdate = '20200101'

    try:
        todate = request.GET['todate'].replace('-','')
    except:
        todate = datetime.today().strftime('%Y%m%d')

    param = {
        'company': company,
        'storecode': storecode,
        'fromdate': fromdate,
        'todate': todate
    }
    print('param',param)
    basedata = Manage_Data(**param)

    # if
    vipcnt = basedata.vipcnt()
    # basedata.newvip()
    newvip_daily = basedata.newvip_daily()
    amount = basedata.amount()
    # basedata.compose_card()
    context={}
    context['report'] = basedata.__dict__
    json_data = json.dumps(basedata.__dict__)
    print('after generate report json_data:',json_data)
    return JsonResponse( json_data )
    # save_reportinput(p2)
    # if productclass == '3':
    #     return render(request, 'class3report.html', context)
    # else:
    #     return render(request, 'report.html', context)
    # # return  HttpResponse('200')
    # return render(request, 'report_no1.html', context)

class ReportData_DateRange(object):
    # today=datetime.date.today()
    def __init__(self,**kwargs):
        self.company = kwargs.get('company','demo')
        self.storelist = kwargs.get('storelist','00,01')
        self.fromdate = kwargs.get('fromdate','')
        self.todate=kwargs.get('todate',TODAY)

        cardpaylist = Paymode.objects.filter(company=self.company, flag='Y', iscash='0').values_list('pcode')
        cashpaylist = Paymode.objects.filter(company=self.company, flag='Y', iscash='1').values_list('pcode')

        self.cardpcodelist = [i[0] for i in cardpaylist]
        self.cashpcodelist = [i[0] for i in cashpaylist]

        self.card_s_amount = 0
        self.card_g_amount = 0
        self.cash_s_amount = 0
        self.cash_g_amount = 0
        self.cash_c_amount = 0
        self.last_cardleftmoney = 0
        self.fromdate_leftmoney = 0
        self.todate_leftmoney = 0

    def get_trans(self):
        self.trans = Expvstoll.objects.filter(company=self.company, storecode__in=self.storelist, flag='Y', valiflag='Y',vsdate__gte=self.fromdate, vsdate__lt=self.todate)
        self.trans_s = self.trans.filter(ttype='S')
        self.trans_g = self.trans.filter(ttype='G')
        self.trans_c = self.trans.filter(ttype__in=('C', 'I'))

    def get_cash_amount(self):
        self.get_trans()
        self.cash_s_amount = Toll.objects.filter(company=self.company, transuuid__in=self.trans_s, pcode__in=self.cashpcodelist).values('company').annotate(cashamount=Sum('totmount')).values('company', 'cashamount')[0]['cashamount']
        print('cash_s_amount=', self.cash_s_amount)
        self.cash_g_amount = Toll.objects.filter(company=self.company, transuuid__in=self.trans_g, pcode__in=self.cashpcodelist).values('company').annotate(cashamount=Sum('totmount')).values('company', 'cashamount')[0]['cashamount']
        print('cash_g_amount=', self.cash_g_amount)
        self.cash_c_amount = Toll.objects.filter(company=self.company, transuuid__in=self.trans_c, pcode__in=self.cashpcodelist).values('company').annotate(cashamount=Sum('totmount')).values('company', 'cashamount')[0]['cashamount']
        print('cash_c_amount=', self.cash_c_amount)

    def get_card_amount(self):
        self.get_trans()
        self.card_s_amount = Toll.objects.filter(company=self.company, transuuid__in=self.trans_s, pcode__in=self.cardpcodelist).values('company').annotate(cardamount=Sum('totmount')).values('company', 'cardamount')[0]['cardamount']
        print('card_s_amount=', self.card_s_amount)
        self.card_g_amount = Toll.objects.filter(company=self.company, transuuid__in=self.trans_g, pcode__in=self.cardpcodelist).values('company').annotate(cardamount=Sum('totmount')).values('company', 'cardamount')[0]['cardamount']
        print('card_g_amount=', self.card_g_amount)

    def get_last_leftmoney(self):
        self.last_cardleftmoney = Cardinfo.objects.filter(company=self.company, storecode__in=self.storelist, status='O', stype='N').values('company').annotate(leftmoney=Sum('leftmoney')).values('company', 'leftmoney')[0]['leftmoney']
        print('last_cardleftmoney=', self.last_cardleftmoney)

def get_reportdata_leftmoney(request):
    # p = json.loads(request.GET['params'])
    company = request.GET['company']
    storelist = request.GET['storelist'].split(',')
    fromdate = request.GET['fromdate']
    todate = request.GET['todate']
    # print('p',p)
    params=(
        ('company',company),
        ('storelist',storelist),
        ('fromdate',fromdate),
        ('todate',todate)
    )
    print('params',params,dict(params))
    reportdata = ReportData_DateRange(**dict(params))
    reportdata.get_card_amount()
    reportdata.get_cash_amount()
    reportdata.get_last_leftmoney()

    params_fromdate = (
        ('company',company),
        ('storelist',storelist),
        ('fromdate',fromdate),
        ('todate',TODAY)
    )
    report_fromdate = ReportData_DateRange(**dict(params_fromdate))
    report_fromdate.get_card_amount()
    report_fromdate.get_cash_amount()
    report_fromdate.get_last_leftmoney()
    fromdate_leftmoney = report_fromdate.last_cardleftmoney + report_fromdate.card_s_amount + report_fromdate.card_g_amount - report_fromdate.cash_c_amount
    reportdata.fromdate_leftmoney = fromdate_leftmoney

    params_todate = (
        ('company',company),
        ('storelist',storelist),
        ('fromdate',todate),
        ('todate',TODAY)
    )
    report_todate = ReportData_DateRange(**dict(params_todate))
    report_todate.get_card_amount()
    report_todate.get_cash_amount()
    report_todate.get_last_leftmoney()
    todate_leftmoney = report_todate.last_cardleftmoney + report_todate.card_s_amount + report_todate.card_g_amount - report_todate.cash_c_amount
    reportdata.todate_leftmoney = todate_leftmoney
    print('reportdata=',reportdata,fromdate_leftmoney,todate_leftmoney)


    return HttpResponse(0, content_type="application/json")

def get_monthlyreportno1(request):
    company=request.GET['company']
    storecode=request.GET['storecode']
    fromdate=request.GET['fromdate']
    todate=request.GET['todate']

    cardpaylist = Paymode.objects.filter(company=company,flag='Y',iscash='0').values_list('pcode')
    cashpaylist = Paymode.objects.filter(company=company, flag='Y', iscash='1').values_list('pcode')

    cardpcodelist = [i[0] for i in cardpaylist]
    cashpcodelist = [i[0] for i in cashpaylist]

    print("cashpaylist1",cardpcodelist )
    print('cashpaylist2',cashpcodelist)

    trans =  Expvstoll.objects.filter(company=company,storecode=storecode,flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)
    trans_s = trans.filter(ttype='S')
    trans_g = trans.filter(ttype='G')
    trans_c = trans.filter(ttype__in=('C','I'))
    cash_s_amount = Toll.objects.filter(company=company,transuuid__in=trans_s,pcode__in=cashpcodelist ).values('company').annotate(cashamount=Sum('totmount')).values('company','cashamount')[0]['cashamount']
    print('cash_s_amount=',cash_s_amount )
    cash_g_amount = Toll.objects.filter(company=company,transuuid__in=trans_g,pcode__in=cashpcodelist ).values('company').annotate(cashamount=Sum('totmount')).values('company','cashamount')[0]['cashamount']
    print('cash_g_amount=',cash_g_amount )
    cash_c_amount = Toll.objects.filter(company=company,transuuid__in=trans_c,pcode__in=cashpcodelist ).values('company').annotate(cashamount=Sum('totmount')).values('company','cashamount')[0]['cashamount']
    print('cash_c_amount=',cash_c_amount)

    card_s_amount = Toll.objects.filter(company=company,transuuid__in=trans_s,pcode__in=cashpcodelist ).values('company').annotate(cardamount=Sum('totmount')).values('company','cardamount')[0]['cardamount']
    print('card_s_amount=',card_s_amount)
    card_g_amount = Toll.objects.filter(company=company,transuuid__in=trans_g,pcode__in=cashpcodelist ).values('company').annotate(cardamount=Sum('totmount')).values('company','cardamount')[0]['cardamount']
    print('card_g_amount=',card_g_amount)

    last_cardleftmoney = Cardinfo.objects.filter(company=company,storecode=storecode,status='O',stype='N').values('company').annotate(leftmoney=Sum('leftmoney')).values('company','leftmoney')[0]['leftmoney']
    print('last_cardleftmoney=',last_cardleftmoney)


    return HttpResponse(0, content_type="application/json")

class CardinfoData(object):
    def __init__(self,*args, **kwargs):
        self.company=kwargs.get('company','demo')
        self.storecode=kwargs.get('storecode','00')
        self.storelist = kwargs.get('storelist','01,').split(',')
        self.cardinfouuid = kwargs.get('cardinfouuid','')
        self.fromdate = kwargs.get('fromdate',datetime.today())
        self.todate = kwargs.get('todate',datetime.today())
        self.fromdate_leftmoney = 0
        self.todate_leftmoney=0
        self.in_amount=0
        self.out_amount=0
        print('storelist',self.storelist)

    def get_date_leftmoney(self):
        try:
            self.cardinfo = Cardinfo.objects.get(flag='Y',company=self.company,uuid=self.cardinfouuid)
            print('self.cardinfo',self.cardinfo.leftmoney)
            if self.cardinfo.status == 'O':
                try:
                    self.fromdate_leftmoney = Cardhistory.objects.filter(flag='Y',company=self.company,transuuid__valiflag='Y',cardinfouuid=self.cardinfo,create_time__lt=self.fromdate).order_by('-create_time').first().leftmoney
                except Exception as e:
                    self.fromdate_leftmoney = self.cardinfo.leftmoney
                    print('from_leftmoney',e)
                print('fromdate_leftmoney',self.cardinfo.ccode,self.fromdate_leftmoney)

                try:
                    print('to_date create_time',  Cardhistory.objects.filter(flag='Y', company=self.company,transuuid__valiflag='Y', cardinfouuid=self.cardinfo,create_time__lt=self.todate).order_by('-create_time').first().create_time)
                    self.todate_leftmoney = Cardhistory.objects.filter(flag='Y', company=self.company,transuuid__valifalg='Y', cardinfouuid=self.cardinfo,create_time__lt=self.todate).order_by('-create_time').first().leftmoney
                except Exception as e:
                    print('todate error',e)
                    self.todate_leftmoney =self.cardinfo.leftmoney
                print('to_leftmoney',self.cardinfo.ccode,self.todate_leftmoney)

                try:
                    print(self.cardinfo.ccode, self.cardinfo.uuid, self.fromdate, self.todate)
                    print( Cardhistory.objects.filter(flag='Y',company=self.company,transuuid__valifalg='Y',cardinfouuid=self.cardinfo, create_time__gte=self.fromdate, create_time__lt=self.todate).count())
                    self.suminfo = Cardhistory.objects.filter(flag='Y',company=self.company,transuuid__valiflg='Y',cardinfouuid=self.cardinfo, create_time__gte=self.fromdate, create_time__lt=self.todate).aggregate(in_amount=Sum('inamount'),out_amount=Sum('outamount'))
                    self.in_amount = self.suminfo['in_amount']
                    self.out_amount = self.suminfo['out_amount']
                except:
                    print('suminfo error',e)
                print('suminfo',self.cardinfo.ccode, self.suminfo)
                if self.suminfo['in_amount'] == None:
                    self.in_amount =0

                if self.suminfo['out_amount'] == None:
                    self.out_amount =0

        except Exception as e:
            print('exception',e)
            self.fromdate_leftmoney =0
        data = dict(init_leftmoney=self.fromdate_leftmoney, in_amount=self.in_amount, out_amount=self.out_amount, last_leftmoney=self.todate_leftmoney,diff_amount=self.fromdate_leftmoney + self.in_amount - self.out_amount - self.todate_leftmoney)

        return data

    def get_total_leftmoney(self):
        try:
            self.cardinfos = Cardinfo.objects.filter(flag='Y',company=self.company,storecode__in=self.storelist,status='O',stype='N')
            print('self.cardinfo',self.cardinfos.count())
            # if self.cardinfo.status == 'O':
            self.fromdate_leftmoney=0
            self.todate_leftmoney=0
            self.in_amount=0
            self.out_amount=0
            for cardinfo in self.cardinfos:
                try:
                    fromdate_leftmoney = Cardhistory.objects.filter(flag='Y',company=self.company,transuuid__valiflag='Y',cardinfouuid=cardinfo,create_time__lt=self.fromdate).order_by('-create_time').first().leftmoney  #.aggregate(from_leftmoney2=Sum('leftmoney'))
                    if fromdate_leftmoney == None:
                        fromdate_leftmoney =0
                except Exception as e:
                    print('exception from_leftmoney',cardinfo.ccode,e)
                    fromdate_leftmoney = cardinfo.leftmoney
                    # fromdate_leftmoney = 0
                self.fromdate_leftmoney = self.fromdate_leftmoney + fromdate_leftmoney
                # print('fromdate_leftmoney',cardinfo.ccode,self.fromdate_leftmoney)

                try:
                    todate_leftmoney = Cardhistory.objects.filter(flag='Y', company=self.company,transuuid__valiflag='Y',cardinfouuid=cardinfo,create_time__lt=self.todate).order_by('-create_time').first().leftmoney
                    if todate_leftmoney == None:
                        todate_leftmoney =0
                except Exception as e:
                    print('except to_leftmoney',cardinfo.ccode,e)
                    todate_leftmoney = cardinfo.leftmoney
                    # todate_leftmoney =0
                self.todate_leftmoney = self.todate_leftmoney + todate_leftmoney
                # print('to_leftmoney',cardinfo.ccode,self.todate_leftmoney)


            # try:
            #     self.suminfo = Cardhistory.objects.filter(flag='Y',company=self.company,cardinfouuid__in=self.cardinfos,create_time__gte=self.fromdate, create_time__lt=self.todate).aggregate(in_amount=Sum('inamount'),out_amount=Sum('outamount'))

            try:
                print('history cnt:',Cardhistory.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',cardinfouuid__in=self.cardinfos, create_time__gte=self.fromdate, create_time__lt=self.todate).count())
                self.suminfo = Cardhistory.objects.filter(flag='Y', company=self.company,transuuid__valiflag='Y', cardinfouuid__in=self.cardinfos,create_time__gte=self.fromdate,create_time__lt=self.todate).\
                    aggregate(in_amount=Sum('inamount'), out_amount=Sum('outamount'))
                # print('suminfo', self.suminfo)
                self.in_amount = self.suminfo['in_amount']
                self.out_amount = self.suminfo['out_amount']
                if self.suminfo['in_amount'] == None:
                    self.in_amount = 0
                if self.suminfo['out_amount'] == None:
                    self.out_amount = 0
            except Exception as e:
                print('except suminfo error', e)
                self.in_amount = 0
                self.out_amount = 0

            print('fromdate_leftmoney', self.fromdate_leftmoney)
            print('suminfo',self.suminfo)
            print('to_leftmoney', self.todate_leftmoney)
            data = dict(init_leftmoney=self.fromdate_leftmoney, in_amount=self.in_amount, out_amount=self.out_amount,
                        last_leftmoney=self.todate_leftmoney,
                        diff_amount=self.fromdate_leftmoney + self.in_amount - self.out_amount - self.todate_leftmoney)
            return data

        except Exception as e:
            print('exception',cardinfo.ccode, e)
            # self.fromdate_leftmoney =0

    def check_data(self):
        # cardpcodelist = Paymode.objects.filter(flag='Y',company=self.company, iscash='0').values('pcode')
        cardpcodelist =['B','B1','B2','B3','B4','Z1','Z2']
        trans = Expvstoll.objects.filter(flag='Y',company=self.company,valiflag='Y',storecode__in=self.storelist,create_time__gte=self.fromdate, create_time__lt=self.todate).order_by('storecode','vsdate','create_time')
        self.misstran=[]
        i=1
        for tran in trans:
            print(tran.storecode, tran.vsdate,tran.exptxserno)
            if tran.ttype in ['C','I']:
                tranitems = Expense.objects.filter(flag='Y',transuuid=tran)
                for item in tranitems:
                    historycnt = Cardhistory.objects.filter(flag='Y',company=tran.company,transuuid=tran,ccode=item.srvcode,inamount=item.s_mount).count()
                    if historycnt != 1:
                        self.misstran.append(tran.exptxserno)


            # if len(tran.ccode) >0:
            #     paycardinfo = Cardinfo.objects.get(company=self.company, flag='Y', ccode=tran.ccode)
            #     defaultpaycode = paycardinfo.cardtypeuuid.defaultpaycode
            #
            #     tolls = Toll.objects.filter(flag='Y',transuuid=tran,pcode__in=cardpcodelist)
            #     cardpayamount =0
            #     for toll in tolls:
            #         cardpayamount = cardpayamount + toll.totmount
            #
            #     historycnt = Cardhistory.objects.filter(flag='Y',company=tran.company,transuuid=tran,ccode=tran.ccode,outamount=cardpayamount).count()
            #     if historycnt != 1:
            #         self.misstran.append(tran.exptxserno)


        print('misstrans',len(self.misstran),self.misstran)
        return self.misstran

def get_lastmonthlist(**kwargs):
    reportdate = kwargs.get('reportdate','20210101')
    num = kwargs.get('num', 0)
    lastmonthlist=[]
    reportdate_date = datetime.strptime(reportdate,'%Y%m%d')
    reportyear = reportdate[0:4]
    reportdate_year = reportdate_date.year
    year = reportdate_year
    month = reportdate_date.month
    for i  in range(1, num+1):
        # print('i=',i)
        # month = reportdate_date.month - i
        month = month - 1
        if month == 0:
            year= year - 1
            month=12
        print(0,year,month)
        if month in [0,1,2,3,4,5,6,7,8,9]:
            lastmonthlist.append(str(year)+'0'+str(month))
        else:
            lastmonthlist.append(str(year)  + str(month))


    print('lastmonthlist',reportdate, lastmonthlist)
    return lastmonthlist

class EmplReport(object):
    def __init__(self, **kwargs):
        self.company = kwargs.get('company', 'yiren')
        self.storelist = kwargs.get('storecode', '01,02,03,04').split(',')

        self.ecode = kwargs.get('ecode','')

        # self.reportmonth = ['202108','202109','202110','202111']
        self.reportmonth=['202112']
        # self.last_three_month = self.genesisdate(reportdate,3)
        self.last_three_month =[]
        # self.last_six_month = self.genesisdate(reportdate,6)
        self.last_six_month = []

        # print('init data',self.company,self.storelist,type(self.storelist))

    # def get_month(self):
    #     self.reportmonth = ['202008','202009','202010','202011','202012','202101','202102','202103','202104','202105','202106','202107']
    #     self.last_three_month =['202005','202006','202007']
    #     self.last_six_month = ['202002','202003','202004','202005','202006','202007']

    def get_dateinfo_by_month(self,month):
        self.last_3_montlist= get_lastmonthlist(month=month,num=4)
        self.last_6_monthlist = get_lastmonthlist(month=month,num=7)
        self.fromdate_3 = self.last_3_montlist[3]+'01'
        self.to_month_3 = self.last_3_montlist[0]+'01'

    def get_empltranst(self,**kwargs):
        ecode = kwargs.get('ecode','')
        fromdate = kwargs.get('fromdate','')
        todate = kwargs.get('todate')
        trans = Expense.objects.filter(company=self.company,storecode__in=self.storelist,flag='Y',
                                            transuuid__flag='Y',transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate)

        empl_pm_trans =  Expense.objects.filter(company=self.company,storecode__in=self.storelist,flag='Y',
                                            transuuid__flag='Y',transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate).filter(pmcode=ecode)
        empl_sec_trans =  Expense.objects.filter(company=self.company,storecode__in=self.storelist,flag='Y',
                                            transuuid__flag='Y',transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate).filter(asscode1=ecode)
        empl_thr_trans =  Expense.objects.filter(company=self.company,storecode__in=self.storelist,flag='Y',
                                            transuuid__flag='Y',transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate).filter(asscode2=ecode)
        empltrans = empl_sec_trans | empl_thr_trans

        # vips = Vip.objects.filter(flag='Y',company=self.company,)
        return empltrans

    # 员工名下客户自己入现金额
    # def get_empl_trans_amount(self,**kwargs):
    #     for empl in Empl.objects.filter(flag='Y', company=self.company, status='Y',position__in=['100', '110']).order_by('-storecode', '-ecode'):
    #         ecode = empl.ecode
    #         ename = empl.ename
    #         empl_storecode = empl.storecode



    # 计算每个美疗师，每个个月份所分配到的护理师的数量
    # 以会员资料建立日期作为评判是否计算的一个条件
    def get_empl_vip_cnt_by_month(self,**kwargs):
        ecode = kwargs.get('ecode','')
        # self.get_month('20200801')
        for month in self.reportmonth:
            last_create_time = datetime.strptime(month+'01','%Y%m%d')
            empl_vip_cnt = Vip.objects.filter(flag='Y',company=self.company,valiflag='Y',create_time__lte=last_create_time,storecode__in=self.storelist,ecode2=self.ecode).values('storecode','ecode2').annotate(vipcnt=Count('uuid')).order_by('storecode')
            empl_vip_cnt_df = pd.DataFrame(empl_vip_cnt, columns=['month','storecode', 'ecode2', 'vipcnt'])
            empl_vip_cnt_df['month']=month
            print(empl_vip_cnt_df)

        return empl_vip_cnt_df

    # 计算每个护理师负责客户每个月到店客数
    def get_empl_trans_vipcnt_by_month(self,**kwargs):
        total_df = pd.DataFrame(columns=['month','storecode','ecode','ename','vipcnt','trans_vip_cnt','trans_vip_times','3monthnotin','6monthnotin'])
        for month in self.reportmonth:
            last3monthlist = get_lastmonthlist(reportdate=month + '01', num=3)
            frommonth_3 = last3monthlist[2]
            tomonth_3 = last3monthlist[0]
            fromdate_3 = frommonth_3 + '01'
            todate_3 = month + '01'
            # print('1',last3monthlist,frommonth_3,tomonth_3,fromdate_3,todate_3)

            last6monthlist = get_lastmonthlist(reportdate=month + '01', num=6)
            frommonth_6 = last6monthlist[5]
            tomonth_6 = last6monthlist[0]
            fromdate_6 = frommonth_6+'01'
            todate_6 = month +'01'
            print('2',last6monthlist,frommonth_6,tomonth_6,fromdate_6,todate_6)

            # print(month, last3monthlist,last6monthlist,fromdate_3,todate_3,fromdate_6,todate_6)

            # last_create_time = datetime.datetime.strptime(todate_6,'%Y%m%d')

            for empl in Empl.objects.filter(flag='Y',company=self.company,status='Y',position__in=['100','110']).order_by('-storecode','-ecode'):
                ecode =empl.ecode
                ename =empl.ename
                empl_storecode=empl.storecode

                vips = Vip.objects.filter(flag='Y',company=self.company,valiflag='Y',storecode__in=self.storelist,ecode2=ecode)
                vipcnt = len(vips)
                # print('vips',vips)
                print(self.company,self.storelist,fromdate_3, todate_3, ecode,month)
                empl_trans_vipcnt_by_month = Expvstoll.objects.filter(flag='Y',valiflag='Y',company=self.company,storecode__in=self.storelist,
                                                             vipuuid__in=vips,vsdate__gte=fromdate_3,vsdate__lt=todate_3,vipuuid__ecode2=ecode).values('vipuuid__ecode2').annotate(trans_vip_cnt=Count('vipuuid', distinct=True),trans_vip_times=Count(Concat('vipuuid','vsdate'), distinct=True))
                print('empl_trans_vipcnt_by_month',empl_trans_vipcnt_by_month, empl_trans_vipcnt_by_month.query)
                empl_trans_vipcnt_by_month_df = pd.DataFrame(empl_trans_vipcnt_by_month,columns=['month','storecode','ecode','ename','trans_vip_cnt','trans_vip_times'])
                # print(empl_trans_vipcnt_by_month_df)

                empl_3month_in_vipcnt = Expvstoll.objects.filter(flag='Y',valiflag='Y',company=self.company,storecode__in=self.storelist,
                                                               vsdate__gte=fromdate_3, vsdate__lt=todate_3, vipuuid__ecode2=ecode).values('vipuuid').distinct().count()
                last_create_time = datetime.strptime(todate_3, '%Y%m%d')
                print('last_create_time',last_create_time,empl_3month_in_vipcnt)
                empl_3month_all_vipcnt =  Vip.objects.filter(flag='Y',company=self.company,valiflag='Y',storecode__in=self.storelist,ecode2=ecode,create_time__lt=last_create_time).count()
                empl_3month_notin_vipcnt = empl_3month_all_vipcnt - empl_3month_in_vipcnt
                print('empl_3month_notin_vipcnt',ecode, month, empl_3month_in_vipcnt, empl_3month_all_vipcnt, empl_3month_notin_vipcnt)

                empl_6month_in_vipcnt = Expvstoll.objects.filter(flag='Y',valiflag='Y',company=self.company,storecode__in=self.storelist,
                                                               vsdate__gte=fromdate_6, vsdate__lt=todate_6, vipuuid__ecode2=ecode).values('vipuuid').distinct().count()
                last_create_time = datetime.strptime(todate_6, '%Y%m%d')
                print('last_create_time',last_create_time,empl_6month_in_vipcnt)
                empl_6month_all_vipcnt =  Vip.objects.filter(flag='Y',company=self.company,valiflag='Y',storecode__in=self.storelist,ecode2=ecode,create_time__lt=last_create_time).count()
                empl_6month_notin_vipcnt = empl_6month_all_vipcnt - empl_6month_in_vipcnt
                print('empl_6month_notin_vipcnt',ecode, month, empl_6month_in_vipcnt, empl_6month_all_vipcnt, empl_6month_notin_vipcnt)


                empl_trans_vipcnt_by_month_df['month']=month
                empl_trans_vipcnt_by_month_df['storecode']=empl_storecode
                empl_trans_vipcnt_by_month_df['ecode']=ecode
                empl_trans_vipcnt_by_month_df['ename']=ename
                empl_trans_vipcnt_by_month_df['vipcnt']=vipcnt
                empl_trans_vipcnt_by_month_df['3monthnotin'] =empl_3month_notin_vipcnt
                empl_trans_vipcnt_by_month_df['6monthnotin'] =empl_6month_notin_vipcnt
                # print(empl_trans_vipcnt_by_month_df)
                total_df = pd.concat([empl_trans_vipcnt_by_month_df,total_df])   #total_df.insert( value=empl_trans_vipcnt_by_month_df,column=['month','storecode','ecode','trans_vipcnt'] )

            print('fromdate', month, fromdate_3, todate_3, last3monthlist,fromdate_6,todate_6,last6monthlist,)
        print(total_df)

        total_df.to_excel("c:/tmp/yirenreport/trans_vipcnt.xls","sheet1")
        return total_df
            # empl_trans_vipcnt_df = pd.DataFrame(vipcnt, columns=['storecode', 'vipcnt'])


    def get_emplteam_data(self,**kwargs):
        total_df = pd.DataFrame(columns=['month','storecode','teamname','emplcnt','trans_vipcnt','trans_viptimes','cashamount','s_amount','g_amount','c20_amount'])
        for month in self.reportmonth:
            fromdate = month+'01'
            todate=month+'31'
            # last_create_time = datetime.datetime.strptime(todate_6,'%Y%m%d')

            for team in Team.objects.filter(flag='Y',company=self.company).order_by('-storecode'):
                teamid = team.teamid
                teamname = team.teamname
                empls = Empl.objects.filter(flag='Y',company=self.company,team=teamid)
                empllist=[]
                for empl in empls:
                    empllist.append(empl.ecode)
                emplcnt = len(empllist)

                trans_vip_list = Expense.objects.filter(flag='Y',company=self.company,transuuid__valiflag='Y',
                                                            transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate).filter(Q(asscode1__in=empllist) | Q(asscode2__in=empllist)  ).values('transuuid__vipuuid').distinct() #annotate(trans_vip_cnt=Count('vipuuid', distinct=True))
                trans_vipcnt  = len(trans_vip_list)

                trans_viptimes_list = Expense.objects.filter(flag='Y',company=self.company,transuuid__valiflag='Y',
                                                            transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate).filter(Q(asscode1__in=empllist) | Q(asscode2__in=empllist)  ).values('transuuid__vipuuid','transuuid__vsdate').distinct() #annotate(trans_vip_cnt=Count('vipuuid', distinct=True))
                trans_viptimes  = len(trans_viptimes_list)

                sec_s_trans_data = Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,ttype='S',
                                                        transuuid__vsdate__lte=todate,asscode1__in=empllist).values('company').\
                                                        annotate(trans_items=Sum(F('stdmins')*F('secperc')),s_amount=Sum('exp_secbasenum')  )
                try:
                    sec_s_amount =  sec_s_trans_data[0]['s_amount']
                except:
                    sec_s_amount = 0

                try:
                    trans_items = sec_s_trans_data[0]['trans_items']
                except:
                    trans_items =0
                month_df = pd.DataFrame(sec_s_trans_data,columns=['trans_items',])
                month_df['month']=month
                month_df['teamname']=teamname
                month_df['emplcnt']=emplcnt
                month_df['trans_vipcnt']=trans_vipcnt
                month_df['trans_viptims']=trans_viptimes


                sec_g_trans_data = Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,ttype='G',
                                                        transuuid__vsdate__lte=todate,asscode1__in=empllist).values('company').annotate(g_amount=Sum('exp_secbasenum')  )
                try:
                    sec_g_amount = sec_g_trans_data[0]['g_amount']
                except:
                    sec_g_amount = 0

                thr_s_trans_data = Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,ttype='S',
                                                        transuuid__vsdate__lte=todate,asscode2__in=empllist).values('asscode2').annotate(trans_items=Sum(F('stdmins')*F('secperc')),s_amount=Sum('exp_secbasenum')  )

                thr_g_trans_data = Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,ttype='G',
                                                        transuuid__vsdate__lte=todate,asscode2__in=empllist).values('asscode2').annotate(g_amount=Sum('exp_secbasenum')  )
                try:
                    thr_s_amount = thr_s_trans_data[0]['s_amount']
                except:
                    thr_s_amount = 0

                try:
                    thr_g_amount = thr_s_trans_data[0]['g_amount']
                except:
                    thr_g_amount = 0

                month_df['s_amount']=sec_s_amount + sec_g_amount
                month_df['g_amount']=sec_g_amount + thr_g_amount


                cards20 = Cardinfo.objects.filter(flag='Y',company=self.company,status='O',cardtypeuuid__suptype='20')
                card20list=[]
                for card in cards20:
                    card20list.append(card.ccode)
                print('len(card20list)',len(card20list) )
                pm_c20_amount =0
                sec_c20_amount=0
                thr_c20_amount=0
                for tran in Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',pmcode__in=empllist,
                                                          transuuid__vsdate__gte=fromdate, ttype__in=('C','I'), transuuid__vsdate__lte=todate):
                    # if tran.pmcode in empllist:
                    try:
                        cardinfo = Cardinfo.objects.filter(flag='Y', company=self.company, status='O',ccode=tran.srvcode)[0]
                        if cardinfo.cardtypeuuid.suptype=='20':
                            if tran.exp_basenum == None:
                                tran.exp_basenum=0
                            item_c20_amount = tran.exp_basenum
                        else:
                            item_c20_amount =0
                    except Exception as e:
                        item_c20_amount = 0
                        print('error',tran.exptxserno, tran.srvcode, e)

                    pm_c20_amount = pm_c20_amount + item_c20_amount

                for tran in Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',
                                                   asscode1__in=empllist,
                                                   transuuid__vsdate__gte=fromdate, ttype__in=('C', 'I'),
                                                   transuuid__vsdate__lte=todate):
                    # if tran.asscode1 in empllist:
                    try:
                        cardinfo = Cardinfo.objects.filter(flag='Y', company=self.company, status='O',ccode=tran.srvcode)[0]
                        if cardinfo.cardtypeuuid.suptype == '20':
                            if tran.exp_secbasenum == None:
                                tran.exp_secbasenum=0
                            item_c20_amount = tran.exp_secbasenum
                        else:
                            item_c20_amount = 0
                    except Exception as e:
                        item_c20_amount = 0
                        print('error', tran.exptxserno, tran.srvcode, e)
                    sec_c20_amount = sec_c20_amount + item_c20_amount

                for tran in Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',
                                                   asscode1__in=empllist,
                                                   transuuid__vsdate__gte=fromdate, ttype__in=('C', 'I'),
                                                   transuuid__vsdate__lte=todate):
                    # if tran.asscode2 in empllist:
                    try:
                        cardinfo = Cardinfo.objects.filter(flag='Y', company=self.company, status='O',ccode=tran.srvcode)[0]
                        if cardinfo.cardtypeuuid.suptype == '20':
                            if tran.exp_thrbasenum == None:
                                tran.exp_thrbasenum=0
                            item_c20_amount = tran.exp_thrbasenum
                        else:
                            item_c20_amount = 0
                    except Exception as e:
                        item_c20_amount = 0
                        print('error', tran.exptxserno, tran.srvcode, e)
                    thr_c20_amount = thr_c20_amount + item_c20_amount
                c20_amount = pm_c20_amount + sec_c20_amount + thr_c20_amount
                month_df['c20_amount'] = c20_amount

                # xamount   资金流水
                pm_trans_xamount_data=  Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',transuuid__vsdate__gte=fromdate,
                                                        transuuid__vsdate__lte=todate,pmcode__in=empllist).values('company').annotate(x_amount=Sum('pmamount')  )
                sec_trans_xamount_data = Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',
                                                               transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate,
                                                               asscode1__in=empllist).values('company').annotate(x_amount=Sum('secamount'))
                thr_trans_xamount_data = Expense.objects.filter(flag='Y', company=self.company, transuuid__valiflag='Y',
                                                               transuuid__vsdate__gte=fromdate,transuuid__vsdate__lte=todate,
                                                               asscode2__in=empllist).values('company').annotate(x_amount=Sum('thramount'))
                try:
                    pmamount = pm_trans_xamount_data[0]['x_amount']
                except:
                    pmamount =0

                try:
                    secamount = sec_trans_xamount_data[0]['x_amount']
                except:
                    secamount =0

                try:
                    thramount = thr_trans_xamount_data[0]['x_amount']
                except:
                    thramount =0
                month_df['cashamount'] = pmamount + secamount + thramount


                total_df = pd.concat([month_df, total_df],sort=False)
                total_df.to_excel("c:/tmp/yirenreport/team_amount.xls",'sheets')
        print(total_df)


    def get_totalempl_data(self):
        empllist = Empl.objects.filter(flag='Y',company=self.company,storecode__in=self.storelist,status='Y')
        self.get_month()
        for empl in empllist:
            for month in self.reportmonth:
                empl_vipcnt_df = self.get_empl_vip_cnt_by_month(ecode=empl.ecode)
                fromdate = month +'01'
                todate = month +'31'
                empl_trans_vipcnt_df = ''

def get_store_dimension_sales(request):
    """
    门店营业按管理属性维度汇总（JSON）。

    GET 参数：company、storecode、dimension（必填）；fromdate / todate（YYYYMMDD，可选，可与 date_from/date_to 同义）；
    days（未给起止日期时回溯天数，默认 90）；date_field=vsdate|cdate；top_n；include_blank；max_lines。
    与助手工具 store_dimension_sales_summary 共用 report.store_dimension_sales.compute_store_dimension_sales_summary。
    """
    from report.store_dimension_sales import (
        STORE_DIM_ANALYSIS_ALLOWED,
        compute_store_dimension_sales_summary,
    )

    company = (request.GET.get("company") or "").strip()
    storecode = (request.GET.get("storecode") or "").strip()
    dimension = (request.GET.get("dimension") or "").strip()

    if not company or not storecode:
        return JsonResponse(
            {"ok": False, "error": "缺少必填参数 company 或 storecode"},
            status=400,
        )
    if not dimension:
        return JsonResponse(
            {
                "ok": False,
                "error": "缺少必填参数 dimension",
                "allowed_dimensions": sorted(STORE_DIM_ANALYSIS_ALLOWED),
            },
            status=400,
        )

    df_raw = (request.GET.get("fromdate") or request.GET.get("date_from") or "").strip()
    dt_raw = (request.GET.get("todate") or request.GET.get("date_to") or "").strip()
    date_from = df_raw.replace("-", "") if df_raw else ""
    date_to = dt_raw.replace("-", "") if dt_raw else ""

    try:
        days = int(request.GET.get("days") or 90)
    except (TypeError, ValueError):
        days = 90

    date_field = (request.GET.get("date_field") or "vsdate").strip().lower()
    if date_field not in {"vsdate", "cdate"}:
        date_field = "vsdate"

    try:
        top_n = int(request.GET.get("top_n") or 50)
    except (TypeError, ValueError):
        top_n = 50

    _ib = request.GET.get("include_blank")
    if _ib is None:
        include_blank = True
    else:
        include_blank = str(_ib).strip().lower() in ("1", "true", "yes", "y")

    try:
        max_lines = int(request.GET.get("max_lines") or 150000)
    except (TypeError, ValueError):
        max_lines = 150000

    data = compute_store_dimension_sales_summary(
        company,
        storecode,
        dimension,
        days=days,
        date_from=date_from,
        date_to=date_to,
        date_field=date_field,
        top_n=top_n,
        include_blank=include_blank,
        max_lines=max_lines,
    )
    if data.get("error"):
        return JsonResponse({"ok": False, **data}, status=400)
    return JsonResponse({"ok": True, "data": data})


def get_testdata(request):
    # get_lastmonthlist(reportdate='20200801',num=3)
    # return HttpResponse(200)
    #
    param = {
        'company': 'yiren',
        'storelist': '01,02,03,04',
        'fromdate': '20211201',
        'todate': '20211231'
    }
    print('param',param)
    emplreport = EmplReport(**param)
    # 计算每个美疗师，每个个月份所分配到的护理师的数量
    # emplcnt_df = emplreport.get_empl_vip_cnt_by_month()

    # 取某月的报表，统计前几个月的数据
    total_df = emplreport.get_empl_trans_vipcnt_by_month()

    # 业务组别数据
    # team_data = emplreport.get_emplteam_data()

    # context={}
    # context['report'] = emplreport.__dict__
    # print(emplreport.__dict_)
    #
    # json_data = json.dumps(emplreport.__dict__)
    # print('after generate report json_data:',json_data)
    # return JsonResponse( json_data )
    return  HttpResponse('200')



@csrf_exempt
def card_balance_report_api(request):
    from report.card_balance_report import build_card_balance_report
    from report.scope import resolve_report_store_scope
    '''卡余额汇总 API（JSON 版，替代 Django Admin）'''
    company = (request.GET.get('company') or '').strip()
    comptype = request.GET.get('comptype', '')
    nature = request.GET.get('nature', '')
    keyword = request.GET.get('keyword', '')
    only_with_balance = request.GET.get('only_with_balance', '1') != '0'

    if not company:
        return JsonResponse({'ok': False, 'error': '缺少 company 参数'}, status=400)

    ok, scope = resolve_report_store_scope(request, company)
    if not ok:
        status = scope.pop('status', 400)
        return JsonResponse(scope, status=status)

    storecodes = scope['storecodes']
    result = build_card_balance_report(
        company=company,
        storecodes=storecodes,
        suptype='',
        comptype=comptype,
        nature=nature,
        keyword=keyword,
        only_with_balance=only_with_balance,
    )

    # Decimal → float 递归转换
    def _to_json(obj):
        if isinstance(obj, dict):
            return {k: _to_json(v) for k, v in obj.items()}
        elif isinstance(obj, (list, tuple)):
            return [_to_json(i) for i in obj]
        elif isinstance(obj, Decimal):
            return float(obj)
        return obj

    data = _to_json(result)
    rows = data.get('summary_rows') or []
    grand = data.get('grand_totals') or {}
    totals = {
        'normal_count': sum(int(r.get('normal_count') or 0) for r in rows),
        'normal_leftmoney': round(sum(float(r.get('normal_leftmoney') or 0) for r in rows), 2),
        'normal_leftqty': sum(float(r.get('normal_leftqty') or 0) for r in rows),
        'gift_count': sum(int(r.get('gift_count') or 0) for r in rows),
        'gift_leftmoney': round(sum(float(r.get('gift_leftmoney') or 0) for r in rows), 2),
        'gift_leftqty': sum(float(r.get('gift_leftqty') or 0) for r in rows),
        'total_count': sum(int(r.get('total_count') or 0) for r in rows),
        'total_leftmoney': round(sum(float(r.get('total_leftmoney') or 0) for r in rows), 2),
        'total_leftqty': sum(float(r.get('total_leftqty') or 0) for r in rows),
    }
    kpis = {
        'card_count': int(grand.get('card_count') or 0),
        'normal_amount': float(grand.get('normal_amount') or 0),
        'gift_amount': float(grand.get('gift_amount') or 0),
        'total_amount': float(grand.get('total_amount') or 0),
        'normal_times': float(grand.get('normal_times') or 0),
        'gift_times': float(grand.get('gift_times') or 0),
    }
    return JsonResponse({
        'ok': True,
        'meta': {
            'company': company,
            'storecodes': storecodes,
            'allowed_storecodes': scope['allowed_storecodes'],
            'comptype': comptype,
            'nature': nature,
            'keyword': keyword,
            'only_with_balance': only_with_balance,
        },
        'kpis': kpis,
        'rows': rows,
        'totals': totals,
        # 兼容旧前端字段
        'summary_rows': rows,
        'grand_totals': grand,
        'diagnostics': data.get('diagnostics'),
    })

@csrf_exempt
def store_performance_api(request):
    '''Store performance report from transaction tables (raw SQL)'''
    company = request.GET.get('company', '')
    storecode = request.GET.get('storecode', '')
    from_date = request.GET.get('from_date', '')
    to_date = request.GET.get('to_date', '')
    if not company:
        return JsonResponse([], safe=False)
    from django.db import connection
    sql = """
        SELECT e.vsdate, e.storecode,
               SUM(CASE WHEN x.TTYPE = 'S' THEN x.S_MOUNT ELSE 0 END) as am_S,
               SUM(CASE WHEN x.TTYPE = 'G' THEN x.S_MOUNT ELSE 0 END) as am_G,
               SUM(CASE WHEN x.TTYPE = 'C' THEN x.S_MOUNT ELSE 0 END) as am_C,
               SUM(CASE WHEN x.TTYPE = 'I' THEN x.S_MOUNT ELSE 0 END) as am_I,
               COUNT(DISTINCT e.uuid) as trans_count
        FROM expvstoll e
        INNER JOIN expense x ON e.uuid = x.transuuid
        WHERE e.company = %s AND e.flag = 'Y' AND e.valiflag = 'Y' AND x.flag = 'Y'
    """
    params = [company]
    if storecode:
        sql += " AND e.storecode = %s"; params.append(storecode)
    if from_date:
        sql += " AND e.vsdate >= %s"; params.append(from_date)
    if to_date:
        sql += " AND e.vsdate <= %s"; params.append(to_date)
    sql += " GROUP BY e.vsdate, e.storecode ORDER BY e.vsdate DESC, e.storecode"
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            cols = [d[0] for d in cursor.description]
            rows = []
            for row in cursor.fetchall():
                d = dict(zip(cols, row))
                d['am_S'] = float(d.get('am_S') or 0)
                d['am_G'] = float(d.get('am_G') or 0)
                d['am_C'] = float(d.get('am_C') or 0)
                d['am_I'] = float(d.get('am_I') or 0)
                d['trans_count'] = int(d.get('trans_count') or 0)
                d['total'] = d['am_S'] + d['am_G'] + d['am_C'] + d['am_I']
                rows.append(d)
        return JsonResponse(rows, safe=False)
    except Exception as exc:
        return JsonResponse({'error': str(exc)}, status=500)


@csrf_exempt
def business_daily_flow_api(request):
    """营业流水表：默认明细行；也可店×日 / 按店合计。"""
    from django.db import connection
    from report.business_flow import build_business_line_flow
    from report.scope import resolve_report_store_scope

    company = (request.GET.get('company') or '').strip()
    from_date = (request.GET.get('from_date') or '').strip()
    to_date = (request.GET.get('to_date') or '').strip()
    view = (request.GET.get('view') or 'line').strip().lower()
    # detail 兼容旧前端：店×日汇总
    if view == 'detail':
        view = 'daily'
    if view not in ('line', 'daily', 'by_store'):
        view = 'line'

    ok, scope = resolve_report_store_scope(request, company)
    if not ok:
        status = scope.pop('status', 400)
        return JsonResponse(scope, status=status)

    storecodes = scope['storecodes']

    if view == 'line':
        try:
            limit = int(request.GET.get('limit') or 5000)
        except (TypeError, ValueError):
            limit = 5000
        try:
            result = build_business_line_flow(
                company=company,
                storecodes=storecodes,
                from_date=from_date,
                to_date=to_date,
                limit=limit,
            )
            meta = {
                'company': company,
                'storecodes': storecodes,
                'allowed_storecodes': scope['allowed_storecodes'],
                'from_date': from_date,
                'to_date': to_date,
                **(result.get('meta') or {}),
                'view': 'line',
            }
            return JsonResponse({
                'ok': True,
                'meta': meta,
                'kpis': result.get('kpis') or {},
                'rows': result.get('rows') or [],
                'totals': result.get('totals') or {},
            })
        except Exception as exc:
            return JsonResponse({'ok': False, 'error': str(exc)}, status=500)

    placeholders = ','.join(['%s'] * len(storecodes))

    if view == 'by_store':
        select_dims = "e.storecode, MAX(s.storename) AS storename"
        group_by = "e.storecode"
        order_by = "e.storecode"
    else:
        select_dims = "e.vsdate, e.storecode, MAX(s.storename) AS storename"
        group_by = "e.vsdate, e.storecode"
        order_by = "e.vsdate DESC, e.storecode"

    sql = f"""
        SELECT {select_dims},
               SUM(CASE WHEN x.TTYPE = 'S' THEN x.S_MOUNT ELSE 0 END) AS am_S,
               SUM(CASE WHEN x.TTYPE = 'G' THEN x.S_MOUNT ELSE 0 END) AS am_G,
               SUM(CASE WHEN x.TTYPE = 'C' THEN x.S_MOUNT ELSE 0 END) AS am_C,
               SUM(CASE WHEN x.TTYPE = 'I' THEN x.S_MOUNT ELSE 0 END) AS am_I,
               COUNT(DISTINCT e.uuid) AS trans_count
        FROM expvstoll e
        INNER JOIN expense x ON e.uuid = x.transuuid
        LEFT JOIN storeinfo s
               ON s.company = e.company AND s.storecode = e.storecode AND s.flag = 'Y'
        WHERE e.company = %s
          AND e.flag = 'Y' AND e.valiflag = 'Y' AND x.flag = 'Y'
          AND e.storecode IN ({placeholders})
    """
    params = [company] + list(storecodes)
    if from_date:
        sql += " AND e.vsdate >= %s"
        params.append(from_date)
    if to_date:
        sql += " AND e.vsdate <= %s"
        params.append(to_date)
    sql += f" GROUP BY {group_by} ORDER BY {order_by}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            cols = [d[0] for d in cursor.description]
            rows = []
            totals = {
                'am_S': 0.0, 'am_G': 0.0, 'am_C': 0.0, 'am_I': 0.0,
                'total': 0.0, 'trans_count': 0,
            }
            for row in cursor.fetchall():
                d = dict(zip(cols, row))
                d['am_S'] = float(d.get('am_S') or 0)
                d['am_G'] = float(d.get('am_G') or 0)
                d['am_C'] = float(d.get('am_C') or 0)
                d['am_I'] = float(d.get('am_I') or 0)
                d['trans_count'] = int(d.get('trans_count') or 0)
                d['total'] = d['am_S'] + d['am_G'] + d['am_C'] + d['am_I']
                if view == 'by_store':
                    d['vsdate'] = ''
                d['storename'] = d.get('storename') or d.get('storecode') or ''
                rows.append(d)
                totals['am_S'] += d['am_S']
                totals['am_G'] += d['am_G']
                totals['am_C'] += d['am_C']
                totals['am_I'] += d['am_I']
                totals['total'] += d['total']
                totals['trans_count'] += d['trans_count']

        kpis = {
            'am_S': round(totals['am_S'], 2),
            'am_G': round(totals['am_G'], 2),
            'am_C': round(totals['am_C'], 2),
            'am_I': round(totals['am_I'], 2),
            'total': round(totals['total'], 2),
            'trans_count': totals['trans_count'],
            'store_count': len(storecodes),
            'row_count': len(rows),
        }
        for key in ('am_S', 'am_G', 'am_C', 'am_I', 'total'):
            totals[key] = round(totals[key], 2)

        return JsonResponse({
            'ok': True,
            'meta': {
                'company': company,
                'storecodes': storecodes,
                'allowed_storecodes': scope['allowed_storecodes'],
                'from_date': from_date,
                'to_date': to_date,
                'view': view,
            },
            'kpis': kpis,
            'rows': rows,
            'totals': totals,
        })
    except Exception as exc:
        return JsonResponse({'ok': False, 'error': str(exc)}, status=500)
