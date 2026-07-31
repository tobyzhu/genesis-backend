var util = require('../../utils/util.js');

Page({
  data: {
    instoreVipList: [],
    instoreVipLoaded: false,
    psstatusLabels: {
      '10': '已开单',
      '20': '配料完成',
      '30': '配料确认',
      '40': '服务完成确认',
      '50': '客户确认',
      '60': '挂账'
    }
  },

  onLoad: function () {
    this.loadList();
  },

  onShow: function () {
    this.loadList();
  },

  onPullDownRefresh: function () {
    var that = this;
    util.getInstoreVipList(that);
    setTimeout(function () {
      wx.stopPullDownRefresh();
    }, 800);
  },

  loadList: function () {
    util.getInstoreVipList(this);
  },

  onTapInstoreVip: function (e) {
    var app = getApp();
    var uuid = e.currentTarget.dataset.vipuuid;
    var vipitem = e.currentTarget.dataset.vipitem || {};
    if (!uuid) {
      return;
    }
    app.globalData.currentvip = Object.assign({}, vipitem, { uuid: uuid });
    wx.navigateTo({
      url: '/vip/vip?uuid=' + encodeURIComponent(uuid)
    });
  }
});
