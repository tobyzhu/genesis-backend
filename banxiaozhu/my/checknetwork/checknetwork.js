var now = new Date();
var util = require('../../utils/util.js');
var viputils = require('../../vip/viputils.js');
var app = getApp();

Page({
  data: {
    showTopTips: false,
    errormsg: '登陆时发生错误',
    storeList: [],
    company: '',
    companyname:'',
    storecode:'',
    storename:'',
    networkType: '',
    wifi_flag: false,
    bssid_flag: false,
    network_allow_flag: false,
    network_disallow_flag: true,
    local_SSID: '',
    local_BSSID: '',
    wifiitem: {},
    storecode: '',
    storeName: '',
    storeIndex: 0,
    usercode: '',
    username: '',
    password: '',
    last_login_time: '',
    isDev:false,
    isLogin: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    if (app.globalData.isDev){
      console.log('is dev')
      app.globalData.tempnetwork.networkenable = true
      app.globalData.tempnetwork.company = app.globalData.democompany
      app.globalData.tempnetwork.companyname=app.globalData.democompanyname
      app.globalData.tempnetwork.storecode = app.globalData.demostorecode
      app.globalData.tempnetwork.storename = app.globalData.demostorename
      app.globalData.tempnetwork.local_SSID = that.data.local_SSID
      app.globalData.tempnetwork.local_BSSID = that.data.local_BSSID
      app.globalData.tempnetwork.networkType = that.data.networkType
      app.globalData.tempnetwork.bssid_flag = that.data.bssid_flag
      wx.reLaunch({
        url: '/my/login/login',
      })     

    } else {
      util.checkNetwork(that)
      console.log('checknework onLoad ,app.globalData.tempnetwork:', app.globalData.tempnetwork)
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

  bindCompanyChange: function (e) {
    var that = this;
    var app = getApp();
    console.log(e)
    that.setData({
      company: e.detail.value
    })
  },

  bindStorecodeChange: function (e) {
    var that = this;
    var app = getApp();
    console.log(e)
    that.setData({
      storecode: e.detail.value
    })
  }, 

  bindApplyNetWork: function(){
    var that = this;
    var app = getApp();
    var ssid= util.get_ssid()
    var bssid = util.get_bssid()
    that.setData({
      local_SSID: ssid,
      local_BSSID:bssid
    })
  },

  bindCheckNetWork: function () {
    var that = this;
    var app = getApp();

    util.checkNetwork(that)
    console.log(that.data.isDev)
  }
})