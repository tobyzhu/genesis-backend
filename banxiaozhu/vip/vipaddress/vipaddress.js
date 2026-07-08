// vip/vipaddress/vipaddress.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');
var log = require('../../utils/log.js');
var app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    vip:{},
    vipaddresslist:[
      {
        id:1,
        receiver:'demo1',
        mtcode:'13901999273',
        province:'北京市',
        city:'北京市',
        address:'sdafsda',
        defaultflag:'Y',
      },
      {
        id:2,
        receiver:'demo2',
        mtcode:'13901999274',
        province:'北京市',
        city:'北京市',
        address:'sdafsdasfasa',
        defaultflag:'N',
      },     
    ],
    newaddress:{}

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    that.setData({
      vip:app.globalData.currentvip
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
  bindNewAddress:function(){
    var that=this;
    wx.navigateTo({
      url: '../newvipaddress/newvipaddress',
    })
  }
})