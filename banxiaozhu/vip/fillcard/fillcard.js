// vip/newcard/newcard.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({
  data: {
    showTopTips: false,
    errormsg: '非会员不允许售卡',
    searchValue: '',
    index: 0,
    vcode: '',
    vname: '',
    ttype: 'I',
    stype: 'N',
    stypename: '正常',
    stypeChecked:false,

    withcardflag: false,
    withcarddisc: '无卡开单',
    vip: {},
    vipuuid_s: '',
    vipuuid_u: '',
    viplist: [],
    vipindex: -1,
    newccode: '',

    payccode: '',
    paycarduuid:'',
    paycardsuptype: '00',
    paycardindex: -1,
    paycardlist: [],

    fillccode:'',
    oldcardtype:'',
    oldcardname:'',
    oldcardtypeindex:-1,
    fillcardindex:-1,
    fillcard:'',
    fillcarduuid:'',
    fillcardindex:-1,
    fillcardlist:[],

    filltype:['续卡','还欠','定金'],
    fillcardtype:'',
    fillcardtypeuuid:'',
    fillcardsuptype: '10',
    fillcardtypelist:[],
    fillcardtypeindex:-1,
    cardtype: '',
    qty: 1,
    price: 0,
    secdisc:1,
    mondisc:0,
    amount: 0,
    leftmoney: 0,
    owemoney: 0,


    cardtypeindex: -1,
    cardtype10index: -1,
    cardtype10list: [],
    cardtype20list: [],
    pmcodeindex: -1,
    pmcodelist: [],
    pmcode: '',
    pmname: '',
    seccodeindex: -1,
    seccodelist: [],
    seccode: '',
    secname: '',
    thrcodeindex: -1,
    thrcode: '',
    thrname: '',
    trhcodelist:[],

    promotionsid: '0',
    promotionsindex: -1,
    promotionslist: []

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp();
    var that = this;
    var vip = app.globalData.currentvip;

    that.setData({
      storecode: app.globalData.storecode,
      vip: app.globalData.currentvip,
      paycardlist: app.globalData.currentvip_amountcardlist,
      payccode: app.globalData.payccode,
      vipuuid: app.globalData.currentvipuuid_u,
      vipuuid_s: app.globalData.currentvipuuid_s,
      pmcodelist: app.globalData.empllist,
      seccodelist: app.globalData.empllist,
      thrcodelist: app.globalData.empllist,
      fillcardlist:app.globalData.currentvip_amountcardlist,
      fillcardtypelist: app.globalData.amountcardtypelist,
      stypelist: app.globalData.stypelist,
      stypeindex:0,
    })


    if (options && options.searchValue) {
      this.setData({
        searchValue: "搜索：" + options.searchValue
      });
    }

    if (that.data.payccode.length == 0) {
      var fillcardsuptype = '00'
    } else {
      var fillcardsuptype = options.suptype
    }
    // 获取可销售储值卡卡类
    that.get_cardtypelist(that.data.fillcardsuptype);

    that.setData({
      fillcardsuptype: fillcardsuptype
    });

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

  get_cardtypelist: function (options) {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_cardtypelist';
    var suptype = options;
    wx.request({
      url: url,
      data: {
        company: app.globalData.company,
        suptype: suptype
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

  bindPaycardChange: function (e) {
    var that = this;
    that.setData({
      paycardindex: e.detail.value,
      payccode: that.data.paycardlist[e.delta.value].ccode,
      paycarduuid: that.data.paycardlist[e.delta.value].uuid
    })

  },


  // bindPaycardChange: function (e) {
  //   console.log(e)
  //   var that = this;
  //   if (e.detail.value < 0) {
  //     that.setData({
  //       paycardindex: -1,
  //       payccode: '',
  //       paycardsuptype: '00'
  //     })
  //   } else {
  //     that.setData({
  //       paycardindex: e.detail.value,
  //       payccode: that.data.paycardlist[e.detail.value].ccode,
  //       paycardsuptype: that.data.paycardlist[e.detail.value].suptype
  //     })
  //   }
  // },


  bindFillcardChange: function (e) {
    var that = this;
    console.log('picker cardtype 发生选择改变，携带值为', e.detail.value);

    that.setData({
      fillcardindex: e.detail.value,
      fillcard: that.data.fillcardlist[e.detail.value].ccode,
      fillcarduuid: that.data.fillcardlist[e.detail.value].uuid,
      oldcardtype: that.data.fillcardlist[e.detail.value].cardtype,
      oldcardname: that.data.fillcardlist[e.detail.value].cardname,

      fillcardtype:that.data.fillcardlist[e.detail.value].cardtype,
      fillcardtypeuuid:that.data.fillcardlist[e.detail.value].cardtypeuuid,
    })

  },

  bindFillCardtypeChange: function (e) {
    var that = this;
    console.log('picker cardtype 发生选择改变，携带值为', e.detail.value);

    that.setData({
      fillcardtypeindex: e.detail.value,
      fillcardsuptype: that.data.fillcardtypelist[e.detail.value].suptype,
      fillcardtype: that.data.fillcardtypelist[e.detail.value].cardtype,
      fillcardtypeuuid: that.data.fillcardtypelist[e.detail.value].uuid,
      price:that.data.fillcardtypelist[e.detail.value].price,
      amount:that.data.fillcardtypelist[e.detail.value].price,
      leftmoney:that.data.fillcardtypelist[e.detail.value].price
      
    })

  },

  bindPriceChanged: function (e) {
    var that = this;
    console.log('picker pricechanged 发生选择改变，携带值为', e.details);
    var price = e.detail.value;
    console.log(e);
    that.setData({
      price:price,
      secdisc:1,
      mondisc:0,
      amount: price,
      leftmoney: price
    })
  },
  
  bindLeftmoneyChanged: function(e){
    var that = this;
    console.log('picker pricechanged 发生选择改变，携带值为', e.details);
    var leftmoney = e.detail.value;
    // if (price < that.data.cardtype10list[that.data.cardtypeindex].price) {
    //   var owemoney = price - that.data.cardtype10list[that.data.cardtypeindex].price
    // } else {
    //   var owemoney = 0
    // };
    console.log(e);
    that.setData({
      leftmoney: leftmoney
    })
  },

  bindStypeChange:function(e){
    viputils.bindStypeChanged(that, e)
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

  bindVipChange: function (e) {
    var that = this;
    console.log(e)
    that.setData({
      vipindex: e.detail.value,
      vcode: that.data.viplist[e.detail.value].vcode,
      vname: that.data.viplist[e.detail.value].vname
    })
  },
  
  bindFillCardHung: function(){
    var that = this;
    var app = getApp();

    if (that.data.payccode.length == 0) {
      that.setData({
        paycardsuptype: '00'
      })
    }

    var hungitem = {
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      ecode: app.globalData.ecode,
      vipuuid: that.data.vipuuid,
      payccode: that.data.payccode,
      paycarduuid:that.data.paycarduuid,
      ttype: that.data.ttype,
      stype: that.data.stype,
      itemcode: that.data.fillcard,
      newcardtype: that.data.fillcardtype,
      newcardtypeuuid: that.data.fillcardtypeuuid,
      price: that.data.price,
      qty: that.data.qty,
      secdisc: that.data.secdisc,
      mondisc: that.data.mondisc,
      amount: that.data.amount,
      leftmoney: that.data.leftmoney,
      pmcode: that.data.pmcode,
      seccode: that.data.seccode,
      thrcode: that.data.thrcode,
      promotionsid: that.data.promotionsid
    }
    console.log(hungitem)
    // var url = app.globalData.host + 'adviser/serviecehung'
    var url = app.globalData.host + 'adviser/fillcardhung/?param=' + JSON.stringify(hungitem)
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
            // title: res.data.msg,
            tite:'success',
            icon: 'none',
            duration: 2000
          })
          var options = {
            vipuuid: that.data.vip.uuid,
            comptype: 'amount'
          }
          viputils.getVipComptypeCardList(that, options)

        }
        else {
          wx.showToast({
            // title: res.data.msg,
            tite: 'success',
            icon: 'success',
            duration: 2000
          })
          setTimeout(function () {
            var options = {
              vipuuid: that.data.vip.uuid,
              comptype: 'amount'
            }
            viputils.getVipComptypeCardList(that, options)
            wx.navigateBack({
              delta: 1
            })
          }, 2000)
          // wx.navigateTo({
          //   url: '../kaidan/kaidan',
          // })
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
  // 搜索入口  
  wxSearchTab: function () {
    wx.redirectTo({
      url: '../queryvip/queryvip'
    })
  },

})