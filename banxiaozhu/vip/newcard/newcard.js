// vip/newcard/newcard.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');
var log = require('../../utils/log.js');
var app = getApp();
Page({

  /**
   * 页面的初始数据
   */
  data: {
    showTopTips: false,
    errormsg: '非会员不允许售卡',
    searchValue: '',
    index: 0,
    vcode: '',
    vname: '',
    ttype:'C',
    ttypename:'售卡',
    // stype:'N',
    // stypename:'正常',
    // stypeChecked:false,

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
    withcarddisc:'无卡开单',
    vip: {},
    vipuuid:'',
    vipuuid_s: '',
    vipuuid_u: '',
    viplist: [],
    vipindex: -1,
    newccode: '',
    payccode: '',
    paycardsuptype:'00',
    paycardindex:-1,
    paycardlist:[],
    newcardsuptype:'10',
    cardtype:'',
    newcardtype:'',
    qty:1,
    price:0,
    secdisc:1,
    mondisc:0,
    s_mount:0,
    leftmoney:0,
    owemoney:0,
    pmcode:'',
    seccode:'',
    thrcode:'',
    newcardtypeindex:-1,
    cardtype10index:-1,
    cardtype10list:[],
    cardtype20list:[],
    amountcardtypeindex:-1,
    amountcardtypelist:[],
    pmcodelist:[],
    pmcode:'',
    pmname:'',
    pmcodeindex:-1,
    seccodelist:[],
    seccode:'',
    secname:'',
    seccodeindex:-1,
    thrcodelist:[],
    thrcode:'',
    thrname:'',
    thrcodeindex:-1,
    promotionsid:'0',
    promotionsindex:0,
    promotionslist:[],
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
    var that = this;
    var app = getApp();
    var vcode='';
    var newccode = '';

    that.setData({
      storecode: app.globalData.storecode,
      vip: app.globalData.currentvip,
      vcode: app.globalData.currentvip.vcode,
      vname: app.globalData.currentvip.vname,
      paycardlist: app.globalData.currentvip_amountcardlist,
      payccode: app.globalData.payccode,
      vipuuid: app.globalData.currentvipuuid_u,
      vipuuid_s: app.globalData.currentvipuuid_s,
      pmcodelist: app.globalData.empllist,
      seccodelist: app.globalData.empllist,
      thrcodelist: app.globalData.empllist,
      amountcardtypelist: app.globalData.amountcardtypelist,
      cardtype10list: app.globalData.amountcardtypelist,
      stypelist:app.globalData.stypelist
    })
    if (that.data.vip.viptype=='10'){
      that.setData({
        showTopTips: false
      })
    } else {
      that.setData({
        showTopTips: true
      })
    }
    console.log('options', options)
    console.log('app.globalData.stypelist',app.globalData.stypelist)

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
  // onPullDownRefresh: function () {

  // },

  // 下拉刷新
  onPullDownRefresh: function () {
    console.log('begin PullDown')
    wx.showNavigationBarLoading()
    util.get_amountcardtypelist()
    util.get_timescardtypelist()
    this.onLoad()
    setTimeout(() => {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    }, 2000);
    console.log('end PullDown')
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
  get_cardtypelist: function(options){
    var that = this;
    var app = getApp();

    var url = app.globalData.host + 'baseinfo/get_cardtypelist';
    var suptype = options;
    wx.request({
      url: url,
      data:{
        company:app.globalData.company,
        suptype:suptype
      },
      method: 'GET',
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        that.setData({
          cardtype10list: res.data
        })

      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }     
    })
  },
    
  bindCardtypeChange: function (e) {
    var that=this;
    console.log('picker cardtype 发生选择改变，携带值为', e.detail.value);

    that.setData({
      newcardtypeindex: e.detail.value,
      // amountcardtypeindex: e.detail.vaue,
      newcardsuptype: that.data.amountcardtypelist[e.detail.value].suptype,
      newcardtype: that.data.amountcardtypelist[e.detail.value].cardtype
    })
    that.onShow()
  },


  withcardChanged:function(e){
    var that = this;
    var app = getApp();
    console.log(e);
    if (e.detail.value) {
      var withcardflag = true
      var withcarddesc = '储值卡付'
    } else {
      var withcardflag = false
      var withcarddesc = '无卡开单'
    };
    console.log('withcardflag',withcardflag,'withcarddesc',withcarddesc)
    that.setData({
      withcardflag: withcardflag,
      withcarddesc: withcarddesc
    });
    // var options={
    //   payccode:that.data.payccode,
    //   vipuuid:that.data.vipuuid,
    //   index: that.data.index
    // };
    that.onShow();
  },
  // bindPaycardChange: function(e){
  //   console.log(e)
  //   var that=this;
  //   if (e.detail.value<0){
  //     that.setData({
  //       paycardindex:-1,
  //       payccode:'',
  //       paycardsuptype:'00'
  //     })
  //   } else {
  //     that.setData({
  //       paycardindex:e.detail.value,
  //       payccode:that.data.paycardlist[e.detail.value].ccode,
  //       paycardsuptype: that.data.paycardlist[e.detail.value].suptype
  //     })
  //   }
  // },
  bindMondiscChanged: function (e) {
    var that = this;
    console.log(e);
    var mondisc = e.detail.value;

    that.setData({
      mondisc: mondisc
    })
  },
  bindPriceChanged:function(e){
    var that=this;
    console.log('picker pricechanged 发生选择改变，携带值为', e.details);
    var price = e.detail.value;
    if (price < that.data.cardtype10list[that.data.newcardtypeindex].price){
      var owemoney = price - that.data.cardtype10list[that.data.newcardtypeindex].price - that.data.mondisc
    } else {
      var owemoney = 0
    };
    console.log(e);
    that.setData({
      price: price,
      leftmoney: price,
      owemoney: owemoney
    })
  },


  bindBackflagChange: function (e) {
    var that = this;
    viputils.bindBackflagChange(that, e)
  },

  bindStypeChange: function (e) {
    var that = this;
    viputils.bindStypeChanged(that, e)
  },

  bindPaycardChange: function (e) {
    var that = this;
    viputils.bindPaycardChange(that, e)
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
  bindPromotionsChange: function(e){
    var that = this;
    var promotionsid = e.detail.value;
    that.setData({
      promotionsid : promotionsid
    })
  },
  bindVipChange: function (e) {
    var that = this;
    console.log(e)
    that.setData({
      vipindex: e.detail.value,
      vcode: that.data.viplist[e.detail.value].vcode,
      vname: that.data.viplist[e.detail.value].vname
    })
  },
  newCardHung:function(e){
    var app= getApp();
    var that = this;
    var host = app.globalData.host;
    var company = app.globalData.company
    var storecode = app.globalData.storecode
    var ecode = app.globalData.ecode
    // var param = options
    console.log('begin',e)
    if (that.data.payccode.length==0) {
      that.setData({
        paycardsuptype: '00'
      })
    }
    if (that.data.vcode.length == 0) {
      wx.showToast({
        title: "非会员不能开卡，请先设置为会员，获得会员号",
        icon: 'failed',
        duration: 2000
      })
      console.log('no vcode')
      return -1;
    }   
    if (that.data.newcardtype.length==0){
      wx.showToast({
        title: "没有选择新卡卡类",
        icon: 'failed',
        duration: 2000
      }) 
      console.log('no newcardtype')
      return -1; 
    }
    if (that.data.leftmoney == 0 && that.data.price == 0){
      wx.showToast({
        title: "没有输入正确金额",
        icon: 'failed',
        duration: 3000
      })
      console.log('no money')
      return -1; 
    }

    if (that.data.leftmoney != 0 || that.data.price != 0) {
      var options = {
        company:app.globalData.company,
        storecode:app.globalData.storecode,
        ecode:app.globalData.ecode,

        vcode: that.data.vcode,
        vipuuid: that.data.vipuuid,
        payccode: that.data.payccode,
        cardtype:'',
        cardtypeuuid:'',

        index: that.data.index,
        suptype: that.data.paycardsuptype,
        ttype: that.data.ttype,
        ttypename: that.data.ttypename,
        stype: that.data.stype,
        stypename: that.data.stypename,

        // itemcode: that.data.newccode,
        // newcardtype: that.data.cardtype10list[that.data.newcardtypeindex].cardtype,
        newcardtype: that.data.newcardtype,
        // itemname: that.data.cardtype10list[that.data.newcardtypeindex].cardname,
        qty: 1,
        price: that.data.price,
        secdisc: 1,
        amount: that.data.price ,
        mondisc: 0,
        leftmoney:that.data.leftmoney,
        pmcode: that.data.pmcode,
        seccode: that.data.seccode,
        thrcode: that.data.thrcode,
        promotionsid: that.data.promotionsid,
        planqty:that.data.planqty,
        planamount: that.data.planamount,
        payedamount: that.data.payedamount,
        oweamount: that.data.oweamount,
        remark: that.data.remark
      }
      console.log('options:', options)

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
          console.log(res)
          console.log(res.data)
          if (res.error){
            wx.showToast({
              title: res.data.msg,
              icon: 'fail',
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

            var amountoptions = {
              vipuuid: that.data.vip.uuid,
              comptype: 'amount'
            }
            viputils.getVipComptypeCardList(that, amountoptions)
            that.onLoad()
          }

        },
        fail: function (res) {
          title.title = '挂账时错误'
          title.icon = 'fail'
          openToast()                    
          console.log(res,"failed")
        },
        complete: function (res) {
          console.log(res,"finished")
        }
      })
    };

  },


  // 搜索入口  
  wxSearchTab: function () {
    wx.redirectTo({
      url: '../queryvip/queryvip'
    })
  },

})