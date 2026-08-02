var crm = require('../../utils/crm.js');

var CHANNELS = [
  { value: '10', label: '电话' },
  { value: '20', label: '微信' },
  { value: '30', label: '短信' },
  { value: '40', label: '到店' },
  { value: '90', label: '其他' },
];
var OUTCOMES = [
  { value: '10', label: '已联系' },
  { value: '20', label: '未接通' },
  { value: '30', label: '待跟进' },
  { value: '40', label: '已拒绝' },
  { value: '50', label: '已预约' },
];

Page({
  data: {
    task: null,
    attempts: [],
    channels: CHANNELS,
    outcomes: OUTCOMES,
    channelIndex: 0,
    outcomeIndex: 1,
    detail: '',
    nextdate: '',
    suggestions: [],
    suggestLoading: false,
    saving: false,
    loading: true,
  },

  onLoad: function (options) {
    this.taskuuid = options.taskuuid || '';
    this.loadTask();
  },

  loadTask: function () {
    var that = this;
    this.setData({ loading: true });
    crm
      .mpTaskDetail(this.taskuuid)
      .then(function (res) {
        that.setData({
          task: res.data || null,
          attempts: (res.data && res.data.attempts) || [],
          loading: false,
        });
      })
      .catch(function (err) {
        that.setData({ loading: false });
        wx.showToast({ title: (err && err.error) || '加载失败', icon: 'none' });
      });
  },

  onChannelChange: function (e) {
    this.setData({ channelIndex: Number(e.detail.value) });
  },

  onOutcomeChange: function (e) {
    this.setData({ outcomeIndex: Number(e.detail.value) });
  },

  onDetailInput: function (e) {
    this.setData({ detail: e.detail.value });
  },

  onNextdateChange: function (e) {
    this.setData({ nextdate: e.detail.value });
  },

  saveAttempt: function () {
    var that = this;
    var detail = this.data.detail.trim();
    if (!detail) {
      wx.showToast({ title: '请填写触达内容', icon: 'none' });
      return;
    }
    this.setData({ saving: true });
    crm
      .mpTaskAttempt(this.taskuuid, {
        channel: CHANNELS[this.data.channelIndex].value,
        outcome: OUTCOMES[this.data.outcomeIndex].value,
        detail: detail,
        nextdate: this.data.nextdate,
      })
      .then(function () {
        that.setData({ detail: '', saving: false });
        wx.showToast({ title: '已保存', icon: 'success' });
        that.loadTask();
      })
      .catch(function (err) {
        that.setData({ saving: false });
        wx.showToast({ title: (err && err.error) || '保存失败', icon: 'none' });
      });
  },

  completeTask: function () {
    var that = this;
    wx.showModal({
      title: '完成回访',
      content: '确认完成本次回访？当前输入内容会作为完成备注。',
      success: function (r) {
        if (!r.confirm) return;
        crm
          .mpTaskComplete(that.taskuuid, { note: that.data.detail })
          .then(function () {
            wx.showToast({ title: '已完成', icon: 'success' });
            that.setData({ detail: '' });
            that.loadTask();
          })
          .catch(function (err) {
            wx.showToast({ title: (err && err.error) || '操作失败', icon: 'none' });
          });
      },
    });
  },

  togglePause: function () {
    var that = this;
    var task = this.data.task;
    var next = task && task.status === '40' ? '20' : '40';
    crm
      .mpTaskStatus(this.taskuuid, { status: next })
      .then(function () {
        wx.showToast({ title: next === '40' ? '已暂停' : '已恢复', icon: 'success' });
        that.loadTask();
      })
      .catch(function (err) {
        wx.showToast({ title: (err && err.error) || '操作失败', icon: 'none' });
      });
  },

  onSuggest: function () {
    var that = this;
    this.setData({ suggestLoading: true });
    crm
      .mpTaskSuggest(this.taskuuid, {
        channel: CHANNELS[this.data.channelIndex].value,
        outcome: OUTCOMES[this.data.outcomeIndex].value,
        variants: 3,
      })
      .then(function (res) {
        that.setData({
          suggestions: (res.data && res.data.variants) || [],
          suggestLoading: false,
        });
      })
      .catch(function (err) {
        that.setData({ suggestLoading: false });
        wx.showToast({ title: (err && err.error) || '话术生成失败', icon: 'none' });
      });
  },

  onUseSuggestion: function (e) {
    var text = e.currentTarget.dataset.text;
    this.setData({
      detail: this.data.detail ? this.data.detail + '\n' + text : text,
    });
  },

  onCopySuggestion: function (e) {
    wx.setClipboardData({
      data: e.currentTarget.dataset.text,
      success: function () {
        wx.showToast({ title: '已复制', icon: 'success' });
      },
    });
  },

  onDeleteAttempt: function (e) {
    var that = this;
    var attemptUuid = e.currentTarget.dataset.uuid;
    if (!attemptUuid) return;
    wx.showModal({
      title: '删除触达记录',
      content: '确定删除这条触达记录？客户流水中的对应记录也会移除。',
      success: function (r) {
        if (!r.confirm) return;
        crm
          .mpTaskAttemptDelete(that.taskuuid, attemptUuid)
          .then(function () {
            wx.showToast({ title: '已删除', icon: 'success' });
            that.loadTask();
          })
          .catch(function (err) {
            wx.showToast({ title: (err && err.error) || '删除失败', icon: 'none' });
          });
      },
    });
  },

  onVipDetail: function () {
    var task = this.data.task;
    if (!task || !task.vip || !task.vip.uuid) return;
    var that = this;
    crm
      .mpVipDetail(task.vip.uuid)
      .then(function (vip) {
        var gd = getApp().globalData;
        gd.currentvip = vip;
        gd.currentvipuuid_s = task.vip.uuid;
        gd.currentvipuuid_u = task.vip.uuid.split('-').join('');
        wx.navigateTo({ url: '/vip/vipinfo/vipinfo' });
      })
      .catch(function (err) {
        wx.showToast({ title: (err && err.error) || '客户详情加载失败', icon: 'none' });
      });
  },

  onTimeline: function () {
    var task = this.data.task;
    if (task && task.vip && task.vip.uuid) {
      wx.navigateTo({ url: '/todolist/crmtask/timeline?vipuuid=' + task.vip.uuid });
    }
  },
});
