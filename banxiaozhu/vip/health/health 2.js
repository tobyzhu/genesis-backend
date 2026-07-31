var util = require('../../utils/util.js');
var app = getApp();

Page({
  data: {
    showForm: false,
    editing: false,
    editingUuid: '',
    saving: false,
    loading: false,
    records: [],
    // 表单字段
    skinTypeIndex: 0,
    allergies: '',
    bodyConcerns: '',
    contraindications: '',
    notes: '',
    // 选项列表
    skinTypeOptions: [
      { value: '', label: '请选择' },
      { value: 'dry', label: '干性' },
      { value: 'oily', label: '油性' },
      { value: 'mixed', label: '混合性' },
      { value: 'sensitive', label: '敏感性' },
      { value: 'normal', label: '中性' },
      { value: 'other', label: '其他' },
    ],
    allergyOptions: [],
    bodyConcernOptions: [],
    contraindicationOptions: [],
    // 客户信息
    vipuuid: '',
  },

  onLoad: function () {
    var that = this;
    var vip = app.globalData.currentvip;
    if (vip && vip.uuid) {
      var uuid = vip.uuid;
      if (uuid.indexOf('-') > -1) uuid = uuid.split('-').join('');
      that.setData({ vipuuid: uuid });
    }
    this.loadHealthOptions();
    this.loadRecords();
  },

  // ===== 数据加载 =====

  loadHealthOptions: function () {
    var that = this;
    var company = app.globalData.company;
    var host = app.globalData.host;
    var segs = ['health_allergies', 'health_body_concerns', 'health_contraindications'];
    var fields = ['allergyOptions', 'bodyConcernOptions', 'contraindicationOptions'];

    for (var i = 0; i < segs.length; i++) {
      (function (idx) {
        wx.request({
          method: 'GET',
          url: host + 'baseinfo/get_appoption_byseg/',
          data: { company: company, seg: segs[idx] },
          header: { 'content-type': 'application/json' },
          success: function (res) {
            if (res.statusCode === 200 && res.data) {
              var opts = [];
              var list = Array.isArray(res.data) ? res.data : [];
              for (var j = 0; j < list.length; j++) {
                var v = list[j].itemvalues || list[j].itemname || '';
                if (v) opts.push(v);
              }
              var obj = {};
              obj[fields[idx]] = opts;
              that.setData(obj);
            }
          },
        });
      })(i);
    }
  },

  loadRecords: function () {
    var that = this;
    var company = app.globalData.company;
    var vipuuid = that.data.vipuuid;
    if (!vipuuid) return;

    that.setData({ loading: true });

    wx.request({
      method: 'GET',
      url: app.globalData.host + 'crm/health_records/',
      data: { company: company, vipuuid: vipuuid },
      header: { 'content-type': 'application/json' },
      success: function (res) {
        if (res.statusCode === 200 && res.data) {
          var list = Array.isArray(res.data) ? res.data : [];
          var records = [];
          for (var i = 0; i < list.length; i++) {
            records.push(that.formatRecord(list[i]));
          }
          that.setData({ records: records });
        }
        that.setData({ loading: false });
      },
      fail: function () {
        that.setData({ loading: false });
      },
    });
  },

  formatRecord: function (raw) {
    // 肤质标签映射
    var skinMap = {
      'dry': '干性', 'oily': '油性', 'mixed': '混合性',
      'sensitive': '敏感性', 'normal': '中性', 'other': '其他',
    };
    var recordDate = raw.record_date || '';
    if (recordDate.length >= 10) recordDate = recordDate.slice(0, 10);
    return {
      uuid: raw.uuid,
      record_date: raw.record_date || '',
      record_date_display: recordDate,
      skin_type: raw.skin_type || '',
      skin_type_label: skinMap[raw.skin_type] || raw.skin_type || '-',
      allergies: raw.allergies || '',
      body_concerns: raw.body_concerns || '',
      contraindications: raw.contraindications || '',
      notes: raw.notes || '',
    };
  },

  // ===== 表单操作 =====

  showAddForm: function () {
    this.setData({
      showForm: true,
      editing: false,
      editingUuid: '',
      skinTypeIndex: 0,
      allergies: '',
      bodyConcerns: '',
      contraindications: '',
      notes: '',
    });
  },

  cancelForm: function () {
    this.setData({
      showForm: false,
      editing: false,
      editingUuid: '',
    });
  },

  bindSkinTypeChange: function (e) {
    this.setData({ skinTypeIndex: e.detail.value });
  },

  bindAllergiesInput: function (e) {
    this.setData({ allergies: e.detail.value });
  },

  bindBodyConcernsInput: function (e) {
    this.setData({ bodyConcerns: e.detail.value });
  },

  bindContraindicationsInput: function (e) {
    this.setData({ contraindications: e.detail.value });
  },

  bindNotesInput: function (e) {
    this.setData({ notes: e.detail.value });
  },

  toggleTag: function (e) {
    var tag = e.currentTarget.dataset.tag;
    var field = e.currentTarget.dataset.field;
    var current = this.data[field] || '';
    var items = current ? current.split(',').map(function (s) { return s.trim(); }).filter(function (s) { return s; }) : [];

    var idx = items.indexOf(tag);
    if (idx > -1) {
      items.splice(idx, 1);
    } else {
      items.push(tag);
    }
    var obj = {};
    obj[field] = items.join(',');
    this.setData(obj);
  },

  saveRecord: function () {
    var that = this;
    var company = app.globalData.company;
    var skin_type = that.data.skinTypeOptions[that.data.skinTypeIndex].value;
    var allergies = that.data.allergies;
    var body_concerns = that.data.bodyConcerns;
    var contraindications = that.data.contraindications;
    var notes = that.data.notes;

    that.setData({ saving: true });

    var dataObj = {
      company: company,
      vipuuid: that.data.vipuuid,
      skin_type: skin_type,
      allergies: allergies,
      body_concerns: body_concerns,
      contraindications: contraindications,
      notes: notes,
    };

    var method = 'POST';
    var url = app.globalData.host + 'crm/health_records/';

    if (that.data.editing) {
      method = 'PUT';
      url = app.globalData.host + 'crm/health_records/' + that.data.editingUuid + '/';
    }

    wx.request({
      method: method,
      url: url,
      data: JSON.stringify(dataObj),
      header: { 'content-type': 'application/json' },
      success: function (res) {
        if (res.statusCode < 300) {
          wx.showToast({ title: that.data.editing ? '已更新' : '已保存', icon: 'success' });
          that.setData({
            showForm: false,
            editing: false,
            editingUuid: '',
            saving: false,
          });
          that.loadRecords();
        } else {
          wx.showToast({ title: '保存失败', icon: 'none' });
          that.setData({ saving: false });
        }
      },
      fail: function () {
        wx.showToast({ title: '网络异常', icon: 'none' });
        that.setData({ saving: false });
      },
    });
  },

  editRecord: function (e) {
    var uuid = e.currentTarget.dataset.uuid;
    var records = this.data.records;
    var record = null;
    for (var i = 0; i < records.length; i++) {
      if (records[i].uuid === uuid) {
        record = records[i];
        break;
      }
    }
    if (!record) return;

    // 找到肤质索引
    var skinIdx = 0;
    for (var i = 0; i < this.data.skinTypeOptions.length; i++) {
      if (this.data.skinTypeOptions[i].value === record.skin_type) {
        skinIdx = i;
        break;
      }
    }

    this.setData({
      showForm: true,
      editing: true,
      editingUuid: uuid,
      skinTypeIndex: skinIdx,
      allergies: record.allergies || '',
      bodyConcerns: record.body_concerns || '',
      contraindications: record.contraindications || '',
      notes: record.notes || '',
    });
  },

  deleteRecord: function (e) {
    var that = this;
    var uuid = e.currentTarget.dataset.uuid;
    wx.showModal({
      title: '确认删除',
      content: '删除此健康档案记录？',
      success: function (res) {
        if (res.confirm) {
          wx.request({
            method: 'DELETE',
            url: app.globalData.host + 'crm/health_records/' + uuid + '/',
            header: { 'content-type': 'application/json' },
            success: function () {
              wx.showToast({ title: '已删除', icon: 'success' });
              that.loadRecords();
            },
            fail: function () {
              wx.showToast({ title: '删除失败', icon: 'none' });
            },
          });
        }
      },
    });
  },
});
