// todolist/crmcase/crmcase.js

var sliderWidth = 96; // 需要设置slider的宽度，用于计算中间位置
var app = getApp();
var host = app.globalData.host;
var company = app.globalData.company;
var storecode = app.globalData.storecode;
var ecode = app.globalData.ecode;
var util = require('../../utils/util.js')
var viputil = require('../../vip/viputils.js');

Page({

  /**
   * 页面的初始数据
   */

  data: {
    vips:[],
    crmcases:[],
    crmcase10list:[],
    crmcase20list:[],
    crmcase30list:[],
    index: 0,
    planbegindate: '2019-03-01',
    time: '12:00',
    host:'',
    tabs: ["未完成", "已完成", "全部"],
    activeIndex: 0,
    sliderOffset: 0,
    sliderLeft: 0,
    parent:'crmcase'  

  },
  getNowTime: function(){
    var now = new Date();
    var year = now.getFullYear();
    var month = now.getMonth() + 1;
    var day = now.getDate();
    if(month < 10) {
      month = '0' + month;
    };
    if(day < 10) {
      day = '0' + day;
    };
    //  如果需要时分秒，就放开
    // var h = now.getHours();
    // var m = now.getMinutes();
    // var s = now.getSeconds();
    var formatDate = year + '-' + month + '-' + day;
    console.log(formatDate)
    this.setData(
      {
        planbegindate: formatDate
      }
    )
    return formatDate;
  },

  getCrmCase: function (options) {
    var app = getApp();
    var status = options
    var host = app.globalData.host;
    var company = app.globalData.company;
    var storecode = app.globalData.storecode;
    var ecode = app.globalData.ecode;
    var that = this;

    var bytype ='crmcase';
    var url = host + "crm/get_crmcaselist/";
    console.log(url);
    wx.request({
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        storecode: storecode,
        ecode: ecode,
        planbegindate: that.data.planbegindate,
        status: status,
        bytype: bytype
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        if (status='10'){
          that.setData({
            crmcase10list: res.data
          })
        }
        if (status='20'){
          that.setData({
            crmcase20list: res.data
          })
        }
        if (status='30'){
          that.setData({
            crmcase30list: res.data
          })
        }       
      }
    }); 
  },
  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    if (options.parent = 'vip'){
      var vipuuid = options.vipuuid
    };

    var app = getApp();
    this.getNowTime();    
    var that = this;
    wx.getSystemInfo({
      success: function (res) {
        that.setData({
          host: app.globalData.host,
          sliderLeft: (res.windowWidth / that.data.tabs.length - sliderWidth) / 2,
          sliderOffset: res.windowWidth / that.data.tabs.length * that.data.activeIndex
        });
        that.getCrmCase10()
        that.getCrmCase20()
        that.getCrmCase('30')
      }
    });
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {
    console.log('on ready')
    // this.getCrmCase()
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
  bindPickerChange: function (e) {
    console.log('picker发送选择改变，携带值为', e.detail.value)
    this.setData({
      index: e.detail.value
    })
  },
  bindPlanBeginDateChange: function (e) {
    var that = this;
    console.log('e.detail:',e.detail);
    that.setData({
      planbegindate: e.detail.value
    });
    that.getCrmCase();
  },
  bindTimeChange: function (e) {
    var that = this;
    that.setData({
      time: e.detail.value
    });
    that.getCrmCase();
  },
  tabClick: function (e) {
    var that=this
    that.setData({
      sliderOffset: e.currentTarget.offsetLeft,
      activeIndex: e.currentTarget.id
    });
    if (e.currentTarget.id='0'){
      that.getCrmCase10()
    }
    if (e.currentTarget.id='1'){
      that.getCrmCase20()
    } 
    if (e.currentTarget.id='2'){
      that.getCrmCase30()
    }   
    console.log(e)

  },
  onClickFinished: function(e){
    console.log('e',e)
    var that = this;
    var crmcaseuuid = e.currentTarget.id;    
    var url = that.data.host + 'crm/update_crmcase/';
    console.log(url)
    wx.request({
      method:'GET',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        crmcaseuuid: crmcaseuuid,
        status: '20'
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success(res) {
        console.log(res.data)
        that.getCrmCase('10')
      }
    });
  },
  queryconsume: function(e){
    var vipuuid = e.currentTarget.id;   
    
    console.log('e:',e,'vipuuid:',vipuuid)    
    wx.navigateTo({
      url: '../../vip/consumequery/consumequery?vipuuid='+vipuuid
    });
  },
  querycrmcasedetail: function(e){
    var vipuuid = e.currentTarget.id;

    console.log('e:', e, 'vipuuid:', vipuuid)
    wx.navigateTo({
      url: '../../vip/crmcasedetailquery/crmcasedetailquery?vipuuid=' + vipuuid
    });  
  },
  getCrmCase10: function () {
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company;
    var storecode = app.globalData.storecode;
    var ecode = app.globalData.ecode;
    var mythis = this;
    var bytype ='crmcase';
    var url = host + "crm/get_crmcaselist/";
    console.log(url);
    wx.request({
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        storecode: storecode,
        ecode: ecode,
        planbegindate: mythis.data.planbegindate,
        status: '10',
        bytype: bytype
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        mythis.setData({
          crmcase10list: res.data
        })
      }
    });
 
  },
  getCrmCase20: function () {
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company;
    var storecode = app.globalData.storecode;
    var ecode = app.globalData.ecode;
    var mythis = this;
    var bytype ='crmcase';
    var url = host + "crm/get_crmcaselist/";
    console.log(url);
    wx.request({
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        storecode: storecode,
        ecode: ecode,
        planbegindate: mythis.data.planbegindate,
        status: '20',
        bytype: bytype        
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        mythis.setData({
          crmcase20list: res.data
        })
      }
    });
    wx.request({
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        storecode: storecode,
        ecode: ecode,
        planbegindate: mythis.data.planbegindate,
        status: '30',
        bytype: bytype        
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        mythis.setData({
          crmcase30list: res.data
        })
      }
    })
 
  },
  getCrmCase30: function () {
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company;
    var storecode = app.globalData.storecode;
    var ecode = app.globalData.ecode;
    var mythis = this;
    var bytype ='crmcase';
    var url = host + "crm/get_crmcaselist/";
    console.log(url);
    wx.request({
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        storecode: storecode,
        ecode: ecode,
        planbegindate: mythis.data.planbegindate,
        status: '30',
        bytype: bytype        
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        mythis.setData({
          crmcase30list: res.data
        })
      }
    })
 
  },
})