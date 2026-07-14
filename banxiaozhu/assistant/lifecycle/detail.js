var assistant = require('../../utils/assistant.js');

var SEGMENT_LABEL = {
  active: '活跃',
  at_risk: '流失预警',
  sleeping: '休眠',
  never_visited: '未消费新客',
};

var TREND_LABEL = {
  declining: '下降',
  growing: '上升',
  stable: '持平',
};

Page({
  data: {
    loading: true,
    error: '',
    vip: null,
    segmentLabel: '',
    amountTrendLabel: '',
    visitTrendLabel: '',
  },

  onLoad: function (options) {
    var uuid = (options && options.vipuuid) || '';
    if (!uuid) {
      this.setData({ loading: false, error: '缺少会员参数' });
      return;
    }
    this.loadDetail(uuid);
  },

  loadDetail: function (vipuuid) {
    var that = this;
    that.setData({ loading: true, error: '' });
    assistant
      .mpLifecycleOne({ vipuuid: vipuuid })
      .then(function (res) {
        var row = res.data || {};
        that.setData({
          loading: false,
          vip: row,
          segmentLabel: SEGMENT_LABEL[row.segment] || row.segment,
          amountTrendLabel: TREND_LABEL[row.amount_trend] || row.amount_trend,
          visitTrendLabel: TREND_LABEL[row.visit_trend] || row.visit_trend,
        });
      })
      .catch(function (err) {
        that.setData({
          loading: false,
          error: (err && err.error) || '加载失败',
        });
      });
  },

  onAskAssistant: function () {
    var vip = this.data.vip;
    if (!vip) return;
    wx.navigateTo({
      url:
        '/assistant/chat/chat?profile=vip_crm&vipuuid=' +
        encodeURIComponent(vip.vipuuid || ''),
    });
  },
});
