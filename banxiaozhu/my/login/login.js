// my/login/login.js
var now = new Date();
var util = require('../../utils/util.js');
var viputils = require('../../vip/viputils.js');
var wxutils = require('../../utils/wxutils.js');

Page({
  data: {
    showTopTips:false,
    errormsg:'登陆时发生错误',
    storeList:[],
    company:'',
    companyname:'',
    networkType:'',
    wifi_flag: false,
    bssid_flag: false,
    network_allow_flag: false,
    network_disallow_flag: true,
    local_SSID:'',
    local_BSSID:'',
    wifiitem:{},
    storecode:'',
    storename:'',
    storeIndex: 0,
    usercode:'',
    username: '',
    password: '',
    last_login_time:'',
    isLogin: false,

    getPhoneNumber: function (e) {
      var app= getApp();
      var that = this;
      // console.log('e', e)
      // wxutils.getPhoneNumber(that,e)
  
      // var session_key = that.data.userinfo.session_key;
      var session_key = that.data.currentSessionKey;
      var msg = e.detail.errMsg;
      var encryptedDataStr = e.detail.encryptedData;
      var iv = e.detail.iv;
      console.log('msg=',msg)
      if (msg == 'getPhoneNumber:ok') {
        console.log('before wx.checkSession')
        wx.checkSession({
          success: function () {
            console.log('success', session_key)
            // that.deciyption(sessionID, encryptedDataStr, iv);
            that.deciyption(session_key, encryptedDataStr, iv);         
          },
          fail: function () {
            console.log('failed')
            wx.login({
              success: res => {
                console.log(res, 'sessionkey过期')
                var url = app.globalData.host + 'wechat/wechatlogin/'
                wx.request({
                  url : url, 
                  header: {
                    'content-type': 'application/x-www-form-urlencoded'
                  },
                  data: {
                    appcode:app.globalData.appcode,
                    code: res.code,
                    encryptedData: detail.encryptedData,
                    iv: detail.iv,
                    nickName: detail.userInfo.nickName,
                    avatarUrl: detail.userInfo.avatarUrl,
                    userInfo: detail.userInfo,
                  }, 
                  success:function (res) {
                    var userinfo = res.data.data;
                    wx.setStorageSync('userinfo', userinfo);
                    that.setData({
                      userinfo: userinfo
                    });
                    that.deciyption(userinfo.session_key, encryptedDataStr, iv);
                  },
                  fail:function(res){
                    console.log(res)
                  }
                })
              }
            })
          }
        })
      }
    },
  
    deciyption(session_key, encryptedData, iv) {
      var app=getApp();
      var that=this;
      var url = app.globalData.host + 'wechat/getphone'
      wx.request({
        method: 'GET',
        url: url,
        data: {
          appcode:app.globalData.appcode,
          encryptedData: encryptedData,
          iv: iv,
          session_key: session_key
        },
        header: {
          'content-type': 'application/json' // 默认值
          // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
        },
        success(res) {
          console.log('success',res)
          app.globalData.company = that.data.company
          app.globalData.storecode = that.data.storecode
          app.globalData.ecode = that.data.usercode
          app.globalData.usercode = that.data.usercode
          app.globalData.network_allow_flag = true
          app.globalData.network_disallow_flag = false
          that.save_Local()       
        },
        fail(res) {
          console.log('fail',res)
        },
      }) 
    },
  },


  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var app = getApp()
    var that = this
    that.get_Local()  
    // var userinfo = wx.getStorageSync('userinfo');
    if (app.globalData.isDev){
      that.setData({
        company: app.globalData.democompany,
        storecode: app.globalData.demostorecode,
        companyname: app.globalData.democompanyname,
        storename: app.globalData.demostorename,
        // local_SSID: app.globalData.demolocal_SSID,
        // local_BSSID: app.globalData.tempnetwork.local_BSSID,
        networkType: '4G',
        networkenable: true
        // bssid_flag: app.globalData.tempnetwork.bssid_flag

        // company: app.globalData.tempnetwork.company,
        // storecode: app.globalData.tempnetwork.storecode,
        // companyname: app.globalData.tempnetwork.companyname,
        // storename: app.globalData.tempnetwork.storename,
        // local_SSID: app.globalData.tempnetwork.local_SSID,
        // local_BSSID: app.globalData.tempnetwork.local_BSSID,
        // networkType: app.globalData.tempnetwork.networkType,
        // networkenable: app.globalData.tempnetwork.networkenable,
        // bssid_flag: app.globalData.tempnetwork.bssid_flag
        // userinfo:userinfo
      })
      console.log('login onLoad:',app.globalData.isDev, that.data.company, that.data.storecode, that.data.usercode)
    } else{
      that.setData({
        company: app.globalData.company,
        companyname: app.globalData.companyname,
        storecode: app.globalData.storecode,
        storename: app.globalData.storename,
        local_SSID: app.globalData.local_SSID,
        local_BSSID: app.globalData.local_BSSID,
        networkType:app.globalData.networkType,
        networkenable: app.globalData.networkenable,
        bssid_flag: app.globalData.bssid_flag
        // userinfo:userinfo
      })
    }
    // that.reWXLogin()
    // wxutils.wxLogin(that)
  },

  /**
   * 生命周期函数--监听页面初次渲染完成
   */
  onReady: function () {

  },

  onShow: function () {

  },

  onHide: function () {

  },

  onUnload: function () {

  },

  onPullDownRefresh: function () {
    var that = this
    console.log('begin PullDown')
    wx.showNavigationBarLoading()
    util.checkNetwork(that);
    setTimeout(() => {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    }, 2000);
    console.log('end PullDown')
  },

  onReachBottom: function () {

  },

  onShareAppMessage: function () {

  },
  bindUsercodeChange:function(e){
    var that=this;
    var app=getApp();
    console.log(e)
    that.setData({
      usercode:e.detail.value
    })
  },

  bindPasswordChange: function (e) {
    var that = this;
    var app = getApp();
    console.log(e)
    that.setData({
      password: e.detail.value
    })
  },

  showTopTips: function () {
    var that = this;
    this.setData({
      showTopTips: true
    });
    setTimeout(function () {
      that.setData({
        showTopTips: false
      });
    }, 3000);
  },

  userLogin: function(){
    var app = getApp();
    var that = this;

    if (that.data.company.length==0){
      that.setData({
        showTopTips:true,
        errormsg:'无使用权限！'
      })
      setTimeout(function () {
        that.setData({
          showTopTips: false
        });
      }, 3000);
    }
    // var netflag = that.checkNetwork()
    var url = app.globalData.host + 'common/check_userpwd'
    wx.request({
      method:'GET',
      url: url,
      data:{
        company: that.data.company,
        storecode: that.data.storecode,
        usercode: that.data.usercode,
        password: that.data.password
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success(res) {
        console.log('success login res',res)
        if (res.data==200){
          app.globalData.company = that.data.company
          app.globalData.storecode = that.data.storecode
          app.globalData.usercode=that.data.usercode
          app.globalData.ecode = that.data.usercode
          app.globalData.network_allow_flag=true
          app.globalData.network_disallow_flag=false
          that.save_Local()
          wx.reLaunch({
            url: '/index/index',
          })
        }
        if (res.data==500){
          var param={
            content:'用户名/密码不对!'
          }
          that.openAlert(param)
        }

      },
      fail: function (res) {
        console.log('fail login res', res);
        var tip =
          '无法连接服务器（超时或拒绝）。请核对 app.js 里 host 的 IP 是否为 192.168.x.x；' +
          '电脑执行 python manage.py runserver 0.0.0.0:8030；' +
          '防火墙放行 8030；手机与电脑同一 WiFi。';
        wx.showModal({
          title: '登录失败',
          content: ((res && res.errMsg) || 'request:fail') + '\n\n' + tip,
          showCancel: false
        });
      }
    })

    // app.globalData.company = that.data.company
    // app.globalData.storecode = that.data.storecode
    // app.globalData.ecode = that.data.usercode
    // app.globalData.usercode = that.data.usercode   
    // app.globalData.network_allow_flag = true
    // app.globalData.network_disallow_flag=false
    // that.save_Local()
    // console.log('success login res',res)
    // wx.reLaunch({
    //   url: '/index/index',
    // })

  },

  checkLogin: function () {
    var app = getApp();
    var that = this
    app.globalData.company = that.data.company
    app.globalData.storecode = that.data.storecode
    app.globalData.companyname = that.data.companyname
    app.globalData.storename = that.data.storename
    app.globalData.isLogin = that.data.isLogin
    app.globalData.usercode = that.data.usercode
    app.globalData.ecode = that.data.usercode
    console.log('login')
  },


  save_Local: function(){
    var that=this;
 
    wx.setStorage({
      key: 'usercode',
      data: that.data.usercode,
    })
    wx.setStorage({
      key: 'password',
      data: that.data.password,
    })
    wx.setStorage({
      key: 'isLogin',
      data: true,
    }) 
    wx.setStorage({
      key: 'last_login_time',
      data: now,
    }) 
      
  },

  get_Local:function(){
    var that=this
    wx.getStorage({
      key: 'userinfo',
      success: function (res) {
        that.setData({ userinfo: res.data })
      },
    }),
    wx.getStorage({
      key: 'usercode',
      success: function (res) {
        that.setData({ usercode: res.data })
      },
    }),
    wx.getStorage({
      key: 'password',
      success: function (res) {
        that.setData({ password: res.data })
      },
    }),
    wx.getStorage({
      key: 'isLogin',
      success: function (res) {
        that.setData({ isLogin: res.data })
      },
    }),
    wx.getStorage({
      key: 'last_login_time',
      success: function (res) {
        that.setData({ last_login: res.data })
      },
    })    
  },

  bindCheckNetwork:function(){
    var that=this;
    var app=getApp();
    util.checkNetwork(that);

  },

  onGotUserInfo: function(){
    wx.navigateTo({
      url: "../authorize/authorize",
    })
  },

  reWXLogin: function () {
    var app = getApp()
    const that = this;
    wx.login({
      success(res) {
        console.log('wx.login res:',res)
        if (res.code) {
              console.log('wx.login res:', res)
              var code = res.code;
              var url = app.globalData.host + 'wechat/wechatlogin/'
              console.log('url', url)
              // userInfo 只存储个人的基础数据
              // wx.setStorageSync('userInfo', res.detail.userInfo);
              // 请求自己的服务器，解密用户信息 获取unionId等加密信息
              wx.request({
                url: url,           //自己的服务接口地址
                // method: 'POST',
                method: 'GET',
                header: {
                  'content-type': 'application/x-www-form-urlencoded'
                },
                data: {
                  appcode: app.globalData.appcode,
                  code: code,
                  encryptedData: res.detail.encryptedData,
                  iv: res.detail.iv,
                  nickName: res.detail.userInfo.nickName,
                  avatarUrl: res.detail.userInfo.avatarUrl,
                  userInfo: res.detail.userInfo,
                },
                success: function (data) {
                  console.log('data', data, data.data.nickname)
                  //4.解密成功后 获取自己服务器返回的结果
                  if (data.statusCode == 200) {
                    console.log('解密成功' + JSON.stringify(data.data));
                    var encryptInfo = data.data;
                    wx.setStorageSync('user_uuid', encryptInfo.user_uuid); // 单独存储openid
                    wx.setStorageSync('encryptInfo', encryptInfo); // 存储解密之后的数据
                    wx.setStorageSync('session_key', encryptInfo.session_key);
                    that.setData({
                      currentSessionKey: encryptInfo.session_key
                    })
                  } else {
                    console.log('解密失败')
                  }
                },
                fail: function (res) {
                  console.log(res);
                  console.log('请求错误')
                }
          })


          // data.then(obj => {
          //   if (!obj.error) {
          //     const result = obj.result.session_key;
          //     // 刷新本次session_key
          //     that.setData({
          //        currentSessionKey: result 
          //        });
          //   }
          // });
        }
      },
      fail(error) {
        throw error;
      }
    });
  },

  getPhoneNumber: function (e) {
    var app= getApp();
    var that = this;
    // console.log('e', e)
    // wxutils.getPhoneNumber(that,e)

    // var session_key = that.data.userinfo.session_key;
    var session_key = that.data.currentSessionKey;
    var msg = e.detail.errMsg;
    var encryptedDataStr = e.detail.encryptedData;
    var iv = e.detail.iv;
    console.log('msg=',msg)
    if (msg == 'getPhoneNumber:ok') {
      console.log('before wx.checkSession')
      wx.checkSession({
        success: function () {
          console.log('success', session_key)
          // that.deciyption(sessionID, encryptedDataStr, iv);
          that.deciyption(session_key, encryptedDataStr, iv);         
        },
        fail: function () {
          console.log('failed')
          wx.login({
            success: res => {
              console.log(res, 'sessionkey过期')
              var url = app.globalData.host + 'wechat/wechatlogin/'
              wx.request({
                url : url, 
                header: {
                  'content-type': 'application/x-www-form-urlencoded'
                },
                data: {
                  appcode:app.globalData.appcode,
                  code: res.code,
                  encryptedData: detail.encryptedData,
                  iv: detail.iv,
                  nickName: detail.userInfo.nickName,
                  avatarUrl: detail.userInfo.avatarUrl,
                  userInfo: detail.userInfo,
                }, 
                success:function (res) {
                  var userinfo = res.data.data;
                  wx.setStorageSync('userinfo', userinfo);
                  that.setData({
                    userinfo: userinfo
                  });
                  that.deciyption(userinfo.session_key, encryptedDataStr, iv);
                },
                fail:function(res){
                  console.log(res)
                }
              })
            }
          })
        }
      })
    }
  },

  deciyption(session_key, encryptedData, iv) {
    var app=getApp();
    var that=this;
    var url = app.globalData.host + 'wechat/getphone'
    wx.request({
      method: 'GET',
      url: url,
      data: {
        appcode:app.globalData.appcode,
        encryptedData: encryptedData,
        iv: iv,
        session_key: session_key
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success(res) {
        console.log('success',res)
        app.globalData.company = that.data.company
        app.globalData.storecode = that.data.storecode
        app.globalData.ecode = that.data.usercode
        app.globalData.usercode = that.data.usercode
        app.globalData.network_allow_flag = true
        app.globalData.network_disallow_flag = false
        that.save_Local()       
      },
      fail(res) {
        console.log('fail',res)
      },
    }) 
  },
  
  getPhoneNumber1: function(e) {
    var app=getApp();
    var that=this;
    console.log(e)
    console.log(e.detail.errMsg)
    console.log(e.detail.iv)
    console.log(e.detail.encryptedData)
    var encryptedData = e.detail.encryptedData
    var iv = e.detail.iv 
    var session_key=wx.getStorageSync('session_key')
    // var netflag = that.checkNetwork()
    var url = app.globalData.host + 'wechat/getphone'
    wx.request({
      method: 'GET',
      url: url,
      data: {
        appcode:app.globalData.appcode,
        encryptedData: encryptedData,
        iv: iv,
        session_key: session_key
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success(res) {
        console.log('success',res)
        wx.setStorageSync('user_uuid', res.data.uuid)
        wx.setStorageSync('userInfo', res.data)
        app.globalData.user_uuid=res.data.uuid
      },
      fail(res) {
        console.log('fail',res)
      },
    })   
  },
  bindDateCheck:function(){
    console.log('now',now)
    console.log(now.getDate(),now.getDate()-30,now.getMonth()+1)
    // console.log(util.dateDelta(now,-1))
    var deltadays = 18
    var year=now.getFullYear()
    var month = now.getMonth()+1
    var day = now.getDate()
    var date2= now.setDate(now.getDate()- deltadays);

    var tt = util.dateDelta(now,-18)
    console.log(2,now.getDate(date2),now,tt)

  },

  openAlert: function (options) {
    wx.showModal({
        content: options.content,
        showCancel: false,
        success: function (res) {
            if (res.confirm) {
                console.log('用户点击确定')
            }
        }
    });
}

})