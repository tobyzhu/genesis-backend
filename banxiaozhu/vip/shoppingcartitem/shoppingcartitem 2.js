// vip/shoppintcartitem/shoppingcartitem.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({
  data: {
    vip:{},
    uuid:'',
    shoppingcartitem:{},
    ttype:'',
    ttypename:'',
    // stypechecked:false,
    // stype:'N',
    // stypename:'正常',

    stypechecked: false,
    stype: 'N',
    stypename: '正常',
    stypelist: [],
    stypeindex: 0,
    earnestflag: false,
    backflag: 'N',
    backflagName: '正常',
    backflagChecked: false,
    
    depositeflag:'N',
    depositeflagname:'带走',
    depositeflagindex:0,
    depositeflaglist:[],
    button_disable:false,

    payccode:'',
    itemcode:'',
    itemname:'',
    qty:1,
    price:0,
    secdisc:1,
    secdiscdesc:'',
    mondisc:0,
    amount:0,
    pmcode:'',
    seccode:'',
    thrcode:'',
    paycardindex:-1,
    paycardlist:[],
    pmcodeindex:-1,
    pmcodelist:[],
    seccodeindex:-1,
    seccodelist:[],
    thrcodeindex:-1,
    thrcodelist:[],
    promotionsid:0,
    promotionsindex:-1,
    promotionslist:[],
    remark:''

  },

  onLoad: function (options) {
    console.log(options)
    var app=getApp();
    var that=this;
    var uuid=options.uuid;
    that.setData({
      vip: app.globalData.currentvip,
      paycardlist:app.globalData.currentvip_amountcardlist,
      pmcodelist:app.globalData.pmcodelist,
      seccodelist:app.globalData.seccodelist,
      thrcodelist:app.globalData.seccodelist,
      stypelist: app.globalData.stypelist,
      depositeflaglist: app.globalData.depositeflaglist,
      uuid: uuid
    })
    // that.get_ShoppingCartItem(uuid)
    viputils.get_ShoppingCartItem(that,uuid)
  },

  onReady: function () {

  },

  onShow: function () {

  },

  onHide: function () {

  },

  onUnload: function () {

  },

  onPullDownRefresh: function () {

  },

  /**
   * 页面上拉触底事件的处理函数
   */
  onReachBottom: function () {

  },

  /**
   * 用户点击右上角分享
   */
  onShareAppMessage: function () {

  },

  bindBackflagChange: function (e) {
    var that = this;
    viputils.bindBackflagChange(that, e)
  },

  bindPriceChange: function (e) {
    var that = this;
    var price = e.detail.value;
    viputils.bindPriceChange(that, price)
  },

  bindQtyChange: function (e) {
    var that = this;
    var qty = e.detail.value;
    viputils.bindQtyChange(that, qty)
  },

  bindPaycardChange: function (e) {
    var that = this;
    viputils.bindPaycardChange(that, e)
  },



  bindStypeChange: function (e) {
    var that = this;
    viputils.bindStypeChanged(that, e)
  },

  bindDepositeflagChange:function(e){
    var that=this;
    viputils.bindDepositeflagChange(that,e)   
  },

  bindPayedAmountChange: function (e) {
    var that = this;
    var payedamount = e.detail.value
    var oweamount = that.data.amount - payedamount
    that.setData({
      payedamount: payedamount,
      oweamount: oweamount
    })
  },


  bindPaycardChange: function (e) {
    var that = this;
    viputils.bindPaycardChange(that,e)
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

  bindRemarkChanged: function(e){
    var that=this;
    var remark = e.detail.value
    that.setData({
      remark:remark
    })
  },    

  modifyClick:function(){
    var app=getApp();
    var that=this;
    var host=app.globalData.host
    var url= host+'adviser/'
    that.setData({
      button_disable:true
    })
    var param={
      oper: 'modify',
      company:app.globalData.company,
      storecode:app.globalData.storecode,
      ecode:app.globalData.ecode,
      uuid:that.data.uuid,
      vipuuid:that.data.vip.uuid,
      payccode:that.data.payccode,
      price: that.data.price,
      qty: that.data.qty,
      secdisc: that.data.secdisc,
      mondisc: that.data.mondisc,
      amount: that.data.amount,
      stype:  that.data.stype,
      pmcode: that.data.pmcode,
      seccode:that.data.seccode,
      thrcode:that.data.thrcode,
      promotionsid:that.data.promotionsid,
      depositeflag:that.data.depositeflag,
      remark:that.data.remark
    }
    console.log('param remark',param)
    var url = app.globalData.host + 'adviser/modify_shoppingcartitem/?param=' + JSON.stringify(param)

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
        // console.log(res.data)
        wx.showToast({
          title: '修改完成',
          icon: 'success',
          duration: 5000
        });
        wx.navigateBack({
          detal:1
        })
      },
      fail: function (res) {
        console.log(res)
        that.setData({
          button_disable:false
        })
      },
      complete: function (res) {
        console.log(res)
      }

    })

  }
})