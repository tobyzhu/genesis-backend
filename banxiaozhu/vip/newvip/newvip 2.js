// vip/newvip/newvip.js
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({

  /**
   * 页面的初始数据
   */
  data: {
    vipTypeList:[
      {
        value:'10',
        title:'会员'
      },
      {
        value:'20',
        title:'非会员'
      },
      {
        value:'30',
        title:'潜在客户'
      }
    ],
    vip:{},
    vipuuid:'',
    viptype:'',
    viptypeindex: 0,
    vcode: '',
    vname: '',
    mtcode: '',
    birthday: '2000-01-01',
    indate:'',
    value1: '',
    title1: '',
    value2: '',
    title2: '',
    value3: '',
    title3: '',
    sourcetitle:'',
    sourcevalue:'',
    pmcode:'',
    pmname:'',
    seccode:'',
    secname:'',
    nextvcode:'',
    viplevel:'C',
    pmcodelist:[],
    seccodelist:[],
    source:[],
    sourceindex:-1,
    sourceid:'',   
    sourcename:'' ,
    vdesc:''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp();
    var that=this;

    // that.get_ecodelist();
    that.setData({
      indate: util.getToday(),
      pmcode:app.globalData.ecode,
      pmcodelist: app.globalData.pmcodelist,
      seccodelist: app.globalData.seccodelist,
      source: app.globalData.sourcelist,
    })
    console.log(app.globalData.sourcelist,that.data.source)
    // that.get_vipsource();
    // that.setData({
    //   pmcode: app.globalData.ecode
    // })
    // 数组对象查找
    var ecode = app.globalData.ecode
    viputils.getIndexByCode(that,{ type: 'pmcode', code: ecode })

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

  bindViptypeChange: function (e) { 
    console.log(e)
    var that=this;
    var vipType = that.data.vipTypeList[e.detail.value]
    // if (vipType.value == '10') {
    //   that.get_nextvcode()
    // }
    that.setData({
      index: e.detail.value,
      viptype: vipType.value
    })

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

  bindPmcodeChange: function (e) {
    var that = this;
    viputils.bindPmcodeChange(that, e)
  },
  bindSeccodeChange: function (e) {
    var that = this;
    viputils.bindSeccodeChange(that, e)
  },
  // bindPmcodeChange: function(e){
  //   var that = this;
  //   console.log(e, that.data.pmcodelist[e.detail.value].ename )
  //   this.setData({
  //     pmcode: that.data.pmcodelist[e.detail.value].ecode,
  //     pmname: that.data.pmcodelist[e.detail.value].ename
  //   })
  // },
  // bindSeccodeChange: function (e) {
  //   var that=this;
  //   console.log(e)
  //   this.setData({
  //     seccode: that.data.seccodelist[e.detail.value].ecode,
  //     secname: that.data.seccodelist[e.detail.value].ename
  //   })
  // },
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
    var that=this;
    console.log(e.detail.value)
    that.setData({
      vdesc: e.detail.value
    })
  },

  addNewVip:function(e){
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company
    var storecode = app.globalData.storecode
    var ecode = app.globalData.ecode    
    var that = this;
    // var url = host + 'baseinfo/vip/'
    var url = host + 'baseinfo/create_vip/'
    // var source = that.data.sourceid
    var viptype = that.data.viptype
    var xinqu = JSON.stringify(that.data.title3)
    var occupation = that.data.occupation
    var vcode = that.data.vcode
    if (vcode.length == 0) {
      vcode= null
    }
    wx.showLoading({
      title:'数据提交中'
    })
    wx.request({
      method:'GET',
      url: url,
      data: { 
        company: company,
        storecode: storecode,
        viptype: that.data.viptype,
        vcode: that.data.vcode,
        vname: that.data.vname,
        mtcode: that.data.mtcode,
        birthday: that.data.birthday,
        ecode: that.data.pmcode,
        ecode2: that.data.seccode,
        source: that.data.sourceid,
        occupation: that.data.occupation,
        vdesc: that.data.vdesc,
        viplevel: that.data.viplevel
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log('res.data:',res.data)
        wx.hideLoading()
        // that.setData({
        //   vip: res.data,
        //   vipuuid: res.data.uuid
        // })
        that.setData({
          vip: res.data[0],
          vipuuid: res.data[0].uuid
        })       
        wx.showToast({
          title: '新增客户完成',
          icon: 'success',
          duration: 3000
        });
        util.get_VipList()
        if (that.data.viptype=='10'){
          util.get_Vip10List()
        }
        if (that.data.viptype=='20'){
          util.get_Vip20List()
        }
        if (that.data.viptype=='30'){
          util.get_Vip30List()
        }
        console.log('that.data.vip',that.data.vip)
        console.log('that.data.vipuuid',that.data.vipuuid)
        util.uuidtostr(that.data.vipuuid)
        wx.navigateTo({
          url: '../vip?uuid=' + util.uuidtostr(that.data.vipuuid),
        })   

      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }
    })
  },
  get_nextvcode: function(){
    var app = getApp();
    var that = this;
    var url = app.globalData.host +'baseinfo/get_nextvcode/';
    wx.request({
      method:'GET',
      url: url,
      data:{
        company:app.globalData.company,
        storecode:app.globalData.storecode,
        pmcode : that.data.pmcode
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res)
        if (res.data.length>32){

        }
        else{
          that.setData({
            nextvcode: res.data,
            vcode: res.data
          })
        }

      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }      
    }) 
  },
 

  get_vipsource:function(){
    var app=getApp()
    var that=this
    var url = app.globalData.host + 'baseinfo/get_appoption_byseg/'

    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        seg:'source'
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res)
        that.setData({
          source: res.data,
        })
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