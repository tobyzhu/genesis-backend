
var util = require('../../utils/util.js');
var viputil = require('../viputils.js');
var sliderWidth = 72;
Page({

  /**
   * 页面的初始数据
   */
  data: {
    network_allow_flag:false,
    vipuuid:"",
    vname:"",
    vip:{},
    payccode:'',
    payccodeindex:-1,
    kaidan_qty:0,
    srvlist:[],
    goodslist:[],
    nopayccodehung:[],
    hung:[],
    amountcardlist:[],
    timescardlist:[],
    cardtype_10_list: [],
    cardtype_20_list: [],
    current:'tab1',
    currentcontent:'Amount Card',
    h_current:'tab1',
    v_current:'tab1',
    h_tabs:[
      {
        key: 'tab1',
        title: '储值账户',
        content: 'Amount Card',
      },
      {
        key: 'tab2',
        title: '疗程账户',
        content: 'Times Card',
      },   
    ],
    grids:[
      {
        id:1,
        text:'单次服务',
        url:'../serviece/serviece'
      },
      {
        id: 2,
        text: '购买商品',
        url: '../goods/goods'
      },
      {
        id: 3,
        text: '储值卡开卡',
        url: '../newcard/newcard'
      },
      {
        id: 4,
        text: "储值卡充值",
        url: "../fillcard/fillcard",
        image: ""
      },
      {
        id: 5,
        text: '疗程卡开卡',
        url: '../newtimescard/newtimescard'
      },
      {
        id: 6,
        text: '开单信息',
        url: '../hungs/hungs'
      }
    ],

    tabs: [
      {
        key: 'tab1',
        title: '储值账户',
        content: 'Amount Card',
      },
      {
        key: 'tab2',
        title: '疗程账户',
        content: 'Times Card',
      },
    ],
    activeIndex: 0,
    sliderOffset: 0,
    sliderLeft: 0
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp();
    var that=this;
    console.log('app.globalData.currentvip_amountcardlist:',app.globalData.currentvip_amountcardlist)
    that.setData({
      vip:app.globalData.currentvip,
      vipuuid: app.globalData.currentvip.uuid,
      vname: app.globalData.currentvip.vname,
      network_allow_flag: app.globalData.network_allow_flag,
      amountcardlist: app.globalData.currentvip_amountcardlist,
      timescardlist: app.globalData.currentvip_timescardlist
      
    })
    wx.getSystemInfo({
      success: function(res) {
          that.setData({
              sliderLeft: (res.windowWidth / that.data.tabs.length - sliderWidth) / 3,
              sliderOffset: res.windowWidth / that.data.tabs.length * that.data.activeIndex
          });
      }
    })

    var param = {
      functionid: 'amountcard',
      key: 'grids'
    }
    util.getWechatFunction(that, param)    

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
    // console.log(e)
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

  onPullDownRefresh: function () {
    var that = this
    console.log('begin PullDown')
    wx.showNavigationBarLoading()

    var options = {
      uuid: that.data.vip.uuid
    }
    viputil.getVipBaseInfo(that, options);

    setTimeout(() => {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    }, 2000);
    console.log('end PullDown')
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
  onChange_h(e) {
    console.log('onChange_h', e)
    this.setData({
      h_current: e.detail.key
    })
  },  
  onChange_v(e) {
    console.log('onChange_v', e)
    this.setData({
      v_current: e.detail.key
    })
  },

  amountcardChange: function (e) {
    var app=getApp();
    var that=this;
    var amountcardlist = this.data.amountcardlist;
    for (var i = 0, len = amountcardlist.length; i < len; ++i) {
      amountcardlist[i].checked = amountcardlist[i].value == e.detail.value;
      app.globalData.payccode = amountcardlist[i].ccode
      app.globalData.payccodeindex=i
    }

    this.setData({
      amountcardlist: amountcardlist,
      payccode: app.globalData.payccode,
      payccodeindex: app.globalData.payccodeindex

    });
  },
  gotoShoppingCart: function () {
    var that = this;
    wx.navigateTo({
      url: '../shoppingcar/shoppingcar',
    })
  },
  tabClick: function (e) {
    var that=this;
    this.setData({
        sliderOffset: e.currentTarget.offsetLeft,
        activeIndex: e.currentTarget.id
    });
    console.log('activeIndex:', that.data.activeIndex)
  }
  
})