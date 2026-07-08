var now = new Date();
var util = require('../../utils/util.js');
var viputils = require('../../vip/viputils.js');
var app = getApp();

// pages/teacher/interview/index.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    crmrptid:1,
    fromdate:'',
    todate:'',
    minileftmoney:0,
    maxleftmoney:0,
    orderflag:'vsdate',
    paramnamelist:['到店客人','未到店客人','预警客人','应补货客人','卡余额不足客人','项目覆盖客人','本月生日客人','新客','本月入会客人']
  },


  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function(options) {
    var that=this;
    var today = util.getToday();
    if (options && options.crmrptid) {
      that.setData({
        crmrptid: options.crmrptid,
        fromdate: today,
        todate: today
      })
    } else {
      that.setData({
        crmrptid: 1,
        fromdate: today,
        todate: today        
      })
    }
  },
  bindFromDateChange: function (e) {
    var that=this;
    that.setData({
        fromdate: e.detail.value
    })
  },
  bindToDateChange: function (e) {
    var that=this;
    that.setData({
        todate: e.detail.value
    })
  }, 
  bindMiniLeftmoneyChange: function (e) {
    var that=this;
    that.setData({
        minileftmoney: e.detail.value
    })
  },  
  bindMaxLeftmoneyChange: function (e) {
    var that=this;
    that.setData({
        maxleftmoney: e.detail.value
    })
  },   
  bindQuery: function(e){
    var that=this;
    var params={
      crmrptid: that.data.crmrptid,
      fromdate: that.data.fromdate,
      todate:that.data.todata,
      orderby:that.data.orderflag
    }
    console.log('that.data.crmrptid',that.data.crmrptid,that.data.fromdate,that.data.todate)
    if (that.data.crmrptid ==1 || that.data.crmrptid== 2 || that.data.crmrptid== 3 || that.data.crmrptid== 4 || that.data.crmrptid== 8 || that.data.crmrptid== 9  || that.data.crmrptid== 10 ) {
      var url='../queryvip/queryvip?crmrptid='+that.data.crmrptid+'&fromdate='+that.data.fromdate+'&todate='+that.data.todate
    }
    if (that.data.crmrptid ==5 || that.data.crmrptid== 6) {
      var url='../queryvip/queryvip?crmrptid='+that.data.crmrptid+'&minileftmoney='+that.data.minileftmoney +'&maxleftmoney='+that.data.maxleftmoney
    }
    wx.navigateTo({
      url: url,
    })
  } 
})