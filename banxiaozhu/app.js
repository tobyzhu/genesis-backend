//var genesis = require('./utils/constant.js');
// var util = require('./utils/util.js');
var wxutils = require('./utils/wxutils.js');
var log = require('./utils/log.js');
App({
  onLaunch: function () {
    var that = this;
    /**
     * 真机调试：不要用 127.0.0.1（会指向手机，报 request:fail ERR_CONNECTION_REFUSED）。
     * 任选其一：
     * 1）改下方 globalData.host 为电脑的局域网 IP，例如 http://192.168.1.8:8030/
     * 2）开发者工具控制台执行一次：
     *    wx.setStorageSync('genesis_api_host', 'http://192.168.1.8:8030/')
     *    重启小程序（会覆盖默认 host，不必改代码）
     * 后端须监听所有网卡：python manage.py runserver 0.0.0.0:8030
     * 微信开发者工具：详情 → 本地设置 → 勾选「不校验合法域名、web-view（业务域名）、TLS 版本以及 HTTPS 证书」
     */
    try {
      var ov = wx.getStorageSync('genesis_api_host');
      if (ov && typeof ov === 'string' && ov.indexOf('http') === 0) {
        that.globalData.host = ov.slice(-1) === '/' ? ov : ov + '/';
        console.log('genesis_api_host from storage:', that.globalData.host);
      }
    } catch (e) {}
    // 登录
    wx.login({
      success: res => {
        console.log('wx.login success.res',res)
        // 发送 res.code 到后台换取 openId, sessionKey, unionId
        console.log('wx.login res:', res)
        var code = res.code;
        var url = that.globalData.host + 'wechat/wechatlogin/'
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
            appcode: that.globalData.appcode,
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
              that.globalData.openid=encryptInfo.openid;
              // that.setData({
              //   currentSessionKey: encryptInfo.session_key
              // })
            } else {
              console.log('解密失败')
            }
          },
          fail: function (res) {
              // console.log(res);
              console.log('请求错误',res)
          }
        })
      }
    })
    // 获取用户信息
    wx.getSetting({
      success: res => {
        if (res.authSetting['scope.userInfo']) {
          // 已经授权，可以直接调用 getUserInfo 获取头像昵称，不会弹框
          wx.getUserInfo({
            success: res => {
              // 可以将 res 发送给后台解码出 unionId
              that.globalData.userInfo = res.userInfo

              // 由于 getUserInfo 是网络请求，可能会在 Page.onLoad 之后才返回
              // 所以此处加入 callback 以防止这种情况
              if (that.userInfoReadyCallback) {
                that.userInfoReadyCallback(res)
              }
            }
          })
        }
      }
    })
  },

  onShow:function(){
    var that = this;
    wx.getStorage({
      key: 'nearlyviplist',
      success: function (res) {
        log.info('app onShow getStorage nearlyvilist',res)
        that.globalData.nearlyviplist = res.data
      }
    }); 
  },

  onHide:function(){

  },

  onError:function(){
  },

  onPageNotFound:function(){

  },

  "globalData": {
    // isDev:true,
    isDev:false,
    appcode:'100',
    openid:'',
    unionid:'',
    userInfo:{},
    wxusertype:'100',
    user_uuid:'',
    tempnetwork:{},
    networkType:'',
    networkenable:false,
    local_SSID:'',
    local_BSSID:'',
    bssid_flag:false,
    network_allow_flag:false,
    demoapptype:'100',
    // dev
    democompany: 'yiren',
    democompanyname: 'yiren',   
    demostorecode: '01',
    demostorename: '01',
    // normal
    // democompany:'demo',
    // democompanyname:'演示版',
    // demostorecode:'88',
    // demostorename:'演示店铺',

    demousercode:'888',
    demoecode:'888',
    apptype:'100',
    tempnetwork:{
      company:'demo',
      companyname:'演示版',
      storecode:'88',
      storename:'88',
      usercode:'888',
      ecode:'888',
    },
    
    company: '',
    companyname:'',
    storecode: '',
    storename:'',
    usercode:'',
    ecode: '', //'1002',
    ename:'',
    isLogin:true,
    last_login_time:'',
    // host: "https://www.softweb.net.cn/genesis/",
    // "host": "https://www.softweb.net.cn/genesis/",
    // host: "http://192.168.71.154:8030/",
    // host: "http://10.211.55.2:8040/",
    // 仅「开发者工具模拟器」可用 127.0.0.1；真机请改为电脑局域网 IP 或使用 genesis_api_host 存储覆盖
    //host: "http://10.211.55.2:8030/",
    // host: "http://192.168.71.54:8030/",
    // 局域网一般为 192.168.x.x；误写为 192.169.x.x 会导致连接超时（与电脑不在同一网段语义）
    host: "http://192.168.1.6:8030/",
    currentStore:{},
    currentCompany:{},
    indexImageUrl:[],
    cardname:'',
    currentvip:{},
    currentvipuuid_s:'',
    currentvipuuid_u:'',
    currentvip_amountcardlist:[],
    currentvip_timescardlist:[],
    currentvip_periodcardlist:[],
    currentvip_cardtype10list: [],
    currentvip_cardtype20list: [],
    currentvip_cardtype30list: [],
    currentvip_cardtype40list: [],
    shoppingcart_item_s_list:[],
    shoppingcart_item_g_list:[],
    current_itemlist:[],
    current_itemindex:-1,
    payccodeindex:-1,
    payccode:'',
    currentvip_shoppingcartitems_s:0,
    currentvip_shoppingcartitems_g:0,
    nearlyviplist:[],
    viplist:[],
    vip10list:[],
    vip20list:[],
    vip30list:[],
    vipinlist:[],
    vipnotinlist:[],
    viplevellist:[],
    empllist:[],
    pmcodelist:[],
    seccodelist:[],
    srvlist:[],
    goodslist:[],
    cardtype:[],
    cardtype10list:[],
    cardtype20list:[],
    cardtype30list:[],
    cardtype40list:[],
    amountcardtypelist:[],
    timescardtypelist:[],
    periodcardtypelist:[],
    roomlist:[],
    instrumentlist: [ ],
    sourcelist:[],
    psstatuslist:[],
    brand:[],
    thismonth_emplarch:[],
    lastmonth_emplarch:[],
    vipcasetypeList:[],
    stypelist:[
        {
          stype:'N',
          stypename:'正常'
        },
        {
          stype:'P',
          stypename:'赠送'
        }
      ],
    depositeflaglist:[
        {
          depositeflag:'N',
          depositeflagname:'带走'
        },
        {
          depositeflag:'Y',
          depositeflagname:'存院'         
        }
      ],
    salonvip_status_list:[
      {
        code:'BOOKING',
        title:'预约'
      },
      {
        code:'FINISHED',
        title:'完成'
      },
      {
        code:'CANCEL',
        title:'取消'
      }
    ],
    vipmanagefunctions:[],
    reporturl:'',
    param:{},
    salonlist:[],
    salonlist_plan:[],
    salonlist_finished:[],
    salonlist_cancel:[],
    salonvip:[]
  },

})  