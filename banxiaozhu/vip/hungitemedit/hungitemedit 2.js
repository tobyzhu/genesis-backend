// vip/shoppintcartitem/shoppingcartitem.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({

  data: {
    vip: {},
    buttonClicked: false,
    uuid: '',
    hungitemuuid:'',
    hungitem:[],
    shoppingcartitem: {},
    psstatus:'',
    psstatuslist:[],
    psstatusindex:-1,
    modifiedflag:true,
    ttype: '',
    ttypename: '',

    stypechecked: false,
    stype: 'N',
    stypename: '正常',
    stypelist: [],
    stypeindex: -1,
    earnestflag: false,
    backflag: 'N',
    backflagName: '正常',
    backflagChecked: false,

    depositeflag:'N',
    depositeflagname:'带走',
    depositeflagindex:0,
    depositeflaglist:[],

    payccode: '',
    item: [],
    itemcode: '',
    itemname: '',
    qty: '',
    price: '',
    secdisc: 1,
    secdiscdesc: '',
    mondisc: 0,
    amount: 0,
    pmcode: '',
    pmname:'',
    seccode: '',
    secname:'',
    thrcode: '',
    thrname:'',
    paycardindex: -1,
    paycardlist: [],
    itemlist: [],
    itemindex: -1,
    pmcodeindex: -1,
    pmcodelist: [],
    seccodeindex: -1,
    seccodelist: [],
    thrcodeindex: -1,
    thrcodelist: [],
    promotionsid: 0,
    promotionsindex: -1,
    promotionslist: [],
    planqty: 0,
    playamount: 0,
    payedamount: 0,
    oweamount: 0,
    remark: ''

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    console.log(options)
    var app = getApp();
    var that = this;
    var uuid = options.uuid;
    that.setData({
      vip: app.globalData.currentvip,
      paycardlist: app.globalData.currentvip_amountcardlist,
      pmcodelist: app.globalData.pmcodelist,
      seccodelist: app.globalData.seccodelist,
      thrcodelist: app.globalData.seccodelist,
      psstatuslist: app.globalData.psstatuslist,
      stypelist: app.globalData.stypelist,
      depositeflaglist: app.globalData.depositeflaglist
    })
    viputils.getHungItem(that, uuid)
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {

  },

  /**
   * 生命周期函数--监听页面隐藏
   */
  onHide: function () {

  },

  /**
   * 生命周期函数--监听页面卸载
   */
  onUnload: function () {

  },

  /**
   * 页面相关事件处理函数--监听用户下拉动作
   */
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
    console.log('picker cardtype 发生选择改变，携带值为', e.detail.value);

    that.setData({
      paycardindex: e.detail.value,
      payccode: that.data.paycardlist[e.detail.value]
      // newcardsuptype: that.data.cardtype10list[e.detail.value].suptype
    })
    that.onShow()
  },

  bindBackflagChange: function (e) {
    var that = this;
    viputils.bindBackflagChange(that, e)

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

  bindDelHungItem:function(e){
    var that=this;
    var app=getApp();
    if (that.data.paycardindex<0){
      var payccode=''
    } else{
      var payccode = that.data.paycardlist[that.data.paycardindex].ccode
    }
    var param = {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      uuid: that.data.hungitemuuid,
      payccode: payccode,
      ttype:that.data.ttype,
      stype: that.data.stype,
      pmcode: that.data.pmcode,
      seccode: that.data.seccode,
      thrcode: that.data.thrcode,
      flag: 'N'
    };
    that.updateHungItem(param)
  },

  bindModifyHungItem:function(e){
    var that = this;
    var app = getApp();
    var qty = that.data.qty;
    var price = that.data.price;
    var secdisc = that.data.secdisc;
    var mondisc = that.data.mondisc;
    var amount = qty * price * secdisc - mondisc;

    if (that.data.paycardindex < 0) {
      var payccode = ''
    } else {
      var payccode = that.data.paycardlist[that.data.paycardindex].ccode
    }
    var param = {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      uuid: that.data.hungitemuuid,
      payccode: payccode,
      ttype:that.data.ttype,
      stype: that.data.stype,
      price: that.data.price,
      qty: that.data.qty,
      secdisc: that.data.secdisc,
      mondisc: that.data.mondisc,
      amount: that.data.amount,
      pmcode: that.data.pmcode,
      seccode: that.data.seccode,
      thrcode: that.data.thrcode,
      depositeflag: that.data.depositeflag,
      remark: that.data.remark
    };
    that.updateHungItem(param)
  },

  updateHungItem:function(option){
    var that=this;
    var app=getApp();
    var param=option
    console.log(param)

    var host = app.globalData.host
    var url = host + "adviser/update_hungitem/";
    console.log(url)
    util.showLoading('更新中')
    wx.request({
      method: 'GET',
      url: url,
      data: param,
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        wx.showToast({
          title: '更新完成！',
        })
        viputils.getVipPage(that,that.data.vip.uuid)
        wx.redirectTo({
          url: '../hungs/hungs',
        })
        // wx.navigateTo({
        //   url: '../hungs/hungs',
        // })
      },
      fail(res){
        util.hideLoading('更新失败！')
      },
      complete(res){
        console.log(res)
      }
    })

  },

  gotoShoppingCart: function () {
    var that = this;
    wx.navigateTo({
      url: '../shoppingcar/shoppingcar',
    })
  }

})