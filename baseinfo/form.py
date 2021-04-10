#coding = utf-8

from django.contrib import admin
from django import forms
from django.forms import widgets
from django.forms import models as form_model
import json
from django.http import HttpResponse
from django.shortcuts import render,get_object_or_404,render_to_response
from django.http import HttpResponse, Http404,HttpResponseRedirect

from .models import Supplier,Goodsct,Goods,Vip,Cardtype,Cardvsdi,Paymode,Srvtopty,Serviece,Srvrptype,Position,Empl

class GoodsForm(forms.Form):
    gcode = forms.CharField(label='编码',initial='pls input',max_length=16,widget=forms.TextInput(attrs={'size':'12'}))
    gname = forms.CharField(label='名称',max_length=32)
#    brand = forms.CharField(label='品牌',initial='',max_length=16)
    goodsct = forms.ModelChoiceField(label='类别',queryset=Goodsct.objects.all())
#    spec = forms.CharField(widget=forms.TextInput())

    class Meta:
        model= Goods
        fields =(('gcode','gname','goodsct'),('barcode','brand','supplierid'),('saleprc','buyprc','pricechangeable'),('qty','unit','spec'),('minivalues','maxvalues'),('saleperc','pmguideperc','valiflag'))

def GoodsForm_view(request):
    goodsform = GoodsForm()
    return render_to_response('goods_form.html',{'goodsform':goodsform.as_p()})


class VipForm(forms.Form):
    vcode = forms.CharField(max_length=16,initial='001')
    vname = forms.CharField(max_length=32,initial='')
    email = forms.EmailField(widget=widgets.EmailInput)
    ecode = form_model.ModelChoiceField(label='顾问',queryset=Empl.objects.all())
#    ecode = forms.ChoiceField(
#        initial=1,
#        label='顾问',
#        widget=widgets.Select
#                             )
#    def __init__(self, *args, **kwargs):
#        super(VipForm,self).__init__(*args, **kwargs)
        # self.fields['user'].widget.choices = ((1, '上海'), (2, '北京'),)
        # 或
#        self.fields['ecode'].widget.choices = Empl.objects.all().values_list('ecode','ename')

def publish(request):
    ret = {'status': False, 'data': '', 'error': '', 'summary': ''}
    if request.method == 'POST':
        request_form = VipForm(request.POST)
        if request_form.is_valid():
            request_dict = request_form.clean()
            print(request_dict)
            ret['status'] = True
        else:
            error_msg = request_form.errors.as_json()
            ret['error'] = json.loads(error_msg)
    return HttpResponse(json.dumps(ret))