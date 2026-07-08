
var util = require('../../utils/util.js')
var viputil = require('../viputils.js');
var app=getApp();
var host = app.globalData.host;
Page({


  data: {
    showTopTips: false,
    uuid:'',
    vip: {},
    vipcasedetail:{},
    empllist:[],
    emplIndex:-1,
    nextemplIndex:-1,
    nextdate:'',
    ecode:'',
    nextecode:'',
    vipcasetypeList:[],
    vipcasetypeIndex:-1,
    vipcasetype:'',
    detail:''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    console.log('options',options)

    that.setData({
      vip: app.globalData.currentvip,
      empllist: app.globalData.empllist,
      vipcasetypeList: app.globalData.vipcasetypeList
    })

    if (options.vipuuid){
      // var vipuuid = options.vipuuid
      // var params={
      //   vipuuid:vipuuid
      // }
      viputil.getVipBaseInfo(that,options)
    } 

    if (options.uuid){
      viputil.get_vipcasedetail(that,options.uuid)

    } else {
      that.setData({
        uuid:'',
      })
    }
    that.setData({
      ecode: app.globalData.ecode
    })

    var ecode = that.data.ecode
    var param = {
      type: 'empl',
      code: ecode
    }

    if (ecode) {
      console.log(ecode,'empl param:',param)
      viputil.getIndexByCode(that, param)
    }


    var vipcasetype = that.data.vipcasetype
    var param = {
      type: 'vipcasetype',
      code: vipcasetype
    }

    if (vipcasetype.len > 0) {
      viputil.getIndexByCode(that, param)
    }

    that.setData({
      nextemplIndex:that.data.emplIndex,
      nextecode: that.data.ecode
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
  bindVipcasetypeChange:function(e){
    console.log('picker vipcasetyp 发生选择改变，携带值为', e.detail.value);
    var that = this;
    if (e.detail.value >= 0) {
      that.setData({
        vipcasetypeIndex: e.detail.value,
        vipcasetype: that.data.vipcasetypeList[e.detail.value].itemname
      })
    }
  },
  bindEmplChange: function (e) {
    console.log('picker empl 发生选择改变，携带值为', e.detail.value);
    var that = this;
    if (e.detail.value>=0){
      that.setData({
        emplIndex: e.detail.value,
        ecode: that.data.empllist[e.detail.value].ecode
      })
    }
  },
  bindNextEmplChange: function (e) {
    console.log('picker empl 发生选择改变，携带值为', e.detail.value);
    var that = this;
    if (e.detail.value>=0){
      that.setData({
        nextemplIndex: e.detail.value,
        nextecode: that.data.empllist[e.detail.value].ecode
      })
    }
  },
  bindDetailChanged:function(e){
    var that=this;
    console.log(e)
    that.setData({
      detail:e.detail.value
    })
  },

  bindNextDateChange: function (e) {
    var that = this;
    console.log(e)
    this.setData({
      nextdate: e.detail.value
    })
  },

  updateVipCaseDetail: function(e){
    var that=this;
    var url = host +'crm/update_vipcasedetail'
    var param={
      uuid: that.data.uuid,
      company:app.globalData.company,
      storecode:app.globalData.storecode,
      ecode:that.data.ecode,
      casetype:that.data.vipcasetypeList[that.data.vipcasetypeIndex].itemname,
      detail:that.data.detail,
      nextdate:that.data.nextdate,
      nextecode:that.data.nextecode,
      vipuuid:that.data.vip.uuid
    }
    wx.request({
      url: url,
      data: param,
      method: 'GET',
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res)
        wx.showToast({
          title: '已完成',
          icon: 'success',
          duration: 3000
        });
        // wx.redirectTo({
        //   url: '../vipcasedetail/vipcasedetail',
        // })
        wx.navigateBack({
          delta:1
        })
        // app.globalData.cardtype10list = res.data
      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }
    });
  }
})