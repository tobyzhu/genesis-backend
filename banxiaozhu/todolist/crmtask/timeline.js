var crm = require('../../utils/crm.js');

Page({
  data: {
    vipuuid: '',
    keyword: '',
    vips: [],
    logs: [],
    detail: '',
    nextdate: '',
    loading: false,
  },

  onLoad: function (options) {
    if (options.vipuuid) {
      this.setData({ vipuuid: options.vipuuid });
      this.loadTimeline();
    }
  },

  onKeywordInput: function (e) {
    this.setData({ keyword: e.detail.value });
  },

  onSearchVip: function () {
    var that = this;
    var keyword = this.data.keyword.trim();
    if (!keyword) return;
    crm
      .mpVipSearch(keyword)
      .then(function (res) {
        that.setData({ vips: res.data || [] });
      })
      .catch(function (err) {
        wx.showToast({ title: (err && err.error) || '搜索失败', icon: 'none' });
      });
  },

  onSelectVip: function (e) {
    var uuid = e.currentTarget.dataset.uuid;
    this.setData({ vipuuid: uuid, vips: [], keyword: '' });
    this.loadTimeline();
  },

  loadTimeline: function () {
    var that = this;
    if (!this.data.vipuuid) return;
    this.setData({ loading: true });
    crm
      .mpTimeline({ vipuuid: this.data.vipuuid })
      .then(function (res) {
        that.setData({ logs: res.data || [], loading: false });
      })
      .catch(function (err) {
        that.setData({ loading: false });
        wx.showToast({ title: (err && err.error) || '加载失败', icon: 'none' });
      });
  },

  onDetailInput: function (e) {
    this.setData({ detail: e.detail.value });
  },

  onNextdateChange: function (e) {
    this.setData({ nextdate: e.detail.value });
  },

  addLog: function () {
    var that = this;
    var detail = this.data.detail.trim();
    if (!detail) {
      wx.showToast({ title: '请填写记录内容', icon: 'none' });
      return;
    }
    crm
      .mpTimelineCreate({
        vipuuid: this.data.vipuuid,
        casetype: '10',
        detail: detail,
        nextdate: this.data.nextdate,
      })
      .then(function () {
        that.setData({ detail: '', nextdate: '' });
        wx.showToast({ title: '已记录', icon: 'success' });
        that.loadTimeline();
      })
      .catch(function (err) {
        wx.showToast({ title: (err && err.error) || '保存失败', icon: 'none' });
      });
  },
});
