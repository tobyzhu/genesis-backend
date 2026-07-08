var app = getApp()

function wxLogin(that){
  wx.login({
    success(res) {
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
          },
          success: function (data) {
            console.log('data', data, data.data.nickname)
            //4.解密成功后 获取自己服务器返回的结果
            if (data.statusCode == 200) {
              console.log('解密成功' + JSON.stringify(data.data));
              var encryptInfo = data.data;
              wx.setStorageSync('user_uuid', encryptInfo.user_uuid); // 单独存储user_uuid 不保存openid
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


      }
    },
    fail(error) {
      throw error;
    }
  });
}

function getPhoneNumber(that,e) {
  console.log('e', e)
  var session_key = that.data.currentSessionKey
  var msg = e.detail.errMsg;
  var encryptedDataStr = e.detail.encryptedData;
  var iv = e.detail.iv;

  if (msg == 'getPhoneNumber:ok') {
    wx.checkSession({
      success: function () {
        console.log('success', session_key)
        // that.deciyption(session_key, encryptedDataStr, iv);
        deciyption(that,session_key, encryptedDataStr, iv);        
      },
      fail: function () {
        console.log('failed')
        wx.login({
          success: res => {
            console.log(res, 'sessionkey过期')
            var url = app.globalData.host + 'wechat/wechatlogin/'
            wx.request({
              url: url,
              header: {
                'content-type': 'application/x-www-form-urlencoded'
              },
              data: {
                appcode: app.globalData.appcode,
                code: res.code,
              },
              success: function (res) {
                console.log(res)

                if (res.statusCode === 200) {
                  console.log('解密成功' + JSON.stringify(res.data));
                  var encryptInfo = res.data.data;
                  wx.setStorageSync('user_uuid', encryptInfo.user_uuid); // 单独存储user_uuid 不保存openid
                  wx.setStorageSync('encryptInfo', encryptInfo); // 存储解密之后的数据
                  wx.setStorageSync('session_key', encryptInfo.session_key);
                  that.setData({
                    currentSessionKey: encryptInfo.session_key
                  })
                } else {
                  console.log('解密失败')
                }


                var userinfo = res.data.data;
                wx.setStorageSync('userinfo', userinfo);
                that.setData({
                  userinfo: userinfo
                });
                that.deciyption(that,userinfo.session_key, encryptedDataStr, iv);
              },
              fail: function (res) {
                console.log(res)
              }
            })
          }
        })
      }
    })
  }
}

function deciyption(that,session_key, encryptedData, iv) {

  var session_key1 = wx.getStorageSync('session_key')
  var url = app.globalData.host + 'wechat/getphone'
  wx.request({
    method: 'GET',
    url: url,
    data: {
      encryptedData: encryptedData,
      iv: iv,
      session_key: session_key1
    },
    header: {
      'content-type': 'application/json' // 默认值
      // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
    },
    success(res) {
      console.log('success')
      if (res.statusCode === 200){
        that.setData({
          mobile: res.data.mobile
        })
        app.globalData.company = that.data.company
        app.globalData.storecode = that.data.storecode
        app.globalData.ecode = that.data.usercode
        app.globalData.usercode = that.data.usercode
        app.globalData.network_allow_flag = true
        app.globalData.network_disallow_flag = false
        that.save_Local()
        wx.reLaunch({
          url: '/index/index',
        })
      }

    },
    fail(res) {
      console.log('fail', res)
    },
  })
}

function bindGetUserInfo (e) {
  if (e.detail.userInfo) {
    //用户按了允许授权按钮
    console.info("用户按了允许授权按钮,e:", e);
    var that = this;
    that.queryUsreInfo(e.detail);
    //授权成功后，跳转进入小程序首页
    // wx.reLaunch({
    //   url: '/pages/index/index'
    // })
  } else {
    //用户按了拒绝按钮
    console.info("用户按了拒绝按钮");
    wx.showModal({
      title: '警告',
      content: '您点击了拒绝授权，将无法进入小程序，请授权之后再进入!!!',
      showCancel: false,
      confirmText: '返回授权',
      success: function (res) {
        if (res.confirm) {
          console.log('用户点击了“返回授权”')
        }
      }
    })
  }
}
//获取用户信息接口
function queryUsreInfo(detail) {
  console.info("queryUsreInfo" + detail);
  wx.login({
    success: function (res) {
      console.log('wx.login res:', res)
      var code = res.code;
      var url = app.globalData.host + 'wechat/wechatlogin/'
      console.log('url', url)
      // userInfo 只存储个人的基础数据
      wx.setStorageSync('userInfo', detail.userInfo);
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
          encryptedData: detail.encryptedData,
          iv: detail.iv,
          nickName: detail.userInfo.nickName,
          avatarUrl: detail.userInfo.avatarUrl,
          userInfo: detail.userInfo,
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
          } else {
            console.log('解密失败')
          }
        },
        fail: function (res) {
          console.log(res);
          console.log('请求错误')
        }
      })
    }
  })
}

module.exports = {
  wxLogin: wxLogin,
  getPhoneNumber: getPhoneNumber,
}
