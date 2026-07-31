// vip/advanceinfo/advanceinfo.js
var app = getApp()
var host = app.globalData.host;
var company = app.globalData.company
var util = require('../../utils/util.js')
var viputil = require('../viputils.js');

Page({

  /**
   * 页面的初始数据
   */
  data: {
    vip:{},
    subreports: [
      {
        id: 1,
        text: "肌骨管理管理",
        url: "./advanceinfoitem/advanceinfoitem",
        image: "../images/workTimeSchedule@2x.png"
      },
    ]

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp();
    var that = this;
    that.setData({
      vip: app.globalData.currentvip,
      // shoppingcartitems: app.globalData.currentvip_shoppingcartitems_s + app.globalData.currentvip_shoppingcartitems_g
    })

    var param = {
      functionid: 'advanceinfo',
      key: 'subreports'
    }
    // util.getWechatFunction(that, param)

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

  getCrmSubReport: function(){
    var that=this;
  }
})