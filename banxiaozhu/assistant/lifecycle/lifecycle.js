var assistant = require('../../utils/assistant.js');
var app = getApp();

var SEGMENTS = [
  { id: '', label: '全部' },
  { id: 'at_risk', label: '预警' },
  { id: 'sleeping', label: '休眠' },
  { id: 'active', label: '活跃' },
  { id: 'high_value', label: '高价值' },
];

var SEGMENT_LABEL = {
  active: '活跃',
  at_risk: '预警',
  sleeping: '休眠',
  never_visited: '新客',
};

Page({
  data: {
    segments: SEGMENTS,
    activeSegment: '',
    loading: false,
    error: '',
    config: {},
    summary: {},
    vips: [],
    storeLabel: '',
    migrations: [],
    migrateSummary: '',
    showMigrations: false,
  },

  onLoad: function () {
    var gd = app.globalData || {};
    this.setData({
      storeLabel: (gd.storename || gd.storecode || '') + '',
    });
    this.loadData();
    this.loadMigrations();
  },

  loadMigrations: function () {
    var that = this;
    assistant
      .mpLifecycleMigrations({ days_back: 7, transition: 'active->at_risk', limit: 30 })
      .then(function (res) {
        var d = res.data || {};
        if (d.error) return;
        var rows = d.migrations || [];
        that.setData({
          migrations: rows,
          migrateSummary:
            '近7天新进入预警 ' + rows.length + ' 人（' + (d.from_date || '') + '→' + (d.to_date || '') + '）',
          showMigrations: rows.length > 0,
        });
      })
      .catch(function () {});
  },

  onPullDownRefresh: function () {
    var that = this;
    this.loadData(function () {
      wx.stopPullDownRefresh();
    });
  },

  onSegmentTap: function (e) {
    var seg = e.currentTarget.dataset.id;
    if (seg === this.data.activeSegment) return;
    this.setData({ activeSegment: seg });
    this.loadData();
  },

  loadData: function (done) {
    var that = this;
    var gd = app.globalData || {};
    if (!gd.company || !gd.storecode || !(gd.ecode || gd.usercode)) {
      that.setData({ error: '请先登录门店账号' });
      if (done) done();
      return;
    }
    that.setData({ loading: true, error: '' });
    assistant
      .mpLifecycleBatch({
        segment: that.data.activeSegment,
        limit: 100,
      })
      .then(function (res) {
        var d = res.data || {};
        var sum = d.summary || {};
        var counts = sum.segment_counts || {};
        var vips = (d.vips || []).map(function (r) {
          r.segment_label = SEGMENT_LABEL[r.segment] || r.segment;
          if (r.value_tier === 'high_value') {
            r.segment_label = '高价值';
          }
          return r;
        });
        that.setData({
          loading: false,
          config: res.config || {},
          summary: {
            active: counts.active || 0,
            at_risk: counts.at_risk || 0,
            sleeping: counts.sleeping || 0,
            never_visited: counts.never_visited || 0,
            high_value: counts.high_value || 0,
            returned: sum.returned_count || vips.length,
            total: sum.total_vip_checked || 0,
          },
          vips: vips,
        });
        if (done) done();
      })
      .catch(function (err) {
        that.setData({
          loading: false,
          error: (err && err.error) || '加载失败',
        });
        if (done) done();
      });
  },

  onVipTap: function (e) {
    var uuid = e.currentTarget.dataset.uuid;
    if (!uuid) return;
    wx.navigateTo({
      url: '/assistant/lifecycle/detail?vipuuid=' + encodeURIComponent(uuid),
    });
  },

  onAskAssistant: function () {
    wx.navigateTo({
      url: '/assistant/chat/chat?profile=vip_crm',
    });
  },

  onCreateCrmTasks: function () {
    var that = this;
    wx.showModal({
      title: '生成回访任务',
      content: '为我的预警客户生成 CRM 回访任务？',
      success: function (res) {
        if (!res.confirm) return;
        wx.showLoading({ title: '生成中…', mask: true });
        assistant
          .mpLifecycleCrmTasks({ segment: 'at_risk', dry_run: false, limit: 30 })
          .then(function (data) {
            wx.hideLoading();
            var r = data.result || {};
            var created = r.created || 0;
            var skipped = r.skipped || 0;
            wx.showModal({
              title: '已生成 ' + created + ' 条',
              content: skipped ? '跳过 ' + skipped + ' 条（已有未完成任务）' : '可在「计划回访」中跟进',
              confirmText: '去查看',
              cancelText: '留在此页',
              success: function (m) {
                if (m.confirm) {
                  wx.navigateTo({ url: '/todolist/planvipcase/planvipcase' });
                }
              },
            });
          })
          .catch(function (err) {
            wx.hideLoading();
            wx.showToast({ title: (err && err.error) || '失败', icon: 'none' });
          });
      },
    });
  },

  onOpenPlanVipCase: function () {
    wx.navigateTo({ url: '/todolist/planvipcase/planvipcase' });
  },
});
