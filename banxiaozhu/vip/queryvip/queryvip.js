var now = new Date();
var util = require('../../utils/util.js');
var viputils = require('../../vip/viputils.js');
var app = getApp();

Page({

  /**
   * 页面的初始数据
   */
  data: {
    searchValue: '',
    crmrptid:0,
    vipList:[],
    fail:false,
    fromdate:'',
    todate:'',
    minileftmoney:0,
    maxleftmoney:5000
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this;
    var app = getApp();
    console.log(options)
    if (options && options.searchValue){
      that.setData({
        searchValue: options.searchValue
      })
      that.get_viplist_bykeyword()
    }
    if(options.fromdate){
      that.setData({
        fromdate:options.fromdate
      })
    }
    if(options.todate){
      that.setData({
        todate:options.todate
      })
    }

    if(options.minileftmoney){
      that.setData({
        minileftmoney:options.minileftmoney
      })
    }    

    if(options.maxleftmoney){
      that.setData({
        maxleftmoney:options.maxleftmoney
      })
    }    

    if (options && options.crmrptid) {
      that.setData({
        crmrptid: options.crmrptid
      })
      var fromdate=that.data.fromdate
      var todate=that.data.todate
      var param={
        crmrptid:options.crmrptid,
        company:app.globalData.company,
        storecode:app.globalData.storecode,
        fromdate:that.data.fromdate,
        todate:that.data.todate,
        minileftmoney:that.data.minileftmoney,
        maxleftmoney:that.data.maxleftmoney,
        ecode:app.globalData.ecode
      }
      viputils.get_viplist_bycrmrptid(that,param)
    }

    
  },

  onReady: function () {
    
  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    
  },


  onHide: function () {
    
  },


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

  onShareAppMessage: function () {
    
  },
  bindFromDateChange: function(e) {
    var that=this;
    that.setData({
        fromdate: e.detail.value
    })
  },
  bindToDateChange: function(e) {
    var that=this;
    that.setData({
        todate: e.detail.value
    })
  },
  get_viplist_bykeyword: function(){
    var that=this;
    var app = getApp();
    var url = app.globalData.host +'baseinfo/get_viplist_byecode';

    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        ecode: app.globalData.ecode,
        searchvalue: that.data.searchValue
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        that.setData({
          fail:false,
          vipList: res.data
        })
      },
      fail: function (res) {
        console.log("failed")
        that.setData({
          fail:true
        })
      },
      complete: function (res) {
        console.log("finished")
      }
    })
  },
  // 搜索入口  
  wxSearchTabVip: function () {
    wx.redirectTo({
      url: '../search/search'
    })
  }  
})