// vip/bookingdetail/bookingdetail.js
var util = require('../../utils/util.js')
var viputil = require('../viputils.js');

Page({

  /**
   * 页面的初始数据
   */
  data: {
    storecode:'',
    operecode:'',    
    bookinguuid:'',
    bookingevent:[],
    vip:{},
    bookingstatus:'10',
    bookingflag:'Y',
    emplIndex: -1,
    roomIndex: -1,
    instrumentIndex: -1,
    empllist: [],
    roomlist: [],
    instrumentlist: [],
    room:'',
    ecode:'',
    instrument:''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    console.log(options);
    var bookingeventid = options.bookingeventid;
    var app = getApp();
    var that = this;
    var host = app.globalData.host;
    // var url = host + 'adviser/bookingevent/' + bookingeventid;
    var url = host + 'adviser/get_bookingevent/';
    var ecode =''
    var room=''
    var instrument=''

    that.setData({
      storecode: app.globalData.storecode,
      operecode: app.globalData.ecode,
      roomlist: app.globalData.roomlist,
      instrumentlist: app.globalData.instrumentlist,
      empllist: app.globalData.seccodelist
    })
    
    wx.request({
      method:'GET',
      url: url,
      data:{
        company:app.globalData.company,
        bookingeventid: bookingeventid
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        console.log('res.data:',res.data[0])
        that.setData({
          bookingevent: res.data[0],
          bookingeventid: bookingeventid
        })
        // 数组对象查找

        var ecode = that.data.bookingevent.ecode
        var param = {
          type:'empl',
          code:ecode
        }
        viputil.getIndexByCode(that,param)

        var room = that.data.bookingevent.roomid
        // that.getIndexByCode({ type: 'room', code: that.data.bookingevent.roomid })
        var param ={
          type:'room',
          code:room
        }
        viputil.getIndexByCode(that, param)
        // that.checkItem()

        var instrument = that.data.bookingevent.instrumentid
        var param = {
          type: 'instrument',
          code: instrument
        }
        viputil.getIndexByCode(that, param)

        that.setData({
          ecode:ecode,
          room: room,
          instrument: instrument
        })

      }
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
 
  bindVcodeChange: function (e) {
    console.log('picker vcode 发生选择改变，携带值为', e.detail.value);
    var that = this;
    var key = 'bookingevent.vcode'
    that.setData({
      [key]: e.detail.value
    })
  },
  bindVnameChange: function (e) {
    console.log('picker vcode 发生选择改变，携带值为', e.detail.value);
    var that = this;
    var key = 'bookingevent.vname'
    that.setData({
      [key]: e.detail.value
    })
  },
  bindmtcodeChange: function (e) {
    console.log('picker vcode 发生选择改变，携带值为', e.detail.value);
    var that = this;
    var key = 'bookingevent.mtcode'
    that.setData({
      [key]: e.detail.value
    })
  },

  bindEmplChange: function (e) {
    console.log('picker empl 发生选择改变，携带值为', e.detail.value);
    var that = this;
    var key = 'bookingevent.ecode'
    that.setData({
      emplIndex: e.detail.value,
      [key]: that.data.empllist[e.detail.value].ecode
    })
  },

  bindRoomChange: function (e) {
    console.log('picker room 发生选择改变，携带值为', e);
    var that = this;
    var index = e.detail.value;
    var key = 'bookingevent.roomid'    
    // console.log(that.data.roomlist[index].roomid)
    that.setData({
      roomIndex: e.detail.value,
      [key]: that.data.roomlist[index].roomid
    })
  },
  bindInstrumentChange: function (e) {
    console.log('picker instrument 发生选择改变，携带值为', e.detail.value);
    var that = this;
    var key = 'bookingevent.instrumentid'
    that.setData({
      instrumentIndex: e.detail.value,
      [key]: that.data.instrumentlist[e.detail.value].instrumentid
    })
  },

  bindBookingDetailChange: function (e) {
    console.log('picker Bookingdetail 发生选择改变，携带值为', e.detail.value);
    var that = this;
    var key = 'bookingevent.bookingdetail'
    that.setData({
      [key]: e.detail.value
    })
  },

  bindBookingDateChange: function (e) {
    var that = this;
    var key = 'bookingevent.bookingdate'
    this.setData({
      [key]: e.detail.value
    })
  },

  bindSTimeChange: function (e) {
    // var that = this;
    // var nowtime = new getTime();
    // console.log(nowtime)
    // var bookingstarttime = new getTime(e.detail.value);
    // console.log(bookingstarttime, bookingstarttime.toTimeString(),bookingstarttime.getHours())
    // var key = 'bookingevent.bookingstarttime'
    this.setData({
      [key]: e.detail.value
    })
  },

  bindEndTimeChange: function (e) {
    var that = this;
    var key = 'bookingevent.bookingendtime'
    this.setData({
      [key]: e.detail.value
    })
  },
  bindRoomSTimeChange: function (e) {
    var that = this;
    var key = 'bookingevent.roomstarttime'
    this.setData({
      [key]: e.detail.value
    })
  },
  bindRoomEndTimeChange: function (e) {
    var that = this;
    var key = 'bookingevent.roomendtime'
    this.setData({
      [key]: e.detail.value
    })
  },
  bindInstrumentSTimeChange: function (e) {
    // console.log(e.detail.value)
    var endtime = ''
    this.setData({
      instrumentbookingstarttime: e.detail.value
    })
  },

  bindInstrumentEndTimeChange: function (e) {
    this.setData({
      instrumentbookingendtime: e.detail.value
    })
  }, 
  checkItem: function(){
    var that = this;
    var stritems = ['instrumentid','bookingdetail']
    // if (that.data.bookingevent) {
    for (var item in stritems){
      var key2 = 'that.data.bookingevent.'+items[item]      
      var value2 = that.data.bookingevent[items[item]]
      console.log('stritems[item]:', stritems[item],'key2:',key2,'values=',value2)     

      if (that.data.bookingevent[stritems[item]] == null) {
        var key = 'bookingevent.' + stritems[item]
        console.log('key:',key)
        that.setData({
          [key]: ''
        })
      }
    }

    // var timeitems = ['roomstarttime', 'roomendtime', 'instrumentbookingstarttime', 'instrumentbookingendtime']
    // // if (that.data.bookingevent) {
    // for (var item in items) {
    //   var key2 = 'that.data.bookingevent.' + items[item]
    //   var value2 = that.data.bookingevent[items[item]]
    //   if (that.data.bookingevent[items[item]] == null) {
    //     var key = 'bookingevent.' + items[item]
    //     console.log('key:', key)
    //     that.setData({
    //       [key]: that.data.bookingevent.bookingstarttime
    //     })
    //   }
    // }    

    // }
  },
  updateBookingEvent: function (e) {
    var app = getApp();
    var that = this;
    var host = app.globalData.host;
    var company = app.globalData.company;
    var storeCode = app.globalData.storeCode;
    // var ecode = app.globalData.ecode;
    var mythis = this;
    var uuid = mythis.data.bookingevent.uuid;
    
    var url = host + 'adviser/bookingevent/'+uuid;
    console.log(mythis.data.vip)
    wx.request({
      method: 'PUT',
      url: url,
      data: that.data.bookingevent,
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
        console.log("completed", res)
      }
    })
  },
  openToast: function () {
    wx.showToast({
      title: '已完成',
      icon: 'success',
      duration: 3000
    });
  },
  openLoading: function () {
    wx.showToast({
      title: '数据加载中',
      icon: 'loading',
      duration: 3000
    });
  }  
}) 