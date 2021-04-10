#encoding = utf-8
from django.shortcuts import render
import json
from django.http import HttpResponse,StreamingHttpResponse
from decimal import *
import requests
import datetime
import requests

# from cashier.models import Expvstoll,Expense,Toll,EmplArchivementDetail
# from baseinfo.models import Serviece,Goods,Cardtype,Empl,Paymode
# from adviser.models import Cardinfo
# from goods.views import FillTransdtl
#
# import common.constants
# from cashier.views import fillcardhistory
def daily():
    company='dsdemo'
    storecode='88'
    fromdate = ( datetime.date.today() + datetime.timedelta(days=-1) ).strftime('%Y%m%d')
    todate = datetime.date.today().strftime('%Y%m%d')

    # trans = Expvstoll.objects.filter(company=company, flag='Y',valiflag='Y',vsdate__gte=fromdate,vsdate__lte=todate)
    # for tran in trans:
    #     tran.set_oldcustflag()

    # url = 'http://localhost:8080/datamanage/dailycheck/?company='+company+'&storecode='+storecode+'&fromdate=20210322&todate=20210331'
    # url = 'http://localhost:8080/cashier/reculate_trans/?company='+company+'&storecode='+storecode+'&transuuid=e91e6d778c6511eba88c00ff2366e0e3'
    url = 'http://localhost:8080/cashier/reculate_trans/?company='+company+'&storecode='+storecode+'&fromdate=20210405&todate=20210405'
    # url = 'http://localhost:8080/cashier/vipitemtrans_confirm/?company='+company+'&storecode='+storecode+'&cashier=88&vipitemtransuuid=ecdafb908f0711eba88c00ff2366e0e3'
    # url = 'http://localhost:8080/cashier/fillcardhistory/?company='+company
    # url = 'http://localhost:8080/cashier/offset_trans/?company='+company+'&storecode='+storecode+'&transuuid=40c7d5db935c11eba88c00ff2366e0e3'

    result = requests.get(url)

    return 0

daily()