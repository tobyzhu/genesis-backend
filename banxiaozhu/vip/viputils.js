var util = require('../utils/util.js');
var log = require('../utils/log.js');
var app = getApp();
var host=app.globalData.host

function getVipBaseInfo(that, options) {
  var app = getApp();
  // var vipuuid=''
  var option_vipuuid=''
  // var that = this;
  if (options.uuid){
    option_vipuuid = options.uuid
  }
  if (options.vipuuid){
    option_vipuuid = options.vipuuid
  }

  console.log('getVipBaseInfo', options);
  // if (options.uuid.length > 32) {
  //   var vipuuid_s = options.uuid.split('-').join('')
  // }
  // else {
  //   var vipuuid_s = options.uuid
  // }

  if (option_vipuuid.length > 32) {
    var vipuuid_s = option_vipuuid.split('-').join('')
  }
  else {
    var vipuuid_s = option_vipuuid
  }
  console.log('options.uuid',options.uuid,option_vipuuid,vipuuid_s)

  var vipuuid_u = util.strtouuid(vipuuid_s);
  var vipuuid = util.strtouuid(vipuuid_s)
  console.log('vipuuid_u,vipuuid',vipuuid_s,vipuuid_u,vipuuid)
  var host = app.globalData.host
  var url = host + "baseinfo/vip/" + vipuuid_u;
  console.log(url)

  wx.request({
    method: 'GET',
    url: url,
    data: {
      //  vipuuid: vipuuid,
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
   success(res) {
      // 来店渠道名称映射
      if (res.data && app.globalData.sourcelist) {
        for (var i = 0; i < app.globalData.sourcelist.length; i++) {
          if (app.globalData.sourcelist[i].itemname == res.data.source) {
            res.data.sourceName = app.globalData.sourcelist[i].itemvalues;
            break;
          }
        }
      }
      // 等级名称映射
      if (res.data && app.globalData.viplevellist) {
        for (var i = 0; i < app.globalData.viplevellist.length; i++) {
          if (app.globalData.viplevellist[i].itemname == res.data.viplevel) {
            res.data.viplevelName = app.globalData.viplevellist[i].itemvalues;
            break;
          }
        }
      }
      that.setData({
        vip: res.data,
        vipuuid_s: vipuuid_s,
        vipuuid_u: vipuuid_u
      }),
        wx.setStorage({
          key: 'currentvip',
          data: res.data
        })
      app.globalData.currentvip = that.data.vip
      app.globalData.currentvipuuid_u = that.data.vipuuid_u
      app.globalData.currentvipuuid_s = that.data.vipuuid_s

      // app.globalData.nearlyviplist.push(that.data.vip)    
      console.log('app.globalData.viplist', app.globalData.nearlyviplist)
      set_nearlyviplist(that.data.vip)
      // viputil.getVipCardList(that, that.data.vip.uuid, '00'),
      getVipCardList(that, that.data.vip.uuid, '10');
      getVipCardList(that, that.data.vip.uuid, '20');
      getVipCardList(that, that.data.vip.uuid, '30');
      getVipCardList(that, that.data.vip.uuid, '40');

      var amountoptions = {
        vipuuid: that.data.vip.uuid,
        comptype: 'amount'
      }
      var timesoptions = {
        vipuuid: that.data.vip.uuid,
        comptype: 'times'
      }
      var periodoptions = {
        vipuuid: that.data.vip.uuid,
        comptype: 'period'
      }

      getVipComptypeCardList(that, amountoptions)
      getVipComptypeCardList(that, timesoptions)
      getVipComptypeCardList(that, periodoptions)

      console.log('set currentvip_amountcardlist：', app.globalData.currentvip_amountcardlist)
    }
  })
}

function getVipCardList(that,vipuuid,suptype) {
  var app = getApp();
  // var that = this;
  // console.log('getVipCardList', options);
  var vipuuid = vipuuid;
  var suptype = suptype;
  var host = app.globalData.host;
  var url = host + "adviser/get_vip_cardlist/";

  //无卡开单时初始化一条记录，其他有卡时不记录
  var fields = [
    { field: "company", value: app.globalData.company },
    { field: "storecode", value: app.globalData.storecode },
    { field: "ecode", value: app.globalData.ecode },
    { field: "vipuuid", value: vipuuid },
    { field: "payccode", value:''},
    { field: "suptype", value:'00'},
    { field: 'hung', value: [] },
    { field: 'fillqty', value: 0 },
    { field: 'fillprice', value: 0 },
    { field: 'fillamount', value: 0 },
    { field: 'consumeqty', value: 0 },
    { field: 'consumeprice', value: 0 },
    { field: 'consumeamount', value: 0 },
    { field:  'desc',value:''}
  ];
 
  wx.request({
    url: url, //仅为示例，并非真实的接口地址
    data: {
      vipuuid: vipuuid,
      suptype: suptype
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      if (suptype == '10') {
        that.setData({
          cardtype_10_list: res.data,
        });
        app.globalData.currentvip_cardtype10list = that.data.cardtype_10_list;      
      };
      if (suptype == '20') {
        that.setData({
          cardtype_20_list: res.data,
        });

        app.globalData.currentvip_cardtype20list = that.data.cardtype_20_list;   
      };
      if (suptype == '30') {
        that.setData({
          cardtype_30_list: res.data,
        });

        app.globalData.currentvip_cardtype30list = that.data.cardtype_30_list;   
      };
      if (suptype == '40') {
        that.setData({
          cardtype_40_list: res.data,
        });
        app.globalData.currentvip_cardtype40list = that.data.cardtype_40_list; 
      };            
    }
  })
}

function getVipComptypeCardList(that, options) {
  var app = getApp();
  var vipuuid = options.vipuuid;
  var comptype = options.comptype;
  var host = app.globalData.host;
  var url = host + "adviser/get_vip_cardlist/";

  wx.request({
    url: url, //仅为示例，并非真实的接口地址
    data: {
      company:app.globalData.company,
      vipuuid: vipuuid,
      comptype: comptype
    },
    header: {
      'content-type': 'application/json' // 默认值
    },
    success(res) {
      if (comptype == 'amount') {
        that.setData({
          amountcardlist: res.data,
        });
        app.globalData.currentvip_amountcardlist = that.data.amountcardlist,
        console.log('globl data:', app.globalData.currentvip_amountcardlist)
      };
      if (comptype == 'times') {
        that.setData({
          timescardlist: res.data,
        });
        app.globalData.currentvip_timescardlist = that.data.timescardlist
      };
      if (comptype == 'period') {
        that.setData({
          periodcardlist: res.data,
        });
        app.globalData.currentvip_periodcardlist = that.data.periodcardlist
      };
    }
  })
}

function addHung(that,options) {
  var that = this;
  var hungitems = that.data.hung.length;
  console.log('addhung.options= ', options)

  if (Object.prototype.toString.call(options.payccode) === '[object Undefined]') {
    var payccode = ''
  } else {
    var payccode = options.payccode
  };

  var hungitems = {
    ttype: options.ttype,
    stype: options.stype,
    // vipuuid: that.data.vip.uuid,
    // vcode: that.data.vip.vcode,
    // payccode : payccode,
    itemcode: options.itemcode,
    qty: options.qty,
    s_price: options.price,
    secdisc: options.secdisc,
    amount: options.amount,
    mondisc: options.mondisc,
    stype: options.stype,
    pmcode: options.pmcode,
    seccode: options.seccode,
    thrcode: options.thrcode,
    promotionsid: options.promotionsid
  };
  console.log('options.suptype:', options.suptype, hungitems);

  if (options.suptype === '10') {
    console.log(options.suptype, 'push', hungitems);
    that.data.cardtype_10_list[options.index].hung.push(hungitems);
  } else if (options.suptype === '20') {
    console.log(options.suptype, 'push', hungitems);
    that.data.cardtype_20_list[options.index].hung.push(hungitems);
  } else if (options.suptype === '00') {
    that.data.nopayccodehung[0].hung.push(hungitems)
    console.log(options.suptype, 'null push');
  };

  var fillqtykey = 'cardtype_' + options.suptype + '_list[' + options.index + '].fillqty';
  var fillpricekey = 'cardtype_' + options.suptype + '_list[' + options.index + '].fillprice';
  var fillamountkey = 'cardtype_' + options.suptype + '_list[' + options.index + '].fillamount';
  var consumeqtykey = 'cardtype_' + options.suptype + '_list[' + options.index + '].consumeqty';
  var consumepricekey = 'cardtype_' + options.suptype + '_list[' + options.index + '].consumeprice';
  var consumeamountkey = 'cardtype_' + options.suptype + '_list[' + options.index + '].consumeamount';

  if ((options.ttype == 'I') || (options.ttype == 'C')) {
    that.setData({
      [fillqtykey]: options.qty,
      [fillpricekey]: options.price,
      [fillamountkey]: options.amount
    })
  };
  if ((options.ttype == 'S') || (options.ttype == 'G')) {
    that.setData({
      [consumeqtykey]: options.qty,
      [consumepricekey]: options.price
    });
    if (options.suptype == '10') {
      that.setData({
        [consumeamountkey]: options.amount + that.data.cardtype_10_list[options.index].consumeamount
      })
    };
    if (options.suptype == '20') {
      that.setData({
        [consumeamountkey]: options.amount + that.data.cardtype_20_list[options.index].consumeamount
      })
    }
  };

}

function newCardHung(that, options) {
  var app = getApp();
  var host = app.globalData.host;
  var company = app.globalData.company
  var storecode = app.globalData.storecode
  var ecode = app.globalData.ecode
  var param = options
  var url = host + 'adviser/newcardhung/?param=' + JSON.stringify(param)
  console.log(url)
  wx.request({
    method: 'POST',
    url: url,
    // data: { 
    // },
    header: {
      // 'content-type': 'application/json' // 默认值
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      
      console.log(res.data)
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }

  })
}

function commitHung(that,options) {
  var app = getApp();
  var host = app.globalData.host;
  var company = app.globalData.company
  var storecode = app.globalData.storecode
  var ecode = app.globalData.ecode
  var param = options
  var url = host + 'adviser/addhung/?param=' + JSON.stringify(param)
  console.log(url)
  wx.request({
    method: 'POST',
    url: url,
    // data: { 
    // },
    header: {
      // 'content-type': 'application/json' // 默认值
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log(res.data)
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }

  })
}

function getHung(that, options) {
  console.log('getHung',options)
  var app = getApp();

  var host = app.globalData.host
  var vipuuid_u = options

  var param = {
    company: app.globalData.company,
    storecode: app.globalData.storecode,
    ecode: app.globalData.ecode,
    vipuuid: app.globalData.currentvip.uuid
  }
  console.log('param',param)
  var url = host + 'adviser/get_hung_byvipuuid/'    
  console.log(url)
  wx.request({
    method: 'GET',
    url: url,
    data: param,
    header: {
      // 'content-type': 'application/json' // 默认值
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('get_hung_byvipuuid',res)
      that.setData({
        hungslist: res.data
      })

    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}

function getHungItem(that, options) {
  console.log('getHungItem', options)
  var mythis=this;
  var app = getApp();

  var host = app.globalData.host
  var hungitemuuid = options
  console.log(options,options.uuid)

  var param = {
    company: app.globalData.company,
    storecode: app.globalData.storecode,
    // ecode: app.globalData.ecode,
    uuid: options
  }
  console.log('param', param)
  var url = host + 'adviser/get_hungitem/'
  console.log(url)
  util.showLoading('数据加载中')
  wx.request({
    method: 'GET',
    url: url,
    data: param,
    header: {
      // 'content-type': 'application/json' // 默认值
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('get_hung_byvipuuid', res)
      that.setData({
        hungitem: res.data,
        hungitemuuid: res.data[0].itemuuid,
        ttype: res.data[0].ttype,
        itemname: res.data[0].itemname,
        price: res.data[0].price,
        qty: res.data[0].qty,
        secdisc: res.data[0].secdisc,
        mondisc: res.data[0].mondisc,
        amount: res.data[0].amount,
        stype:  res.data[0].stype,
        pmcode: res.data[0].pmcode,
        seccode:res.data[0].seccode,
        thrcode:res.data[0].thrcode,
        psstatus: res.data[0].psstatus,
        depositeflag: res.data[0].depositeflag,
        remark:res.data[0].remark,
        payccode: res.data[0].payccode || ''
      });

      // 根据 payccode 自动选中付款卡
      var pc = that.data.payccode;
      var found = -1;
      if (pc && that.data.paycardlist && that.data.paycardlist.length > 0) {
        for (var i = 0; i < that.data.paycardlist.length; i++) {
          var c = that.data.paycardlist[i];
          if (typeof c === "string" && c == pc) { found = i; break; }
          if (typeof c === "object" && c.ccode == pc) { found = i; break; }
        }
        if (found >= 0) {
          that.setData({ paycardindex: found });
        }
      }
      if (that.data.ttype=='S'){
        that.setData({
          ttypename:'服务'
        })
      }
      if (that.data.ttype == 'G') {
        that.setData({
          ttypename: '商品'
        })
      }
      if (that.data.ttype == 'C') {
        that.setData({
          ttypename: '售卡'
        })
      }
      if (that.data.ttype == 'I') {
        that.setData({
          ttypename: '充值'
        })
      }
      var stypeparam = {
        type: 'stype',
        code: that.data.stype
      }
      console.log('stypeparam：', stypeparam)
      getIndexByCode(that, stypeparam)

      var depositeflagparam = {
        type: 'depositeflag',
        code: that.data.depositeflag
      }
      console.log('depositeflagparam: ', depositeflagparam)
      getIndexByCode(that, depositeflagparam)
     

      if (that.data.psstatus == '10') {
        that.setData({
          modifiedflag: true,
        })
      } else {
        that.setData({
          modifiedflag: false
        })      
      }

      mythis.getIndexByCode(that,{ type: 'pmcode', code: that.data.pmcode })
      mythis.getIndexByCode(that,{ type: 'seccode', code: that.data.seccode })
      mythis.getIndexByCode(that,{ type: 'thrcode', code: that.data.thrcode })   
      mythis.getIndexByCode(that, { type: 'psstatus', code: that.data.psstatus })         
      util.hideLoading('数据加载完成！')
    },
    fail: function (res) {
      console.log("failed")
      util.hideLoading('数据加载失败！')
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}

function updateHungItem(that,options){

}

function get_viplist_bycrmrptid(that, param) {
  // var that = this;
  var app = getApp();
  var url = app.globalData.host + 'crm/get_viplist_bycrmrptid'
  wx.showLoading({
    title:'数据加载中...'
  })

  wx.request({
    method: 'GET',
    url: url,
    data:param,
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('get_viplist_bycrmtypeid', res.data)
      that.setData({
        vipList: res.data
      })

    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
      setTimeout(() => {
        wx.hideLoading()
      }, 2000);

    }
  })
}

function bindQtyChange (that, qty) {
  // var index = that.data.itemindex;
  // console.log('e=', e, 'index=', index);
  // var list = that.data.itemlist;
  // var qty = e.detail.value;
  var price = that.data.price;
  var secdisc = that.data.secdisc;
  var mondisc = that.data.mondisc;
  var amount = qty * price * secdisc - mondisc;

  var fields = [
    { field: 'qty', value: qty },
    { field: 'price', value: price },
    { field: 'secdisc', value: secdisc },
    { field: 'mondisc', value: mondisc },
    { field: 'amount', value: amount }
  ]

  for (var item in fields) {
    var key = fields[item].field;
    that.setData({
      [key]: fields[item].value
    })
  };
}

function bindSecdiscChange(that,secdisc){
  var qty = that.data.qty;
  var price = that.data.price;
  var mondisc = that.data.mondisc;
  var amount = qty * price * secdisc - mondisc; 
  var fields = [
    { field: 'qty', value: qty },
    { field: 'price', value: price },
    { field: 'secdisc', value: secdisc },
    { field: 'mondisc', value: mondisc },
    { field: 'amount', value: amount }
  ]

  for (var item in fields) {
    var key = fields[item].field;
    that.setData({
      [key]: fields[item].value
    })
  };
}

function bindMondiscChange(that,mondisc){
  var qty = that.data.qty;
  var price = that.data.price;
  var secdisc = that.data.secdisc;
  var amount = qty * price * secdisc - mondisc; 
  var fields = [
    { field: 'qty', value: qty },
    { field: 'price', value: price },
    { field: 'secdisc', value: secdisc },
    { field: 'mondisc', value: mondisc },
    { field: 'amount', value: amount }
  ]

  for (var item in fields) {
    var key = fields[item].field;
    that.setData({
      [key]: fields[item].value
    })
  };
}

function bindPriceChange (that,price) {
  // var price = e.detail.value;
  var qty = that.data.qty;
  var secdisc = that.data.secdisc;
  var mondisc = that.data.mondisc;
  var amount = qty * price * secdisc - mondisc;

  var fields = [
    { field: 'qty', value: qty },
    { field: 'price', value: price },
    { field: 'secdisc', value: secdisc },
    { field: 'mondisc', value: mondisc },
    { field: 'amount', value: amount }
  ]

  for (var item in fields) {
    var key = fields[item].field;
    that.setData({
      [key]: fields[item].value
    })
  };
}

function bindBackflagChange(that,e){
  var app = getApp();
  console.log(e)
  if (e.detail.value) {
    var backflag = 'Y'
    var backflagName = '退'
    var backflagChecked = true
  } else {
    var backflag = 'N'
    var backflagName = '正常'
    var backflagChecked = false
  };
  that.setData({
    backflag: backflag,
    backflagName: backflagName,
    backflagChecked: backflagChecked
  }); 
  if (that.data.backflag == 'Y') {
    var qty = -Math.abs(that.data.qty)
  } else {
    var qty = Math.abs(that.data.qty)
  }

  var price = that.data.price;
  var secdisc = that.data.secdisc;
  var mondisc = that.data.mondisc;
  var amount = qty * price * secdisc - mondisc;

  var fields = [
    { field: 'qty', value: qty },
    { field: 'price', value: price },
    { field: 'secdisc', value: secdisc },
    { field: 'mondisc', value: mondisc },
    { field: 'amount', value: amount }
  ]
  for (var item in fields) {
    var key = fields[item].field;
    that.setData({
      [key]: fields[item].value
    })
  };
}

function bindStypeChanged(that,e){
  if (e.detail.value>=0){
    console.log(e, that.data.stypelist[e.detail.value].itemname)
    that.setData({
      stypeindex: e.detail.value,
      stype: that.data.stypelist[e.detail.value].itemname,
      stypename: that.data.stypelist[e.detail.value].itemvalues
    })
  }
}

function bindStypeChanged_old (that,e) {
  console.log('bindStypeChanged e:',e)
  var app = getApp();
  var stypeindex = 0
  var stype = 'N'
  var stypename = '正常'
  var stypechecked = false
  var earnestflag = false
  var stypechecked = false;
  var stypeflag = e.detail.value
  if (that.data.backflag == 'Y' && stypeflag == 2) {
    wx.showToast({
      title: '退操作，不能够选择交易为定金！',
    })
  } else {
    if (e.detail.value) {
      console.log('e.detail.value',e.detail.value)
      if (e.detail.value == 0) {
        var stypeindex = e.detail.value
        var stype='N'
        var stypename='正常'
        var stypechecked = true
        var earnestflag = false
        console.log('e.detail.value == 0',stype)
      }
      if (e.detail.value == 1) {
        var stypeindex = e.detail.value
        var stype='P'
        var stypename='赠送'
        var stypeindex = e.detail.value
        var stypechecked = true
        var earnestflag = false
        console.log('e.detail.value == 1',stype)
      }

      if (e.detail.value == 2) {
        var earnestflag = true

        console.log('e.detail.value == 2',stype)
      }
      var stype = that.data.stypelist[e.detail.value].itemname
      var stypename = that.data.stypelist[e.detail.value].itemvalues
      var stypeindex = e.detail.value
      console.log('stype',stype,stypename,stypeindex)

    } else {
      var stypeindex = 0
      var stype = 'N'
      var stypename = '正常'
      var stypechecked = false
      var earnestflag = false
    };
    that.setData({
      stype: stype,
      stypename: stypename,
      stypeindex: stypeindex,
      stypechecked: stypechecked,
      earnestflag: earnestflag
    });
    console.log('that.stype',that.data.stype,that.data.stypename,that.data.stypeindex)
    // viputils.bindStypeChanged(that, e)
  }
}

function bindDepositeflagChange(that,e){
  var app=getApp()
  if (e.detail.value >=0){
    that.setData({
      depositeflagindex:e.detail.value,
      depositeflagindexname: that.data.depositeflaglist[e.detail.value].depositeflagname,
      depositeflag:that.data.depositeflaglist[e.detail.value].depositeflag
    })
  }
}

function bindViplevelChange(that,e) {
  var idx = parseInt(e.detail.value, 10);
  if (isNaN(idx)) idx = -1;
  var list = that.data.viplevellist || [];
  if (idx >= 0 && idx < list.length && list[idx]) {
    var row = list[idx];
    console.log(e, row.viplevelname)
    that.setData({
      viplevelindex: idx,
      viplevel: row.ecode || '',
      viplevelname: row.ename || row.viplevelname || row.ecode || ''
    })
  }
}

function bindPmcodeChange(that,e) {
  var idx = parseInt(e.detail.value, 10);
  if (isNaN(idx)) idx = -1;
  var list = that.data.pmcodelist || [];
  if (idx >= 0 && idx < list.length && list[idx]) {
    var row = list[idx];
    console.log(e, row)
    that.setData({
      pmcodeindex: idx,
      pmcode: row.ecode || '',
      pmname: row.ename || row.cname || row.name || row.ecode || ''
    })
  }
}

function bindSeccodeChange (that,e) {
  var idx = parseInt(e.detail.value, 10);
  if (isNaN(idx)) idx = -1;
  var list = that.data.seccodelist || [];
  if (idx >= 0 && idx < list.length && list[idx]) {
    var row = list[idx];
    console.log(e)
    that.setData({
      seccodeindex: idx,
      seccode: row.ecode || '',
      secname: row.ename || row.cname || row.name || row.ecode || ''
    })
  }
}

function bindThrcodeChange(that, e) {
  var idx = parseInt(e.detail.value, 10);
  if (isNaN(idx)) idx = -1;
  var list = that.data.thrcodelist || [];
  if (idx >= 0 && idx < list.length && list[idx]) {
    var row = list[idx];
    console.log(e)
    that.setData({
      thrcodeindex: idx,
      thrcode: row.ecode || '',
      thrname: row.ename || row.cname || row.name || row.ecode || ''
    })
  }
}

function bindPromotionsChange(that,e) {
  if (e.detail.value >= 0) {
      var promotionsid = e.detail.value;
      that.setData({
        promotionsid: promotionsid
      })
  }
}

function bindPaycardChange(that, e) {
  log.info('picker cardtype 发生选择改变，携带值为', e.detail.value);

  if (e.detail.value < 0) {
    that.setData({
      paycardindex: -1,
      payccode: '',
      paycardsuptype: '00'
    })
  } else {
    that.setData({
      paycardindex: e.detail.value,
      payccode: that.data.paycardlist[e.detail.value].ccode,
      paycardsuptype: that.data.paycardlist[e.detail.value].suptype
    })
  }

  // that.setData({
  //   paycardindex: e.detail.value,
  //   payccode: that.data.paycardlist[e.detail.value]
  //   // newcardsuptype: that.data.cardtype10list[e.detail.value].suptype
  // })
  that.onShow()
}

function getVipPage(that){
  var pages = getCurrentPages(); // 获取页面栈
  if (pages.length > 0) {
    for (var page in pages) {
      if (pages[page].route == 'vip/vip') {
        that.setData({
          vipPage: pages[page]
          // vipuuid
        })
      }
    }
  }
}

function getVipKaidanPage(that) {
  var pages = getCurrentPages(); // 获取页面栈
  if (pages.length > 0) {
    for (var page in pages) {
      if (pages[page].route == 'vip/kaidan/kaidan') {
        console.log(pages[page])
        that.setData({
          vipuuid: pages[page].data.vipuuid,
          payccode: pages[page].data.payccode, 
          // vipuuid
        })
      }
    }
  }
}

// 对服务项目补充开单需要的相关字段信息
function init_itemlist(that) {
  // var that = this;
  var app = getApp();
  var fields = [
    { filed: 'payccode', value: '' },
    { field: 'qty', value: 0 },
    { field: 'secdisc', value: 1 },
    // {field:'s_price',value:0},
    { field: 'amount', value: 0 },
    { field: 'mondisc', value: 0 },
    { field: 'pmcode', value: '' },
    { field: 'seccode', value: '' },
    { field: 'thrcode', value: '' },
    // { field: 'stype', value: 'N' },
    { field: 'promotionsid', value: '0' }
  ];
  for (var index in that.data.itemlist) {
    for (var item in fields) {
      var key = 'itemlist[' + index + '].' + fields[item].field;
      // console.log(key);
      that.setData({
        [key]: fields[item].value
      })
    };
  }
  app.globalData.current_itemlist = that.data.itemlist
}

function set_nearlyviplist(vip) {
  var app = getApp()
  var nearlyviplist = app.globalData.nearlyviplist
  console.log(nearlyviplist)
  var vipuuid = vip.uuid
  var index=-1
  if (vipuuid.length > 0) {
    console.log('vipuuid:',vipuuid,vip.mtcode)
    function pFn(p) { return p.uuid == vipuuid; }
    index = nearlyviplist.findIndex(pFn)
    console.log('nearlyviplist findIndex:', index)
    if (index >= 0) {
      nearlyviplist.splice(index, 1)
      nearlyviplist.unshift(vip)
      app.globalData.nearlyviplist = nearlyviplist
    } else {
      nearlyviplist.unshift(vip)
      app.globalData.nearlyviplist = nearlyviplist     
    }
    wx.setStorage({
      key: 'nearlyviplist',
      data: nearlyviplist,
    })
    console.log(nearlyviplist)
  }
}

function get_shoppingcart(that) {
  var app = getApp();
  var thisutil=this;
  // var that = this;

  var host = app.globalData.host
  var vipuuid_u = app.globalData.currentvip.uuid
  var returnlist = 'item_s_list'
  var ttype = 'S'
  console.log('app.globalData.currentvip.uuid',vipuuid_u)

  that.setData({
    item_s_list: [],
    item_g_list: []
  })

  var options = {
    vipuuid: vipuuid_u,
    returnlist: 'item_s_list',
    ttype: 'S'
  }
  get_shoppingcart_ttype(that,options)
  var options = {
    vipuuid: vipuuid_u,
    returnlist: 'item_g_list',
    ttype: 'G'
  }
  get_shoppingcart_ttype(that,options)
}

function get_ShoppingCartItem(that, option) {
  var app = getApp()
  // var that = this;
  var uuid = option
  var param = {
    company: app.globalData.company,
    storecode: app.globalData.storecode,
    ecode: app.globalData.ecode,
    vipuuid: that.data.vip.uuid,
    uuid: uuid
  };
  var url = app.globalData.host + 'adviser/get_shoppingcartitem/?param=' + JSON.stringify(param)
  wx.request({
    method: 'POST',
    // data:{},
    url: url,
    header: {
      // 'content-type': 'application/json' // 默认值
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      that.setData({
        shoppingcartitem: res.data[0],
        uuid: res.data[0].uuid,
        payccode: res.data[0].ccode,
        itemcode: res.data[0].itemcode,
        itemname: res.data[0].itemname,
        ttype: res.data[0].ttype,
        stype: res.data[0].stype,
        price: res.data[0].price,
        qty: res.data[0].qty,
        secdisc: res.data[0].secdisc,
        mondisc: res.data[0].mondisc,
        amount: res.data[0].amount,
        pmcode: res.data[0].pmcode,
        seccode: res.data[0].seccode,
        thrcode: res.data[0].thrcode,
        promotionsid: res.data[0].promotionsid,
        secdiscdesc: res.data[0].secdisc * 100 + '%',
        planqty: res.data[0].planqty,
        planamount: res.data[0].planamount,
        payedamount: res.data[0].payedamount,
        oweamount: res.data[0].oweamount,
        remark: res.data[0].remark,
        depositeflag:res.data[0].depositeflag

      })

      if (res.data.length > 0) {
        // that.init_ShoppiongCartItem(returnlist)
      }

      var stypeparam = {
        type: 'stype',
        code: that.data.stype
      }
      console.log('stypeparam：',stypeparam)
      getIndexByCode(that, stypeparam)
 
      var depositeflagparam = {
        type: 'depositeflag',
        code: that.data.depositeflag
      }
      console.log('depositeflagparam',depositeflagparam)
      getIndexByCode(that, depositeflagparam)
      
      var paycardparam = {
        type: 'paycard',
        code: that.data.payccode
      }
      getIndexByCode(that, paycardparam)

      var pmparam = {
        type: 'pmcode',
        code: that.data.pmcode
      }
      getIndexByCode(that, pmparam)
      var secparam = {
        type: 'seccode',
        code: that.data.seccode
      }
      getIndexByCode(that, secparam)
      var thrparam = {
        type: 'thrcode',
        code: that.data.thrcode
      }
      getIndexByCode(that, thrparam)
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}

function get_shoppingcart_ttype(that,options) {
  var app = getApp();
  // var that = this;
  var host = app.globalData.host
  var vipuuid = options.vipuuid
  var returnlist = options.returnlist
  var ttype = options.ttype

  var param = {
    company: app.globalData.company,
    storecode: app.globalData.storecode,
    ecode: app.globalData.ecode,
    vipuuid: vipuuid,
    ttype: ttype
  }
  var url = host + 'adviser/get_shoppingcart/?param=' + JSON.stringify(param)
  // var url = host + 'adviser/get_shoppingcart/'    
  console.log(url)
  wx.request({
    method: 'POST',
    url: url,
    // data: param,
    header: {
      // 'content-type': 'application/json' // 默认值
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log(res)
      that.setData({
        [returnlist]: res.data
      })
      if (ttype=='S'){
        app.globalData.shoppingcart_item_s_list=res.data
        if (res.data.length > 0) {
          app.globalData.currentvip_shoppingcarditems_s = res.data.length
        }
      }
      if (ttype == 'G') {
        app.globalData.shoppingcart_item_g_list = res.data
        if (res.data.length > 0) {
          app.globalData.currentvip_shoppingcarditems_g = res.data.length
          // that.init_ShoppiongCartItem(returnlist)
        }
      }
      // if (ttype == 'C') {
      //   app.globalData.shoppingcart_item_c_list = res.data
      // }      
      console.log('res.data.length:', res.data.length,app.globalData.shoppingcart_item_s_list,app.globalData.shoppingcart_item_g_list,)
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}

// 对象数组查找  通过findindex
function getIndexByCode(that,options) {
  var app=getApp()
  console.log('getIndexByCode options:',options)
  var codetype = options.type;
  var code = options.code;
  var index = -1;

  if (codetype=='viptype'){
    function pFn(p) { return p.value == code; }
    index = that.data.vipTypeList.findIndex(pFn)
    console.log('vipTypeList:', index)
    that.setData({
      viptypeindex: index
    })
    if (index >= 0) {
      that.setData({
        viptype: that.data.vipTypeList[index].value
      })
    }  
  }

  if (codetype == 'vipcasetype') {
    function pFn(p) { return p.itemname == code; }
    index = that.data.vipcasetypeList.findIndex(pFn)
    that.setData({
      vipcasetypeIndex: index
    })
  }

  if (codetype == 'stype') {
    function pFn(p) { return p.itemname == code; }
    index = that.data.stypelist.findIndex(pFn)
    that.setData({
      stypeindex: index
    })
  }

  if (codetype == 'depositeflag') {
    function pFn(p) { return p.depositeflag == code; }
    index = that.data.depositeflaglist.findIndex(pFn)
    that.setData({
      depositeflagindex: index
    })
  } 
  if (codetype == 'paycard') {
    function pFn(p) { return p.ccode == code; }
    index = that.data.paycardlist.findIndex(pFn)
    that.setData({
      paycardindex: index
    })
    if (index >= 0) {
      that.setData({
        payccode: that.data.paycardlist[index].ccode
      })
    }
  }; 

  if (codetype == 'empl') {
    function pFn(p) { return p.ecode == code; }
    index = that.data.empllist.findIndex(pFn)
    console.log('emplindex:', index)
    that.setData({
      emplIndex: index
    })
  };
  if (codetype == 'empluuid') {
    function pFn(p) { return p.uuid == code; }
    index = that.data.empllist.findIndex(pFn)
    console.log('emplindex:', index)
    that.setData({
      emplIndex: index
    })
  };


  if (codetype == 'pmcode') {
    function pFn(p) { return p.ecode == code; }
    index = that.data.pmcodelist.findIndex(pFn)
    console.log('pmcodeindex:', index)
    that.setData({
      pmcodeindex: index
    })
    if (index >=0){
      that.setData({
        pmcode: that.data.pmcodelist[index].ecode,
        pmname: that.data.pmcodelist[index].ename
      })
    }
  };
  if (codetype == 'seccode') {
    function pFn(p) { return p.ecode == code; }
    index = that.data.seccodelist.findIndex(pFn)
    console.log('seccodeindex:', index)
    that.setData({
      seccodeindex: index
    })
    if (index >= 0) {
      that.setData({
        seccode: that.data.seccodelist[index].ecode,
        secname: that.data.seccodelist[index].ename
      })
    }
  };
  if (codetype == 'thrcode') {
    function pFn(p) { return p.ecode == code; }
    index = that.data.thrcodelist.findIndex(pFn)
    console.log('thrcodeindex:', index)
    that.setData({
      thrcodeindex: index
    })
    if (index >= 0) {
      that.setData({
        thrcode: that.data.thrcodelist[index].ecode,
        thrname: that.data.thrcodelist[index].ename
      })
    }
  }; 
  if (codetype == 'room') {
    function pFn(p) { return p.roomid == code; }
    index = that.data.roomlist.findIndex(pFn)
    console.log('roomindex:', index)
    that.setData({
      roomIndex: index
    })
  };
  if (codetype == 'instrument') {
    function pFn(p) { return p.instrumentid == code; }
    index = that.data.instrumentlist.findIndex(pFn)
    console.log('instrumentindex:', index)
    that.setData({
      instrementIndex: index
    })
  };
  if (codetype == 'source') {
    console.log('source:',codetype,code,that.data.source)
    function pFn(p) { return p.itemname == code; }
    index = that.data.source.findIndex(pFn)
    console.log('sourceindex:', index)
    that.setData({
      sourceindex: index
    })
  };

  if (codetype == 'psstatus') {
    console.log('psstatus:', codetype, code, app.globalData.psstatuslist)
    function pFn(p) { return p.itemname == code; }
    index = that.data.psstatuslist.findIndex(pFn)
    console.log('psstatusindex:', index)
    that.setData({
      psstatusindex: index
    })
  };

  if (codetype == 'salonvip_status') {
    console.log('get index salonvip_status :', codetype, code, app.globalData.salonvip_status_list )
    function pFn(p) { return p.code == code; }
    index = that.data.salonvip_status_list.findIndex(pFn)
    console.log('salonvip_index:', index)
    that.setData({
      salonvip_status_index: index
      // salonvip_status_index: index
    })
  } ; 

  if (codetype == 'salonlist') {
    console.log('get index salonlist :', codetype, code, app.globalData.salonlist )
    function pFn(p) { return p.uuid == code; }
    index = that.data.salonlist.findIndex(pFn)
    console.log('salonlist_index:', index)
    that.setData({
      salonlistindex: index
    })
  } ;  

  if (codetype == 'viplevellist') {
    console.log('get index viplevellist :', codetype, code, app.globalData.viplevellist )
    function pFn(p) { return p.uuid == code; }
    index = that.data.viplevellist.findIndex(pFn)
    console.log('viplevel_index:', index)
    that.setData({
      viplevellistindex: index
    })
  } ;  

}

function get_vipcasedetail_byvipuuid(that){
  var url = host + 'crm/get_vipcasedetail_byvipuuid'

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company: app.globalData.company,
      vipuuid: app.globalData.currentvipuuid_s
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log(res)
      that.setData({
        vipcasedetail:res.data
      })
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
  
}

function get_vipcasedetail(that, options){
  var url = host + 'crm/get_vipcasedetail'
  var uuid = options

  wx.request({
    method: 'GET',
    url: url,
    data: {
      uuid: uuid
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log(res)
      that.setData({
        vipcasedetail: res.data[0]
      })
      that.setData({
        uuid: uuid,
        ecode: that.data.vipcasedetail.ecode,
        vipcasetype: that.data.vipcasedetail.casetype,
        detail: that.data.vipcasedetail.detail,
        created_date: that.data.vipcasedetail.created_date,
        nextdate: that.data.vipcasedetail.nextdate,
        nextecode: that.data.vipcasedetail.nextecode,
        status: that.data.vipcasedetail.status
      })
      var ecode = that.data.ecode
      var param = {
        type: 'empl',
        code: ecode
      }
      if (ecode) {
        getIndexByCode(that, param)
      }

      var vipcasetype = that.data.vipcasetype
      var param = {
        type: 'vipcasetype',
        code: vipcasetype
      }
      console.log('vipcasetype=',vipcasetype)
      if (vipcasetype){
        getIndexByCode(that, param)
      }

    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })
}

function get_goodsstockqty(that,options){
  var url = host + 'goods/get_goodstockqty'
  var gcode = options

  wx.request({
    method: 'GET',
    url: url,
    data: {
      company:app.globalData.company,
      storecode:app.globalData.storecode,
      gcode: gcode
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success: function (res) {
      console.log('goodsstock',gcode, res)
      that.setData({
        stockqty2: res.data
      })
    },
    fail: function (res) {
      console.log("failed")
    },
    complete: function (res) {
      console.log("finished")
    }
  })  
}

function getVipConsume(that,options) {
  console.log('getvipconsume option',options)
  var company = app.globalData.company;

  var url = app.globalData.host + 'crm/get_vipconsumelist/';
  console.log(url)
  wx.showLoading({
    title: '数据加载中',
  })
  wx.request({
    method: 'GET',
    url: url, //仅为示例，并非真实的接口地址
    data: {
      company: company,
      vipuuid: options.vipuuid,
      fromdate: options.fromdate,
      todate: options.todate,
      keyword:options.keyword
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success(res) {
      console.log(res.data)
      // setTimeout(200)
      if (that && typeof that.buildConsumeGroups === 'function') {
        that.buildConsumeGroups(res.data)
      } else {
        that.setData({
          consumedetail: res.data
        })
      }
    },
    complete(res){
      wx.hideLoading()
    }
  });
}

function get_vipPage(that) {
  var pages = getCurrentPages(); // 获取页面栈
  if (pages.length > 0) {
    for (var page in pages) {
      if (pages[page].route == 'vip/vip') {
        var vipPage = pages[page]
        return vipPage;
      }
    }
  }
}

function get_SalonVipList(that,options) {
  console.log('getsalonviplist option',options)
  var company = app.globalData.company;
  var storecode = app.globalData.storecode;
  var type = options.type;
  var vipuuid = options.vipuuid;
  var salon_id = options.salon_id;

  var url = app.globalData.host + 'crm/get_salonvip_list/';
  console.log(url)
  wx.showLoading({
    title: '数据加载中',
  })
  wx.request({
    method: 'GET',
    url: url, 
    data: {
      type: type,
      company: company,
      storecode: storecode,
      vipuuid: vipuuid,
    },
    header: {
      // 'content-type': 'application/json' // 默认值
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success(res) {
      console.log('salonviplist res, res.data:',res, res.data)
      // setTimeout(200)
      that.setData({
        salonviplist: res.data
      })
    },
    complete(res){
      wx.hideLoading()
    }
  });
}

function get_SalonVipDetail(that,options) {
  console.log('getsalonvip option',options)
  var company = app.globalData.company;
  var storecode = app.globalData.storecode;
  var salonvip_uuid = options

  var url = app.globalData.host + 'crm/get_salonvip_detail/';
  console.log(url)
  wx.showLoading({
    title: '数据加载中',
  })
  wx.request({
    method: 'GET',
    url: url, //仅为示例，并非真实的接口地址
    data: {
      company: company,
      storecode: storecode,
      uuid: salonvip_uuid
    },
    header: {
      // 'content-type': 'application/json' // 默认值
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success(res) {
      console.log('salonvip res, res.data:',res, res.data)
      // setTimeout(200)
      that.setData({
        salonvip: res.data[0]
      })

    },
    complete(res){
      wx.hideLoading()
    }
  });
}

module.exports = {
  getVipBaseInfo: getVipBaseInfo,
  getVipCardList: getVipCardList,
  getVipComptypeCardList: getVipComptypeCardList,
  bindQtyChange: bindQtyChange,
  bindPriceChange: bindPriceChange,
  bindSecdiscChange:bindSecdiscChange,
  bindMondiscChange:bindMondiscChange,
  bindBackflagChange: bindBackflagChange,
  bindStypeChanged: bindStypeChanged,
  bindDepositeflagChange:bindDepositeflagChange,
  bindPmcodeChange: bindPmcodeChange,
  bindSeccodeChange: bindSeccodeChange,
  bindThrcodeChange: bindThrcodeChange,
  bindPromotionsChange: bindPromotionsChange,
  bindPaycardChange: bindPaycardChange,
  getVipPage: getVipPage,
  getVipKaidanPage: getVipKaidanPage,
  commitHung: commitHung,
  newCardHung: newCardHung,
  getHung: getHung,
  getHungItem: getHungItem,
  init_itemlist: init_itemlist,
  getIndexByCode:getIndexByCode,
  set_nearlyviplist: set_nearlyviplist,
  get_shoppingcart: get_shoppingcart,
  get_ShoppingCartItem: get_ShoppingCartItem,
  get_shoppingcart_ttype: get_shoppingcart_ttype,
  get_viplist_bycrmrptid: get_viplist_bycrmrptid,
  get_vipcasedetail_byvipuuid: get_vipcasedetail_byvipuuid,
  get_vipcasedetail: get_vipcasedetail,
  get_goodsstockqty:get_goodsstockqty,
  getVipConsume:getVipConsume,
  get_SalonVipList: get_SalonVipList,
  get_SalonVipDetail:get_SalonVipDetail,
}
