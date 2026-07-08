
// import { $wuxSelect } from '../../wux/packages/lib/index'
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({
  data: {
    index:0,
    suptype:'20',
    vip: {},
    cardtuuid:'',
    ccode: '',
    cardtypeuuid:'',
    cardtype: '',
    cardname: '',
    srvcode: '',
    srvname: '',
    leftmoney: 0,
    qty: 1,
    qtyindex: 1,
    qtylist: [0,1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 32, 36, 40, 48, 50],

    price: 0,
    lastqty: 0,
    fillqty: 0,
    fillprice:0,
    fillamount: 0,
    consumeqty: 1,
    consumeprice:0,
    leftqty: 0,
    amount:0,
    payccodestatus:'',
    ttype:'S',
    stype: 'N',
    stypename: '正常',
    stypeChecked: false,
    stypelist:[],
    stypeindex:0,

    pmcode:'',
    pmcodelist:[],
    pmcodeindex: -1,
    seccode:'',
    seccodelist:[],
    seccodeindex: -1,
    thrcode:'',
    thrcodelist:[],
    thrcodeindex:-1,
    priceList: [],
    priceListIndex:-1,
    timescardlist:[],
    promotionsid:''
  },


  onLoad: function (options) {
    var app = getApp();
    var that = this;
    console.log(options)
    var index= options.index
    var ccode = options.ccode; 
    // var vip= app.globalData.currentvip;
    that.setData({
      storecode: app.globalData.storecode,
      vip: app.globalData.currentvip,
      // paycardlist: app.globalData.currentvip_amountcardlist,
      // payccode: app.globalData.payccode,
      timescardlist: app.globalData.currentvip_timescardlist,
      vipuuid: app.globalData.currentvipuuid_u,
      vipuuid_s: app.globalData.currentvipuuid_s,
      pmcodelist: app.globalData.pmcodelist,
      seccodelist: app.globalData.seccodelist,
      thrcodelist: app.globalData.seccodelist,
      stypelist: app.globalData.stypelist,
      stypeindex:0,
    })


    var that = this;
    console.log('20card onLoad!',options)

    var cardtype = that.data.timescardlist[index].cardtype
    var cardname = that.data.timescardlist[index].cardname
    var leftqty = that.data.timescardlist[index].leftqty
    var status = that.data.timescardlist[index].status
    var comsumeprice = that.data.timescardlist[index].price
    var stype = that.data.timescardlist[index].stype

    // console.log(cardtype)
    // that.getPriceList(cardtype)
    that.setData({
      ccode: ccode,
      cardtype: cardtype,
      cardname: cardname,
      leftqty: leftqty,
      payccodestatus: status,
      srvcode: cardtype,
      consumeprice: comsumeprice,
      index: options.index,
      stype: stype
    })    
    var param={
      type:'stype',
      code: stype
    }
    viputils.getIndexByCode(that,param)
    if (that.data.stype=='P'){
      that.setData({
        stypename:'赠送'
      })
    } else{
      that.setData({
        stypename:'正常'
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
  onShow: function (options) {

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
  radioChange: function (e) {
    console.log('radio发生change事件，携带value值为：', e.detail.value, e);
    var priceList = this.data.priceList;
    for (var i = 0, len = priceList.length; i < len; ++i) {
      priceList[i].checked = priceList[i].value == e.detail.value;
    };
    console.log(priceList);
    this.setData({
      priceList: priceList
    });
  },

  getPriceList: function (options) {
    var app = getApp();
    var that = this;
    var host = app.globalData.host;
    var company = app.globalData.company;
    var storeCode = app.globalData.storeCode;
    // var ecode = app.globalData.ecode;
    var mythis = this;
    var url = host + 'baseinfo/get_servieceprice/';
    var srvcode=that.data.srvcode;
    var priceList=[];
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company:company,
        srvcode:srvcode
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success: function (res) {
        console.log(res.data);
        priceList:res.data;
        that.setData({
          priceList:res.data
        })
      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("completed", res)
      }
    })
  },

  bindPriceListChange(e){
    var that=this;
    var priceListIndex = e.detail.value;
    console.log('picker price 发生选择改变，携带值为', e.detail.value);
    // priceList
    that.setData({
      priceListIndex: e.detail.value,
      fillqty: that.data.priceList[priceListIndex].qty,
      fillprice:that.data.priceList[priceListIndex].price,
      fillamount:that.data.priceList[priceListIndex].amount,
      leftqty: that.data.lastqty + that.data.fillqty - that.data.consumeqty
    })    
  },  
  bindConsumeqtyChange(e){
    console.log(e)
    var that=this;
    that.setData({
      consumeqty:that.data.qtylist[e.detail.value],
      qtyindex: e.detail.value
      // lastqty: that.data.leftqty + that.data.fillqty - that.data.consumeqty
    })
  },
  bindStypeChange: function (e) {
    var that = this;
    viputils.bindStypeChanged(that, e)
  },
  //
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
  
  gotoShoppingCart: function () {
    var that = this;
    wx.navigateTo({
      url: '../shoppingcar/shoppingcar',
    })
  },


  timescardHung: function () {
    var that = this;
    var app = getApp();
    // var len = that.data.srvList.length;
    // console.log(len)
    
    var param={
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      ecode: app.globalData.ecode,
      vipuuid: that.data.vipuuid,
      payccode: that.data.ccode,
      cardtype:that.data.cardtype,
      ttype: that.data.ttype,
      stype: that.data.stype,
      itemcode: that.data.srvcode,
      price: that.data.consumeprice,
      qty: that.data.consumeqty,
      secdisc: 1,
      mondisc: 0,
      amount: that.data.consumeqty * that.data.consumeprice,
      pmcode: that.data.pmcode,
      seccode: that.data.seccode,
      thrcode: that.data.thrcode,
      promotionsid: that.data.promotionsid
    }
    console.log(param)
    // var url = app.globalData.host + 'adviser/serviecehung'
    var url = app.globalData.host + 'adviser/addshoppingcart/?param=' + JSON.stringify(param)
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
        console.log('servieceitem hung success!')
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
})