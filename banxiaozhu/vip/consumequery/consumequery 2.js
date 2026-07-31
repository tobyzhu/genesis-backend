// vip/consumequery/consumequery.js
// vip/shoppintcartitem/shoppingcartitem.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');
Page({

  /**
   * 页面的初始数据
   */
  data: {
    vip:{},
    consumedetail:[],
    consumeGroups: [],
    // fromdate:'',
    // todate:'',
    searchValue:'',
    fromdate : util.datetostr(new Date()),
    todate : util.datetostr(new Date()),

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    console.log('consumequery onload options',options)
    var app = getApp();
    var that = this;
    var thatdate = new Date()
    var todate= new Date()
    var fromdate = new Date()
    var fromdate = fromdate.setMonth(fromdate.getMonth() - 600 )
    console.log('fromdate,todate',fromdate,todate)
    var param={
      company:app.globalData.company,
      fromdate:util.datetostr(fromdate),
      todate:util.datetostr(todate),
    }
    if (options && options.searchValue) {
      that.setData({
        vip: app.globalData.currentvip,
        searchValue: options.searchValue
      })
      var vipuuid = that.data.vip.uuid;
      param.vipuuid=vipuuid;
      param.keyword = options.searchValue;
    }
    else if (options && options.vipuuid) {
      var vipuuid = options.vipuuid
      param.vipuuid=vipuuid;
      param.keyword = '';
      console.log('vipuuid1',vipuuid)
    } 
    else {
      console.log('app.globalData.currentvip',app.globalData.currentvip)
      that.setData({
        vip: app.globalData.currentvip
      })
      var vipuuid = that.data.vip.uuid
      param.vipuuid=vipuuid;
      param.keyword = '';
    }
    console.log('consume param',param)
    // that.getVipConsume(vipuuid)
    viputils.getVipConsume(that,param)

  },

  formatGroupDate: function (vsdate) {
    var s = String(vsdate || '');
    if (s.length === 8) {
      return s.slice(0, 4) + '/' + s.slice(4, 6) + '/' + s.slice(6, 8);
    }
    return s;
  },

  buildConsumeGroups: function (rows) {
    var list = Array.isArray(rows) ? rows : [];
    var map = {};
    var groups = [];
    list.forEach(function (item) {
      var d = String(item.vsdate || '');
      if (!map[d]) {
        map[d] = {
          dateKey: d,
          dateLabel: d.length === 8 ? (d.slice(0, 4) + '/' + d.slice(4, 6) + '/' + d.slice(6, 8)) : d,
          items: []
        };
        groups.push(map[d]);
      }
      map[d].items.push(item);
    });
    this.setData({
      consumedetail: list,
      consumeGroups: groups
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
  getNowTime: function (option) {
    var now = new Date();
    conslon.log(now)
    var year = now.getFullYear();
    var month = now.getMonth() + 1;
    var day = now.getDate();
    if (month < 10) {
      month = '0' + month;
    };
    if (day < 10) {
      day = '0' + day;
    };
    //  如果需要时分秒，就放开
    // var h = now.getHours();
    // var m = now.getMinutes();
    // var s = now.getSeconds();
    var formatDate = year + '-' + month + '-' + day;
    console.log(formatDate)
    this.setData(
      {
        planbegindate: formatDate
      }
    )
    return formatDate;
  },
  getVipConsume: function (options) {
    var app = getApp();
    var company = app.globalData.company;
    var that = this;
    var vipuuid = options;
    var now = new Date();
    var fromdate = new Date();
    var todate = new Date();
    fromdate.setMonth(now.getMonth() - 3)

    var fromdatestring = that.setDateFormat('20190101')
    var todatestring = that.setDateFormat('20200120')
    console.log(fromdatestring, todatestring)

    var url = app.globalData.host + '/crm/get_vipconsumelist/';
    console.log(url)
    wx.request({
      method: 'GET',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        vipuuid: vipuuid,
        fromdate: fromdatestring,
        todate: todatestring
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success(res) {
        console.log(res.data)
        that.setData({
          consumedetail: res.data
        })
      }
    });

  },
  setDateFormat: function (option) {
    // var now = new Date;
    var day = option;
    var year = day.getFullYear();
    var month = day.getMonth() + 1;
    var day = day.getDate();
    if (month < 10) {
      month = '0' + month;
    };
    if (day < 10) {
      day = '0' + day;
    };
    //  如果需要时分秒，就放开
    // var h = now.getHours();
    // var m = now.getMinutes();
    // var s = now.getSeconds();
    var returndata = year + month + day;
    console.log('returndata:',returndata)
    return returndata;
  },  

  bindFromDateChange: function (e) {
    this.setData({
        fromdate: e.detail.value
    })
  },
  bindToDateChange: function (e) {
    this.setData({
        todate: e.detail.value
    })
  },

  // 搜索入口  
  wxSearchConsume: function () {
    wx.redirectTo({
      url: '../consumesearch/consumesearch',
    })
    // wx.redirectTo({
    //   url: '../goodsquery/goodsquery'
    // })
  } 

})