
var util = require('../utils/util.js')

Page({

  /**
   * 页面的初始数据
   */
  data: {
    company:'',
    companyname:'',
    storecode:'',
    storename:'',
    ecode:'',
    ename:'',
    empllist:[],
    emplIndex:-1,
    isLogin:false,

    thismonth: '',
    thismonth_vipcnt: 0,
    thismonth_viptimes: 0,
    thismonth_yeji: 0,
    thismonth_shihao: 0,
    thismonth_emplarch: [],

    lastmonth: '',
    lastmonth_vipcnt: 0,
    lastmonth_viptimes: 0,
    lastmonth_yeji: 0,
    lastmonth_shihao: 0,
    lastmonth_emplarch: [],
    viplist:[]

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    var app=getApp();
    if (app.globalData.isLogin){
      console.log('app.globalData.isLogin True：',app.globalData.isLogin)
    } else {
      console.log('app.globalData.isLogin False：', app.globalData.isLogin)
      wx.navigateTo({
        url: '/my/authorize/authorize',
      })
    }

    that.setData({
      company:app.globalData.company,
      companyname:app.globalData.companyname,
      storecode:app.globalData.storecode,
      storename:app.globalData.storename,
      ecode:app.globalData.ecode,
      ename:app.globalData.ename

    })
    util.get_emplarch_bymonth(that)
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
  bindShareReferral: function () {
    var that = this;
    that.setData({ showShareDialog: true });
    wx.shareAppMessage({
      title: '帮小主 - 美业门店管理系统，员工手机就能用',
      path: '/my/login/login',
    })
  },

  onShareAppMessage: function () {
    return {
      title: '帮小主 - 美业门店管理系统，员工手机就能用',
      path: '/my/login/login',
      imageUrl: '/images/logo_share.png',
    }
  },
  bindLogout:function(){
    var app=getApp();
    var that=this;
    app.globalData.company=''
    app.globalData.storecode='',
    app.globalData.ecode='',
    app.globalData.usercode='',
    app.globalData.isLogin=false

    wx.reLaunch({
      url: './login/login',
    })
  }
})