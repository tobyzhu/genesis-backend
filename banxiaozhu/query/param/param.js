
var app=getApp()
var util = require('../../utils/util.js')
var wxCharts = require('../../utils/wxcharts.js');
// const regeneratorRuntime = require('../../lib/regenerator-runtime/runtime')
// import ad from '../index/ad'
// ad({})

Page({

  /**
   * 页面的初始数据
   */
  data: {
    openid:'',
    storelist: [],
    vipcntlist:[],
    storcode:[],
    vsdate:[],
    fromdate:'',
    todate:'',
    prevdate:'',
    reportdate:'',
    nextdate:'',
    reportdate_data:[],
    thismonthdata:[],
    premonthdata:[],
    storedata:[],
    imagearray:[],
    reporttype:'',
    reportdata:[]
  },

  /**
   * 生命周期函数--监听页面加载at
   */
  onLoad: function (options) {
    var that=this;
    console.log('options',options)
    var openid = app.globalData.openid
    var thismonth= util.getMonth(  new Date())+1;
    var premonth = util.getPreMonth(  new Date());
    console.log(thismonth,premonth)
    var key1 ='thismonthdata'
    var key2 ='premonthdata'
    var reporttype = options.reporttype
    console.log('reporttype=',reporttype)
    
    that.setData({
      reporttype:reporttype,
      reportdate:util.getToday(),
      fromdate:util.getToday(),
      todate:util.getToday()
    })
    // util.get_VipcntList(that,thismonth,key1);
    // util.get_VipcntList(that,premonth,key2);  
    // util.get_DailyStoreData(that,thismonth,key1);
    // util.get_DailyStoreData(that,premonth,key2);     
    
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

  imageError: function(e) {
    console.log('image3发生error事件，携带值为', e.detail.errMsg)
  },

  bindFromDateChange: function(e){
    var that=this
    console.log(e.detail.value)
    that.setData({
      fromdate:e.detail.value
    })
  },

  bindToDateChange: function(e){
    var that=this
    console.log(e.detail.value)
    that.setData({
      todate:e.detail.value
    })
  },  

  yesterday:function(e){
    var that=this;
    var fromdate = util.dateDelta(util.getToday(), -1)
    var todate = fromdate
    that.setData({
      fromdate: fromdate,
      todate:todate
    })
  },
  today:function(e){
    var that=this;
    var fromdate = util.getToday()
    var todate = fromdate
    that.setData({
      fromdate: fromdate,
      todate:todate
    })
  },

  thismonth:function(e){
    var that=this;
    var date = new Date();
    var year = date.getFullYear();
    var month = date.getMonth() + 1;
    if (month < 10) {
      month = '0' + month;
    };

    var fromdate = year+'-'+month +'-01'
    var todate = util.getToday()
    that.setData({
      fromdate: fromdate,
      todate:todate
    })
  },
  lastmonth:function(e){
    var that=this;
    var date = new Date();
    var year = date.getFullYear();
    var month = date.getMonth() + 1;

    if (month < 10) {
      var month = '0' + month;
      var lastdate = util.getLastMonthLastDate()
    };
    if (month==1){
      var year= year-1
      var month='12'
      var lastdate ='31'
    }

    var fromdate = year + '-' + month + '-01'
    var todate = year +'-'+ month +'-'+ lastdate 
    that.setData({
      fromdate: fromdate,
      todate:todate
    })
  },
  clickQuery: function(e){
    var that=this;
    var fromdate=that.data.fromdate
    var todate = that.data.todate
    console.log('that.data',fromdate,todate)
    var url = app.globalData.host + 'report/get_dailystoredata/'
    var param = {
      company:app.globalData.company,
      storecode:app.globalData.storecode,
      appcode:app.globalData.appcode,
      openid:app.globalData.openid,
      ecode:app.globalData.ecode,
      fromdate:fromdate,
      todate:todate,
      reporttype:that.data.reporttype
    }

    if (that.data.reporttype == 'coredata'){
      var url = app.globalData.host + 'report/get_dailystoredata/'
    }
    if (that.data.reporttype == 'emplarch_detail'){
      // get_archivementdetail_byecode
      var url = app.globalData.host + 'cashier/get_archivementdetail_byecode/'
    }  
    if (that.data.reporttype == 'emplarch_sum'){
      var url = app.globalData.host + 'cashier/get_archivementsum_byecode/'
    }
    app.globalData.reporturl = url
    app.globalData.param = param
    app.globalData.reporttype = that.data.reporttype
    console.log('that.data.reporttype',that.data.reporttype)
    if (that.data.reporttype == 'emplarch_detail'){
      wx.navigateTo({
        url: '../emplarch_detail/emplarch_detail',
      })    
    }
    else {
      wx.navigateTo({
        url: '../result/result',
      })
    }


  },

  // getList: function(url,param) {
  //   var that=this;
  //   var url = app.globalData.host +'report/'
  //   return new Promise((resolve, reject) => {
  //     util.getData(url,param)
  //     .then((res) => {
  //       that.setData({
  //         reportdata: res
  //       })
  //       console.log(res)
  //       resolve()
  //     })
  //       .catch((err) => {
  //         console.error(err)
  //         reject(err)
  //       })
  //   })
  // },

})