// vip/serviece/serviece.js
// import data from './data'
// import { $stopWuxRefresher, $stopWuxLoader } from '../../wux/packages/lib/index'

Page({
  data: {
    storecode: '',
    vipuuid: '',
    vip: {},
    vcode: '',
    payccode: '',
    suptype: '10',
    index: 0,
    consumeqty: 0,
    count: 20,
    page: 1,
    scrollTop: 0,
    totalsrvList: [],
    srvList: [],
  },
  onLoad(options) {
    var app = getApp();
    var that = this;
    var vip = app.globalData.currentvip;

    console.log('options', options)
    if (options && options.searchValue) {
      that.setData({
        searchValue: options.searchValue
      })
      that.get_serviecelist_bykeyword()

    }
    else {
      var payccode = options.payccode;
      that.setData({
        vipuuid: options.vipuuid,
        payccode: options.payccode,
        storecode: app.globalData.storecode,
        index: options.index
      });
      this.getBaseInfo();
      wx.showLoading();
      // this.getServiece();
      wx.getStorage({
        key: 'srvlist',
        success: function (res) {
          console.log(res.data),
            wx.hideLoading()
          that.setData({
            totalsrvList: res.data,
            srvList: res.data.slice(0, that.data.count)
          })
          that.init_srvList()
        }
      });
    }
  },
  onChange(e) {
    const { checkedItems, items } = e.detail
    const params1 = {}
    const params2 = {}
    const parmas3 = {}
    console.log('e.detail', e.detail)

    console.log(checkedItems, items)

    checkedItems.forEach((n) => {
      if (n.checked) {
        if (n.value === 'brand') {
          const selected = n.children.filter((n) => n.checked).map((n) => n.value).join(' ')
          params1.sort = n.value
          // params.order = selected
          params1.brand = selected
        } else if (n.value === 'displayclass1') {
          const selected = n.children.filter((n) => n.checked).map((n) => n.value).join(' ')
          // params.displayclass1 = n.value
          // params.order = n.sort === 1 ? 'asc' : 'desc'
          params2.displayclass1 = selected
        } else if (n.value === 'price') {
          params3.sort = n.value
        } else if (n.value === 'tags') {
          n.children.filter((n) => n.selected).forEach((n) => {
            if (n.value === 'language') {
              const selected = n.children.filter((n) => n.checked).map((n) => n.value).join(' ')
              params3.language = selected
            } else if (n.value === 'query') {
              const selected = n.children.filter((n) => n.checked).map((n) => n.value).join(' ')
              params3.query = selected
            }
          })
        }
      }
    })
    var params = Object.assign(params1, params2, parmas3)
    console.log('params', params)
    // this.getRepos(params)
    this.getServiece(params)
  },
  onUnload: function () {
    var that = this;
    var pages = getCurrentPages(); // 获取页面栈
    console.log('pages:', pages, that.data.srvList)
    if (pages.length > 0) {
      var currPage = pages[pages.length - 1]; // 当前页面
      var prevPage = pages[pages.length - 2]; // 上一个页面
      for (var item in that.data.srvList) {

        if (that.data.srvList[item].qty != 0) {
          var options = {
            index: that.data.index,
            suptype: that.data.suptype,
            ttype: 'S',
            stype: 'N',
            vipuuid: that.data.vipuuid,
            vcode: that.data.vcode,
            payccode: that.data.payccode,
            itemcode: that.data.srvList[item].svrcdoe,
            qty: that.data.srvList[item].qty,
            price: that.data.srvList[item].price,
            secdisc: that.data.srvList[item].secdisc,
            amount: that.data.srvList[item].amount,
            mondisc: that.data.srvList[item].mondisc,
            pmcode: that.data.srvList[item].pmcode,
            seccode: that.data.srvList[item].seccode,
            thrcode: that.data.srvList[item].thrcode,
            promotinsid: that.data.srvList[item].promotionsid
          }
          console.log('route:', currPage.route, 'options:', options)
          prevPage.addHung(options);
        };
      }
    }

  },

  // 获取服务项目
  getServiece(params = {}) {
    var that = this;
    var app = getApp();
    const data = params
    var url = app.globalData.host + "baseinfo/get_serviece"
    wx.showLoading()
    wx.request({
      url: url,
      // data,
      data: {
        company: app.globalData.company,
        type: 'serviece'
      },
      success: (res) => {
        console.log(res)

        wx.hideLoading()
        that.setData({
          srvList: res.data
        })
        that.init_srvList()

      },
      fail: (res) => {
        console.log(res)
      },
      complete: (res) => {
        console.log(res)
      }

    })
  },
  init_srvList: function () {
    var that = this;
    var app = getApp();
    var fields = [
      { filed: 'payccode', value: '' },
      { field: 'qty', value: 0 },
      { field: 'secdisc', value: 1 },
      // {field:'s_price',value:0},
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

  },
  // 获取服务相关基本信息的入口，通过调用相关函数，可以获取品牌，显示分类，该客户推荐服务项目，等
  getBaseInfo: function () {
    var app = getApp();
    var host = app.globalData.host;
    this.get_serviecebrand();
  },

  // 消费数量修改
  bindConsumeqtyChange: function (e) {

    var index = e.currentTarget.id;
    console.log('e=', e, 'index=', index);
    var that = this;
    var list = that.data.srvList;
    var qty = e.detail.value;
    var price = that.data.srvList[index].price;
    var secdisc = that.data.srvList[index].secdisc;
    var mondisc = that.data.srvList[index].mondisc;
    var amount = qty * price * secdisc - mondisc;

    var fields = [
      { field: 'qty', value: qty },
      { field: 'price', value: price },
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
  bindPickerChange(e) {
    console.log('picker发送选择改变，携带值为', e.detail.value)
    this.setData({
      index: e.detail.value
    })
  },
  bindMultiPickerChange(e) {
    console.log('picker发送选择改变，携带值为', e.detail.value)
    this.setData({
      multiIndex: e.detail.value
    })
  },
  bindMultiPickerColumnChange(e) {
    var that = this
    console.log('修改的列column为', e.detail.column, '，值value为', e.detail.value)
    const data = {
      multiArray: this.data.multiArray,
      multiIndex: this.data.multiIndex
    }
    var multiArray = that.data.multiArray
    var multiIndex = that.data.multiIndex

    // console.log(that.data.multiArray[e.detail.column][e.detail.value].name)

    data.multiIndex[e.detail.column] = e.detail.value
    switch (e.detail.column) {
      case 0:
        console.log('case 0 begin e', 'data.multiindex:', data.multiIndex, 'multiArray:', data.multiArray)
        var brand = that.data.multiArray[e.detail.column][e.detail.value].code
        var type = 'goods'
        var key1 = 'multiArray[1]'
        console.log('case 0 brand:', brand, 'key:', key1)
        that.get_goodsdisplayclass(brand)
        // 根据品牌去显示类别
        // var brand = that.data.multiArray[e.detail.column][e.detail.value].code
        // var type='goods'
        // var key1 = 'multiArray[0]'
        // console.log('case 0 brand:',brand,'key:',key1)
        // viputil.get_displayclass(that,type,brand,key1)
        // console.log(that.data.multiIndex)
        data.multiIndex[1] = 0
        data.multiIndex[2] = 0
        break
      case 1:
        console.log('case 1 begin e', e)
        console.log('data.multiindex:', data.multiIndex, 'multiArray:', data.multiArray)
        // 根据显示类别显示明细
        // var brand = that.data.multiArray[e.detail.column][e.detail.value].code
        var brand = that.data.multiArray[0][that.data.multiIndex[0]].code
        var brandname = that.data.multiArray[0][that.data.multiIndex[0]].name
        // var type = 'goods'
        var displayclass = that.data.multiArray[1][that.data.multiIndex[1]].code
        var displayclassname = that.data.multiArray[1][that.data.multiIndex[1]].name
        // var key2 = 'multiArray[1]'
        // viputil.get_itemlist_brandanddisplayclasse(that, type, brand, key2)
        console.log('brand name:', brandname, ' displayclass name:', displayclassname)

        var options = {
          brand: brand,
          displayclass: displayclass
        }
        that.get_itemlist_brandanddisplayclasse(options)
        data.multiIndex[2] = 0
        break
      case 2:
        console.log('case 2 begin e', e)
    }
    // console.log('case 0 ,end :',data)
    this.setData(data)
  },

  get_serviecebrand: function () {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_brandlist'
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        type: 'serviece'
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        var key = 'multiArray[0]'
        that.setData({
          [key]: res.data
        })
        if (res.data.length > 0) {
          var brand = that.data.multiArray[0][0].code
          // console.log('get goodsdisplayclass brand:', brand)
          that.get_goodsdisplayclass(brand);
        } else {
          var key1 = 'multiArray[1]'
          var key2 = 'multiArray[2]'
          that.setData({
            [key1]: [],
            [key2]: []
          })
        }

      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }
    })
  },
  get_goodsdisplayclass: function (options) {
    console.log('get_goodsdisplayclass options:', options)
    var that = this;
    var app = getApp();
    var brand = options;
    var url = app.globalData.host + 'baseinfo/get_displayclass_bybrand'
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        type: 'serviece',
        brand: brand,
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log('get displayclass by brand:', res.data)
        var key = 'multiArray[1]'
        that.setData({
          [key]: res.data
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
  get_itemlist_brandanddisplayclasse: function (options) {
    var that = this;
    var app = getApp();
    var url = app.globalData.host + 'baseinfo/get_itemlist_brandanddisplayclasse';
    var brand = options.brand;
    var displayclass = options.displayclass
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        type: 'serviece',
        brand: brand,
        displayclass1: displayclass
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        var key = 'multiArray[2]';
        that.setData({
          [key]: res.data,
          goodslist: res.data
        });
        var fields = [
          {
            field: 'ttype',
            value: 'S'
          },
          {
            field: 'stype',
            value: 'N'
          },
          {
            field: 'secdisc',
            value: 1
          },
          {
            field: 'mondisc',
            value: 0
          },
          {
            field: 'qty',
            value: 0
          },
          {
            field: 'amount',
            value: 0
          },
          {
            field: 'pmcode',
            value: ''
          },
          {
            field: 'seccode',
            value: ''
          }, ,
          {
            field: 'thrcode',
            value: ''
          }
        ]
        for (var goods in that.data.goodslist) {
          for (var item in fields) {
            var key = 'goodslist[' + goods + '].' + fields[item].field
            console.log('key', key)
            that.setData({
              [key]: fields[item].value
            })
          }
        }

      },
      fail: function (res) {
        console.log("failed")
      },
      complete: function (res) {
        console.log("finished")
      }
    })
  },
  get_serviecelist_bykeyword: function () {
    var that = this;
    var app = getApp();
    // var url = app.globalData.host + 'baseinfo/get_goodslist_bykeyword';
    var url = app.globalData.host + 'baseinfo/get_serviece';
    // console.log(xinqu)
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: app.globalData.company,
        // ecode: app.globalData.ecode,
        searchvalue: that.data.searchValue

      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        that.setData({
          fail: false,
          srvList: res.data
        })
        console.log('1')
        that.init_srvList()
        console.log('2')
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
  // 搜索入口  
  wxSearchTabServiece: function () {
    wx.redirectTo({
      url: '../serviecesearch/serviecesearch'
    })
  }
})