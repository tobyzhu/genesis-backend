// vip/shoppintcartitem/shoppingcartitem.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');
var log = require('../../utils/log.js');
var app = getApp();

Page({
  data: {
    vip: {},
    uuid: '',
    shoppingcartitem: {},
    ttype: '',
    ttypename: '',
    stypechecked: false,
    stype: 'N',
    stypename: '正常',
    stypelist:[],
    stypeindex:0,
    earnestflag:false,
    backflag:'N',
    backflagName:'正常',
    backflagChecked:false,
    depositeflag:'N',
    depositeflagname:'带走',
    depositeflagindex:0,
    depositeflaglist:[],
    cardbuttonflag:false,
    stockqty2:0,
    stockqty3:0,

    item:[],
    itemcode: '',
    itemname: '',
    qty: '',
    price: 0,
    secdisc: 1,
    secdiscdesc: '',
    mondisc: 0,
    amount: 0,
    pmcode: '',
    seccode: '',
    thrcode: '',
    payccode: '',
    paycardindex: -1,
    paycardlist: [],
    paycardsuptype:'00',
    itemlist:[],
    itemindex:-1,
    pmcodeindex: -1,
    pmcodelist: [],
    seccodeindex: -1,
    seccodelist: [],
    thrcodeindex: -1,
    thrcodelist: [],
    promotionsid: 0,
    promotionsindex: -1,
    promotionslist: [],
    planqty:0,
    playamount:0,
    payedamount:0,
    oweamount:0,
    remark:''

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    log.info('itemedit.onload options',options)
    var app = getApp();
    var that = this;
    var uuid = options.uuid;
    that.setData({
      vip: app.globalData.currentvip,
      paycardlist: app.globalData.currentvip_amountcardlist,
      pmcodelist: app.globalData.pmcodelist,
      seccodelist: app.globalData.seccodelist,
      thrcodelist: app.globalData.seccodelist,
      itemlist: app.globalData.current_itemlist,
      itemindex:  options.index,
      ttype: app.globalData.current_itemlist[options.index].ttype,
      itemcode: app.globalData.current_itemlist[options.index].itemcode,
      itemname: app.globalData.current_itemlist[options.index].itemname,
      qty: 1,
      price: app.globalData.current_itemlist[options.index].price,
      amount: app.globalData.current_itemlist[options.index].price,
      stypelist: app.globalData.stypelist,
      stypeindex:0,
      depositeflaglist:app.globalData.depositeflaglist
    })
    if (that.data.ttype =='G'){
      viputils.get_goodsstockqty(that,that.data.itemcode)
    }
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
    var that=this;
    var price = e.detail.value;
    viputils.bindPriceChange(that,price)
  },


  bindQtyChange: function (e) {
    var that=this;
    var qty = e.detail.value;
    viputils.bindQtyChange(that,qty)
  },

  bindSecdiscChange:function(e){
    var that=this;
    var secdisc = e.detail.value;
    viputils.bindSecdiscChange(that,secdisc)
  },
  bindMondiscChange:function(e){
    var that=this;
    var mondisc = e.detail.value;
    viputils.bindMondiscChange(that,mondisc)
  },

  bindPaycardChange: function (e) {
    var that = this;
    viputils.bindPaycardChange(that, e)
  },

  bindBackflagChange:function(e){
    var that=this;
    viputils.bindBackflagChange(that,e)
  },

  bindStypeChange: function (e) {
    var that = this;
    viputils.bindStypeChanged(that, e)
  },
  bindDepositeflagChange:function(e){
    var that=this;
    viputils.bindDepositeflagChange(that,e)   
  },


  bindPayedAmountChange: function(e){
    var that = this;
    var payedamount = e.detail.value
    var oweamount = that.data.amount - payedamount
    that.setData({
      payedamount:payedamount,
      oweamount:oweamount
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

  gotoShoppingCart: function () {
    var that = this;
    wx.navigateTo({
      url: '../shoppingcar/shoppingcar',
    })
  },

  addItemToCart: function () {
    var that = this;
    var app = getApp();
    var len = that.data.itemlist.length;
    console.log(len)

    
    if (that.data.paycardindex==-1){
      that.setData({
        payccode:'',
        cardbuttonflag:true
      })
    } else{
      that.setData({
        payccode: that.data.paycardlist[that.data.paycardindex].ccode,
        cardbuttonflag:true
      })
    }

    if (that.data.qty != 0) {
        if (that.data.backflag=='Y'){
          var qty = -that.data.qty
        } else {
          var qty = that.data.qty
        }
        var hungitem = {
          company: app.globalData.company,
          storecode: app.globalData.storecode,
          ecode: app.globalData.ecode,
          vipuuid: that.data.vip.uuid,
          payccode: that.data.payccode,
          ttype: that.data.ttype,
          stype: that.data.stype,
          itemcode: that.data.itemcode,
          price: that.data.price,
          qty: that.data.qty,
          // qty: qty,
          secdisc: that.data.secdisc,
          mondisc: that.data.mondisc,
          amount: that.data.amount ,
          pmcode: that.data.pmcode,
          seccode: that.data.seccode,
          thrcode: that.data.thrcode,
          promotionsid: that.data.promotionsid,
          payedamount:that.data.payedamount,
          oweamount: that.data.oweamount,
          remark: that.data.remark,
          depositeflag: that.data.depositeflag
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
            console.log(res)
            console.log('servieceitem hung success!')
            if (res.error) {
              wx.showToast({
                title: '加入购物车失败！' ,//res.data.msg,
                icon: 'none',
                duration: 2000
              })
              that.setData({
                cardbuttonflag:true
              })
            }
            else {
              wx.showToast({
                title: '已加入购物车!',//res.data.msg,
                icon: 'success',
                duration: 2000
              })
              setTimeout(function () {
                wx.navigateBack({
                  delta: 1
                })
                // that.setData({
                //   srvList: app.globalData.srvList
                // })
                // that.init_srvList()
                // viputils.init_itemlist(that)
              }, 2000)
            }
          },
          fail: function (res) {
            console.log("failed")
            that.setData({
              cardbuttonflag:false
            })
          },
          complete: function (res) {
            console.log("finished")
          }
        })
    }
  }

})