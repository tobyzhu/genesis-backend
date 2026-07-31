var util = require('../../utils/util.js');

function toNumber(v) {
  var n = parseFloat(v);
  return isNaN(n) ? 0 : n;
}

function parseDateInt(s) {
  var t = String(s || '').replace(/[^0-9]/g, '');
  var n = parseInt(t || '0', 10);
  return isNaN(n) ? 0 : n;
}

/** 后端无法解析卡类名时，用当前会员持卡列表（开单页已加载）兜底显示 */
function enrichHungPaycardRows(rows) {
  var app = getApp();
  var lists = []
    .concat(app.globalData.currentvip_amountcardlist || [])
    .concat(app.globalData.currentvip_timescardlist || []);
  var byCcode = {};
  lists.forEach(function (row) {
    if (row && row.ccode) {
      byCcode[String(row.ccode).trim()] = row;
    }
  });
  return rows.map(function (r) {
    var pc = String(r.payccode || '').trim();
    if (!pc || !byCcode[pc]) {
      return r;
    }
    var c = byCcode[pc];
    var tn = String(r.paycardtypename || '').trim();
    var missingName =
      !tn ||
      tn === '-' ||
      (r.paycardtype && tn === String(r.paycardtype));
    if (missingName && (c.cardname || c.carddesc)) {
      r.paycardtypename = c.cardname || tn || '';
      if (!r.paycardtype && c.cardtype) {
        r.paycardtype = c.cardtype;
      }
    }
    return r;
  });
}

/** 同声传译插件 onStop 返回字段兼容 */
function extractVoiceResult(res) {
  if (!res) {
    return '';
  }
  if (typeof res.result === 'string') {
    return res.result;
  }
  if (Array.isArray(res.result)) {
    return res.result.join('');
  }
  if (res.resultStr) {
    return String(res.resultStr);
  }
  return '';
}

/**
 * 微信同声传译插件（需在小程序后台添加「微信同声传译」）。
 * 参考：https://developers.weixin.qq.com/miniprogram/dev/platform-capabilities/extended/translator.html
 */
function initWechatSIReco(page) {
  try {
    var plugin = requirePlugin('WechatSI');
    if (!plugin || typeof plugin.getRecordRecognitionManager !== 'function') {
      console.warn('WechatSI: getRecordRecognitionManager 不可用', plugin);
      return null;
    }
    var mgr = plugin.getRecordRecognitionManager();
    mgr.onStart(function () {
      if (page._voiceStartWatchdog) {
        clearTimeout(page._voiceStartWatchdog);
        page._voiceStartWatchdog = null;
      }
      try {
        wx.hideLoading();
      } catch (e2) {}
      wx.showLoading({ title: '聆听中，松手结束', mask: true });
      page._voiceRecoDidStart = true;
      console.log('WechatSI onStart');
    });
    mgr.onStop(function (res) {
      if (page._voiceStartWatchdog) {
        clearTimeout(page._voiceStartWatchdog);
        page._voiceStartWatchdog = null;
      }
      try {
        wx.hideLoading();
      } catch (e3) {}
      page._voiceRecoDidStart = false;
      page.setData({ voiceRecording: false });
      var text = extractVoiceResult(res).trim();
      console.log('WechatSI onStop', res, 'text=', text);
      var held = page._voicePressStartAt ? Date.now() - page._voicePressStartAt : 0;
      if (held > 0 && held < 500) {
        wx.showToast({ title: '请按住至少半秒再松开', icon: 'none' });
        return;
      }
      if (!text) {
        wx.showToast({ title: '未识别到语音，请重试', icon: 'none' });
        return;
      }
      page.handleVoiceCommandText(text);
    });
    mgr.onError(function (err) {
      if (page._voiceStartWatchdog) {
        clearTimeout(page._voiceStartWatchdog);
        page._voiceStartWatchdog = null;
      }
      try {
        wx.hideLoading();
      } catch (e4) {}
      page._voiceRecoDidStart = false;
      page.setData({ voiceRecording: false });
      var msg = '未知错误';
      if (err && typeof err === 'object') {
        var parts = [];
        if (err.retcode != null) {
          parts.push('retcode:' + err.retcode);
        }
        if (err.msg) {
          parts.push(String(err.msg));
        }
        if (err.errMsg) {
          parts.push(String(err.errMsg));
        }
        msg = parts.length ? parts.join(' ') : JSON.stringify(err);
      } else if (err) {
        msg = String(err);
      }
      console.warn('WechatSI onError', err);
      wx.showModal({
        title: '语音识别出错',
        content: String(msg),
        showCancel: false
      });
    });
    return mgr;
  } catch (e) {
    console.error('WechatSI requirePlugin 失败（需在公众平台添加「微信同声传译」插件，且 app.json 中版本与后台一致）', e);
    return null;
  }
}

