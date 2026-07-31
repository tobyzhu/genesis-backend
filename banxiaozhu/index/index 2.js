var util = require('../utils/util.js');
Page({
  data: {
    imgUrls: [],
    indicatorDots: false,
    autoplay: false,
    interval: 5000,
    duration: 1000,
    width:0,
    height:150,
    searchValue: '',
    grids:[]
  },
  onLoad(e){
    var that=this;
    var app = getApp()
    var height = wx.getAppBaseInfo().windowHeight
    var width = wx.getAppBaseInfo().windowWidth

    util.get_indexImageUrl()

    var param={
      functionid:'index',
      key:'grids'
    }
    util.getWechatFunction(that,param)

    that.setData({
      imgUrls: app.globalData.indexImageUrl,
      width :width
    })

    util.showLoading('加载中...');
    console.log('that.data.width',that.data.width)
    util.get_source()
    util.get_empllist()
    util.get_pmcodelist()
    util.get_seccodelist()
    util.get_amountcardtypelist()
    util.get_timescardtypelist()
    util.get_periodcardtypelist()
    util.get_VipList()
    util.get_SrvList()
    util.get_GoodsList()
    util.get_RoomList()
    util.get_InstrumentList()
    util.get_PsStatusList()
    util.get_vipcasetype()
    util.get_stypelist()
    // util.get_Vip10List()
    // util.get_Vip20List()
    // util.get_Vip30List()
    // util.get_VipInList()
    // util.get_VipNotinList()
    // util.get_emplarch_bymonth()
    util.get_SalonList()
    util.get_ViplevelList()
    
    setTimeout(function () {
      // wx.hideLoading()
      util.hideLoading()
    }, 2000)
  },
  changeIndicatorDots(e) {
    this.setData({
      indicatorDots: !this.data.indicatorDots
    })
  },
  changeAutoplay(e) {
    this.setData({
      autoplay: !this.data.autoplay
    })
  },
  intervalChange(e) {
    this.setData({
      interval: e.detail.value
    })
  },
  durationChange(e) {
    this.setData({
      duration: e.detail.value
    })
  },
  wxSearchTab: function () {
    wx.redirectTo({
      url: '../search/search'
    })
  }

})