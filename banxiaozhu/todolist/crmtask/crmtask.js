var app = getApp();
var crm = require('../../utils/crm.js');

var STATUSES = [
  { key: '', label: '全部' },
  { key: 'today', label: '今日' },
  { key: 'overdue', label: '超期' },
  { key: 'in_progress', label: '进行中' },
  { key: 'completed', label: '已完成' },
];

Page({
  data: {
    storeLabel: '',
    counts: { total: 0, today: 0, overdue: 0, in_progress: 0, completed: 0 },
    groups: [],
    statuses: STATUSES,
    activeStatus: '',
    activeGroup: '',
    tasks: [],
    total: 0,
    page: 1,
    pageSize: 20,
    loading: false,
    keyword: '',
    error: '',
  },

  onLoad: function () {
    var gd = app.globalData || {};
    this.setData({
      storeLabel: (gd.storename || gd.storecode || '') + '',
    });
    this.loadSummary();
    this.loadTasks(true);
  },

  onPullDownRefresh: function () {
    var that = this;
    this.loadSummary();
    this.loadTasks(true, function () {
      wx.stopPullDownRefresh();
    });
  },

  onReachBottom: function () {
    if (this.data.tasks.length < this.data.total) {
      this.loadTasks(false);
    }
  },

  loadSummary: function () {
    var that = this;
    crm
      .mpTaskSummary({})
      .then(function (res) {
        var d = res.data || {};
        that.setData({
          counts: d.counts || { total: 0, today: 0, overdue: 0, in_progress: 0, completed: 0 },
          groups: d.groups || [],
          error: '',
        });
      })
      .catch(function (err) {
        that.setData({ error: (err && err.error) || '统计加载失败' });
      });
  },

  loadTasks: function (reset, done) {
    var that = this;
    var page = reset ? 1 : this.data.page + 1;
    this.setData({ loading: true });
    var params = {
      page: page,
      page_size: this.data.pageSize,
      rule_type: this.data.activeGroup,
      keyword: this.data.keyword,
    };
    var filterParams = crm.mpTaskFilterParams(this.data.activeStatus);
    for (var k in filterParams) {
      if (filterParams.hasOwnProperty(k)) {
        params[k] = filterParams[k];
      }
    }
    crm
      .mpTaskList(params)
      .then(function (res) {
        var d = res.data || {};
        var items = d.items || [];
        var tasks = reset ? items : that.data.tasks.concat(items);
        that.setData({
          tasks: tasks,
          total: d.total || 0,
          page: page,
          loading: false,
          error: '',
        });
        if (done) done();
      })
      .catch(function (err) {
        that.setData({ loading: false, error: (err && err.error) || '任务加载失败' });
        if (done) done();
      });
  },

  onStatusTap: function (e) {
    var key = e.currentTarget.dataset.key;
    this.setData({ activeStatus: key });
    this.loadTasks(true);
  },

  onGroupTap: function (e) {
    var key = e.currentTarget.dataset.key;
    this.setData({ activeGroup: key });
    this.loadTasks(true);
  },

  onKeywordInput: function (e) {
    this.setData({ keyword: e.detail.value });
  },

  onSearch: function () {
    this.loadTasks(true);
  },

  onTaskTap: function (e) {
    var uuid = e.currentTarget.dataset.uuid;
    wx.navigateTo({ url: '/todolist/crmtask/detail?taskuuid=' + uuid });
  },

  onVipTap: function (e) {
    var uuid = e.currentTarget.dataset.uuid;
    if (!uuid) return;
    var that = this;
    crm
      .mpVipDetail(uuid)
      .then(function (vip) {
        var gd = app.globalData;
        gd.currentvip = vip;
        gd.currentvipuuid_s = uuid;
        gd.currentvipuuid_u = uuid.split('-').join('');
        wx.navigateTo({ url: '/vip/vipinfo/vipinfo' });
      })
      .catch(function (err) {
        wx.showToast({ title: (err && err.error) || '客户详情加载失败', icon: 'none' });
      });
  },

  onOpenLifecycle: function () {
    wx.navigateTo({ url: '/assistant/lifecycle/lifecycle' });
  },

  onOpenAssistant: function () {
    wx.navigateTo({ url: '/assistant/chat/chat?profile=vip_crm' });
  },

  onOpenTimeline: function () {
    wx.navigateTo({ url: '/todolist/crmtask/timeline' });
  },
});
