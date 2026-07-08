// vip/timescardquery/timescardquery.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    searchValue:'',
    vip:{},
    vipuuid:'',
    payccode:'',
    storecode:'',
    index:-1,
    timescardtypelist:[],
    timescardtypeuuid:'',
    timescardtype:'',
    timescardname:'',
    timescardtypeindex:-1

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp();
    var that = this;
    var vip = app.globalData.currentvip;

    console.log('options', options)
    if (options && options.searchValue) {
      that.setData({
        searchValue: options.searchValue
      })
      that.getTimesCardtypeList()

    }
    else {
      wx.showLoading();
      // this.getServiece();
      wx.getStorage({
        key: 'timescardtypelist',
        success: function (res) {
          console.log(res.data),
            wx.hideLoading()
          that.setData({
            timescardtypelist: res.data,
            // timescardtypelist: res.data.slice(0, that.data.count)
          })
          that.init_timecardtypeList()
          wx.hideLoading()
        }
      });
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
  timescardtypeChange: function(e){
    var app=getApp()
    var that=this
    console.log('radio发生change事件，携带value值为：', e.detail.value);

    var timescardtypelist = this.data.timescardtypelist;

    for (var i = 0, len = timescardtypelist.length; i < len; ++i) {
      if (i <=100){
        console.log('timescardtypelist[i].cardtype=', timescardtypelist[i].cardtype)
        timescardtypelist[i].checked = timescardtypelist[i].cardtype == e.detail.value;
        if (timescardtypelist[i].checked) {
          that.setData({
            index: i,
            timescardtypeindex: i,
            timescardtype: timescardtypelist[i].cardtype,
            timescardname: timescardtypelist[i].cardname,
            timescardtypeuuid: timescardtypelist[i].uuid
          })
        }
      }

    }

    this.setData({
      timescardtypelist: timescardtypelist
    });
  },

  // 获取服务项目
  getTimesCardtypeList() {
    var that = this;
    var app = getApp();
    var params={
      company:app.globalData.company,
      searchvalue:that.data.searchValue,
      comptype:'times'

    }
    const data = params
    var url = app.globalData.host + "baseinfo/get_cardtypelist_bykeyword"
    wx.showLoading()
    wx.request({
      url: url,
      data,
      success: (res) => {
        console.log(res)

        wx.hideLoading()
        that.setData({
          timescardtypelist: res.data
        })
        that.init_timecardtypeList()
        wx.hideLoading()
      },
      fail: (res) => {
        console.log(res)
      },
      complete: (res) => {
        console.log(res)
        wx.hideLoading()
      }

    })
  },
  // 对服务项目补充开单需要的相关字段信息
  init_timecardtypeList: function () {
    var that = this;
    var app = getApp();
    var fields = [
      { filed: 'payccode', value: '' },
      { field: 'qty', value: 0 },
      { field: 'secdisc', value: 1 },
      // {field:'s_price',value:0},
      { field: 'amount', value: 0 },
      { field: 'mondisc', value: 0 },
      { field: 'pmcode', value: '' },
      { field: 'seccode', value: '' },
      { field: 'thrcode', value: '' },
      { field: 'stype', value: 'N' },
      { field: 'promotionsid', value: '0' }
    ];
    for (var index in that.data.timescardtypelist) {
      for (var item in fields) {
        var key = 'timescardtypelist[' + index + '].' + fields[item].field;
        // console.log(key);
        that.setData({
          [key]: fields[item].value
        })
      };
    }
  },
  confirm: function() {
    var app=getApp()
    var that=this
    var cardtype = that.data.timescardtypelist[that.data.index].cardtype
    var cardname = that.data.timescardtypelist[that.data.index].cardname
    // var cardtype = that.data.timescardtypelist[that.data.index]
    wx.redirectTo({
      url: '../newtimescard/newtimescard?cardtype='+cardtype+'&cardname='+cardname+'&searchvalue='+that.data.searchValue
    })

  },
  // 搜索入口  
  wxSearchTab: function () {
    wx.redirectTo({
      url: '../timescardsearch/timescardsearch'
    })
  }

})