var assistant = require('../../utils/assistant.js');
var app = getApp();

var WELCOME_GENERAL =
  '你好，我是门店智能助手。\n可查询未结账客人、会员信息、门店流水等。\n直接输入问题，或点下方快捷问题。';

var WELCOME_VIP_CRM =
  '你好，我是客户管理助手。\n可查询生命周期分级、流失预警、休眠客户，并为单客生成运营方案。\n直接输入问题，或点下方快捷问题。';

var QUICK_PROMPTS_GENERAL = [
  '今天有哪些未结账客人？',
  '最近7天门店流水概况',
  '搜一下会员',
];

var QUICK_PROMPTS_VIP_CRM = [
  '有哪些流失预警的客户？',
  '休眠客户有多少？',
  '本店活跃客户概况',
  '13800001234 这个客户给运营方案',
];

Page({
  data: {
    messages: [],
    inputText: '',
    threadId: null,
    sending: false,
    scrollToId: '',
    quickPrompts: QUICK_PROMPTS_GENERAL,
    profile: 'general',
    vipuuid: '',
    storeLabel: '',
  },

  onLoad: function (options) {
    var gd = app.globalData || {};
    var profile = (options && options.profile) || 'general';
    var vipuuid = (options && options.vipuuid) || '';
    var threadId = options && options.thread_id ? parseInt(options.thread_id, 10) : null;
    var welcome = profile === 'vip_crm' ? WELCOME_VIP_CRM : WELCOME_GENERAL;
    var prompts = profile === 'vip_crm' ? QUICK_PROMPTS_VIP_CRM : QUICK_PROMPTS_GENERAL;

    this.setData({
      profile: profile,
      vipuuid: vipuuid,
      quickPrompts: prompts,
      storeLabel: (gd.companyname || gd.company || '') + ' · ' + (gd.storename || gd.storecode || ''),
      messages: [
        {
          id: 'welcome',
          role: 'assistant',
          content: welcome,
        },
      ],
    });

    if (threadId && !isNaN(threadId)) {
      this.setData({ threadId: threadId });
      this.loadThread(threadId);
    }
  },

  loadThread: function (threadId) {
    var that = this;
    assistant
      .mpThreadDetail(threadId)
      .then(function (data) {
        var msgs = (data.messages || []).map(function (m, idx) {
          return {
            id: 'm' + (m.id || idx),
            role: m.role,
            content: m.content,
          };
        });
        if (msgs.length) {
          that.setData({ messages: msgs });
          that.scrollToBottom();
        }
      })
      .catch(function () {
        wx.showToast({ title: '历史会话加载失败', icon: 'none' });
      });
  },

  onInput: function (e) {
    this.setData({ inputText: e.detail.value });
  },

  onQuickTap: function (e) {
    var text = e.currentTarget.dataset.text;
    if (!text || this.data.sending) return;
    this._sendText(text);
  },

  onSendTap: function () {
    this._sendText((this.data.inputText || '').trim());
  },

  sendMessage: function () {
    this._sendText((this.data.inputText || '').trim());
  },

  _sendText: function (text) {
    var that = this;
    text = (text || '').trim();
    if (!text || that.data.sending) return;

    var gd = app.globalData || {};
    if (!gd.company || !gd.storecode || !(gd.ecode || gd.usercode)) {
      wx.showModal({
        title: '无法发送',
        content: '请先登录并确认门店信息（company/storecode/ecode）。',
        showCancel: false,
      });
      return;
    }

    var userMsg = {
      id: 'u' + Date.now(),
      role: 'user',
      content: text,
    };
    var pendingId = 'pending' + Date.now();
    var pendingMsg = {
      id: pendingId,
      role: 'assistant',
      content: '正在分析，通常需要 30–90 秒，请稍候…',
      pending: true,
    };

    that.setData({
      sending: true,
      inputText: '',
      messages: that.data.messages.concat([userMsg, pendingMsg]),
    });
    that.scrollToBottom(pendingId);

    assistant
      .mpChat({
        message: text,
        threadId: that.data.threadId,
        profile: that.data.profile,
        vipuuid: that.data.vipuuid,
      })
      .then(function (data) {
        var msgs = that.data.messages.filter(function (m) {
          return m.id !== pendingId;
        });
        msgs.push({
          id: 'a' + (data.assistant_message_id || Date.now()),
          role: 'assistant',
          content: data.answer || '（无回答内容）',
        });
        that.setData({
          messages: msgs,
          threadId: data.thread_id || that.data.threadId,
          sending: false,
        });
        that.scrollToBottom();
      })
      .catch(function (err) {
        var msgs = that.data.messages.filter(function (m) {
          return m.id !== pendingId;
        });
        var tip = (err && err.error) || '请求失败';
        msgs.push({
          id: 'err' + Date.now(),
          role: 'assistant',
          content: '抱歉，助手暂时不可用：' + tip + '\n\n若提示超时，请稍等后重试；若提示 DeepSeek/API Key，请检查后端 .env 配置。',
          error: true,
        });
        that.setData({ messages: msgs, sending: false });
        that.scrollToBottom();
      });
  },

  scrollToBottom: function (anchorId) {
    var that = this;
    var id = anchorId;
    if (!id) {
      var list = that.data.messages;
      id = list.length ? list[list.length - 1].id : '';
    }
    if (id) {
      that.setData({ scrollToId: id });
    }
  },

  onNewChat: function () {
    var welcome = this.data.profile === 'vip_crm' ? WELCOME_VIP_CRM : WELCOME_GENERAL;
    this.setData({
      threadId: null,
      messages: [
        {
          id: 'welcome',
          role: 'assistant',
          content: welcome,
        },
      ],
    });
  },
});
