var util = require('../../utils/util.js')

Page({
  data:{  
    bookinglist:[],
    bookingstatus:[
      { value: '100', label: '未到店', color: 'black' },    
      { value: '200', label: '到到店', color: 'blue' },
      { value: '300', label: '服务中', color: 'green' },
      { value: '400', label: '离店', color: 'red' }
    ],
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    var today = util.getToday();
    that.getBookingList(today )
    that.setData({
      bookingdate: today
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
  open: function () {
    wx.showActionSheet({
      itemList: ['未到店','到店', '离店'],
      success: function (res) {
        if (!res.cancel) {
          console.log(res.tapIndex)
        }
      }
    });
  },
  bindBookingDateChange: function(e) {
    var app = getApp();
    var that = this;
    var bookingdate = e.detail.value
    console.log(e.detail.value);
    that.getBookingList(bookingdate);
    that.setData({
      bookingdate:bookingdate
    })
  },

  getBookingList: function (options){
    var app = getApp();
    var company = app.globalData.company;
    var storecode = app.globalData.storecode;
    var bookingdate = options
    var that = this;
    var host = app.globalData.host;
    console.log(host)
    var url = host + 'adviser/get_bookinglist'
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: company,
        storecode: storecode,
        bookingdate: bookingdate
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        that.setData({
          bookinglist: res.data
        })
        for (var item in that.data.bookinglist) {
          var bookingstatus = that.data.bookinglist[item].bookingstatus; 
          console.log(bookingstatus); 
          if (bookingstatus =='100'){
            var status = '未到店';
            var key10 = 'bookinglist[' + item + '].status';
            console.log('key10', key10, 'bookingstatus', bookingstatus)
            that.setData({
              [key10]: status
            })           
          } 
          if (bookingstatus == '200') {
            var status = '已到店';
            var key20 = 'bookinglist[' + item + '].status';
            that.setData({
              [key20]: status
            })
          } 
          if (bookingstatus == '310') {
            var status = '已离店';
            var key30 = 'bookinglist[' + item + '].status';
            that.setData({
              [key30]: status
            })
          }
          if (bookingstatus == '390') {
            var status = '取消预约';
            var key30 = 'bookinglist[' + item + '].status';
            that.setData({
              [key30]: status
            })
          }                                                        
        }       
      },
      fail(res){
        console.log(res)
      },
      finished(res){
        console.log(res)
      }
    }) 
  },
  changeStatus: function(options){
    var app  = getApp();
    var that = this;
    var host = app.globalData.host;
    console.log('changestatus options',options)
    var index = options.index;
    var bookinglistindex = options.bookinglistindex;
    var bookingeventid = that.data.bookinglist[bookinglistindex].bookingeventid;
    var status = options.status;
  
    var key = 'bookinglist[0].bookingstatus'

    that.setData({
      [key]:status
    })
    var param = that.data.bookinglist[0]
    console.log('param',param)
    console.log(that.data.bookinglist[index])
    var url = host + 'adviser/bookingevent/' + bookingeventid;
    var url = host + 'adviser/update_bookingevent/?param=' + JSON.stringify(param);
    console.log(url, param)
    wx.request({
      method:'POST',
      url: url,
      // data: that.data.bookinglist[bookinglistindex],
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res){
        console.log(res)
        console.log('success')
        that.getBookingList(that.data.bookingdate)
      }
    })
  },

  openActions: function (e) {
    var that = this;
    console.log(e,e.currentTarget.id);
    var bookinglistindex = e.currentTarget.id;
    var bookingevent = that.data.bookinglist[e.currentTarget.id];
    var itemStatus = ['100', '200', '310', '390', ''];
    wx.showActionSheet({
      itemList: ['未到店','到店', '离店', '取消预约','预约详情','更多操作'],
      success: function (res) {
        var index = res.tapIndex;
        console.log('res:',res,'index:',index);
        if (index < 4){
          var status = itemStatus[index]
          var options = { index: index, status: status, bookinglistindex: bookinglistindex}
          console.log('openactions options',options)
          that.changeStatus(options)
        };
        if (index == 4) {
          var bookingeventid = bookingevent.bookingeventid
          console.log(bookingeventid)
          wx.navigateTo({
            url: '../../vip/bookingdetail/bookingdetail?bookingeventid='+bookingeventid,
          })
        };
        if (index == 5) {
          var vipuuid = bookingevent.vipuuid
          console.log(vipuuid)
          wx.redirectTo({
            url: '../../vip/vip?uuid=' + vipuuid,
          })
        }

      }
    });
  }    
})