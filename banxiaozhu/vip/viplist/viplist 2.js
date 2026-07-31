// vip/viplist/viplist.js
var sliderWidth = 96;
var app = getApp();
var host = app.globalData.host;
var company = app.globalData.company
var util = require('../../utils/util.js')
var viputil = require('../viputils.js');

Page({

  /**
   * 页面的初始数据
   */
  data: {

    vipTypeList: [
      {
        id:'10',
        name:'会员'
      },
      {
        id:'20',
        name:'散客'
      },
      {
        id:'30',
        name:'潜在客户'
      }
    ],
    activeIndex: 0,
    sliderOffset: 0,
    sliderLeft: 0,
    vip10list:[],
    vip20list:[],
    vip30list:[]

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function () {
    var app=getApp();
    var that = this;
    wx.getSystemInfo({
      success: function (res) {
        that.setData({
          sliderLeft: (res.windowWidth / that.data.vipTypeList.length - sliderWidth) / 2,
          sliderOffset: res.windowWidth / that.data.vipTypeList.length * that.data.activeIndex
        });
      }
    });
    that.setData({
      vip10list:app.globalData.vip10list,
      vip20list:app.globalData.vip20list,
      vip30list:app.globalData.vip30list
    })
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
    var that = this;
    var app = getApp();
    util.get_Vip10List();
    util.get_Vip20List();
    util.get_Vip30List();
    that.setData({
      vip10list: app.globalData.vip10list,
      vip20list: app.globalData.vip20list,
      vip30list: app.globalData.vip30list
    });
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
  // 下拉刷新
  onPullDownRefresh: function () {
    var that = this
    console.log('begin PullDown')
    wx.showNavigationBarLoading()
    util.get_Vip10List()
    util.get_Vip20List()
    util.get_Vip30List()
    // util.get_timescardtypelist()
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



  vipTypeClick: function (e) {
    console.log(e)
    this.setData({
      sliderOffset: e.currentTarget.offsetLeft,
      activeIndex: e.currentTarget.id
    });
  }
})