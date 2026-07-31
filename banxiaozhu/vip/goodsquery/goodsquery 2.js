Page({

  /**
   * 页面的初始数据
   */
  data: {
    searchValue: '',
    vipList: [],
    goodsList:[],
    fail: false
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this;
    var app = getApp();
    console.log('options',options)
    if (options && options.searchValue) {
      that.setData({
        searchValue: options.searchValue
      })
      that.get_goodslist_bykeyword()
    }



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
  get_goodslist_bykeyword: function () {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_goodslist_bykeyword';
    // console.log(xinqu)
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        // ecode: app.globalData.ecode,
        searchvalue: that.data.searchValue

      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        that.setData({
          fail: false,
          goodsList: res.data
        })
      },
      fail: function (res) {
        console.log("failed")
        that.setData({
          fail: true
        })
      },
      complete: function (res) {
        console.log("finished")
      }

    })

  },
  // 搜索入口  
  wxSearchTabGoods: function () {
    wx.redirectTo({
      url: '../goodssearch/goodssearch'
    })
  }
})