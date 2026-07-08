var app=getApp()
var util = require('../../utils/util.js')
var wxCharts = require('./utils/wxcharts.js');
Page({

  /**
   * 页面的初始数据
   */
  data: {
    param:{},
    ecode:'',
    fromdate:'',
    todate:'',
    sum:{},
    detail:[],
    filtered_detail:[],
    stypelist:[],
    stypelistindex:-1,
    ttypelist:[
      {
        ttype:'S',
        ttypename:'服务'
      },
      {
        ttype:'G',
        ttypename:'商品'
      },
      {
        ttype:'C',
        ttypename:'售卡'
      },   
      {
        ttype:'I',
        ttypename:'充值'
      },    
    ],
    ttypelistindex:-1,
    cdatelist:[],
    cdatelistincex:-1


  },


  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this
    console.log('begin')
    that.setData({
      param: app.globalData.param,
      // ttypelist: app.globalData.ttypelist,
      stypelist: app.globalData.stypelist
    })
    console.log('1')
    that.getArchivementDetail()
    console.log('2')
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
  bindTtypeChange: function(e){
    var that=this;
    console.log(e);
    that.setData({
      ttypelistindex: e.detail.value
    })
    var ttypename = that.data.ttypelist[e.detail.value].ttypename;
    that.setData({
      filtered_detail: that.data.detail.filter(item => item.ttype = ttypename)
    })
  },

  getArchivementDetail: function(){
    var that=this;
    var host = app.globalData.host;
    var company = app.globalData.company;
    var url = host + "cashier/get_archivementdetail_byecode/"
    var storecode= app.globalData.storecode
    var ecode=that.data.ecode
    var fromdate=that.data.fromdate
    var todate = that.data.todate
    var openid = app.globalData.openid
    console.log('that.data',fromdate,todate)
    // util.get_ArchivementDetailbyEcode(that,ecode, fromdate,todate);

    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        ecode: that.data.param.ecode,
        fromdate: that.data.param.fromdate,
        todate: that.data.param.todate,
        openid: app.globalData.openid
      },
      // header: {
      //   'content-type': 'application/json' // 默认值
      // },
      success(res) {
        // console.log(fromdata, todata)
        console.log('get_ArchivementDetail res.data', res.data)
        app.globalData.detail= res.data
        that.setData({
          detail:res.data,
          filtered_detail: res.data
          // sum:res.data[1:8]
        })
        // var filtered_detail= that.data.detail.filter(item => item.cdate >= '20241204')
        // wx.setStorage({
        //   key: 'emplarchivedetail',
        //   data: res.data
        // })
      }
    });
  }

})