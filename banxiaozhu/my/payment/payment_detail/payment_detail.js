// my/payment/payment_detail/payment_detail.js

var app=getApp()

Page({

  /**
   * 页面的初始数据
   */
  data: {
    payment_detail:[],
    openid:''

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    var openid = app.globalData.openid
    // var url = app.globalData.host+'common/query_companyorder/'
    var url = app.globalData.host+'common/companyorder/' 
    wx.request({
      method:'GET',
      url: url,
      header: {
        'content-type': 'application/json' // 默认值
      },
      data:{
        // openid:openid
        search:openid
      },
      success: function(res){
        console.log(res)
        that.setData({
          payment_detail: res.data.results
        })

      },
      fail: function(res){

      },
      finished: function(res){

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

  }
})