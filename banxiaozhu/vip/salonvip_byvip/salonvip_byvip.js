var app=getApp()
var appcode=app.globalData.appcode;
var host = app.globalData.host;
var company = app.globalData.company;
var util = require('../../utils/util.js');
var viputil = require('../viputils.js');

Page({
  data: {
    vip:{},
    vipuuid_s:'',
    salonviplist:[],
    salonlist:[],
    right: [
      {
        text:'修改',
        style: 'background-color: #108ee9; color: white',
      },
      {
        text: '删除',
        style: 'background-color: #F4333C; color: white',
      }],
  },
  onLoad: function (options) {
    var that =this;

    console.log('salonvip onload',options)
    if (options.vipuuid){
      viputil.getVipBaseInfo(that,options)

    } else{
      var vip = app.globalData.currentvip;
      that.setData({
        vip:app.globalData.currentvip,
        vipuuid_s: app.globalData.currentvipuuid_s
      })
    }
    if (viputil.getVipBaseInfoCallback){
      console.log('callback ')
    }

    // var vip = that.data.vip;
    // console.log('vip.uuid',that.data.vip.uuid)
    // var params ={
    //   type:  'vip',
    //   vipuuid: that.data.vip.uuid
    // }
    // viputil.get_SalonVipList(that, params)
  },


  onReady: function () {

  },

  /**
   * 生命周期函数--监听页面显示
   */
  onShow: function () {
    var that=this;
    var vip = that.data.vip;
    console.log('vip.uuid',that.data.vip.uuid)
    var params ={
      type:  'vip',
      vipuuid: that.data.vip.uuid
    }
    viputil.get_SalonVipList(that, params)
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
    console.log('onPullDOwnRefresh')
    var that=this;
    that.get_SalonVip(that.data.vip.uuid)
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
  
  bindNewSalonVip:function(){
    var that=this;
    var url="../salonvip_edit/salonvip_edit" 
    wx.navigateTo({
      url: url,
      vipuuid: that.data.vipuuid
    })
  },

  onSalonVipClick: function(e){
    var app=getApp();
    var that=this;
    console.log('onSalonVipClick e',e)
    var index=e.detail.index
    var text=e.detail.value.text
    var salonvip_uuid = e.currentTarget.id
    console.log('index=',index,'text=',text,'uuid=',salonvip_uuid)
    if (index==1){
      console.log(text,'delete')
      var params={
        oper:'delete',
        company:app.globalData.company,
        storecode:app.globalData.storecode,
        ecode:app.globalData.ecode,
        salonvip_uuid:salonvip_uuid
      }
      that.delete_SalonVipItem(params)
    }
    if (index==0){
      console.log(text,'修改','salonvip_uuid=',salonvip_uuid)
      wx.navigateTo({
        url: '../salonvip_edit/salonvip_edit?salonvip_uuid='+salonvip_uuid,
      })     
    }

  },

  delete_SalonVipItem:function(options){
    var app=getApp();
    var that=this;
    var params = options;
    // var url = app.globalData.host + 'crm/delete_salonvip/?param=' + JSON.stringify(params)
    var url = app.globalData.host + 'crm/delete_salonvip'
    wx.request({
      method: 'GET',
      url: url,
      data: params,
      header: {
        // 'content-type': 'application/json' // 默认值
        'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        if (res.error) {
          wx.showToast({
            title: res.data.msg,
            icon: 'none',
            duration: 2000
          })
        }
        else {
          wx.showToast({
            title: res.data.msg,
            icon: 'success',
            duration: 2000
          })
          setTimeout(function () {
            // wx.navigateBack({
            //   delta: 1
            // })
          }, 2000)
        }
        var params={
          type:'vip',
          company: app.globalData.company,
          vipuuid: that.data.vip.uuid
        }
        viputil.get_SalonVipList(that,params)
      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }
    })

  },
  

})