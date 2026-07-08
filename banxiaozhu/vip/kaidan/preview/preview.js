// vip/kaidan/preview/preview.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    hungitems:[
      {
        ttype:'S',
        srvcode:'1001',
        srvname:'测试',
        qty:1,
        price:9800,
        disc:1.0,
        amount:9800,
        modisc:0,
        pmcode:'Eddie',
        seccode:'Lisa'
      }
    ],
    right: [{
      text: 'Cancel',
      style: 'background-color: #ddd; color: white',
    },
    {
      text: 'Delete',
      style: 'background-color: #F4333C; color: white',
    }],
    left: [{
      text: 'Reply',
      style: 'background-color: #108ee9; color: white',
    },
    {
      text: 'Cancel',
      style: 'background-color: #ddd; color: white',
    }],

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

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