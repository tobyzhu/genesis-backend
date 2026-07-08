// todolist/crmcasedetail/crmcasedetail.js
// import { $wuxSelect } from '../../wux/packages/lib/index'

Page({

  /**
   * 页面的初始数据
   */
  data: {
    value1: '',
    title1: '',
    value2: '',
    title2: '',
    value3: '',
    title3: '',
    parent:'',
    methos:'',
    options1: [
      {
      title: '正常',
      value: '1',
      },
      {
        title: '按时到店后,有等待',
        value: '2',
      },
      {
        title: '服务感受一般',
        value: '3',
      },
      {
        title: '不专业',
        value: '4',
      },
    ],
    options2: [
      {
        title: '已使用',
        value: '1',
      },
      {
        title: '未使用',
        value: '2',
      },
      {
        title: '未提货',
        value: '3',
      },
      {
        title: '已收货',
        value: '4',
      },
    ],  
    options3: [
      {
        title: '有过敏,邀请到店处理',
        value: '1',
      },
      {
        title: '有过敏,在家冰敷处理',
        value: '2',
      },
      {
        title: '无过敏',
        value: '3',
      },
    ],   
    options4: [
      {
        title: '全素食',
        value: '1',
      },
      {
        title: '配合营养餐',
        value: '2',
      },
      {
        title: '每周2次以上运动',
        value: '3',
      },
      {
        title: '每周瑜伽',
        value: '4',
      },
    ],             
    theme:[],
    detail:[],
    crmcase:{},
    theme:[
      {
        id:1,
       theme:'产品使用情况',
       title:'',
       value:'',
       click:'',
       detail:['有过敏','已使用','未使用','要补货','注意按摩手法']
       },
      {
        id:2, 
        theme:'有无过敏现象',
        detai:[]
        },
      {id:3, theme:'是否坚持使用'},
      {id:4, theme:'是否注意运动与饮食'},
      {id:5, theme:'下次预约时间'}
    ],
    crmcasedetail:[
      {
        id:1,
        actiontype:'产品有没有使用',
        theme:'产品使用情况',
        detail:[
          {}
        ],
        ecode:''
      },
      {
        id: 1,
        actiontype: '回访',
        theme: '?',
        detail: '',
        ecode: ''
      },
    ],
    crmcaseuuid:'',
    vname:'',
    casedesc:'',
    detaildescription:'',
    term:['满意没有问题','皮肤有过敏','预约时间到但是还是等了一下'],
    selectterm:'',
    termIndex:0,
    returndata:{},
    ecode:'',
    empluuid:'',
    crmcasedetailuuid:''
  },

  /**
   * 生命周期函数--监听页面加载
   */
  onLoad: function (options) {
    var that = this;
    var parent = options.parent;
    that.setData({
      parent: parent
    })
    
    console.log(options);
    if (that.data.parent == 'preview') {
      var crmcasedetailuuid = options.crmcasedetailuuid;
      that.setData({
        method:'PUT',
        crmcasedetailuuid: options.crmcasedetailuuid
      })
      console.log('from preview',crmcasedetailuuid);
      that.get_crmcasedetail(crmcasedetailuuid);
    } else if (that.data.parent ='crmcase') {
      console.log('from list',options);
      this.setData({
        method:'POST',
        crmcase: options.crmcase,
        crmcaseuuid: options.uuid,
        vname: options.vname,
        casedesc: options.casedesc
      });
      console.log(this.data.crmcase)
    } else {
      console.log(options)
    }

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
  bindTermChange: function (e) {
    console.log('picker Term 发生选择改变，携带值为', e.detail.value);
    console.log(e);
    var that = this;
    var detaildescription = that.data.detaildescription +' '+ that.data.term[e.detail.value];
    console.log(this.data.term[e.detail.value],detaildescription);
    this.setData({
      termIndex: e.detail.value,
      detaildescription: detaildescription
    })
  },
  addCrmCaseDetail: function(empluuid){
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company
    var storecode = app.globalData.storecode
    var ecode = app.globalData.ecode
    var that = this;
    var url =  host + "crm/AddCrmCaseDetail"
    console.log(url);
    wx.request({
      method: 'POST',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        storecode: storecode,
        caseid: that.data.crmcaseuuid,
        detaildescription: that.data.detaildescription,
        // ecode:ecode
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function(res) {
        console.log(res.data)
        wx.showToast({
          title: '已完成',
          icon: 'success',
          duration: 3000
        });
      },
      fail: function(res){
        console.log("failed")
        wx.showToast({
          title: '保存失败',
          icon: 'failed',
          duration: 3000
        });
      },
      complete:function(res){
        console.log("finished")
      }

    })    
  },
  updateCrmCaseDetail: function (e) {
    var app = getApp();
    var host = app.globalData.host;
    var company = app.globalData.company
    var storecode = app.globalData.storecode
    var ecode = app.globalData.ecode
    var that = this;
    var url = host + "crm/UpdateCrmCaseDetail"
    console.log(url);
    wx.request({
      method: 'PUT',
      url: url, //仅为示例，并非真实的接口地址
      data: {
        company: company,
        storecode: storecode,
        crmcasedetailuuid:  that.data.crmcasedetailuuid,
        detaildescription: that.data.detaildescription,
        // ecode:ecode
      },
      header: {
        'content-type': 'application/json' // 默认值
        // 'content-type': 'application /x-www-form-urlencoded;charset=utf-8'
      },
      success: function (res) {
        console.log(res.data)
        wx.showToast({
          title: '已完成',
          icon: 'success',
          duration: 3000
        });
      },
      fail: function (res) {
        console.log("failed")
        wx.showToast({
          title: '保存失败',
          icon: 'failed',
          duration: 3000
        });
      },
      complete: function (res) {
        console.log("finished")
      }

    })
  },
  detaildescriptionChange:function(e){
    console.log(e.detail.value)
    var that=this
    that.setData({
      detaildescription: e.detail.value
    })
  },
  onClick1() {
    var that=this;
    $wuxSelect('#wux-select1').open({
      value: this.data.value1,
      multiple: true,
      toolbar: {
        title: '请选择',
        confirmText: '确定',
      },
      options: that.data.options1,
      onChange: (value, index, options) => {
        console.log('onChange', value, index, options)
        this.setData({
          value1: value,
          title1: index.map((n) => options[n].title),
          // detaildescription: that.data.detaildescription + index.map((n) => options[n].title),
        })
      },
      onConfirm: (value, index, options) => {
        console.log('onConfirm', value, index, options)
        this.setData({
          value1: value,
          title1: index.map((n) => options[n].title),
          detaildescription: that.data.detaildescription + ','+ index.map((n) => options[n].title),          
        })
      },
    })
  }, 
  onClick2() {
    var that = this;
    $wuxSelect('#wux-select1').open({
      value: this.data.value2,
      multiple: true,
      toolbar: {
        title: '请选择',
        confirmText: '确定',
      },
      options: that.data.options2,
      onChange: (value, index, options) => {
        console.log('onChange', value, index, options)
        this.setData({
          value2: value,
          title2: index.map((n) => options[n].title),
          // detaildescription: that.data.detaildescription + index.map((n) => options[n].title),          
        })
      },
      onConfirm: (value, index, options) => {
        console.log('onConfirm', value, index, options)
        this.setData({
          value2: value,
          title2: index.map((n) => options[n].title),
          detaildescription: that.data.detaildescription + ',' + index.map((n) => options[n].title),          
        })
      },
    })
  },   
  onClick3() {
    var that=this;
    $wuxSelect('#wux-select3').open({
      value: this.data.value3,
      multiple: true,
      toolbar: {
        title: '请选择',
        confirmText: '确定',
      },
      options: that.data.options3,
      onChange: (value, index, options) => {
        console.log('onChange', value, index, options)
        this.setData({
          value3: value,
          title3: index.map((n) => options[n].title),
          // detaildescription: that.data.detaildescription + index.map((n) => options[n].title),          
        })
      },
      onConfirm: (value, index, options) => {
        console.log('onConfirm', value, index, options)
        this.setData({
          value3: value,
          title3: index.map((n) => options[n].title),
          detaildescription: that.data.detaildescription + ',' + index.map((n) => options[n].title),          
        })
      },
    })
  },  
  onClick4() {
    var that=this;
    $wuxSelect('#wux-select4').open({
      value: this.data.value4,
      multiple: true,
      toolbar: {
        title: '请选择',
        confirmText: '确定',
      },
      options: that.data.options4,
      onChange: (value, index, options) => {
        console.log('onChange', value, index, options)
        this.setData({
          value4: value,
          title4: index.map((n) => options[n].title),
          // detaildescription: that.data.detaildescription + index.map((n) => options[n].title),          
        })
      },
      onConfirm: (value, index, options) => {
        console.log('onConfirm', value, index, options)
        this.setData({
          value4: value,
          title4: index.map((n) => options[n].title),
          detaildescription: that.data.detaildescription + ',' + index.map((n) => options[n].title),          
        })
      },
    })
  },
  get_crmcasedetail:function(options){
    console.log(options);
    var app = getApp();
    var that=this;
    var host = app.globalData.host;
    var uuid = options    
    var url = host +'crm/get_crmcasedetail_bycaseid';

    wx:wx.request({
      url: url,
      data: {
        company: app.globalData.company,
        uuid : uuid
      },
      header: {
        'content-type': 'application/json' // 默认值
      },
      method: 'GET',
      dataType: 'json',
      responseType: 'text',
      success: function(res) {
        console.log(res);
        that.setData({
          crmcaseuuid: res.data[0].crmcaseuuid,
          vname: res.data[0].vname,
          casedesc: res.data[0].casedesc,
          detaildescription: res.data[0].detaildescription
        })        
      },
      fail: function(res) {},
      complete: function(res) {},
    })
  }    
})