var app = getApp();

function _tenantPayload(extra) {
  var gd = app.globalData || {};
  var data = {
    company: gd.company || '',
    storecode: gd.storecode || '',
    ecode: gd.ecode || gd.usercode || '',
  };
  if (extra && typeof extra === 'object') {
    for (var k in extra) {
      if (extra.hasOwnProperty(k)) {
        data[k] = extra[k];
      }
    }
  }
  return data;
}

function mpChat(params) {
  params = params || {};
  return new Promise(function (resolve, reject) {
    wx.request({
      url: app.globalData.host + 'assistant/mp/api/chat/',
      method: 'POST',
      header: { 'content-type': 'application/json' },
      timeout: 120000,
      data: _tenantPayload({
        message: params.message || '',
        thread_id: params.threadId || null,
        profile: params.profile || 'general',
        vipuuid: params.vipuuid || '',
        agent: 'deepseek',
      }),
      success: function (res) {
        if (res.statusCode === 200 && res.data && res.data.ok) {
          resolve(res.data);
          return;
        }
        var err = (res.data && (res.data.error || res.data.detail)) || ('HTTP ' + res.statusCode);
        if (res.statusCode === 500 && res.data && res.data.error) {
          err = res.data.error;
        }
        reject({ error: err, statusCode: res.statusCode, raw: res });
      },
      fail: function (res) {
        var msg = (res && res.errMsg) || '网络请求失败';
        if (msg.indexOf('timeout') >= 0) {
          msg = '请求超时（分析较慢，请稍后重试或换更具体的问题）';
        }
        reject({ error: msg, raw: res });
      },
    });
  });
}

function mpThreadDetail(threadId) {
  return new Promise(function (resolve, reject) {
    var q = _tenantPayload({});
    var query =
      'company=' +
      encodeURIComponent(q.company) +
      '&storecode=' +
      encodeURIComponent(q.storecode) +
      '&ecode=' +
      encodeURIComponent(q.ecode);
    wx.request({
      url: app.globalData.host + 'assistant/mp/api/threads/' + threadId + '/?' + query,
      method: 'GET',
      timeout: 30000,
      success: function (res) {
        if (res.statusCode === 200 && res.data && res.data.ok) {
          resolve(res.data);
          return;
        }
        reject(res.data || { error: 'load failed' });
      },
      fail: reject,
    });
  });
}

function mpLifecycleBatch(params) {
  params = params || {};
  return new Promise(function (resolve, reject) {
    wx.request({
      url: app.globalData.host + 'assistant/mp/api/vip/lifecycle/',
      method: 'POST',
      header: { 'content-type': 'application/json' },
      timeout: 120000,
      data: _tenantPayload({
        segment: params.segment || '',
        viptype: params.viptype || '',
        limit: params.limit || 100,
      }),
      success: function (res) {
        if (res.statusCode === 200 && res.data && res.data.ok) {
          resolve(res.data);
          return;
        }
        reject({ error: (res.data && res.data.error) || ('HTTP ' + res.statusCode), raw: res });
      },
      fail: function (res) {
        reject({ error: (res && res.errMsg) || '网络请求失败', raw: res });
      },
    });
  });
}

function mpLifecycleOne(params) {
  params = params || {};
  return new Promise(function (resolve, reject) {
    wx.request({
      url: app.globalData.host + 'assistant/mp/api/vip/lifecycle/one/',
      method: 'POST',
      header: { 'content-type': 'application/json' },
      timeout: 60000,
      data: _tenantPayload({
        vipuuid: params.vipuuid || '',
        telph: params.telph || '',
        vcode: params.vcode || '',
      }),
      success: function (res) {
        if (res.statusCode === 200 && res.data && res.data.ok) {
          resolve(res.data);
          return;
        }
        reject({ error: (res.data && res.data.error) || ('HTTP ' + res.statusCode), raw: res });
      },
      fail: function (res) {
        reject({ error: (res && res.errMsg) || '网络请求失败', raw: res });
      },
    });
  });
}

function mpLifecycleMigrations(params) {
  params = params || {};
  return new Promise(function (resolve, reject) {
    wx.request({
      url: app.globalData.host + 'assistant/mp/api/vip/lifecycle/migrations/',
      method: 'POST',
      header: { 'content-type': 'application/json' },
      timeout: 60000,
      data: _tenantPayload({
        days_back: params.days_back || 7,
        transition: params.transition || '',
        limit: params.limit || 100,
      }),
      success: function (res) {
        if (res.statusCode === 200 && res.data && res.data.ok) {
          resolve(res.data);
          return;
        }
        reject({ error: (res.data && res.data.error) || ('HTTP ' + res.statusCode), raw: res });
      },
      fail: function (res) {
        reject({ error: (res && res.errMsg) || '网络请求失败', raw: res });
      },
    });
  });
}

function mpLifecycleCrmTasks(params) {
  params = params || {};
  return new Promise(function (resolve, reject) {
    wx.request({
      url: app.globalData.host + 'assistant/mp/api/vip/lifecycle/crm-tasks/',
      method: 'POST',
      header: { 'content-type': 'application/json' },
      timeout: 60000,
      data: _tenantPayload({
        segment: params.segment || 'at_risk',
        dry_run: params.dry_run !== false,
        limit: params.limit || 50,
      }),
      success: function (res) {
        if (res.statusCode === 200 && res.data && res.data.ok) {
          resolve(res.data);
          return;
        }
        reject({ error: (res.data && res.data.error) || ('HTTP ' + res.statusCode), raw: res });
      },
      fail: function (res) {
        reject({ error: (res && res.errMsg) || '网络请求失败', raw: res });
      },
    });
  });
}

module.exports = {
  mpChat: mpChat,
  mpThreadDetail: mpThreadDetail,
  mpLifecycleBatch: mpLifecycleBatch,
  mpLifecycleOne: mpLifecycleOne,
  mpLifecycleMigrations: mpLifecycleMigrations,
  mpLifecycleCrmTasks: mpLifecycleCrmTasks,
};
