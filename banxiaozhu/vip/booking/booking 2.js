// vip/booking/booking.js

var util = require('../../utils/util.js')
// var common = require(‘common.js’);


Page({

  data: {
    companyid:'',
    storecode:'',
    operecode:'',  
    vip:{},  
    vipuuid:'',
    vname:'',
    bookingoperdate:'',
    bookingdate:'',
    bookingstarttime:'',
    bookingendtime:'',
    roomstarttime:'',
    roomendtime:'',
    instrumentstarttime:'',
    instrumentendtime:'',
    emplIndex:-1,
    ecode:'',
    roomid:'',
    roomIndex:-1,
    instrumentid:'',
    instrumentIndex:-1,
    roomlist:[],
    instrumentlist:[],
    empllist:[],
    bookingdetail:''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp();
    var that= this;
    var parent = options.parent;
    var today = util.getToday();
    var empllist= app.globalData.seccodelist
    console.log(today, empllist)

    // that.get_Bookingable_Empllist();
    that.setData({
      companyid: app.globalData.company,
      storecode: app.globalData.storecode,
      operecode: app.globalData.ecode,
      vip: app.globalData.currentvip,
      bookingdate:today,
      // vname:options,
      roomlist: app.globalData.roomlist,
      instrumentlist:app.globalData.instrumentlist,
      empllist:app.globalData.seccodelist
    })


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
  
  bindBookingDateChange: function (e) {
    var bookingdate = e.detail.value.split('-').join('');
    console.log(bookingdate)
    this.setData({
      bookingdate: bookingdate
    })
  },
  
  bindEmplChange: function (e) {
    console.log('picker empl 发生选择改变，携带值为', e.detail.value);
    var that = this;
    if (e.detail.value >= 0 && that.data.empllist.length > 0) {
      that.setData({
        emplIndex: e.detail.value,
        ecode: that.data.empllist[e.detail.value].ecode
      })
    }
  }, 


  bindSTimeChange: function (e) {
    console.log(e.detail.value)
    var starttime = e.detail.value
    var endtime = parseInt(starttime.substring(0, 2))+2
    this.setData({
      bookingstarttime: e.detail.value,
      bookingendtime: String(endtime) + starttime.substring(2, 5)
    })
  },

  bindEndTimeChange: function (e) {
    this.setData({
      bookingendtime: e.detail.value
    })
  }, 
  bindRoomSTimeChange: function (e) {
    console.log(e.detail.value)
    var endtime = ''
    this.setData({
      roomstarttime: e.detail.value
    })
  },

  bindRoomEndTimeChange: function (e) {
    this.setData({
      roomendtime: e.detail.value
    })
  }, 


  bindInstrumentSTimeChange: function (e) {
    // console.log(e.detail.value)
    var endtime = ''
    this.setData({
      instrumentstarttime: e.detail.value
    })
  },

  bindInstrumentEndTimeChange: function (e) {
    this.setData({
      instrumentendtime: e.detail.value
    })
  },    


  bindRoomChange: function (e) {
    console.log('picker room 发生选择改变，携带值为', e.detail.value);
    var that = this;
    var index = e.detail.value;
    that.setData({
      roomIndex: e.detail.value,
      roomid: that.data.roomlist[index].roomid,
      roomstarttime: that.data.bookingstarttime,
      roomendtime:that.data.bookingendtime
    })
  },
  bindInstrumentChange: function (e) {
    console.log('picker instrument 发生选择改变，携带值为', e.detail.value);
    var that = this;
    that.setData({
      instrumentIndex: e.detail.value,
      instrumentid: that.data.instrumentlist[e.detail.value].instrumentid,
      instrumentstarttime: that.data.bookingstarttime,
      instrumentendtime: that.data.bookingendtime
    })
  },

  bindBookingDetailChange: function(e) {
    console.log('picker Bookingdetail 发生选择改变，携带值为', e.detail.value);
    var that = this;
    that.setData({
      bookingdetail: e.detail.value
    })
  },

  checkBookingItem:function(e){
    var app = getApp();
    var that = this;
    if (that.data.bookingstartdate==None ) {

    } 
  },

  addBookingEvent:function(e){
    var app = getApp();
    var that = this;
    var host = app.globalData.host;
    var company = app.globalData.company;
    var storeCode = app.globalData.storeCode;
    // var ecode = app.globalData.ecode;
    // var url = host + 'adviser/bookingevent/';
    var param = {
      company: app.globalData.company,
      storecode: that.data.storecode,
      creater: app.globalData.ecode,
      bookingstartdate: that.data.bookingdate.split('-').join(''),
      bookingstarttime: that.data.bookingstarttime,
      bookingendtime: that.data.bookingendtime,
      vcode: that.data.vip.vcode,
      vname: that.data.vip.vname,
      mtcode: that.data.vip.mtcode,
      ecode: that.data.ecode,
      roomid: that.data.roomid,
      roomstarttime: that.data.roomstarttime,
      roomendtime: that.data.roomendtime,
      instrumentid: that.data.instrumentid,
      instrumentstarttime: that.data.instrumentstarttime,
      instrumentendtime: that.data.instrumentendtime,
      bookingdetail: that.data.bookingdetail,
      bookingstatus: '100',
      operecode: app.globalData.ecode,
      bookingflag: 'Y',
      vipuuid: that.data.vip.uuid
      };
    var url = host + 'adviser/add_bookingevent/?param=' + JSON.stringify(param);
    wx.request({
      method:'POST',
      url: url,
      // data: param,
      header: {
        'content-type': 'application/json' // 默认值
      },
      success: function (res) {
        console.log(res.data)
        wx.showToast({
          title: '已完成',
          icon: 'success',
          duration: 3000
        });
      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("completed",res)
      }      
    })
  },

  get_Bookingable_Empllist: function() {
    var app = getApp();
    var that = this;
    var url = app.globalData.host + 'adviser/get_bookingable_empllist'
    wx.request({
      method:'GET',
      url: url,
      data:{
        company: app.globalData.company,
        storecode:app.globalData.storecode
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success: function (res) {
        console.log(res.data)
        that.setData({
          empllist: res.data
        })
      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("completed", res)
      } 
    })
  }
})