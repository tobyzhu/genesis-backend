// vip/crmcasedetailquery/crmcasedetailquery.js
Page({

  /**
   * 页面的初始数据
   */
  data: {
    vip:{},
    vipuuid:'',
    crmcasedetaillist:[],
    parent:'preview'
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    var vipuuid = options.vipuuid;
    that.setData({
      vipuuid:vipuuid
    })
    console.log(options,vipuuid)
    that.get_vip_crmcasedetail(vipuuid)

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

  onReachBottom: function () {

  },

  onShareAppMessage: function () {

  },
  get_vip_crmcasedetail: function(options){
    var app = getApp();
    var that = this;
    var host = app.globalData.host;
    var company = app.globalData.company;
    var storeCode = app.globalData.storeCode;
    var vipuuid = options;
    var fromdate ='';
    var todate ='z'
    // var ecode = app.globalData.ecode;
    var that = this;
    var url = host + 'crm/get_vip_crmcasedetail/';
    console.log(that.data.vip)
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: company,
        vipuuid: vipuuid
        // fromdate:fromdate,
        // todate:todate

      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success: function (res) {
        console.log(res.data),
        that.setData({
          crmcasedetaillist: res.data
        })

      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("completed", res)
      }
    })
  } 
})