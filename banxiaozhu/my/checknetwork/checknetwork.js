var util = require('../../utils/util.js');
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
    showDevLogin: false,
    isLogin: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this;
    var app = getApp();
    var devMode = util.isDevEnvironment();

    that.setData({ showDevLogin: devMode });

    // 开发环境：跳过 WiFi 校验，直达登录
    if (devMode) {
      app.globalData.company = app.globalData.democompany || 'demo';
      app.globalData.storecode = app.globalData.demostorecode || '88';
      app.globalData.companyname = app.globalData.democompanyname || '';
      app.globalData.storename = app.globalData.demostorename || '';
      app.globalData.networkenable = true;
      wx.reLaunch({
        url: '/my/login/login'
      });
      return;
    }

    util.checkNetwork(that);
    console.log('checknework onLoad ,app.globalData.tempnetwork:', app.globalData.tempnetwork);
  },

  /** 仅开发环境：手动进入演示登录 */
  goLogin: function () {
    if (!util.isDevEnvironment()) {
      wx.showToast({ title: '请先连接门店 WiFi', icon: 'none' });
      return;
    }
    var app = getApp();
    app.globalData.company = app.globalData.democompany || 'demo';
    app.globalData.storecode = app.globalData.demostorecode || '88';
    app.globalData.companyname = app.globalData.democompanyname || '';
    app.globalData.storename = app.globalData.demostorename || '';
    app.globalData.networkenable = true;
    wx.reLaunch({
      url: '/my/login/login'
    });
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
    console.log(e)
    that.setData({
      company: e.detail.value
    })
  },

  bindStorecodeChange: function (e) {
    var that = this;
    console.log(e)
    that.setData({
      storecode: e.detail.value
    })
  }, 

  bindApplyNetWork: function(){
    var that = this;
    var ssid= util.get_ssid()
    var bssid = util.get_bssid()
    that.setData({
      local_SSID: ssid,
      local_BSSID:bssid
    })
  },

  bindCheckNetWork: function () {
    var that = this;
    util.checkNetwork(that)
  }
})
