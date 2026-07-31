// vip/vipindex/vipindex.js
var util = require('../../utils/util.js')
var viputils = require('../viputils.js');
var app=getApp()

Page({
  data: {
    value: '',    
    alphabet: [],
    viplist:[],
    vip:{},
    vname:[],
    searchValue: '',
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp()
    var that = this;
    // from search
    if (options && options.searchValue) {
      this.setData({
        searchValue: "搜索：" + options.searchValue
      });
    }

    // that.setData({
    //   viplist: app.globalData.viplist,
    // })

    // console.log('onLoad',that.data.viplist);
    // const alphabet = []
    // 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach((initial) => {
    //   var cells = that.data.viplist.filter(item => item.pinyin.charAt(0).toUpperCase() === initial.toUpperCase())
    //   var vname = that.data.viplist.filter(item => item.pinyin.charAt(0).toUpperCase() === initial.toUpperCase()).vname
    //   // console.log(cells)
    //   alphabet.push({
    //     initial,
    //     vname,
    //     cells
    //   })
    // })

    // this.setData({
    //   alphabet,
    // })
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
    var that=this;
    var app=getApp();
    that.setData({
      viplist: app.globalData.viplist,
    })

    console.log('onshow', that.data.viplist);
    const alphabet = []
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach((initial) => {
      var cells = that.data.viplist.filter(item => item.pinyin.charAt(0).toUpperCase() === initial.toUpperCase())
      var vname = that.data.viplist.filter(item => item.pinyin.charAt(0).toUpperCase() === initial.toUpperCase()).vname
      // console.log(cells)
      alphabet.push({
        initial,
        vname,
        cells
      })
    })

    this.setData({
      alphabet,
    })

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
    var that = this
    console.log('begin PullDown')
    wx.showNavigationBarLoading()
    util.get_VipList()
    setTimeout(() => {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()

      that.setData({
        viplist: app.globalData.viplist,
      })

    }, 2000);
    console.log('end PullDown')  

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
  onIndexChange(e) {
    var that = this;
    var index =e.detail;
    console.log('onIndexChange', e.detail,'index=',index);
    that.data.alphabet.indexOf(index.index);
    // wx.setStorage({
    //   key: '',
    //   data: '',
    // })
  },  
  onChange(e) {
    var that=this;
    console.log('onChange', e.detail)
    var index = e.detail;
    console.log('onIndexChange', e.detail, 'index=', index);
    that.data.alphabet.indexOf(index.index);
    that.setData({

    })
  },
  onSearchChange(e) {
    console.log('onSearchChange', e)
    var that=this;

    this.setData({
      value: e.detail.value,
    })
  },
  onSearchFocus(e) {
    console.log('onFocus', e)
  },
  onSearchBlur(e) {
    console.log('onBlur', e)
  },
  onSearchConfirm(e) {
    var app = getApp();
    var that = this;
    var keyword = e.detail.value;
    var list = that.data.viplist;

    // const alphabet = [];
    // var len = that.data.viplist.length;
    // var arr = [];
    var reg = new RegExp(keyword);
    // for (var i = 0; i < len; i++) {
    //   if (that.data.viplist[i].vname.match(reg)) {
    //     var cells = that.data.viplist[i]
    //     var initial = list[i].pinyin.charAt(0).toUpperCase()
    //     alphabet.push({
    //       initial,
    //       cells
    //     })
    //   }
    // }


    // const alphabet = []
    // 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach((initial) => {
    //   // var cells = that.data.viplist.filter(item => item.pinyin.charAt(0).toUpperCase() === initial.toUpperCase())
    //   var cells = that.data.viplist.filter(item => (item.pinyin.charAt(0).toUpperCase() === initial.toUpperCase() & (item.vname == keyword | item.vcode==keyword | item.mtcode==keyword |item.pinyin==keyword)    ) )
    //   if (cells.length  > 0){
    //     console.log(cells)
    //     alphabet.push({
    //       initial,
    //       cells
    //     })
    //   }
    // })

    // this.setData({
    //   alphabet,
    // })

  },
  onSearchClear(e) {
    console.log('onClear', e)
   
  },
  onSearchCancel(e) {
    console.log('onCancel', e)
  },
  // 搜索入口  
  wxSearchTabVip: function () {
    wx.navigateTo({
      // url: '../search/search',
      url: '../queryvip/queryvip',
    })
  }
})