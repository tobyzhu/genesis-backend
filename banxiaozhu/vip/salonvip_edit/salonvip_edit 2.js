// vip/salonvip_edit/salonvip_edit.js

var util = require('../../utils/util.js');
const { get_SalonVip } = require('../viputils.js');
var viputil = require('../viputils.js');
var app=getApp();
var host = app.globalData.host;
Page({


  data: {
    showTopTips: false,
    salonvip_uuid:'',
    vip: {},
    vipcasedetail:{},
    empllist:[],
    emplIndex:-1,
    nextemplIndex:-1,
    nextdate:'',
    ecode: '',
    inviter_ecode: '',
    inviter_ecode_index: -1,
    inviter_ecode_uuid: '',
    nextecode: '',
    salon_id: '',
    salon_code: '',
    salon_name: '',
    guest_name: '',
    guest_mobile: '',
    description: '',
    vipuuid: '',
    salonlist:[],
    salonlistindex: -1,
    // salonListcvipcasetype:'',
    salonvip:{
      'uuid':'',
      'inviter_ecode_id':'',
      'salon_id':'',
      'salon_code':'',
      'salon_name':'',
      'guest_name':'',
      'guest_mobile':'',
      'vipuuid_id':'',
      'description':'',
      'status':'BOOKING',
    },
    description: '',
    salonvip_status: '',
    salonvip_status_list: [],
    salonvip_status_index: 0,
    inviter_date: '',
    summary: '',
    summary_ecode: '',
    summary_ecode_index: 0,
    vipcnt: 1,
    vipcntlist:[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20],
    vipcntlistindex:1,
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    console.log('salonvip_edit onload options',options)

    that.setData({
      ecode: app.globalData.ecode,
      vip: app.globalData.currentvip,
      vipuuid: app.globalData.currentvip.uuid,
      empllist: app.globalData.empllist,
      salonlist: app.globalData.salonlist,
      salonvip_status_list: app.globalData.salonvip_status_list,
      guest_name: app.globalData.currentvip.vname,
      guest_mobile: app.globalData.currentvip.mtcode
      // salonvip2: options.item
    })
    // that.data.salonvip.mtcode=that.data.guest_mobile

    if (options.vipuuid){
      viputil.getVipBaseInfo(that,options)
      that.setData({
        inviter_ecode_id :'',
        guest_name: that.data.vip.vname,
        guest_mobile: that.data.vip.mtcode

      })
    }

    console.log('options.salonvip_uuid',options.salonvip_uuid)
    if (options.salonvip_uuid){
      that.setData({
        salonvip_uuid: options.salonvip_uuid,
        guest_name: that.data.vip.vname
      })
      that.get_SalonVipDetail(options.salonvip_uuid)
      var empluuid = that.data.inviter_ecode_uuid
      var param = {
        type: 'empluuid',
        code: empluuid
      }
      if (empluuid) {
        console.log(ecode,'empl param:',param)
        viputil.getIndexByCode(that, param)

        that.setData({
          inviter_ecode_index: that.data.emplIndex, 
          // inviter_ecode: that.data.
        })
        that.setData({
          // inviter_empl_index:that.data.emplIndex,
          inviter_ecode: that.data.empllist[that.data.inviter_ecode_index].ecode,
          inviter_ecode_uuid: that.data.empllist[that.data.inviter_ecode_index].uuid
        })
      }

      var ecode = that.data.summary_ecode
      var param = {
        type: 'empl',
        code: ecode
      }
      if (ecode) {
        console.log(ecode,'empl param:',param)
        viputil.getIndexByCode(that, param)
        that.setData({
          summary_ecode_index:that.data.emplIndex,
          summary_ecode: that.data.ecode,
          summary_ecode_uuid: that.data.empllist[that.data.emplIndex].uuid
        })
      }
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
  bindSalonVipStatusChange:function(e){
    console.log('picker bindSalonVipStatusChange 发生选择改变，携带值为', e.detail.value);
    var that = this;
    if (e.detail.value >= 0) {
      that.setData({
        salonvip_status_index: e.detail.value,
        salonvip_status: that.data.salonvip_status_list[e.detail.value].code
      })
    }
  },
  bindSalonChange: function (e) {
    console.log('picker salonlist 发生选择改变，携带值为', e.detail.value);
    var that = this;
    if (e.detail.value>=0){
      that.setData({
        salonlistindex: e.detail.value,
        salon_id: that.data.salonlist[e.detail.value].uuid
        // salonvip.salon_id: that.data.salonlist[e.detail.value].uuid
      })
      // that.setData({
      //   salonvip.salon_id: that.data.salonlist[salonlistindex].uuid
      // })
    }
  },

  bindGuestNameChange:function(e){
    console.log('bindguestnamechange',e)
    var that = this;
    if (e.detail.value){
      that.setData({
        guest_name : e.detail.value
      })
    }
  },

  bindGuestMobileChange:function(e){
    console.log('bindguestmobilechange',e)
    var that = this;
    if (e.detail.value){
      that.setData({
        guest_mobile : e.detail.value
      })
    }
  },
  bindInviterDateChange:function(e){
    console.log('bindInviterDatechange',e)
    var that = this;
    if (e.detail.value){
      that.setData({
        inviter_date : e.detail.value
      })
    }
  },


  bindDescriptionChange:function(e){
    console.log('binddescriptionchange',e)
    var that = this;
    if (e.detail.value){
      that.setData({
        description : e.detail.value
      })
    }
  },

  bindInviterEmplChange: function (e) {
    console.log('picker empl 发生选择改变，携带值为', e.detail.value);
    var that = this;
    if (e.detail.value>=0){
      that.setData({
        inviter_ecode_index: e.detail.value,
        inviter_ecode: that.data.empllist[e.detail.value].ecode,
        inviter_ecode_uuid: that.data.empllist[e.detail.value].uuid
      })
    }
  },

  bindSummaryEmplChange: function (e) {
    console.log('picker summary empl 发生选择改变，携带值为', e.detail.value);
    var that = this;
    if (e.detail.value >= 0) {
      that.setData({
        summary_ecode_index: e.detail.value,
        summary_ecode: that.data.empllist[e.detail.value].ecode
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

  bindSummaryChange: function (e) {
    var that = this;
    console.log(e)
    that.setData({
      summary: e.detail.value
    })
  },
  bindVipcntChange: function(e){
    var that=this;
    console.log(e);
    var index = e.detail.value
    console.log("index",index)
    that.setData({
      vipcnt: that.data.vipcntlist[index],
      vipcntlistindex: index
    })
  },

  updateSalonVip: function(e){
    var that=this;
    var url = host +'crm/update_salonvip'


    var param={
      company: app.globalData.company,
      storecode: app.globalData.storecode,
      salonvip_uuid: that.data.salonvip_uuid,
      vipcnt: that.data.vipcnt,
      empl_uuid: that.data.inviter_ecode_uuid,
      // salon_id: that.data.salonlist[that.data.salonlistindex].uuid,
      salon_id: that.data.salon_id,
      guest_name: that.data.guest_name,
      guest_mobile: that.data.guest_mobile,
      description: that.data.description,
      status: that.data.salonvip_status_list[that.data.salonvip_status_index].code,
      vipuuid: that.data.vip.uuid,
      inviter_date: that.data.inviter_date,
      summary: that.data.summary,
      summary_ecode: that.data.summary_ecode
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
        
        wx.navigateBack({
          delta: 1
        })

      },
      fail: function (res) {
        console.log("failed", res )
      },
      complete: function (res) {
        console.log("finished", res )
      }
    });
  },

  get_SalonVipDetail: function(options) {
    console.log('getsalonvip option',options)
    var that = this;
    var company = app.globalData.company;
    var storecode = app.globalData.storecode;
    var salonvip_uuid = options
    var url = app.globalData.host + 'crm/get_salonvip_detail/';
    console.log(url)
    wx.showLoading({
      title: '数据加载中',
    })
    wx.request({
      method: 'GET',
      url: url, 
      data: {
        company: company,
        storecode: storecode,
        salonvip_uuid: salonvip_uuid
      },
      header: {
        // 'content-type': 'application/json' // 默认值
        'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success(res) {
        console.log('salonvip res, res.data:',res, res.data)
        // setTimeout(200)
        that.setData({
          salonvip: res.data[0]
        })

        var param = {
          type: 'salonvip_status',
          code: res.data[0].status
        }

        if (res.data[0].status) {
          viputil.getIndexByCode(that, param)
          that.setData({
            salonvip_status_index:that.data.salonvip_status_index,
            // salonvip_status: that.data.salonvip.status
          })
        }

        var param = {
          type: 'salonlist',
          code: res.data[0].salon_id
        }
        console.log('param', param )
        if (res.data[0].status) {
          viputil.getIndexByCode(that, param)
        }   
 
        var param = {
          type: 'empl',
          code: res.data[0].summary_ecode
        }
        console.log('param', param )
        if (res.data[0].status) {
          viputil.getIndexByCode(that, param)
          that.setData({
            summary_ecode_index: that.data.emplIndex
          })
        }           
        console.log('that.data.salonvip',that.data.salonvip)
        that.setData({
          salonvip_uuid: options,
          salon_id: that.data.salonvip.salon_id,
          vipuuid: that.data.salonvip.vipuuid_id,
          vipcnt: that.data.salonvip.vipcnt,
          vipcntlistindex: that.data.salonvip.vipcnt,
          description: that.data.salonvip.description,
          inviter_ecode_uuid: that.data.salonvip.inviter_ecode_id,
          inviter_date: that.data.salonvip.inviter_date,
          summary: that.data.salonvip.summary,
          summary_ecode: that.data.salonvip.summary_ecode
        })
        console.log('that.data.vipcnt',that.data.vipcnt,that.data.salonvip.vipcnt)
      },
      complete(res){

        var empluuid = that.data.inviter_ecode_uuid
        var param = {
          type: 'empluuid',
          code: empluuid
        }
        if (empluuid) {
          console.log(empluuid,'empluuid param:',param)
          viputil.getIndexByCode(that, param)

          that.setData({
            inviter_ecode_index: that.data.emplIndex, 
            // inviter_ecode: that.data.
          })
          that.setData({
            // inviter_empl_index:that.data.emplIndex,
            inviter_ecode: that.data.empllist[that.data.inviter_ecode_index].ecode,
            inviter_ecode_uuid: that.data.empllist[that.data.inviter_ecode_index].uuid
          })
      }
    
        wx.hideLoading()
      }

    });
  }

})