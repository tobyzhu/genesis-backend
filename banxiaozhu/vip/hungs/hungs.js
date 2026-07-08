
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({
  data: {
    vipuuid:'',
    vip:{},
    hungslist:[],
    hungdate:''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this;
    var app = getApp();
    var today = util.getToday();
    console.log('Hungs onLoad', options)

    that.setData({
      vip: app.globalData.currentvip
    })
    var vipuuid = that.data.vip.uuid
    console.log('vipuuid',vipuuid)
    viputils.getHung(that,vipuuid)
  

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
  open: function () {
    wx.showActionSheet({
      itemList: ['未到店', '到店', '离店'],
      success: function (res) {
        if (!res.cancel) {
          console.log(res.tapIndex)
        }
      }
    });
  },
  bindHungDateChange: function (e) {
    var app = getApp();
    var that = this;
    var hungdate = e.detail.value
    console.log(e.detail.value);
    // that.getBookingList(bookingdate);
    that.setData({
      hungdate: hungdate
    })
  },

  changeStatus: function (options) {
    var app = getApp();
    var that = this;
    var host = app.globalData.host;
    console.log('changestatus options', options)
    var index = options.index;
    var bookinglistindex = options.bookinglistindex;
    var bookingeventid = that.data.bookinglist[bookinglistindex].bookingeventid;
    var status = options.status;

    var key = 'bookinglist[0].bookingstatus'

    that.setData({
      [key]: status
    })
    var param = that.data.bookinglist[0]
    console.log('param', param)
    console.log(that.data.bookinglist[index])
    var url = host + 'adviser/bookingevent/' + bookingeventid;
    var url = host + 'adviser/update_bookingevent/?param=' + JSON.stringify(param);
    console.log(url, param)
    wx.request({
      method: 'POST',
      url: url,
      // data: that.data.bookinglist[bookinglistindex],
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        console.log(res)
        console.log('success')
        that.getBookingList(that.data.bookingdate)
      }
    })
  },

  openActions: function (e) {
    var that = this;
    console.log(e, e.currentTarget.id);
    var hungsindex = e.currentTarget.id;
    var hungsitem = that.data.hungist[e.currentTarget.id];
    var itemStatus = ['10', '20', '30', '40', ''];
    wx.showActionSheet({
      itemList: ['已开单', '已配料', '已服务', '已确认', '作废'],
      success: function (res) {
        var index = res.tapIndex;
        console.log('res:', res, 'index:', index);
        // if (index < 4) {
        //   var status = itemStatus[index]
        //   var options = { index: index, status: status, bookinglistindex: bookinglistindex }
        //   console.log('openactions options', options)
        //   that.changeStatus(options)
        // };
        // if (index == 4) {
        //   var bookingeventid = bookingevent.bookingeventid
        //   console.log(bookingeventid)
        //   wx.navigateTo({
        //     url: '../../vip/bookingdetail/bookingdetail?bookingeventid=' + bookingeventid,
        //   })
        // }

      }
    });
  }
})