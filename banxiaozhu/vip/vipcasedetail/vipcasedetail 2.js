var app=getApp()
var appcode=app.globalData.appcode;
var host = app.globalData.host;
var company = app.globalData.company;
var util = require('../../utils/util.js');
var viputil = require('../viputils.js');

Page({
  data: {
    vip:{},
    vipcasedetal:[],
    vipuuid_s:''

  },


  onLoad: function (options) {
    var that =this;

    console.log('vipcasedetail onload',options)
    if (options.vipuuid){
      viputil.getVipBaseInfo(that,options)

    } else{
      var vip = app.globalData.currentvip;
      that.setData({
        vip:app.globalData.currentvip,
        vipuuid_s: app.globalData.currentvipuuid_s
      })
    }
    if (viputil.getVipBaseInfoCallback){
      console.log('callback ')
    }

    // viputil.get_vipcasedetail_byvipuuid(that,vip)
  },


  onReady: function () {
    console.log('onread')

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    console.log('onshow') 
    var that=this;
    var vip = that.data.vip;
    viputil.get_vipcasedetail_byvipuuid(that,vip)
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
  bindNewVipCaseDetail:function(){
    var that=this;
    var url="../vipcasedetail_edit/vipcasedetail_edit" 
    wx.navigateTo({
      url: url,
    })
  }
})