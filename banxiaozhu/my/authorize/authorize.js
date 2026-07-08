var app=getApp()

Page({
  data: {
    //判断小程序的API，回调，参数，组件等是否在当前版本可用。
    canIUse: wx.canIUse('button.open-type.getUserInfo'),
    userInfo:{},
    nickName:'',
    avatarUrl:'',
    gender:'',
    province:'',
    city:'',
    country:''
  },
  onLoad: function () {
    var that = this;
    // 查看是否授权
    // wx.getSetting({
    //   success: function (res) {
    //     console.log(res)
    //     if (res.authSetting['scope.userInfo']) {
    //       wx.getUserInfo({
    //         success: function (res) {
    //           var userInfo = res.userInfo
    //           wx.setStorageSync('userInfo', res.userInfo);

    //           console.info("已经授权,getUserInfo res:",res);
    //           that.setData({
    //             userInfo: userInfo
    //           })
    //           // that.queryUsreInfo(res);
    //           //从数据库获取用户信息
    //           that.queryUsreInfo(res);
    //           //用户已经授权过
    //           // wx.reLaunch({
    //           //   url: '/index/index'
    //           // })
    //         }
    //       });
    //     }
    //   }
    // })
  },
  bindGetUserInfo: function (e) {
    if (e.detail.userInfo) {
      //用户按了允许授权按钮
      console.info("用户按了允许授权按钮,e:",e);
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
  },
  //获取用户信息接口
  queryUsreInfo: function (detail) {
    console.info("queryUsreInfo" + detail);
    wx.login({
      success: function (res) {
        console.log('wx.login res:',res)
        var code = res.code;
        var url = app.globalData.host +'wechat/wechatlogin/'
        console.log('url',url)
        // userInfo 只存储个人的基础数据
        wx.setStorageSync('userInfo', detail.userInfo);
        // 请求自己的服务器，解密用户信息 获取unionId等加密信息
        wx.request({
          url: url,           //自己的服务接口地址
          // method: 'POST',
          method:'GET',
          header: {
            'content-type': 'application/x-www-form-urlencoded'
          },
          data: {
            appcode:app.globalData.appcode,
            code: code,
            encryptedData: detail.encryptedData,
            iv: detail.iv,
            nickName: detail.userInfo.nickName,
            avatarUrl: detail.userInfo.avatarUrl,
            userInfo: detail.userInfo,
          },
          success: function (data) {
            console.log('data',data,data.data.nickname)
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
  },
})

