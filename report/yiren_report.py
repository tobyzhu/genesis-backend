from django.shortcuts import render
import datetime, time
from django.db.models import Avg, Count, Sum, F, Max
import json
from django.http import HttpResponse, StreamingHttpResponse
from django.db.models import Q, F
import uuid
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import os
import genesis.settings as settings

# Create your views here.
from .models import DailyReportNo1, ReportClassData
import cashier.models
import adviser.models
from adviser.views
import baseinfo.models  # Appoption,Storeinfo,Vip,Cardtype,Serviece,Goods,Paymode,Empl
import goods.models
# from baseinfo.models import BRAND,DISPLAYCLASS1,DISPLAYCLASS2,MARKETCLASS1,MARKETCLASS2,MARKETCLASS3,MARKETCLASS4,FINANCECLASS1,FINANCECLASS2,ARCHIVEMENTCLASS1,ARCHIVEMENTCLASS2
from common.models import *
from wechat.models import *
import common.constants

class StoreReport(object):
    def __init__(self, **kwargs):
        default_fromdate = ''
        default_todate = ''
        company = kwargs.get('company', 'yiren')
        storelist = kwargs.get('storecode', '01,02,03,04')
        fromdate = kwargs.get('fromdate', default_fromdate)
        todate = kwargs.get('todate', default_todate)

        return ''

    # def vipcnt(self):
    # def vip_times(self):
    #
    # def empl_vipcnt(self):

    # def empl_archivement_sum(self):
