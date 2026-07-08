// vip/newcard/newcard.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');
var log = require('../../utils/log.js');
var app = getApp();

Page({
  data: {
    showTopTips: false,
    errormsg: '非会员不允许售卡',
    searchValue: '',
    vipPage: '',
    index: 0,
    vcode: '',
    vname: '',
    ttype: 'C',
    ttypename:'售卡',
    // stype: 'N',
    // stypename: '正常',

    stypechecked: false,
    stype: 'N',
    stypename: '正常',
    stypelist: [],
    stypeindex: 0,
    earnestflag: false,
    backflag: 'N',
    backflagName: '正常',
    backflagChecked: false,



    withcardflag: false,
    withcarddisc: '无卡开单',
    vip: {},
    vipuuid_s: '',
    vipuuid_u: '',
    viplist: [],
    vipindex: -1,
    newccode: '',
    payccode: '',
    paycardsuptype: '00',
    paycardindex: -1,
    paycardlist: [],
    newcardsuptype: '20',
    newcardtype:'',
    newcardname:'',
    qty: 1,
    qtyindex:-1,
    qtylist:[1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,32,36,40,48,50],
    price: 0,
    secdisc: 1,
    mondisc: 0,
    amount: 0,
    leftmoney: 0,
    owemoney: 0,
    cardtype10index: -1,
    cardtype20index: -1,
    cardtype10list: [],
    cardtype20list: [],
    serviecePrice:[],
    serviecePriceIndex:[],
    pmcodelist: [],
    pmcode: '',
    pmname: '',
    pmcodeindex: -1,
    seccodelist: [],
    seccode: '',
    secname: '',
    seccodeindex: -1,
    thrcodelist:[],
    thrcode: '',
    thrname: '',
    thrcodeindex: -1,
    promotionsid: '0',
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
    console.log('options',options)
    var that = this;
    
    that.setData({
      vip:app.globalData.currentvip,
      paycardlist:app.globalData.currentvip_amountcardlist,
      payccode: app.globalData.payccode,
      vipuuid:app.globalData.currentvipuuid_u,
      vipuuid_s: app.globalData.currentvipuuid_s,
      pmcodelist: app.globalData.empllist,
      seccodelist: app.globalData.empllist,
      thrcodelist: app.globalData.empllist,
      stypelist: app.globalData.stypelist
    })

    viputils.getVipPage(that);
    // options: 分为从搜索卡类返回，还是从开单界面进入
    if (options)  {
      if (options.searchValue){
        that.setData({
          searchValue: options.searchValue
        });
      }
      if (options.cardtype) {
        console.log('options.cardtype',options.cardtype)
        that.setData({
          newcardtype: options.cardtype,
          newcardname: options.cardname
        });
        // 获得该卡类的价格及次数
        that.get_serviecePrice()
      }
    }
    if (that.data.vip.viptype == '10') {
      that.setData({
        showTopTips: false
      })
    } else {
      that.setData({
        showTopTips: true
      })
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

  bindBackflagChange: function (e) {
    var that = this;
    viputils.bindBackflagChange(that, e)
  },

  bindStypeChange: function (e) {
    var that = this;
    viputils.bindStypeChanged(that, e)
    // if (e.detail.value>=0){
    //   console.log(e, that.data.stypelist[e.detail.value].itemname)
    //   that.setData({
    //     stypeindex: e.detail.value,
    //     stype: that.data.stypelist[e.detail.value].itemname,
    //     stypename: that.data.stypelist[e.detail.value].itemvalues
    //   })
    // }
    // console.log('that.data.stype',that.data.stype)
  },

  bindPaycardChange: function (e) {
    var that = this;
    viputils.bindPaycardChange(that,e)
  },

  bindCardtypeChange: function (e) {
    var that = this;
    console.log('picker cardtype 发生选择改变，携带值为', e.detail.value);
    that.setData({
      cardtypeindex: e.detail.value,
      newcardsuptype: that.data.cardtype10list[e.detail.value].suptype
    })
    that.onShow()
  },


  bindQtyChanged:function(e){
    var that = this;
    console.log('picker QtyChanged 发生选择改变，携带值为', e);
    var qty = e.detail.value;
    // var qty = that.data.qtylist[qtyindex]
    var price = that.data.price
    var mondisc= that.data.mondisc
    var amount = qty * price - mondisc
    that.setData({
      // qtyindex:qtyindex,
      qty: qty,
      leftmoney:amount,
      amount: amount
    })
  },

  bindPriceChanged: function (e) {
    var that = this;
    console.log('picker pricechanged 发生选择改变，携带值为');
    var price = e.detail.value;
    var qty = that.data.qty
    var mondisc = that.data.mondisc
    var amount = qty * price - mondisc
    that.setData({
      price: price,
      leftmoney: amount,
      amount: amount
    })
  },

  bindMondiscChanged: function (e) {
    var that = this;
    console.log(e);
    var mondisc = e.detail.value;
    var qty = that.data.qty
    var price = that.data.price
    that.setData({
      mondisc: mondisc,
      leftmoney: qty*price,
      amount: qty*price - mondisc 
    })
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
  bindAmountChanged:function(e){
    var that = this;
    console.log('picker pricechanged 发生选择改变，携带值为', e.details);
    var amount = e.detail.value;
    var qty = that.data.qty
    var mondisc = that.data.mondisc
    var price = (amount / qty ).toFixed(4)
    that.setData({
      price: price ,
      leftmoney: amount,
      amount: amount
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

  bindPromotionsChange: function (e) {
    var that = this;
    var promotionsid = e.detail.value;
    that.setData({
      promotionsid: promotionsid
    })
  },
  bindRemarkChanged: function(e){
    var that=this;
    var remark = e.detail.value
    that.setData({
      remark:remark
    })

  },
  
  get_serviecePrice:function(){
    var app = getApp();
    var that = this;
    // const data = params
    var url = app.globalData.host + "baseinfo/get_srvprice"
    wx.showLoading()
    wx.request({
      url: url,
      data:{
        company:app.globalData.company,
        srvcode: that.data.newcardtype
        // qty: that.data.qtylist[that.data.qtyindex]
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: (res) => {
        console.log(res)
        if (res.data.length>0){
          that.setData({
            serviecePrice: res.data
          })
          for (var item in that.data.serviecePrice) {
            var key = 'serviecePrice[' + item + '].desc'
            var qty = that.data.serviecePrice[item].qty
            var price = that.data.serviecePrice[item].price
            var amount = that.data.serviecePrice[item].amount
            var desc = qty + '次*' + price + "元=" + amount + '元'
            that.setData({
              [key]: desc
            })
          };
          wx.hideLoading()
        }

      },
      fail: (res) => {
        console.log(res)
      },
      complete: (res) => {
        console.log(res)
      }
    })
  },

  newTimesCardHung: function () {
    var app = getApp();
    var that = this;
    var host = app.globalData.host;
    var company = app.globalData.company
    var storecode = app.globalData.storecode
    var ecode = app.globalData.ecode
    // var param = options

    if (that.data.payccode.length == 0) {
      that.setData({
        paycardsuptype: '00'
      })
    }
    if (that.data.newcardtype.length == 0) {
      wx.showToast({
        title: "没有选择新卡卡类",
        icon: 'failed',
        duration: 2000
      })
      return -1;
    }

    if (that.data.price != 0 || that.data.leftmoney != 0) {
      var options = {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        ecode: app.globalData.ecode,

        vcode: that.data.vcode,
        vipuuid: that.data.vipuuid,
        payccode: that.data.payccode,
        cardtype: '',
        cardtypeuuid: '',

        // index: that.data.index,
        suptype: that.data.paycardsuptype,
        ttype: that.data.ttype,
        ttypename: that.data.ttypename,
        stype: that.data.stype,
        stypename: that.data.stypename,
        newcardtype: that.data.newcardtype,
        // itemname: that.data.cardtype10list[that.data.newcardtypeindex].cardname,
        qty: that.data.qty,
        price: that.data.price,
        secdisc: 1,
        amount: that.data.amount,
        mondisc: that.data.mondisc,
        leftmoney: that.data.leftmoney,
        pmcode: that.data.pmcode,
        seccode: that.data.seccode,
        thrcode: that.data.thrcode,
        promotionsid: that.data.promotionsid,
        planqty:that.data.planqty,
        planamount:that.data.planamount,
        payedamount: that.data.payedamount,
        oweamount: that.data.oweamount,
        remark: that.data.remark
      }
      var url = host + 'adviser/newcardhung/?param=' + JSON.stringify(options)

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
          log.info(res)
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
            var timesoptions = {
              vipuuid: that.data.vip.uuid,
              comptype: 'times'
            }
            viputils.getVipComptypeCardList(that, timesoptions)
            that.onLoad()
            // wx.navigateTo({
            //   url: '../kaidan/kaidan',
            // })            
          }

          console.log(res.data)
        },
        fail: function (res) {
          title.title = '挂账时错误'
          title.icon = 'fail'
          openToast()
          console.log(res, "failed")
        },
        complete: function (res) {
          console.log(res, "finished")
        }
      })

      // wx.redirectTo({
      //   url: '/vip/vip?uuid=' + that.data.vipuuid_s
      // })
      wx.navigateBack({
        delta: 1
      })
    };

  },
  // 搜索入口  
  wxSearchTab: function () {
    wx.redirectTo({
      url: '../timescardsearch/timescardsearch'
    })
  },

})