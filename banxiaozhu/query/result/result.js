var app=getApp()
var util = require('../../utils/util.js')
var wxCharts = require('../../utils/wxcharts.js');
var viputils = require('../../vip/viputils.js')
Page({

  /**
   * 页面的初始数据
   */
  data: {
    reportname:'',
    sub_reportname:'',
    url:'',
    param:{},
    result:{},
    testurl:'',
    reporttype:'',
    reportdata:[]
    // reportdata:[
    //     {itemname:'日期范围', value:'2020-12-02   2020-12-05'},
    //     {itemname:'客数',value:8},
    //     {itemname:'客次',value:9},
    //     {itemname:'项次',value:10},
    //     {itemname:'资金流水',value:9999}
    // ],

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {

    var that=this
    console.log('option',options)

    var url = app.globalData.reporturl
    var reporttype  = app.globalData.reporttype
    var param = app.globalData.param
    console.log('result onload,params,url ',url,param,reporttype, typeof(param))
    if (app.globalData.reporttype =='emplarch_sum') {
      var reportname ='员工业绩汇总'
    }

    
    that.setData({
      company:app.globalData.company,
      reporttype: reporttype, 
      param: param,
      reportname: reportname,
    })

    // `priceObj.${optionId}`
    for (var item in that.data.reportdata){
      var key = item.toString()
      // var value = 'item.${key}'
      console.log('item',item,key,that.data.reportdata[item])
      // that.setData({
      //   [key]:value
      // })
    }
    console.log('param',param) 
    util.commonrequest(that,url,param,'reportdata')
    console.log('url',that.data.url)
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
  onShareAppMessage: function (options) {
    console.log(options.webViewUrl)
  },
  onResize:function(res) {
    console.log(res)
    res.size.windowWidth // 新的显示区域宽度
    res.size.windowHeight // 新的显示区域高度
  }
})