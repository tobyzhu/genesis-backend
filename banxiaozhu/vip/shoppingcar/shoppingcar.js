  var util = require('../../utils/util.js');
  var viputils = require('../viputils.js');
  var log = require('../../utils/log.js');
  var app=getApp();

  Page({
    data: {
      right: [
      // {
      //   text: 'Cancel',
      //   style: 'background-color: #ddd; color: white',
      // },
      {
        text:'修改',
        style: 'background-color: #108ee9; color: white',
      },
      {
        text: '删除',
        style: 'background-color: #F4333C; color: white',
      }],
      left: [{
        text: 'Reply',
        style: 'background-color: #108ee9; color: white',
      },
      {
        text: 'Cancel',
        style: 'background-color: #ddd; color: white',
      }],
      vip:[],
      vipuuid:'',
      pmcodelist: [],
      pmcode: '',
      pmname: '',
      pmcodeindex: -1,
      seccodelist: [],
      seccode: '',
      secname: '',
      seccodeindex: -1,
      thrcodelist: [],
      thrcode: '',
      thrname: '',
      thrcodeindex: -1,
      promotionsid: '0',
      promotionsindex: -1,
      promotionslist: [],
      pushhung:{},
      pushhung_g:{},
      pushhung_s:{},
      item_s_list:[],
      item_g_list:[],
      button_disable:true,
    },

    onLoad: function (options) {
      var that=this;
      var app = getApp();
      that.setData({
        vipuuid: app.globalData.currentvip.uuid,
        vip: app.globalData.currentvip,
        pmcodelist: app.globalData.pmcodelist,
        seccodelist: app.globalData.seccodelist,
        thrcodelist: app.globalData.seccodelist,    

      })
      viputils.get_shoppingcart(that)
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
      var that=this;
      viputils.get_shoppingcart(that)

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

    // onShoppingCartOpen:function(e){
    //   var app = getApp();
    //   var that = this;
    //   console.log(e)
    //   // var index = e.detail.index
    //   // var text = e.detail.value.text
    //   var uuid = e.currentTarget.id
    //   // console.log('index=', index, 'text=', text, 'uuid=', uuid)
    //   wx.navigateTo({
    //     url: '../shoppingcartitem/shoppingcartitem?uuid=' + uuid,
    //   })  
    // },
    onShoppingCartClick: function(e){
      var app=getApp();
      var that=this;
      console.log(e)
      var index=e.detail.index
      var text=e.detail.value.text
      var uuid = e.currentTarget.id
      console.log('index=',index,'text=',text,'uuid=',uuid)
      if (index==1){
        console.log(text,'delete')
        var params={
          oper:'delete',
          company:app.globalData.company,
          storecode:app.globalData.storecode,
          ecode:app.globalData.ecode,
          uuid:uuid
        }
        that.modify_ShoppingCartItem(params)
      }
      if (index==0){
        console.log(text,'修改','uuid=',uuid)
        // var params = {
        //   oper: 'edit',
        //   company: app.globalData.company,
        //   storecode: app.globalData.storecode,
        //   ecode: app.globalData.ecode,
        //   uuid: uuid
        // }
        wx.navigateTo({
          url: '../shoppingcartitem/shoppingcartitem?uuid='+uuid,
        })     
      }

    },

    init_ShoppiongCartItem:function(options){
      var app=getApp();
      var that=this;
      var stypenme='正常'
      console.log('options',options)
      for (var item in options){
        var stypenamekey = options + '[' + item + '].stypename'
        var checkkey = options+'['+item+'].checked'
        var valuekey = options + '[' + item + '].value'
        var stype = options[item].stype

        if (stype = 'P') {
          var stypename = '赠送'
        }
        if (stype = 'N') {
          var stypename = '正常'
        }
        if (stype = 'E') {
          var stypename = '定金'
        }

        console.log('checkkey:', checkkey,'stypenamekey:',stypenamekey,stypename)
        that.setData({
          [stypenamekey]: stypename
        })
      }
    },

    modify_ShoppingCartItem:function(options){
      var app=getApp();
      var that=this;
      var params = options;
      var url = app.globalData.host + 'adviser/modify_shoppingcartitem/?param=' + JSON.stringify(params)
      wx.request({
        method: 'POST',
        url: url,
        // data: this.servieceItem,
        header: {
          // 'content-type': 'application/json' // 默认值
          'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
        },
        success: function (res) {
          console.log(res.data)
          if (res.error) {
            wx.showToast({
              title: res.data.msg,
              icon: 'none',
              duration: 2000
            })
          }
          else {
            wx.showToast({
              title: res.data.msg,
              icon: 'success',
              duration: 2000
            })
            setTimeout(function () {
              // wx.navigateBack({
              //   delta: 1
              // })
            }, 2000)
          }

          viputils.get_shoppingcart(that)
        },
        fail: function (res) {
          console.log("failed")
        },
        complete: function (res) {
          console.log("finished")
        }
      })

    },
    
    confirmHung: function(e){
      console.log(e)
      var app=getApp();
      var that=this;
      var hungitems={}
      var uuids = []
      var companykey ='pushhung.company'
      var storecodekey ='pushhung.storecode'
      var ecodekey ='pushhung.ecode'
      var vcodekey ='pushhung.vcode'
      var vipuuidkey ='pushhung.vipuuid'
      var uuidskey='pushhung.uuids'
      var i_item=0

      that.setData({
        [companykey] : app.globalData.company,
        [storecodekey] : app.globalData.storecode,
        [ecodekey]:  app.globalData.ecode,
        [vipuuidkey] : that.data.vip.uuid,
        [uuidskey]:[],
        button_disable:true
             
      })

      if (that.data.item_g_list.length>0 ){
        for (var g_item in that.data.item_g_list) {
          console.log('g_item', g_item, 'uuid：', that.data.item_g_list[g_item].uuid)
          var uuidskey = 'pushhung.uuids[' + g_item + ']'
          that.setData({
            [uuidskey]: that.data.item_g_list[g_item].uuid
          })
        }
      }
      else {
        g_item=0
      }
      
      if (that.data.item_s_list.length>0){
        for (var s_item in that.data.item_s_list) {
          console.log('s_item', s_item, 'uuid：', that.data.item_s_list[s_item].uuid)
          i_item = Number(g_item) + Number(s_item) + 1
          var uuidskey = 'pushhung.uuids[' + i_item  + ']'
  
          that.setData({
            [uuidskey]: that.data.item_s_list[s_item].uuid
          })
        }       
      }

      var param = that.data.pushhung
      var url = app.globalData.host + 'adviser/shoppingcarthung/?param=' + JSON.stringify(param)
      log.info('shoppingcar confirmHung url: ', url)
      wx.showLoading({
        title: '正在努力处理中...',
      })
      wx.request({
        method: 'POST',
        url: url,
        // data: { 
        // },
        header: {
          // 'content-type': 'application/json' // 默认值
          'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
        },
        success: function (res) {
          console.log(res)
          wx.hideLoading({
            complete: (res1) => {    

              if (res.error) {
                wx.showToast({
                  title: '开单确认时出错！',
                  icon: 'none',
                  duration: 2000
                })
                viputils.get_shoppingcart(that)
              }
              else {
                wx.showToast({
                  title: '开单确认成功！',
                  icon: 'success',
                  duration: 2000
                })
    
                setTimeout(function () {
                  wx.navigateBack({
                    delta: 1
                  })
                }, 2000)
              }    

            },
          })
        },
        fail: function (res) {
          wx.hideLoading({
            complete: (res) => {
              console.log(res,"failed")   
            },
          })
          viputils.get_shoppingcart(that)
          that.setData({
            button_disable:false
          })
        },
        complete: function (res) {
          console.log("finished")
        }
      })
    }
  })