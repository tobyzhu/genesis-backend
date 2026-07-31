var app = getApp();
var host = app.globalData.host;
var company = app.globalData.company
var util = require('../utils/util.js')
var viputil = require('../vip/viputils.js');

Page({
  data: {
    grids:[
    {
      id: 1,
      text: "核心数据",
      url: "../query/vipcnt/vipcnt",
      image: "../images/todaybooking_black.png"
      // image:"../images/appointmentTimeIcon@2x.png"
    },
    {
      id: 2,
      text: "业绩查询",
      url: "../query/empl_archivement/empl_archivement",
      image: "../images/viplist.png"
    },
    {
      id: 3,
      text: "销售机会分析",
      url: "../query/empl_archivement/empl_archivement",
      image: "../images/viplist.png"
    }   
    ],
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    var param = {
      functionid: 'todolist',
      key: 'grids'
    }
    util.getWechatFunction(that, param)

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
    
  }
})
