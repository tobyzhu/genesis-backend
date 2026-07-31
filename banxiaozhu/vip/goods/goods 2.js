var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({
  data: {
    storecode:'',
    scrollTop: 100,

    vipuuid:'',
    vcode:'',
    vname:'',

    vip:{},

    ttype: 'G',
    ttypename: '商品',
    stype: 'N',
    stypename: '正常',
    index: 0,

    payccode: '',
    paycardsuptype: '10',
    paycardindex:-1,
    paycardlist:[],

    multiArray: [[{}],[{}]],
    multiIndex: [0, 0],
    goodsList:[],
    itemlist:[],
    hung:[],
    value: 1,
    customItem: '全部',
    pmcodelist: [],
    pmcode: '',
    pmname: '',
    pmcodeindex: -1,
    seccodelist: [],
    seccode: '',
    secname: '',
    seccodeindex: -1,
    thrcodelist: [],
    thrcode: '',
    thrname: '',
    thrcodeindex: -1,
    promotionsid: '0',
    promotionsindex: -1,
    promotionslist: [
      {
        promotionsid: '0',
        promotionsname: '正常'
      }
    ]
  },


  onLoad: function(options){
    var app = getApp();
    var that = this;
    that.setData({
      storecode: app.globalData.storecode,
      vip: app.globalData.currentvip,
      paycardlist: app.globalData.currentvip_amountcardlist,
      payccode: app.globalData.payccode,
      vipuuid: app.globalData.currentvipuuid_u,
      vipuuid_s: app.globalData.currentvipuuid_s,
      pmcodelist: app.globalData.pmcodelist,
      seccodelist: app.globalData.seccodelist,
      thrcodelist: app.globalData.seccodelist,
      itemlist: app.globalData.goodslist
    })

    viputils.getVipPage(that);

    if (options && options.searchValue) {
      that.setData({
        searchValue: options.searchValue
      })
      that.get_itemlist_bykeyword()
    }
    else {
      // util.get_GoodsList(that)
      viputils.init_itemlist(that)
      app.globalData.current_itemlist = that.data.itemlist

    }

    // that.get_goodsbrand()
    // viputil.get_brandlist(that,'goods',key)

  },

  bindPmcodeChange: function (e) {
    var that = this;
    viputils.bindPmcodeChange(that, e)
  },
  bindSeccodeChange: function (e) {
    var that = this;
    viputils.bindSeccodeChange(that, e)
  },
  bindThrcodeChange: function (e) {
    var that = this;
    viputils.bindThrcodeChange(that, e)
  },
  

  bindPaycardChange: function (e) {
    var that = this;
    that.setData({
      paycardindex: e.detail.value
    })
    that.onShow()
  },

  get_itemlist_bykeyword: function () {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_goodslist_bykeyword';
    // var url = app.globalData.host + 'baseinfo/get_goods';
    // console.log(xinqu)
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        // ecode: app.globalData.ecode,
        searchvalue: that.data.searchValue

      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        that.setData({
          fail: false,
          itemlist: res.data
        })
        app.globalData.current_itemlist = that.data.itemlist
        // viputils.init_itemlist(that)

      },
      fail: function (res) {
        console.log("failed")
        that.setData({
          fail: true
        })
      },
      complete: function (res) {
        console.log("finished")
      }

    })

  },

  get_itemlist_brandanddisplayclasse: function (options) {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_itemlist_brandanddisplayclasse';
    var brand = options.brand;
    var displayclass=options.displayclass
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        type: 'goods',
        brand: brand,
        displayclass1: displayclass
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        var key = 'multiArray[2]';
        that.setData({
          [key]: res.data,
          goodslist:res.data
        });
        var fields = [
          {
            field: 'ttype',
            value: 'G'
          },
          {
            field: 'stype',
            value: 'N'
          },          
          {
            field: 'secdisc',
            value: 1
          },
          {
            field: 'mondisc',
            value: 0
          },
          {
            field: 'qty',
            value: 0
          },
          {
            field: 'amount',
            value: 0
          },
          {
            field: 'pmcode',
            value: ''
          },
          {
            field: 'seccode',
            value: ''
          }, ,
          {
            field: 'thrcode',
            value: ''
          }                                        
        ]
        for (var goods in that.data.goodslist){
          for (var item in fields){
            var key = 'goodslist['+goods+'].'+fields[item].field
            console.log('key',key)
            that.setData({
              [key]: fields[item].value
            })
          }
        }

      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }
    })
  },
  
  onSearchChange(e) {
    console.log('onSearchChange', e)
    var that = this;

    this.setData({
      value: e.detail.value,
    })
  },
  onSearchFocus(e) {
    console.log('onFocus', e)
  },
  onSearchBlur(e) {
    console.log('onBlur', e)
  },
  onSearchConfirm(e) {
    console.log('onConfirm',e)
    var app = getApp();
    var that = this;
    var keyword = e.detail.value;
    var list = that.data.viplist;
    var reg = new RegExp(keyword);
  },
  onSearchClear(e) {
    console.log('onClear', e)

  },
  onSearchCancel(e) {
    console.log('onCancel', e)
  },

  gotoShoppingCart: function () {
    var that = this;
    wx.navigateTo({
      url: '../shoppingcar/shoppingcar',
    })
  },

  goodsAddShoppingCart: function () {
    var that = this;
    var app = getApp();
    var len = that.data.itemlist.length;
    for (var i = 0; i < len; i++) {
      if (that.data.itemlist[i].qty != 0) {
        var hungitem = {
          company: app.globalData.company,
          storecode: app.globalData.storecode,
          ecode: app.globalData.ecode,
          vipuuid: that.data.vipuuid,
          payccode: that.data.payccode,
          ttype: that.data.ttype,
          stype: that.data.stype,
          itemcode: that.data.itemlist[i].itemcode,
          price: that.data.itemlist[i].price,
          qty: that.data.itemlist[i].qty,
          secdisc: that.data.itemlist[i].secdisc,
          mondisc: that.data.itemlist[i].mondisc,
          amount: that.data.itemlist[i].amount,
          pmcode: that.data.pmcode,
          seccode: that.data.seccode,
          thrcode: that.data.thrcode,
          promotionsid: that.data.promotionsid
        }
        console.log(hungitem)
        // var url = app.globalData.host + 'adviser/serviecehung'
        var url = app.globalData.host + 'adviser/addshoppingcart/?param=' + JSON.stringify(hungitem)
        wx.request({
          method: 'POST',
          url: url,
          // data: this.servieceItem,
          header: {
            // 'content-type': 'application/json' // 默认值
            'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
          },
          success: function (res) {
            console.log(res.data)
            console.log('itemlist hung success!')
            if (res.error) {
              wx.showToast({
                title: res.data.msg,
                icon: 'none',
                duration: 2000
              })
            }
            else {
              wx.showToast({
                title: res.data.msg,
                icon: 'success',
                duration: 2000
              })
              setTimeout(function () {
                wx.navigateBack({
                  delta: 1
                })
              }, 2000)
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
    }
  },


  // 搜索入口  
  wxSearchTabGoods: function () {
    wx.redirectTo({
      url: '../goodssearch/goodssearch',
    })
    // wx.redirectTo({
    //   url: '../goodsquery/goodsquery'
    // })
  } 
})

