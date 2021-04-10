#coding = utf-8

from django.shortcuts import render
import datetime,time
from django.db.models import Avg,Count,Sum,F,Max
import json
from django.http import HttpResponse,StreamingHttpResponse
from django.db.models import Q,F
import uuid
import numpy as np
import pandas as pd
import os
import genesis.settings as settings

# Create your views here.
from .models import DailyReportNo1,ReportClassData
from cashier.models import Expvstoll,Expense,Toll
from adviser.models import Cardinfo
from adviser.views import *
from baseinfo.models import *  #Appoption,Storeinfo,Vip,Cardtype,Serviece,Goods,Paymode,Empl
from goods.models import Goodstranslog
from baseinfo.models import BRAND,DISPLAYCLASS1,DISPLAYCLASS2,MARKETCLASS1,MARKETCLASS2,MARKETCLASS3,MARKETCLASS4,FINANCECLASS1,FINANCECLASS2,ARCHIVEMENTCLASS1,ARCHIVEMENTCLASS2
from common.models import *
from wechat.models import WechatUser
import common.constants
from matplotlib import pyplot as plt

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

