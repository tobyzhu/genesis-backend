var util = require('../../utils/util.js');

Page({

  /**
   * 页面的初始数据
   */
  data: {
    isLogin:false,
    isDev:false,
    company:'',
    storecode:'',
    ecode:'',
    ename:'',

    viplist:[],
    empllist:[],
    roomlist:[],
    instrumentlist:[],
    srvlist:[],
    goodslist:[],
    cardtype:[],
    goodsdisplay:[],
    serviecedisplay:[],
    cardtypedisplay:[],
    ssid:'',
    pwd:'',
    bssid:'',
    brand:'',
    model:'',
    code:''

  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app=getApp();
    var that=this;
    that.setData({
      company:app.globalData.company,
      storecode:app.globalData.storecode,
      ecode:app.globalData.ecode,
      isLogin:app.globalData.isLogin,
      isDev:app.globalData.isDev,
      bssid_flag: app.globalData.bssid_flag,
      network_allow_flag: app.globalData.network_allow_flag,
      networkType: app.globalData.networkType,
      local_BSSID: app.globalData.local_BSSID


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
  clearCache:function(){
    var that=this;
    var app=getApp();
    try {
      wx.clearStorageSync()
      console.log('clear finished')
    } catch (e) {
      console.log(e)
      // Do something when catch error
    }
  },
  updateCache: function(){
    util.get_pmcodelist()
    util.get_seccodelist()
    util.get_amountcardtypelist()
    util.get_timescardtypelist()
    util.get_periodcardtypelist()
    util.get_VipList()
    util.get_SrvList()
    util.get_GoodsList()
    util.get_RoomList()
    util.get_InstrumentList()
    util.get_Vip10List()
    util.get_Vip20List()
    util.get_Vip30List()
    util.get_VipInList()
    util.get_VipNotinList()
  },

  getVipList: function(){
    // this.getNowTime()
    var app = getApp();
    var host = app.globalData.host;
    // var company = app.globalData.company
    var mythis = this;
    var url = host + "baseinfo/get_viplist_byecode/";
    // var url = host + "baseinfo/vip/";
    console.log(url);
    wx.request({
      method:'GET',
      url: url, 
      data: {
        company: app.globalData.company,
        ecode: app.globalData.ecode
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        console.log('res.data:',res.data)
        mythis.setData({
          viplist: res.data
        })
        wx.setStorage({
          key: 'viplist',
          data: mythis.data.viplist
        })
      },
      fail(res){
        // console.log(data)
        console.log(res)
      }
    });
  },
  getRoomList: function () {
    // this.getNowTime()
    var app = getApp();
    var host = app.globalData.host;
    // var company = app.globalData.company
    var mythis = this;
    var url = host + "baseinfo/get_roomlist/";
    // var url = host + "baseinfo/vip/";
    console.log(url);
    wx.request({
      method: 'GET',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        console.log('res.data', res.data)
        mythis.setData({
          roomlist: res.data
        })
        wx.setStorage({
          key: 'roomlist',
          data: mythis.data.roomlist
        })
      }
    });

  },
  getInstrumentList: function () {
    // this.getNowTime()
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company
    var mythis = this;
    var url = host + "baseinfo/get_instrumentlist/";
    // var url = host + "baseinfo/vip/";
    console.log(url);
    wx.request({
      method: 'GET',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        console.log('res.data', res.data)
        // mythis.setData({
        //   instrumentlist: res.data
        // })
        wx.setStorage({
          key: 'instrumentlist',
          // data: mythis.data.instrumentlist
          data: res.data
        })
      }
    });

  },

  getEmplList:function(){
    // this.getNowTime()
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company
    var that = this;
    console.log('getEmplList')
    that.get_pmcodelist();
    that.get_seccodelist();
   

  },

  get_pmcodelist :function() {
    var that=this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_pmcodelist/';
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log('res.data.results:', res.data)
        // console.log('res.data.results',res.data[0-99])
        that.setData({
          pmcodelist: res.data
        })
        console.log('2', that.data);
        wx.setStorage({
          key: 'pmcodelist',
          data: that.data.pmcodelist
        })

      },
      fail: function (res) {
        console.log("failed")

        // return []
      },
      complete: function (res) {
        console.log("finished")
      }
    });
  } ,


  get_seccodelist: function () {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_seccodelist/';
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log('res.data.results:', res.data)
        // console.log('res.data.results',res.data[0-99])
        that.setData({
          seccodelist: res.data
        })
        console.log('2', that.data);
        wx.setStorage({
          key: 'seccodelist',
          data: that.data.seccodelist
        })

      },
      fail: function (res) {
        console.log("failed")

        // return []
      },
      complete: function (res) {
        console.log("finished")
      }
    });
  },

  getSrvList: function () {
    // this.getNowTime()
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company
    var mythis = this;
    var url = host + "baseinfo/serviece/";
    // var url = host + "baseinfo/vip/";
    console.log(url);
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: company,
        ecode: app.globalData.ecode
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        // pages=xxx  res.data.results
        console.log('res.data.results:', res.data.results)
        // console.log('res.data.results',res.data[0-99])
        mythis.setData({
          srvlist: res.data.results
        });
        // app.globalData.srvlist = res.data.results;
        wx.setStorage({
          key: 'srvlist',
          data: mythis.data.srvlist
        })
      }
    });
  },  
  getGoodsList: function () {
    // this.getNowTime()
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company
    var mythis = this;
    var url = host + "baseinfo/goods/";
    // var url = host + "baseinfo/vip/";
    console.log(url);
    wx.request({
      method: 'GET',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        ecode: app.globalData.ecode
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      success(res) {
        console.log('res.data.results:', res.data.results)
        // console.log('res.data.results',res.data[0-99])
        mythis.setData({
          goodslist: res.data.results
        })
        wx.setStorage({
          key: 'goodslist',
          data: res.data.results
          // data: mythis.data.goodslist
        })
      }
    });
  },    
  getCardtypeList: function (options) {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_cardtypelist';
    var suptype = '10';
    var cardtypekey='cardtype'+suptype+'list'
    wx.request({
      url: url,
      data: {
        company: app.globalData.company,
        suptype: suptype
      },
      method: 'GET',
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log('res.data:', res.data)
        // console.log('res.data.results',res.data[0-99])
        // that.setData({
        //   [cardtypekey]: res.data.results
        // })
        console.log('2', that.data);
        wx.setStorage({
          key: 'cardtype10list',
          data: res.data
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

  get_itemdisplay:function(){
    var that=this;
    var app=getApp();
    var ttypes=['goods','serviece','cardtype']
    that.get_itemdisplaybyttype('goods')
    that.get_itemdisplaybyttype('serviece')
    that.get_itemdisplaybyttype('cardtype')
  },

  get_itemdisplaybyttype: function (options) {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_brandlist'
    var ttype =options;
    // if (ttype =='goods'){
    //   var itemlength = that.data.goodsdisplay.length
    // };
    // if (ttype == 'serviece') {
    //   var itemlength = that.data.serviecedisplay.length
    // };
    // if (ttype == 'cardtype') {
    //   var itemlength = that.data.cardtypedisplay.length
    // };    
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        type: ttype
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        var key = ttype + 'display'
        that.setData({
          [key]: res.data
        })
      
        for (var i = 0; i < res.data.length; ++i) {
          console.log('i=',i)
          if (ttype == 'goods') {
            var brand = that.data.goodsdisplay[i].code
          }
          if (ttype == 'serviece') {
            var brand = that.data.serviecedisplay[i].code
          }
          if (ttype == 'cardtype') {
            var brand = that.data.cardtypedisplay[i].code
          }

          var options = {
            item: i,
            ttype: ttype,
            brand: brand
          }
          // console.log('get_displayclassbybrand, options=',options)
          that.get_displayclassbybrand(options)

        };
 
      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }
    })
  },

  get_displayclassbybrand: function (options) {
    console.log('get_goodsdisplayclass options:', options)
    var that = this;
    var app = getApp();
    var item = options.item
    var ttype = options.ttype;
    var brand = options.brand;
    var url = app.globalData.host + 'baseinfo/get_displayclass_bybrand'
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        type: ttype,
        brand: brand,
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        // console.log('get displayclass by brand:', res.data)
        var key = ttype+'display['+item+'].displayclass'
        // console.log('key:',key)
        that.setData({
          [key]: res.data
        })

        // console.log('ttype=', ttype)
        if (ttype == 'serviece') {
          wx.setStorage({
            key: 'serviecedisplay',
            data: that.data.serviecedisplay,
          })
        };
        if (ttype == 'goods') {
          // console.log('goods,?ttype=', ttype, that.data.goodsdisplay)
          wx.setStorage({
            key: 'goodsdisplay',
            data: that.data.goodsdisplay,
          })
        };
        if (ttype == 'cardtype') {
          wx.setStorage({
            key: 'cardtypedisplay',
            data: that.data.cardtypedisplay,
          })
        };
      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }
    })
  },

  getCache: function(){
    var that = this;
    wx.getStorage({
      key: 'viplist',
      success: function (res) {
        console.log('3',res.data),
        that.globalData.viplist = res.data
      }
    })     
  },

  getWifiInfo: function(){
    var that = this;
    wx.getConnectedWifi({
      WifiInfo:{
      },
      success:function(res){
        console.log(res.wifi.SSID),
        console.log(res.wifi.BSSID),
        that.setData({
          ssid: res.wifi.SSID,
          bssid: res.wifi.BSSID
        })
      },
      fail:function(res){
        console.log(res)
      },
      complete:function(res){
        console.log(res)
      }
    })
    wx.getSystemInfo({
      success: function(res) {
        console.log(res.brand),
        console.log(res.model),
        that.setData({
          model:res.model,
          brand:res.brand
        })
      },
    })
  },

  getUserInfo:function(){
    var app=getApp();
    var that=this;
    var host = app.globalData.host;
    var code='';
    wx.login({
      success(res) {
        console.log('res.code:',res.code)
        if (res.code) {
          // 发起网络请求
          wx.request({
            url: host+'my/login/login',
            data: {
              code: res.code
            }
          })
        } else {
          console.log('登录失败！' + res.errMsg)
        }
      }
    })
    wx.request({
      method:'GET',
      url: '',
      appid:'',
      secret:'',
      js_code:that.data.code,
      grant_type:'authorization_code'
    })

  },
  
  soterAuthentication: function(){
    wx.checkIsSupportSoterAuthentication({
      success(res) {
        console.log(res)
        // res.supportMode = [] 不具备任何被SOTER支持的生物识别方式
        // res.supportMode = ['fingerPrint'] 只支持指纹识别
        // res.supportMode = ['fingerPrint', 'facial'] 支持指纹识别和人脸识别
      }
    });
    wx.checkIsSoterEnrolledInDevice({
      checkAuthMode: 'fingerPrint',
      success(res) {
        console.log(res,res.isEnrolled)
      }
    });

    wx.startSoterAuthentication({
      requestAuthModes: ['fingerPrint'],
      challenge: '123456',
      authContent: '请用指纹解锁',
      success(res) {
        console.log(res)
      }
    })
  }



})