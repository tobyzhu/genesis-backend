// vip/vip.js
var app = getApp();
var host = app.globalData.host;
var company = app.globalData.company
var util = require('../utils/util.js')
var viputil = require('./viputils.js');
var log = require('../utils/log.js');


Page({
  data: {
    vip: {},
    cardlist: [],
    vipstr:'',
    uuid: '',
    vipuuid:'',
    vipuuid_s:'',
    vipuuid_u:'',
    hung:[],
    caritems:0,
    mtcode:'',
    grids: [
      {
        id: 1,
        text: "预约",
        url: "./booking/booking",
        image: "../images/workTimeSchedule@2x.png"
      },
      {
        id: 2,
        text: "客户回访",
        url: "./vipcrmcase/vipcrmcase",
        image: "../images/chatHistoryIcon@2x.png"
      },
      {
        id: 3,
        text: "开单",
        url: "./kaidan/kaidan",
        image: "../images/kaidan.png"
      },
      {
        id: 4,
        text: "最近消费",
        url: '../vip/consumequery/consumequery?vipuuid=',
        image: "../images/list.png"
      },
      {
        id: 8,
        text: "基础资料",
        url: "../vip/vipinfo/vipinfo",
        image: "../images/vipinfo.png"
      },      

      {
        id: 9,
        text: "购物车",
        url: "../vip/shoppingcar/shoppingcar",
        image: "../images/cart.png"
      },
    ]  ,    
    cardtype_10_list:[],
    cardtype_20_list:[],
    item_s_list:[],
    item_g_list:[],
    shoppingcartitems:0
  },   

  // this options is vip object  
  onLoad: function (options) {

    var app = getApp();
    var that = this;
    that.setData({
      vip: app.globalData.currentvip,
      // shoppingcartitems: app.globalData.currentvip_shoppingcartitems_s + app.globalData.currentvip_shoppingcartitems_g
    })

    var param = {
      functionid: 'vip',
      key: 'grids'
    }
    util.getWechatFunction(that, param)

    
    var bssid = util.get_bssid()
    console.log('bssid:',bssid)

    that.getVipBaseInfo(options);

    var vipuuid_u = that.data.vipuuid_u;
    var vipuuid_s = that.data.vipuuid_s;


    var goodskey = 'grids[3].url';
    var newcardkey = 'grids[4].url';
    var fillcardkey ='grids[5].url';
    var newtimescardkey = 'grids[6].url';
    var shoppingcartkey ='grids[10].url'
    // var consumequerykey ='grids[6].url';

  },
  onShow: function(options){
    var that=this;
    var app=getApp();
    var cartitems= 10
    that.setData({
      // vip: app.globalData.currentvip,
      shoppingcartitems: app.globalData.currentvip_shoppingcartitems_s + app.globalData.currentvip_shoppingcartitems_g
    })
  },

  onPullDownRefresh: function () {
    var that = this
    console.log('begin PullDown')
    wx.showNavigationBarLoading()

    var options={
      uuid: that.data.vip.uuid
    }
    viputil.getVipBaseInfo(that,options);
    
    setTimeout(() => {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    }, 2000);
    console.log('end PullDown')
  },


  initData: function() {
    var that = this;
    // 获取数据 -> 从后端(暂时放入初始化数据data)
    that.setData({
        mtcode: that.data.mtcode,
      });
  },
   // 拨打电话给收件人
  callGetPhone(e) {
    console.log(e)
    var that=this
    let telPhone = e.currentTarget.dataset.getphone;
    that.callPhone(telPhone);
  },
  

  /**
    * 拨打电话 - 可简单封装工具集
   */
  callPhone(phoneNumber) {
    wx.makePhoneCall({
      phoneNumber: phoneNumber,
      success: function() {
        console.log("拨打电话成功！")
      },
      fail: function() {
        console.log("拨打电话失败！")
      }
    })
  },

  getVipBaseInfo: function(options){
    var app = getApp();
    var that = this;

    console.log('getVipBaseInfo', options);
    if (options.uuid.length > 32) {
      var vipuuid_s = options.uuid.split('-').join('')
    }
    else {
      var vipuuid_s = options.uuid
    }
    var vipuuid_u = util.strtouuid(vipuuid_s);
    var vipuuid = util.strtouuid(vipuuid_s)
    var host = app.globalData.host
    var url = host + "baseinfo/vip/"+vipuuid_u;
    // var url = host + 'baseinfo/get_vipbaseinfo/'
    console.log(url)

    wx.request({
      method:'GET',
      url: url, 
      data: {
        // company: app.globalData.company,
        // storecode: app.globalData.storecode,
        // vipuuid: vipuuid_s
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
     success(res) {
       if (res.data=='未找到'){
         log.info('vip.js getVipBaseInfo 未找到：', res.data)
         // 

       }
        // 来店渠道名称映射
        if (res.data && app.globalData.sourcelist) {
          for (var i = 0; i < app.globalData.sourcelist.length; i++) {
            if (app.globalData.sourcelist[i].itemname == res.data.source) {
              res.data.sourceName = app.globalData.sourcelist[i].itemvalues;
              break;
            }
          }
        }
        // 等级名称映射
        if (res.data && app.globalData.viplevellist) {
          for (var i = 0; i < app.globalData.viplevellist.length; i++) {
            if (app.globalData.viplevellist[i].itemname == res.data.viplevel) {
              res.data.viplevelName = app.globalData.viplevellist[i].itemvalues;
              break;
            }
          }
        }


        that.setData({
          vip: res.data,
          vipuuid_s: vipuuid_s,
          vipuuid_u: vipuuid_u
        }),
        wx.setStorage({
          key: 'currentvip',
          data: res.data[0]
        })
        app.globalData.currentvip = that.data.vip
        app.globalData.currentvipuuid_u =  that.data.vipuuid_u
        app.globalData.currentvipuuid_s = that.data.vipuuid_s  

        // app.globalData.nearlyviplist.push(that.data.vip)    
        console.log('app.globalData.viplist', app.globalData.nearlyviplist)
        viputil.set_nearlyviplist(that.data.vip)


        var amountoptions = {
          company:app.globalData.company,
          vipuuid: that.data.vip.uuid,
          comptype: 'amount'
        }
        var timesoptions = {
          company:app.globalData.company,
          vipuuid: that.data.vip.uuid,
          comptype: 'times'
        }
        var periodoptions = {
          company:app.globalData.company,
          vipuuid: that.data.vip.uuid,
          comptype: 'period'
        }

        viputil.getVipComptypeCardList(that, amountoptions)
        viputil.getVipComptypeCardList(that, timesoptions)
        viputil.getVipComptypeCardList(that, periodoptions)

        log.info('vip.js getVipBaseInfo currentvip_amountcardlist：', app.globalData.currentvip_amountcardlist)

        viputil.get_shoppingcart(that)

      }
    })
 },
 
});