Page({
  data: {
    vipuuid: '',
    hungItems: [],
    saleGroups: [],
    saleRechargeItems: [],
    serviceGoodsItems: [],
    serviceGroups: [],
    activeTab: 'sale',
    loaded: false,
    selectedCount: 0,
    selectedAmount: '0.00',
    selectedQty: '0',
    checkboxRenderFlag: true,
    saleExtraDue: '0.00',
    saleRequiredNoncard: '0.00',
    cardPaidAmount: '0.00',
    nonCardPaymodes: [],
    nonCardPaymodeIndex: -1,
    extraPaymode: '',
    extraPaymodeName: '',
    pay1Amount: '0.00',
    pay2Mode: '',
    pay2ModeName: '',
    pay2Amount: '0.00',
    salePaySummaryText: '',
    servicePaySummaryText: '',
    tabCalcMap: {
      sale: null,
      service: null
    },
    calcPendingMap: {
      sale: false,
      service: false
    },
    calcReadyMap: {
      sale: false,
      service: false
    },
    checkoutCalcReady: false,
    voiceRecording: false,
    voicePluginReady: false,
    voiceMicReady: false,
    voiceMicAuthorized: false,
    voiceMicDenied: false,
    voicePluginHint: '',
    lastVoiceText: ''
  },

  /**
   * 同步拉起录音前必须先知道麦克风授权状态（getSetting 在进页时完成）。
   * start() 必须在用户 touchstart 的同步栈内调用，不能在 authorize/getSetting 回调里调用，否则 onStart 往往永远不触发。
   */
  refreshMicAuth: function () {
    var that = this;
    wx.getSetting({
      success: function (res) {
        var auth = res.authSetting || {};
        if (auth['scope.record'] === true) {
          that._micAuthorized = true;
          that._micDenied = false;
        } else if (auth['scope.record'] === false) {
          that._micAuthorized = false;
          that._micDenied = true;
        } else {
          that._micAuthorized = false;
          that._micDenied = false;
        }
        that.setData({
          voiceMicReady: true,
          voiceMicAuthorized: that._micAuthorized,
          voiceMicDenied: that._micDenied
        });
      },
      fail: function () {
        that._micAuthorized = false;
        that._micDenied = false;
        that.setData({
          voiceMicReady: true,
          voiceMicAuthorized: false,
          voiceMicDenied: false
        });
      }
    });
  },

  /** 插件在 app.json 声明后，部分真机需在 onShow 再 require 才成功 */
  initVoicePlugin: function () {
    if (!this._voiceReco) {
      this._voiceReco = initWechatSIReco(this);
    }
    var ready = !!this._voiceReco;
    this.setData({
      voicePluginReady: ready,
      voicePluginHint: ready ? '' : '未检测到同声传译插件，请按说明在公众平台添加后重新上传小程序'
    });
    return ready;
  },

  onLoad: function (options) {
    var app = getApp();
    var vip = app.globalData.currentvip || {};
    var vipuuid = options.vipuuid || vip.uuid || '';
    this.setData({ vipuuid: vipuuid });
    this.initVoicePlugin();
    this.refreshMicAuth();
    this._shortfallTimer = null;
    this._shortfallReqSeq = { sale: 0, service: 0 };
    this._shortfallSig = { sale: '', service: '' };
    this._shortfallCache = { sale: {}, service: {} };
    this.loadHungItems();
  },

  onShow: function () {
    this.initVoicePlugin();
    this.refreshMicAuth();
  },

  showVoicePluginHelp: function () {
    wx.showModal({
      title: '如何启用语音',
      content:
        '1. 登录 mp.weixin.qq.com → 你的小程序\n' +
        '2. 设置 → 第三方设置 → 插件管理 → 添加插件\n' +
        '3. 搜索并添加「微信同声传译」（provider: wx069ba97219f66d99）\n' +
        '4. 插件版本需与项目 app.json 里 WechatSI.version 一致（当前 0.3.6，可按后台可选版本改）\n' +
        '5. 添加后重新上传/预览小程序\n' +
        '未启用时可用下方「文字指令」代替。',
      showCancel: false
    });
  },

  /** 无语音插件时，用文字输入走同一套指令解析 */
  openTextCommandTap: function () {
    var that = this;
    if (wx.canIUse && wx.canIUse('showModal.object.editable')) {
      wx.showModal({
        title: '输入指令',
        editable: true,
        placeholderText: '例如：结账、全选、售卡结账',
        success: function (res) {
          if (res.confirm && res.content) {
            that.handleVoiceCommandText(String(res.content).trim());
          }
        }
      });
    } else {
      wx.showModal({
        title: '文字指令',
        content: '当前微信版本不支持弹窗输入。请升级微信，或使用已启用插件的「按住说话」。',
        showCancel: false
      });
    }
  },

  loadHungItems: function () {
    var app = getApp();
    var that = this;
    if (!that.data.vipuuid) {
      wx.showToast({ title: '缺少会员信息', icon: 'none' });
      that.setData({ loaded: true });
      return;
    }
    wx.request({
      method: 'GET',
      url: app.globalData.host + 'adviser/get_hung_byvipuuid/',
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        vipuuid: that.data.vipuuid
      },
      success: function (res) {
        var rows = Array.isArray(res.data) ? res.data : [];
        rows = enrichHungPaycardRows(rows);
        var items = rows.map(function (r, idx) {
          var payccode = r.payccode || '';
          var payccodeTail = '';
          if (payccode) {
            var s = String(payccode);
            payccodeTail = s.length > 4 ? s.slice(-4) : s;
          }
          return {
            key: (r.itemuuid || '') + '_' + idx,
            itemuuid: r.itemuuid || '',
            hunguuid: r.hunguuid || '',
            exptxserno: r.exptxserno || '',
            vsdate: r.vsdate || '',
            psstatus: r.psstatus || '',
            ttype: r.ttype || '',
            payccode: payccode,
            payccodeTail: payccodeTail,
            paycardtype: r.paycardtype || '',
            paycardtypename: r.paycardtypename || '',
            paytype: r.paytype || '',
            paytypename: r.paytypename || '',
            itemname: r.itemname || '',
            ttypename: r.ttypename || '',
            stypename: r.stypename || '',
            amount: toNumber(r.amount).toFixed(2),
            qty: String(toNumber(r.qty)),
            payamount: toNumber(r.payamount).toFixed(2),
            payqty: String(toNumber(r.payqty)),
            planPaymode: r.paytype || '',
            planPaymodeName: r.paytypename || '',
            planPayAmount: toNumber(r.amount).toFixed(2),
            checked: true
          };
        });
        items.sort(function (a, b) {
          var d = parseDateInt(b.vsdate) - parseDateInt(a.vsdate);
          if (d !== 0) {
            return d;
          }
          return String(b.exptxserno || '').localeCompare(String(a.exptxserno || ''));
        });
        that.setGroupedItems(items, true);
        that.recalcSelected();
        that.refreshTabSummaries();
        that.updateAllShortfalls(true);
      },
      fail: function () {
        that.setData({ loaded: true });
        wx.showToast({ title: '加载开单失败', icon: 'none' });
      }
    });
  },

  onSelectChange: function (e) {
    var selected = {};
    (e.detail.value || []).forEach(function (id) {
      selected[id] = true;
    });
    var activeTab = this.data.activeTab;
    var items = (this.data.hungItems || []).map(function (o) {
      var t = String(o.ttype || '').toUpperCase();
      var isSaleRecharge = (t === 'C' || t === 'I');
      var inCurrentTab = (activeTab === 'sale' && isSaleRecharge) || (activeTab === 'service' && !isSaleRecharge);
      if (inCurrentTab) {
        var gid = String(o.exptxserno || o.hunguuid || o.key);
        o.checked = !!selected[gid];
      }
      return o;
    });
    this.setGroupedItems(items);
    this.recalcSelected();
    this.refreshTabSummaries();
    this.scheduleShortfallRecalc();
  },

  switchToSaleTab: function () {
    this.setData({ activeTab: 'sale' });
    this.applyActiveTabCalc();
  },

  switchToServiceTab: function () {
    this.setData({ activeTab: 'service' });
    this.applyActiveTabCalc();
  },

  setGroupedItems: function (items, loaded) {
    var saleRechargeItems = [];
    var serviceGoodsItems = [];
    (items || []).forEach(function (it) {
      var t = String(it.ttype || '').toUpperCase();
      var isSaleRecharge = (t === 'C' || t === 'I');
      if (isSaleRecharge) {
        saleRechargeItems.push(it);
      } else {
        serviceGoodsItems.push(it);
      }
    });
    var saleGroupMap = {};
    var saleGroups = [];
    saleRechargeItems.forEach(function (it) {
      var gid = String(it.exptxserno || it.hunguuid || '未分组');
      if (!saleGroupMap[gid]) {
        saleGroupMap[gid] = {
          groupKey: gid,
          exptxserno: it.exptxserno || '',
          checked: false,
          items: []
        };
        saleGroups.push(saleGroupMap[gid]);
      }
      saleGroupMap[gid].items.push(it);
      if (it.checked) {
        saleGroupMap[gid].checked = true;
      }
    });

    var serviceGroupMap = {};
    var serviceGroups = [];
    serviceGoodsItems.forEach(function (it) {
      var gid = String(it.exptxserno || it.hunguuid || '未分组');
      if (!serviceGroupMap[gid]) {
        serviceGroupMap[gid] = {
          groupKey: gid,
          exptxserno: it.exptxserno || '',
          checked: false,
          items: []
        };
        serviceGroups.push(serviceGroupMap[gid]);
      }
      serviceGroupMap[gid].items.push(it);
      if (it.checked) {
        serviceGroupMap[gid].checked = true;
      }
    });
    var patch = {
      hungItems: items || [],
      saleGroups: saleGroups,
      saleRechargeItems: saleRechargeItems,
      serviceGoodsItems: serviceGoodsItems,
      serviceGroups: serviceGroups
    };
    if (typeof loaded === 'boolean') {
      patch.loaded = loaded;
    }
    this.setData(patch);
  },

  selectAllTap: function () {
    var items = (this.data.hungItems || []).map(function (o) {
      o.checked = true;
      return o;
    });
    this.setData({ checkboxRenderFlag: false });
    var that = this;
    setTimeout(function () {
      that.setGroupedItems(items);
      that.setData({ checkboxRenderFlag: true });
      that.recalcSelected();
      that.refreshTabSummaries();
      that.scheduleShortfallRecalc();
    }, 0);
  },

  clearAllTap: function () {
    var items = (this.data.hungItems || []).map(function (o) {
      o.checked = false;
      return o;
    });
    this.setData({ checkboxRenderFlag: false });
    var that = this;
    setTimeout(function () {
      that.setGroupedItems(items);
      that.setData({ checkboxRenderFlag: true });
      that.recalcSelected();
      that.refreshTabSummaries();
      that.scheduleShortfallRecalc();
    }, 0);
  },

  getSelectedSignatureByTab: function (tab) {
    return this.getSelectedHungIdsByTab(tab).sort().join(',');
  },

  scheduleShortfallRecalc: function () {
    var that = this;
    if (that._shortfallTimer) {
      clearTimeout(that._shortfallTimer);
    }
    that._shortfallTimer = setTimeout(function () {
      that.updateAllShortfalls(false);
    }, 120);
  },

  getSelectedHungIdsByTab: function (tab) {
    var hmap = {};
    (this.data.hungItems || []).forEach(function (o) {
      if (!o.checked) {
        return;
      }
      var t = String(o.ttype || '').toUpperCase();
      var isSaleRecharge = (t === 'C' || t === 'I');
      var inTargetTab = (tab === 'sale' && isSaleRecharge) || (tab === 'service' && !isSaleRecharge);
      if (inTargetTab && o.hunguuid) {
        hmap[o.hunguuid] = true;
      }
    });
    return Object.keys(hmap);
  },

  updateShortfallByTab: function (tab, signature) {
    var app = getApp();
    var that = this;
    var hids = that.getSelectedHungIdsByTab(tab);
    if (!that.data.vipuuid) {
      return;
    }
    var sig = signature != null ? signature : that.getSelectedSignatureByTab(tab);
    var cache = (that._shortfallCache && that._shortfallCache[tab]) || {};
    var cached = cache[sig];
    if (cached) {
      var mapCached = that.data.tabCalcMap || {};
      mapCached[tab] = cached;
      var doneMapCached = that.data.calcReadyMap || {};
      doneMapCached[tab] = true;
      var pdMapCached = that.data.calcPendingMap || {};
      pdMapCached[tab] = false;
      var allReadyCached = !!doneMapCached.sale && !!doneMapCached.service && !pdMapCached.sale && !pdMapCached.service;
      that.setData({
        tabCalcMap: mapCached,
        calcReadyMap: doneMapCached,
        calcPendingMap: pdMapCached,
        checkoutCalcReady: allReadyCached
      });
      that.applyActiveTabCalc();
      return;
    }

    var pendingMap = that.data.calcPendingMap || {};
    pendingMap[tab] = true;
    that.setData({
      calcPendingMap: pendingMap,
      checkoutCalcReady: false
    });
    that._shortfallReqSeq[tab] = (that._shortfallReqSeq[tab] || 0) + 1;
    var reqId = that._shortfallReqSeq[tab];
    wx.request({
      method: 'GET',
      url: app.globalData.host + 'adviser/get_checkout_shortfall/',
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        vipuuid: that.data.vipuuid,
        hunguuids: JSON.stringify(hids)
      },
      success: function (res) {
        if (that._shortfallReqSeq[tab] !== reqId) {
          return;
        }
        var data = res.data || {};
        var due = toNumber(data.total_extra_due).toFixed(2);
        var required = toNumber(data.required_noncard != null ? data.required_noncard : data.total_extra_due).toFixed(2);
        var list = Array.isArray(data.paymodes) ? data.paymodes : [];
        var idx = -1;
        for (var i = 0; i < list.length; i += 1) {
          var n = String(list[i].pname || '');
          if (n.indexOf('现金') !== -1) {
            idx = i;
            break;
          }
        }
        if (idx < 0 && list.length > 0) {
          idx = 0;
        }
        var selected = idx >= 0 ? list[idx] : null;
        var modeCode = selected ? (selected.pcode || '') : '';
        var modeName = selected ? (selected.pname || '') : '';
        var items = (that.data.hungItems || []).map(function (it) {
          var t = String(it.ttype || '').toUpperCase();
          var isSaleRecharge = (t === 'C' || t === 'I');
          var inTab = (tab === 'sale' && isSaleRecharge) || (tab === 'service' && !isSaleRecharge);
          if (inTab && !it.planPaymode) {
            it.planPaymode = modeCode;
            it.planPaymodeName = modeName;
            it.planPayAmount = it.amount;
          }
          return it;
        });
        var calcData = {
          saleExtraDue: due,
          saleRequiredNoncard: required,
          cardPaidAmount: toNumber(data.card_paid_amount).toFixed(2),
          nonCardPaymodes: list,
          nonCardPaymodeIndex: idx,
          extraPaymode: selected ? (selected.pcode || '') : '',
          extraPaymodeName: selected ? (selected.pname || '') : '',
          pay1Amount: required,
          pay2Mode: '',
          pay2ModeName: '',
          pay2Amount: '0.00'
        };
        that._shortfallCache[tab][sig] = calcData;
        var map = that.data.tabCalcMap || {};
        map[tab] = calcData;
        var doneMap = that.data.calcReadyMap || {};
        doneMap[tab] = true;
        var pdMap = that.data.calcPendingMap || {};
        pdMap[tab] = false;
        var allReady = !!doneMap.sale && !!doneMap.service && !pdMap.sale && !pdMap.service;
        that.setData({
          tabCalcMap: map,
          calcReadyMap: doneMap,
          calcPendingMap: pdMap,
          checkoutCalcReady: allReady
        });
        that.applyActiveTabCalc();
        that.setGroupedItems(items);
      },
      fail: function () {
        if (that._shortfallReqSeq[tab] !== reqId) {
          return;
        }
        var pdMap = that.data.calcPendingMap || {};
        pdMap[tab] = false;
        that.setData({
          calcPendingMap: pdMap,
          checkoutCalcReady: false
        });
      }
    });
  },

  updateAllShortfalls: function (force) {
    var saleSig = this.getSelectedSignatureByTab('sale');
    var serviceSig = this.getSelectedSignatureByTab('service');
    if (force || this._shortfallSig.sale !== saleSig) {
      this._shortfallSig.sale = saleSig;
      this.updateShortfallByTab('sale', saleSig);
    }
    if (force || this._shortfallSig.service !== serviceSig) {
      this._shortfallSig.service = serviceSig;
      this.updateShortfallByTab('service', serviceSig);
    }
  },

  applyActiveTabCalc: function () {
    var tab = this.data.activeTab || 'sale';
    var calc = (this.data.tabCalcMap || {})[tab];
    if (!calc) {
      return;
    }
    this.setData({
      saleExtraDue: calc.saleExtraDue,
      saleRequiredNoncard: calc.saleRequiredNoncard,
      cardPaidAmount: calc.cardPaidAmount || '0.00',
      nonCardPaymodes: calc.nonCardPaymodes || [],
      nonCardPaymodeIndex: calc.nonCardPaymodeIndex,
      extraPaymode: calc.extraPaymode || '',
      extraPaymodeName: calc.extraPaymodeName || '',
      pay1Amount: calc.pay1Amount || '0.00',
      pay2Mode: calc.pay2Mode || '',
      pay2ModeName: calc.pay2ModeName || '',
      pay2Amount: calc.pay2Amount || '0.00'
    });
    this.recalcPaymentSplit(true);
  },

  refreshTabSummaries: function () {
    var saleMap = {};
    var serviceMap = {};
    (this.data.hungItems || []).forEach(function (o) {
      if (!o.checked) return;
      var t = String(o.ttype || '').toUpperCase();
      var isSaleRecharge = (t === 'C' || t === 'I');
      var k = String(o.paytypename || o.paytype || '未设置');
      var amt = toNumber(o.payamount || o.amount);
      var target = isSaleRecharge ? saleMap : serviceMap;
      target[k] = (target[k] || 0) + amt;
    });
    function mapToText(m) {
      var ks = Object.keys(m);
      if (ks.length === 0) return '暂无';
      return ks.map(function (k) {
        return k + ' ¥' + toNumber(m[k]).toFixed(2);
      }).join('；');
    }
    this.setData({
      salePaySummaryText: mapToText(saleMap),
      servicePaySummaryText: mapToText(serviceMap)
    });
  },

  onNonCardPaymodeChange: function (e) {
    var idx = Number(e.detail.value);
    var item = (this.data.nonCardPaymodes || [])[idx];
    if (!item) {
      return;
    }
    var tab = this.data.activeTab || 'sale';
    var map = this.data.tabCalcMap || {};
    map[tab] = map[tab] || {};
    map[tab].nonCardPaymodeIndex = idx;
    map[tab].extraPaymode = item.pcode || '';
    map[tab].extraPaymodeName = item.pname || '';
    this.setData({
      tabCalcMap: map,
      nonCardPaymodeIndex: idx,
      extraPaymode: item.pcode || '',
      extraPaymodeName: item.pname || ''
    });
    this.recalcPaymentSplit();
  },

  onPay1AmountInput: function (e) {
    var v = String((e.detail && e.detail.value) || '').trim();
    if (v === '') {
      v = '0';
    }
    var tab = this.data.activeTab || 'sale';
    var map = this.data.tabCalcMap || {};
    map[tab] = map[tab] || {};
    map[tab].pay1Amount = v;
    this.setData({ pay1Amount: v, tabCalcMap: map });
    this.recalcPaymentSplit(false);
  },

  onPay1AmountBlur: function (e) {
    var v = String((e.detail && e.detail.value) || this.data.pay1Amount || '').trim();
    var total = toNumber(this.data.saleRequiredNoncard);
    var n = toNumber(v);
    if (n < 0) {
      n = 0;
    }
    if (n > total) {
      n = total;
    }
    var tab = this.data.activeTab || 'sale';
    var map = this.data.tabCalcMap || {};
    map[tab] = map[tab] || {};
    map[tab].pay1Amount = n.toFixed(2);
    this.setData({ pay1Amount: n.toFixed(2), tabCalcMap: map });
    this.recalcPaymentSplit(true);
  },

  recalcPaymentSplit: function (normalizePay1) {
    var total = toNumber(this.data.saleRequiredNoncard);
    var a1 = toNumber(this.data.pay1Amount);
    if (a1 < 0) {
      a1 = 0;
    }
    if (a1 > total) {
      a1 = total;
    }
    var remain = total - a1;
    var cashMode = '';
    var cashName = '';
    var list = this.data.nonCardPaymodes || [];
    for (var i = 0; i < list.length; i += 1) {
      var n = String(list[i].pname || '');
      if (n.indexOf('现金') !== -1) {
        cashMode = list[i].pcode || '';
        cashName = list[i].pname || '';
        break;
      }
    }
    if (!cashMode && list.length > 0) {
      cashMode = list[0].pcode || '';
      cashName = list[0].pname || '';
    }
    var patch = {
      pay2Mode: remain > 0 ? cashMode : '',
      pay2ModeName: remain > 0 ? cashName : '',
      pay2Amount: remain.toFixed(2)
    };
    if (normalizePay1) {
      patch.pay1Amount = a1.toFixed(2);
    }
    var tab = this.data.activeTab || 'sale';
    var map = this.data.tabCalcMap || {};
    map[tab] = map[tab] || {};
    map[tab].pay2Mode = patch.pay2Mode;
    map[tab].pay2ModeName = patch.pay2ModeName;
    map[tab].pay2Amount = patch.pay2Amount;
    if (patch.pay1Amount !== undefined) {
      map[tab].pay1Amount = patch.pay1Amount;
    }
    patch.tabCalcMap = map;
    this.setData(patch);
  },

  onItemPaymodeChange: function (e) {
    var key = e.currentTarget.dataset.key;
    var idx = Number(e.detail.value);
    var pm = (this.data.nonCardPaymodes || [])[idx];
    if (!pm || !key) {
      return;
    }
    var items = (this.data.hungItems || []).map(function (it) {
      if (it.key === key) {
        it.planPaymode = pm.pcode || '';
        it.planPaymodeName = pm.pname || '';
        it.planPayAmount = it.amount;
      }
      return it;
    });
    this.setGroupedItems(items);
  },

  recalcSelected: function () {
    var count = 0;
    var amount = 0;
    var qty = 0;
    (this.data.hungItems || []).forEach(function (o) {
      if (o.checked) {
        count += 1;
        amount += toNumber(o.amount);
        qty += toNumber(o.qty);
      }
    });
    this.setData({
      selectedCount: count,
      selectedAmount: amount.toFixed(2),
      selectedQty: String(qty)
    });
  },

  /** 首次未授权时单独点一次授权（避免在异步回调里 start） */
  tapRequestMicAuth: function () {
    var that = this;
    if (that._micDenied) {
      wx.showModal({
        title: '麦克风已被拒绝',
        content: '请到设置中开启麦克风后再使用语音。',
        confirmText: '去设置',
        success: function (r) {
          if (r.confirm) {
            wx.openSetting({
              success: function () {
                that.refreshMicAuth();
              }
            });
          }
        }
      });
      return;
    }
    wx.authorize({
      scope: 'scope.record',
      success: function () {
        that._micAuthorized = true;
        that._micDenied = false;
        that.setData({ voiceMicAuthorized: true, voiceMicDenied: false });
        wx.showToast({ title: '已授权，请按住说话', icon: 'none' });
      },
      fail: function () {
        that._micDenied = true;
        that.setData({ voiceMicAuthorized: false, voiceMicDenied: true });
        wx.showModal({
          title: '需要麦克风',
          content: '请允许录音，或到设置中开启。',
          confirmText: '去设置',
          success: function (r) {
            if (r.confirm) {
              wx.openSetting({
                success: function () {
                  that.refreshMicAuth();
                }
              });
            }
          }
        });
      }
    });
  },

  /** 按住说话时拦截 touchmove，减少页面滚动触发 touchcancel（与 catchtouchcancel 冲突导致渲染层告警） */
  onVoiceTouchMove: function () {},

  onVoiceTouchStart: function () {
    if (!this.data.loaded || !this.data.hungItems || this.data.hungItems.length === 0) {
      return;
    }
    if (!this.data.voiceMicReady) {
      wx.showToast({ title: '正在检测麦克风权限…', icon: 'none' });
      return;
    }
    if (!this._voiceReco) {
      this.initVoicePlugin();
    }
    if (!this._voiceReco) {
      var page = this;
      wx.showModal({
        title: '语音插件未启用',
        content: '请先在微信公众平台添加「微信同声传译」插件，或使用「文字指令」。',
        confirmText: '查看说明',
        cancelText: '文字指令',
        success: function (res) {
          if (res.confirm) {
            page.showVoicePluginHelp();
          } else if (res.cancel) {
            page.openTextCommandTap();
          }
        }
      });
      return;
    }

    var that = this;

    if (that._micDenied) {
      wx.showModal({
        title: '需要麦克风权限',
        content: '请在设置中开启麦克风，或使用下方「授权麦克风」。',
        confirmText: '去设置',
        success: function (r) {
          if (r.confirm) {
            wx.openSetting({
              success: function () {
                that.refreshMicAuth();
              }
            });
          }
        }
      });
      return;
    }

    if (!that._micAuthorized) {
      wx.showToast({ title: '请先点「授权麦克风」', icon: 'none' });
      return;
    }

    /* 已授权：start 必须紧跟在用户触摸同步栈内，禁止前面再套异步 API */
    that._voiceFingerDown = true;
    that._voiceStartInvoked = false;
    that._voicePressStartAt = Date.now();
    that._voiceRecoDidStart = false;
    that.setData({ voiceRecording: true });
    try {
      if (that._voiceStartWatchdog) {
        clearTimeout(that._voiceStartWatchdog);
      }
      that._voiceStartInvoked = true;
      that._voiceStartWatchdog = setTimeout(function () {
        that._voiceStartWatchdog = null;
        if (!that._voiceRecoDidStart) {
          try {
            wx.hideLoading();
          } catch (ew) {}
          that.setData({ voiceRecording: false });
          wx.showModal({
            title: '录音未启动',
            content:
              '若使用开发者工具模拟器，语音插件可能无法录音，请换真机预览。\n\n否则请检查：已添加「微信同声传译」插件且版本与 app.json 一致；网络正常；微信与基础库为较新版本。',
            showCancel: false
          });
        }
      }, 4000);
      that._voiceReco.start({ lang: 'zh_CN', duration: 60000 });
    } catch (e) {
      if (that._voiceStartWatchdog) {
        clearTimeout(that._voiceStartWatchdog);
        that._voiceStartWatchdog = null;
      }
      that.setData({ voiceRecording: false });
      wx.showModal({
        title: '无法开始录音',
        content: String(e && e.message ? e.message : e),
        showCancel: false
      });
    }
  },

  onVoiceTouchEnd: function () {
    this._voiceFingerDown = false;
    if (!this._voiceStartInvoked) {
      try {
        wx.hideLoading();
      } catch (e6) {}
      this.setData({ voiceRecording: false });
      return;
    }
    this.setData({ voiceRecording: false });
    if (this._voiceReco) {
      try {
        this._voiceReco.stop();
      } catch (e) {
        try {
          wx.hideLoading();
        } catch (e5) {}
        if (this._voiceRecoDidStart) {
          wx.showToast({ title: '结束录音失败', icon: 'none' });
        }
      }
    }
  },

  /**
   * 根据识别文本执行结账页操作（与手动点击一致，结账仍走 submitCheckout 校验）。
   */
  handleVoiceCommandText: function (text) {
    var raw = String(text || '').trim();
    this.setData({ lastVoiceText: raw });
    if (!raw) {
      wx.showToast({ title: '未识别到内容', icon: 'none' });
      return;
    }
    var norm = raw.replace(/\s+/g, '');
    if (/取消全选|全部不选|清空选择|都不要|全不选/.test(norm)) {
      this.clearAllTap();
      wx.showToast({ title: '已取消全选', icon: 'none' });
      return;
    }
    if (/售卡|充值结账|售卡结账|卡项|买卡/.test(norm)) {
      this.switchToSaleTab();
      wx.showToast({ title: '已切到售卡/充值', icon: 'none' });
      return;
    }
    if (/服务结账|商品结账|服务商品|做服务/.test(norm)) {
      this.switchToServiceTab();
      wx.showToast({ title: '已切到服务/商品', icon: 'none' });
      return;
    }
    if ((/全选|都要|全要|全部勾选/.test(norm)) && !/不/.test(norm)) {
      this.selectAllTap();
      wx.showToast({ title: '已全选', icon: 'none' });
      return;
    }
    if (/结账|收款|确认结账|确认支付|立即结账|结一下|结下账|买单|支付/.test(norm)) {
      this.submitCheckout();
      return;
    }
    wx.showModal({
      title: '未识别的指令',
      content: '识别：' + raw + '\n请说：结账、全选、取消全选、售卡结账、服务结账',
      showCancel: false
    });
  },

  submitCheckout: function () {
    var app = getApp();
    var that = this;
    var selected = (that.data.hungItems || []).filter(function (o) {
      return o.checked;
    });
    if (selected.length === 0) {
      wx.showToast({ title: '请先选择项目', icon: 'none' });
      return;
    }

    var hungMap = {};
    selected.forEach(function (o) {
      if (o.hunguuid) {
        hungMap[o.hunguuid] = true;
      }
    });
    var hids = Object.keys(hungMap);
    if (hids.length === 0) {
      wx.showToast({ title: '选中项目缺少开单号', icon: 'none' });
      return;
    }
    var extraDue = toNumber(that.data.saleExtraDue);
    if (extraDue > 0 && !that.data.extraPaymode) {
      wx.showToast({ title: '请选择补差额付款方式', icon: 'none' });
      return;
    }
    var extraPayments = [];
    var p1 = toNumber(that.data.pay1Amount);
    var p2 = toNumber(that.data.pay2Amount);
    if (that.data.extraPaymode && p1 > 0) {
      extraPayments.push({ pcode: that.data.extraPaymode, amount: p1 });
    }
    if (that.data.pay2Mode && p2 > 0) {
      extraPayments.push({ pcode: that.data.pay2Mode, amount: p2 });
    }
    util.showLoading('结账中');
    wx.request({
      method: 'POST',
      url: app.globalData.host + 'adviser/checkout_hungs/',
      data: {
        company: app.globalData.company,
        storecode: app.globalData.storecode,
        vipuuid: that.data.vipuuid,
        hunguuids: hids,
        extra_paymode: that.data.extraPaymode,
        extra_pay_amount: extraDue,
        extra_payments: extraPayments
      },
      header: {
        'content-type': 'application/json'
      },
      success: function (res) {
        if (res.data && res.data.ok) {
          wx.showToast({ title: '结账成功', icon: 'success' });
          that.loadHungItems();
          return;
        }
        var msg = (res.data && res.data.message) || '结账失败';
        if (res.data && res.data.code === 'INSUFFICIENT_AMOUNT') {
          msg = msg + '，还需支付 ¥' + toNumber(res.data.need_pay).toFixed(2);
        }
        if (res.data && res.data.code === 'INSUFFICIENT_TIMES') {
          msg = msg + '，还差 ' + toNumber(res.data.need_qty) + ' 次';
        }
        wx.showModal({
          title: '提示',
          content: msg,
          showCancel: false
        });
      },
      fail: function () {
        wx.showToast({ title: '结账失败', icon: 'none' });
      },
      complete: function () {
        wx.hideLoading();
      }
    });
  }
});
