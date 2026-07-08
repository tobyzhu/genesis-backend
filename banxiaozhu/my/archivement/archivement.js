var util = require('../../utils/util.js')

Page({
  data: {
    company: '',
    storecode: '',
    ecode: '',
    ename: '',
    isLogin: false,
    thismonth:'',
    thismonth_vipcnt:0,
    thismonth_viptimes:0,
    thismonth_yeji:0,
    thismonth_shihao:0,
    thismonth_shichao:0,
    thismonth_emplarch: [],

    lastmonth:'',
    lastmonth_vipcnt:0,
    lastmonth_viptimes:0,
    lastmonth_yeji:0,
    lastmonth_shihao:0,
    lastmonth_shichao:0,
    lastmonth_emplarch:[]

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that=this;
    var app=getApp();
    that.setData({
      company:app.globalData.company,
      storecode:app.globalData.storecode,
      ecode:app.globalData.ecode
    })
    util.get_emplarch_bymonth(that)

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
  init_emplarch:function(){
    var that=this;
    var app=getApp()
    var today = new Date();


    console.log('today ',today.toDateString())

    var thisyear = today.getFullYear();
    // var thismonth = today.getMonth() +1
    var thismonth = util.getMonth(today);
    console.log('this month=',thismonth)


    // var thisday = today.getDate();
    if (today.getMonth()==1){
      var lastyear = (thisyear -1).toString()
      var lastmonth = lastyear + '12'
      console.log(lastmonth)

    } else {
      var lastyear = thisyear.toString()
      var lastmonth = today.getMonth()
      if (lastmonth<9){
        lastmonth =lastyear+'0'+lastmonth
        console.log(lastmonth)
      }
    }

    var url = app.globalData.host + "cashier/get_emplarch_bymonth/";
    // var url = host + "baseinfo/vip/";
    console.log(url);
    wx.request({
      method: 'GET',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        ecode: app.globalData.ecode,
        month: thismonth
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        that.setData({
          thismonth: thismonth,
          thismonth_emplarch: res.data
        })
        var vipcnt = 0
        var viptimes = 0
        var yeji = 0
        var shihao = 0
        for (var item in that.data.thismonth_emplarch){
          vipcnt = vipcnt + that.data.thismonth_emplarch[item].vipcnt
          viptimes = viptimes + that.data.thismonth_emplarch[item].viptimes  
          yeji = yeji + Number(that.data.thismonth_emplarch[item].yejiamount)
          shihao = shihao + Number(that.data.thismonth_emplarch[item].shihao )               
        }
        that.setData({
          thismonth_vipcnt: vipcnt,
          thismonth_viptimes: viptimes,
          thismonth_yeji: yeji.toFixed(2),
          thismonth_shihao: shihao.toFixed(2)

        })

      }
    });

    wx.request({
      method: 'GET',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        ecode: app.globalData.ecode,
        month: lastmonth
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        that.setData({
          lastmonth:lastmonth,
          lastmonth_emplarch: res.data
        })
      }
    });

  },
  sum_emplarch: function(){

  }
})