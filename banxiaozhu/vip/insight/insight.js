var util = require('../../utils/util.js');
var app = getApp();

Page({
  data: {
    dateRangeOptions: [
      { label: '近3个月', months: 3 },
      { label: '近6个月', months: 6 },
      { label: '近12个月', months: 12 },
      { label: '全部', months: 0 },
    ],
    dateRangeIndex: 2,
    loading: false,
    hasData: false,
    insight: {
      total_visits: 0,
      total_spent: '0',
      avg_spend: '0',
      last_visit: '暂无',
      avg_cycle: '—',
      days_since: '暂无',
      card_count: '0张',
      preferred_items: [],
      preferred_employee: null,
    },
  },

  onLoad: function () {
    this.loadInsight();
  },

  bindDateRangeChange: function (e) {
    this.setData({ dateRangeIndex: e.detail.value }, function () {
      this.loadInsight();
    }.bind(this));
  },

  loadInsight: function () {
    var that = this;
    var company = app.globalData.company;
    var vip = app.globalData.currentvip;
    if (!vip || !vip.uuid) {
      that.setData({ loading: false, hasData: false });
      return;
    }
    var vipuuid = vip.uuid;
    // 去掉 uuid 中的连字符
    if (vipuuid.indexOf('-') > -1) {
      vipuuid = vipuuid.split('-').join('');
    }

    var opt = that.data.dateRangeOptions[that.data.dateRangeIndex];
    var now = new Date();
    var dateTo = util.datetostr(now);
    var dateFrom;
    if (opt.months > 0) {
      var d = new Date(now);
      d.setMonth(d.getMonth() - opt.months);
      dateFrom = util.datetostr(d);
    } else {
      dateFrom = '20100101';
    }
    // format to YYYYMMDD
    dateFrom = dateFrom.replace(/-/g, '');
    dateTo = dateTo.replace(/-/g, '');

    that.setData({ loading: true });

    var url = app.globalData.host + 'crm/vip_insight/';
    wx.request({
      method: 'GET',
      url: url,
      data: {
        company: company,
        vipuuid: vipuuid,
        date_from: dateFrom,
        date_to: dateTo,
      },
      header: { 'content-type': 'application/json' },
      success: function (res) {
        if (res.statusCode === 200 && res.data) {
          var raw = res.data;
          var insight = that.formatInsight(raw);
          that.setData({
            insight: insight,
            hasData: true,
            loading: false,
          });
        } else {
          that.setData({ loading: false, hasData: false });
        }
      },
      fail: function () {
        that.setData({ loading: false, hasData: false });
      },
    });
  },

  formatInsight: function (raw) {
    var total_spent = parseFloat(raw.total_spent || 0).toFixed(0);
    // 统计周期有数据才算有数据
    var hasData = raw.total_visits > 0;

    // 最近到店
    var last_visit = '暂无';
    if (raw.last_visit_date) {
      var s = String(raw.last_visit_date);
      if (s.length === 8) {
        last_visit = s.slice(0, 4) + '-' + s.slice(4, 6) + '-' + s.slice(6, 8);
      } else {
        last_visit = s;
      }
    }

    // 距上次到店
    var days_since = '暂无';
    if (raw.days_since_last_visit != null && raw.days_since_last_visit >= 0) {
      days_since = raw.days_since_last_visit + '天前';
    }

    // 平均周期
    var avg_cycle = '—';
    if (raw.avg_visit_cycle != null) {
      avg_cycle = raw.avg_visit_cycle + '天';
    }

    // 活跃卡数
    var card_count = (raw.card_count != null ? raw.card_count : 0) + '张';

    // 偏好项目
    var preferred_items = [];
    if (raw.preferred_items && raw.preferred_items.length) {
      for (var i = 0; i < raw.preferred_items.length; i++) {
        var item = raw.preferred_items[i];
        preferred_items.push({
          srvcode: item.srvcode || '',
          srvname: item.srvname || '',
          count: item.count || 0,
          total: parseFloat(item.total_amount || 0).toFixed(0),
        });
      }
    }

    // 偏好员工
    var preferred_employee = null;
    if (raw.preferred_employee && raw.preferred_employee.ecode) {
      preferred_employee = {
        ecode: raw.preferred_employee.ecode,
        ename: raw.preferred_employee.ename || raw.preferred_employee.ecode,
        count: raw.preferred_employee.count || 0,
      };
    }

    return {
      total_visits: raw.total_visits || 0,
      total_spent: total_spent,
      avg_spend: hasData ? parseFloat(raw.avg_spend || 0).toFixed(0) : '0',
      last_visit: last_visit,
      avg_cycle: avg_cycle,
      days_since: days_since,
      card_count: card_count,
      preferred_items: preferred_items,
      preferred_employee: preferred_employee,
    };
  },
});
