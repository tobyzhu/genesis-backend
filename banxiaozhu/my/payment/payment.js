// my/payment/payment.js
var app= getApp()
var util = require("../../utils/util.js")
var log = require("../../utils/log.js")
var wxutils = require("../../utils/wxutils.js")

Page({

  /**
   * 页面的初始数据
   */
  data: {
    userInfo:{},
    company:'',
    storecode:'',
    companyitem:'',
    companyitemlist:[
      {
        "id": 3,
        "company_item_code": "100",
        "company_item_name": "季付按月计费服务费",
        "company_item_desc": "",
        "company_item_qty": 1,
        "company_pay_period": "4",
        "company_item_price": "0.03"
        // "checked":true
      },
      {
        "id": 4,
        "company_item_code": "101",
        "company_item_name": "季付按月计费服务费",
        "company_item_desc": "",
        "company_item_qty": 1,
        "company_pay_period": "4",
        "company_item_price": "0.04"
      }
    ],
    companyitemindex:-1

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

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

  itemChange: function (e) {
    var that=this
    console.log('radio发生change事件，携带value值为：',e, e.detail.value);

    var radioItems = that.data.companyitemlist;
    for (var i = 0, len = radioItems.length; i < len; ++i) {
      // radioItems[i].checked = radioItems[i].id == e.detail.value;
      radioItems[i].checked = i == e.detail.value;     
    }

    that.setData({
      companyitemlist: radioItems,
      companyitemindex: e.detail.value
    });
  },

  // 支付按钮点击事件
  bindPayment: function(){
    var that = this;
    var openid = app.globalData.openid
    var appcode = app.globalData.appcode
    var company = app.globalData.company
    var storecode = app.globalData.storecode

    var host= app.globalData.host
    var url = host+'/wechat/payment/'
    wx.request({      
      url: url,
      data: {
        appcode:appcode,
        company:company,
        storecode:storecode,
        openid: openid,   // 这里正常项目不会只有openid一个参数
        companyitemid:that.data.companyitemlist[that.data.companyitemindex].id
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success: function(res){
        console.log('success res',res)
        if(res.statusCode == 200){
          var payModel = res.data;
          wx.requestPayment({
            'timeStamp': String(payModel.timeStamp),
            'nonceStr': payModel.nonceStr,
            'package': 'prepay_id='+payModel.prepay_id,
            'signType': 'MD5',
            'paySign': payModel.sign,
            'success': function (res) {
              console.log('wx.requestPayment success res',res)
              wx.showToast({
                title: '支付成功',
                icon: 'success',
                duration: 2000
              })
            },
            'fail': function (res) {
              console.log('wx.requestPayment fail res',res)
              wx.showToast({
                title: '提交失败，请检查网络或者稍后再试！',
                icon:'warn',
                duration:2000
              })
            }
          })
        }
      },
      fail: function(res){
        console.log('fail res',res)
        wx.showToast({
          title: '提交失败，请检查网络或者稍后再试！',
          icon:'fail',
          duration:2000
        })      
 
      }
    })
  },

  bindQueryPayedList: function(){
    var that=this;
    wx.navigateTo({
      url: './payment_detail/payment_detail',
    })
  }

})