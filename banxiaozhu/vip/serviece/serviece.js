
// import { $stopWuxRefresher, $stopWuxLoader } from '../../wux/packages/lib/index'
var util = require('../../utils/util.js');
var viputils = require('../viputils.js');

Page({
  data: {
    right: [{
      text: 'Cancel',
      style: 'background-color: #ddd; color: white',
    },
    {
      text: '修改',
      style: 'background-color: #F4333C; color: white',
    }],
    storecode:'',
    vipPage:'',
    vipuuid:'',
    vip:{},
    vcode:'',
    vname:'',
    payccode:'',
    paycardsuptype: '00',
    paycardindex: -1,
    paycardlist:[],
    cardtype_10_index:-1,
    cardtype_10_list: [],
    suptype:'10',
    ttype: 'S',
    ttypename: '服务',
    stype: 'N',
    stypename: '正常',
    stypeChecked:false,
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
    index:0,
    consumeqty:0,
    count: 20,
    page: 1,
    scrollTop: 0,    
    totalsrvList:[],
    srvList:[],
    itemlist:[],
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
    promotionsindex: 0,
    promotionslist: [
      {
        promotionsid: '0',
        promotionsname: '正常'
      }
    ]
  },
  onLoad(options) {
    console.log('serviece onload')
    var app = getApp();
    var that = this;
    // var vip= app.globalData.currentvip;
    that.setData({
      storecode:app.globalData.storecode,
      vip: app.globalData.currentvip,
      paycardlist: app.globalData.currentvip_amountcardlist ,
      payccode: app.globalData.payccode,
      vipuuid: app.globalData.currentvipuuid_u,
      vipuuid_s: app.globalData.currentvipuuid_s,
      pmcodelist: app.globalData.pmcodelist,
      seccodelist: app.globalData.seccodelist,
      thrcodelist: app.globalData.seccodelist

    })

    viputils.getVipPage(that);

    if (options && options.searchValue) {
      that.setData({
        searchValue: options.searchValue
      })
      that.get_serviecelist_bykeyword()
      
    }
    else {
      // util.get_SrvList(that)
      that.setData({
        itemlist: app.globalData.srvList
      })
      app.globalData.current_itemlist=that.data.itemlist

    }
  },

  onChange(e) {
  
  },

  onShow(e){
    var that=this;
    var app=getApp();
    console.log('serviece onShow')
    // that.setData({
    //   itemlist: app.globalData.current_itemlist
    // })
    // console.log(that.data.itemlist)
  },

  onUnload: function () {
    var that = this;
    var pages = getCurrentPages(); // 获取页面栈
    console.log('pages:', pages,that.data.srvList)
   
  },

  // 下拉刷新
  onPullDownRefresh: function () {
    var that=this
    console.log('begin PullDown')
    wx.showNavigationBarLoading()
    // util.get_amountcardtypelist()
    // util.get_timescardtypelist()
    // that.onLoad()
    that.getServiece()
    setTimeout(() => {
      wx.hideNavigationBarLoading()
      wx.stopPullDownRefresh()
    }, 2000);
    console.log('end PullDown')
  },

// 获取服务项目
  getServiece(params = {}) {
    var that=this;
    var app = getApp();
    // const data = params

    // var url = app.globalData.host + "baseinfo/get_serviece"
    var url = app.globalData.host + "adviser/get_vip_itemlist"
    wx.showLoading({
      title: '数据加载中',
    })
    wx.request({
      method:'GET',
      url: url,
      data:{
        company:app.globalData.company,
        vipuuid: that.data.vip.uuid,
        ttype:'S'
      },
      success: (res) => {
        console.log(res)
        that.setData({
          // srvList:res.data,
          itemlist:res.data
        })
        // that.init_srvList()
        viputils.init_itemlist(that)
        wx.hideLoading()
      },
      fail:(res)=>{
        console.log(res)
      },
      complete:(res)=>{
        console.log(res)
      }
      
    })
  },   
  // 对服务项目补充开单需要的相关字段信息
  init_srvList: function(){
    var that=this;
    var app = getApp();
    var fields = [
      { filed: 'payccode', value: '' },
      { field: 'qty', value: 0 },
      { field: 'secdisc', value: 1 },
      // { field:'s_price',value:0},
      { field: 'amount', value: 0 },
      { field: 'mondisc', value: 0 },
      { field: 'pmcode', value: '' },
      { field: 'seccode', value: '' },
      { field: 'thrcode', value: '' },
      { field: 'stype', value: 'N' },
      { field: 'promotionsid', value: '0' }
    ];
    for (var index in that.data.srvList) {
      for (var item in fields) {
        var key = 'srvList[' + index + '].' + fields[item].field;
        // console.log(key);
        that.setData({
          [key]: fields[item].value
        })
      };
    }
    app.globalData.current_itemlist = that.data.srvList   
  },

// 获取服务相关基本信息的入口，通过调用相关函数，可以获取品牌，显示分类，该客户推荐服务项目，等
  getBaseInfo: function () {
    var app = getApp();
    var host = app.globalData.host;
    this.get_serviecebrand();
  },
  bindStypeChange: function (e) {
    var that = this;
    viputils.bindStypeChange(that, e)
  },
  //
  bindPmcodeChange:function(e){
    var that=this;
    viputils.bindPmcodeChange(that,e)
  },
  bindSeccodeChange: function (e) {
    var that = this;
    viputils.bindSeccodeChange(that, e)
  },
  bindThrcodeChange: function (e) {
    var that = this;
    viputils.bindThrcodeChange(that, e)
  },
  // 消费数量修改
  bindConsumeqtyChange:function(e){

    var index = e.currentTarget.id;
    console.log('e=',e,'index=',index) ;
    var that=this;
    var list = that.data.srvList; 
    var qty = e.detail.value;
    var price = that.data.srvList[index].price; 
    var secdisc = that.data.srvList[index].secdisc;
    var mondisc = that.data.srvList[index].mondisc; 
    var amount = qty*price*secdisc - mondisc;

    var fields = [
      { field: 'qty', value:qty},
      { field: 'price', value:price},
      { field: 'secdisc', value: secdisc },
      { field: 'mondisc', value: mondisc },  
      { field: 'amount', value: amount }         
    ]

    for (var item in fields) {
      var key = 'srvList[' + index + '].' + fields[item].field;
      that.setData({
        [key]: fields[item].value
      })
    };
  },
  bindPaycardChange: function (e) {
    var that = this;
    console.log('picker cardtype 发生选择改变，携带值为', e.detail.value);

    that.setData({
      paycardindex: e.detail.value,
      // newcardsuptype: that.data.cardtype10list[e.detail.value].suptype
    })
    that.onShow()
  },
  get_serviecelist_bykeyword: function () {
    var that = this;
    var app = getApp();
    // var url = app.globalData.host + 'baseinfo/get_goodslist_bykeyword';
    var url = app.globalData.host + 'baseinfo/get_serviece';
    // console.log(xinqu)
    wx.showLoading({
      title: '数据加载中',
    })
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        searchvalue: that.data.searchValue
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        that.setData({
          fail: false,
          // srvList: res.data,
          itemlist:res.data
        })
        app.globalData.current_itemlist = that.data.itemlist
        // that.init_srvList()
        // viputils.init_itemlist(that)
        wx.hideLoading()
      },
      fail: function (res) {
        console.log("failed")
        that.setData({
          fail: true
        })
      },
      complete: function (res) {
        console.log("finished")
      }

    })

  },

  onSearchChange(e) {
    console.log('onSearchChange', e)
    var that = this;

    this.setData({
      value: e.detail.value,
    })
  },
  onSearchFocus(e) {
    console.log('onFocus', e)
  },
  onSearchBlur(e) {
    console.log('onBlur', e)
  },
  onSearchConfirm(e) {
    console.log('onConfirm', e)
    var app = getApp();
    var that = this;
    var keyword = e.detail.value;
    var list = that.data.viplist;
    var reg = new RegExp(keyword);
  },
  onSearchClear(e) {
    console.log('onClear', e)

  },
  onSearchCancel(e) {
    console.log('onCancel', e)
  },
  onItemClick: function (e) {
    var app = getApp();
    var that = this;
    console.log(e)
    var index = e.detail.index
    var text = e.detail.value.text
    var itemindex = e.currentTarget.id
    console.log('index=', index, 'text=', text, 'uuid=', itemindex)
    // if (index == 0) {
    //   console.log(text, 'delete')
    //   var params = {
    //     oper: 'delete',
    //     company: app.globalData.company,
    //     storecode: app.globalData.storecode,
    //     ecode: app.globalData.ecode,
    //     uuid: uuid
    //   }
    //   that.modify_ShoppingCartItem(params)
    // }
    if (index == 1) {
      console.log('修改', 'itemindex=', itemindex)
      // var params = {
      //   oper: 'edit',
      //   company: app.globalData.company,
      //   storecode: app.globalData.storecode,
      //   ecode: app.globalData.ecode,
      //   uuid: uuid
      // }
      wx.navigateTo({
        url: '../itemsedit/itemsedit?index=' + itemindex,
      })
    }

  },

  gotoShoppingCart:function(){
    var that=this;
    wx.navigateTo({
      url: '../shoppingcar/shoppingcar',
    })
  },

  addServieceToCart:function(){
    var that=this;
    var app=getApp();
    var len=that.data.itemlist.length;
    console.log(len)
    for (var i = 0; i < len; i++) {
      if (that.data.itemlist[i].qty!=0) {
        var hungitem = {
          company:app.globalData.company,
          storecode:app.globalData.storecode,
          ecode:app.globalData.ecode,
          vipuuid: that.data.vipuuid,
          payccode: that.data.payccode.ccode,
          ttype:that.data.ttype,
          stype:that.data.stype,
          itemcode: that.data.itemlist[i].itemcode,
          price: that.data.itemlist[i].price,
          qty: that.data.itemlist[i].qty,
          secdisc: that.data.itemlist[i].secdisc,
          mondisc: that.data.itemlist[i].mondisc,
          amount: that.data.itemlist[i].qty * that.data.itemlist[i].price ,
          pmcode:that.data.pmcode,
          seccode:that.data.seccode,
          thrcode:that.data.thrcode,
          promotionsid: that.data.promotionsid
        }
        console.log(hungitem)
        // var url = app.globalData.host + 'adviser/serviecehung'
        var url = app.globalData.host + 'adviser/addshoppingcart/?param=' + JSON.stringify(hungitem)
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
            console.log('servieceitem hung success!')
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
                // that.setData({
                //   srvList: app.globalData.srvList
                // })
                // that.init_srvList()
                viputils.init_itemlist(that)
              }, 2000)
            }
          },
          fail: function (res) {
            console.log("failed")
          },
          complete: function (res) {
            console.log("finished")
          }
        })
      }
    }
  },
  // 搜索入口  
  wxSearchTabServiece: function () {
    // wx.navigateTo({
    //   url: '../serviecesearch/serviecesearch',
    // })
    wx.redirectTo({
      url: '../serviecesearch/serviecesearch'
    })
  } 
})