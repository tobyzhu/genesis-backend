
var app=getApp()
var util = require('../../utils/util.js')
var wxCharts = require('../../utils/wxcharts.js');
// import ad from '../index/ad'
// ad({})

Page({

  /**
   * 页面的初始数据
   */
  data: {
    openid:'',
    storelist: ['01','02','03','04'],
    vipcntlist:[],
    storcode:[],
    detail:[],
    vsdate:[],
    fromdate:'2020-06-01',
    todate:'2020-06-13',
    prevdate:'',
    reportdate:'',
    nextdate:'',
    reportdate_data:[],
    thismonthdata:[],
    premonthdata:[],
    storedata:[],
    imagearray:[
      {
        id:1,
        mode: 'scaleToFill',
        text: '到店客数',
        src:"http://localhost:8080/report/images/?filename=yiren2019102220191130abc.jpg"
      },
    ]


    
  },

  /**
   * 生命周期函数--监听页面加载at
   */
  onLoad: function (options) {
    var that=this;
    var openid = app.globalData.openid
    var thismonth= util.getMonth(  new Date())+1;
    var premonth = util.getPreMonth(  new Date());
    console.log(thismonth,premonth)
    var key1 ='thismonthdata'
    var key2 ='premonthdata'
    that.setData({
      reportdate:util.getToday(),
      fromdate:util.getToday(),
      todate:util.getToday()
    })
    // util.get_VipcntList(that,thismonth,key1);
    // util.get_VipcntList(that,premonth,key2);  
    // util.get_DailyStoreData(that,thismonth,key1);
    // util.get_DailyStoreData(that,premonth,key2);     
    that.get_data()
    
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
    // var now1 = getDate()；
    // console.log('now:',now1,util.getToday())
    // var fromdate = now.util.strtodate(util.getMonth(util.getToday())+'01')
    var fromdate = util.getMonth(util.getToday()) +'-01'
    var todate = util.getToday()
    that.setData({
      fromdate: fromdate,
      todate:todate
    })
  },
  clickQuery(e){
    var that=this;
    var fromdate=that.data.fromdate
    var todate = that.data.todate
    console.log('that.data',fromdate,todate)
    util.get_DailyStoreData(that,fromdate,todate);
  },

  onClick(e) {
    var that=this;
    console.log('onClick', e,that.data.reportdate)
    if (e.detail.type==='left'){
      var reportdate = util.dateDelta(that.data.reportdate, -1)
      that.setData({
        reportdate: reportdate
      })
      console.log('reportdate',that.data.reportdate,util.datetostr(reportdate))
    }
    if (e.detail.type === 'right') {
      var reportdate =  util.dateDelta(that.data.reportdate, 1)
      that.setData({
        reportdate: reportdate
      })
      console.log('reportdate',that.data.reportdate,util.datetostr(reportdate))
    }
    var reportdate_data = []
    console.log('reportdate string ',util.datetostr(reportdate) )
    var cells = that.data.thismonthdata.filter(item => item.vsdate == util.datetostr(reportdate))

    console.log(cells)
    reportdate_data.push({
      cells
    })
    that.setData({
      reportdate_data:reportdate_data
    })


  },


  get_data: function(){
    var that=this;
    var host = app.globalData.host;
    var company = app.globalData.company;
    var url = host + "cashier/json_test/"
    var storecode= app.globalData.storecode
    var ecode=that.data.ecode

    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company
      },
      // header: {
      //   'content-type': 'application/json' // 默认值
      // },
      success(res) {
        console.log('json_test res.data', res.data)
        that.setData({
          detail:res.data,
        })
      }
    });
  }

})