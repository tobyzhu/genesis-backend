// vip/newvip/newvip.js
// import { $wuxSelect } from '../../wux/packages/lib/index'
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({

  /**
   * 页面的初始数据
   */
  data: {
    vipTypeList: [
      {
        value: '10',
        title: '会员'
      },
      {
        value: '20',
        title: '非会员'
      },
      {
        value: '30',
        title: '潜在客户'
      }
    ],
    vip:[],
    viptype: '',
    viptypeindex: -1,
    vcode: '',
    vname: '',
    mtcode: '',
    birthday: '2000-01-01',
    indate:'',
    viplevel: 'C',
    viplevelname:'',
    viplevellist:[],
    viplevellistindex:-1,
    pmcode: '',
    pmname: '',
    pmcodeindex:-1,
    pmcodelist: [],
    seccodeindex:-1,
    seccode: '',
    secname: '',
    seccodelist: [],
    thrcodeindex:-1,
    thrcode:'',
    thrname:'',
    thrcodelist:[],
    source: [],
    sourceindex: -1,
    sourceid: '',
    sourcename: '',
    vdesc: ''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp();
    var that = this;
    // var testdate = util.strtodate('20190501')
    // console.log('getDate date', testdate)
    
    that.setData({
      vip: app.globalData.currentvip,
      viptype: app.globalData.currentvip.viptype,
      vcode: app.globalData.currentvip.vcode,
      vname: app.globalData.currentvip.vname,
      mtcode: app.globalData.currentvip.mtcode,
      birthday: app.globalData.currentvip.birth,
      indate:app.globalData.currentvip.indate,
      // birthday: util.strtodate(app.globalData.currentvip.birth),
      pmcode: app.globalData.currentvip.ecode,
      pmcodelist:app.globalData.pmcodelist,
      seccode: app.globalData.currentvip.ecode2,
      seccodelist:app.globalData.seccodelist,
      source:app.globalData.sourcelist,
      viplevellist: app.globalData.viplevellist
    })

    // that.get_vipsource()
    var viptypeoption={
      type:'viptype',
      code: that.data.viptype
    }
    viputils.getIndexByCode(that, viptypeoption)

    var pmcodeoption={
      type:'pmcode',
      code:that.data.vip.ecode
    }
    viputils.getIndexByCode(that,pmcodeoption)
    
    var seccodeoption = {
      type: 'seccode',
      code: that.data.vip.ecode2
    }
    viputils.getIndexByCode(that,seccodeoption)

    var sourceoption = {
      type: 'source',
      code: that.data.vip.source
    }
    viputils.getIndexByCode(that, sourceoption)

    var vipleveloption = {
      type: 'viplevel',
      code: that.data.vip.viplevellist
    }
    viputils.getIndexByCode(that, vipleveloption)
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
    var that = this
    console.log('begin PullDown')
    wx.showNavigationBarLoading()
    that.onLoad()
    setTimeout(() => {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
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

  bindViptypeChange: function (e) {
    console.log(e)
    var that = this;
    var vipType = that.data.vipTypeList[e.detail.value]
    // if (vipType.value == '10') {
    //   that.get_nextvcode()
    // }
    that.setData({
      viptypeindex: e.detail.value,
      viptype: that.data.vipTypeList[e.detail.value].value
    })
    // var viptypeoption = {
    //   type: 'viptype',
    //   code: that.data.viptype
    // }
    // viputils.getIndexByCode(that, viptypeoption)

  },
  bindDateChange: function (e) {
    this.setData({
      birthday: e.detail.value
    })
  },
  bindIndateChange: function(e){
    var that=this;
    that.setData({
      indate: e.detail.value
    })
  },

  bindVnameChange: function (e) {
    // console.log(e.data)
    this.setData({
      vname: e.detail.value
    })
  },
  bindMtcodeChange: function (e) {
    // console.log(e.data)
    this.setData({
      mtcode: e.detail.value
    })
  },
  bindViplevelChange:function(e){
    var that = this;
    viputils.bindViplevelChange(that, e)   
  },
  bindPmcodeChange: function (e) {
    var that = this;
    viputils.bindPmcodeChange(that, e)
  },
  bindSeccodeChange: function (e) {
    var that = this;
    viputils.bindSeccodeChange(that, e)
  },
  bindThrcodeChange: function (e) {
    var that = this;
    viputils.bindThrcodeChange(that, e)
  },
  bindSourceChange: function (e) {
    var that = this;
    console.log(e)
    this.setData({
      sourceid: that.data.source[e.detail.value].itemname,
      sourcename: that.data.source[e.detail.value].itemvalues,
      sourceindex: e.detail.value
    })
  },
  bindDescChange: function (e) {
    var that = this;
    console.log(e.detail.value)
    that.setData({
      vdesc: e.detail.value
    })
  },
  updateVipInfo: function (e) {
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company
    var storeCode = app.globalData.storeCode
    var ecode = app.globalData.ecode
    var that = this;
    // var url = host + 'baseinfo/vip/'+that.data.vip.uuid+'/'
    var url = host + 'baseinfo/update_vip/'
    // var url = that.data.vip.url
    var source = that.data.sourcetitle
    // var xinqu = JSON.stringify(mythis.data.title3)
    // var occupation = that.data.occupation
    var vcode = that.data.vcode
    if (vcode == null){
      vcode=''
    }
    if (vcode.length == 0) {
      vcode = ''
    }
    wx.showLoading({
      title: '数据更新中',
    })
    console.log(url)
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        uuid : that.data.vip.uuid,
        viptype: that.data.viptype,
        // vcode: that.data.vcode,
        vname: that.data.vname,
        mtcode: that.data.mtcode,
        birthday: that.data.birthday,
        indate: that.data.indate,
        ecode: that.data.pmcode,
        ecode2: that.data.seccode,
        source: that.data.sourceid,
        vdesc: that.data.vdesc,
        viplevel: that.data.viplevel
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res)
        var param={
          uuid:that.data.vip.uuid
        }
        viputils.getVipBaseInfo(that, param)
        setTimeout(function () {
          that.setData({
            showTopTips: false
          });
        }, 1000);
        that.onLoad()
        wx.hideLoading();
        console.log('after update,onload',that.data.vip, app.globalData.currentvip)
        wx.navigateBack({
          delta: 1
        })

        // mythis.setData({
        //   // returndata: res.data.results
        // })
      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")


      }

    })
  }

})