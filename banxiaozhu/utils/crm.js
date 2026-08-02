// 客户关怀小程序端 API：员工个人视角，自动携带 company/storecode/ecode。
var app = getApp();

function tenantPayload(extra) {
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

function request(url, method, data, timeout) {
  return new Promise(function (resolve, reject) {
    wx.request({
      url: app.globalData.host + url,
      method: method || 'GET',
      header: { 'content-type': 'application/json' },
      timeout: timeout || 30000,
      data: data || {},
      success: function (res) {
        if (res.statusCode === 200 && res.data && res.data.ok) {
          resolve(res.data);
          return;
        }
        var msg =
          (res.data && (res.data.error || res.data.detail)) ||
          'HTTP ' + res.statusCode;
        reject({ error: msg, statusCode: res.statusCode, raw: res });
      },
      fail: function (res) {
        var msg = (res && res.errMsg) || '网络请求失败';
        if (msg.indexOf('timeout') >= 0) {
          msg = '请求超时，请稍后重试';
        }
        reject({ error: msg, raw: res });
      },
    });
  });
}

function mpTaskSummary(params) {
  return request('crm/mp/tasks/summary/', 'GET', tenantPayload(params || {}));
}

function mpTaskList(params) {
  return request('crm/mp/tasks/', 'GET', tenantPayload(params || {}));
}

function mpTaskDetail(uuid) {
  return request('crm/mp/tasks/' + uuid + '/', 'GET', tenantPayload({}));
}

function mpTaskAttempt(uuid, data) {
  return request(
    'crm/mp/tasks/' + uuid + '/attempt/',
    'POST',
    tenantPayload(data || {})
  );
}

function mpTaskAttemptDelete(uuid, attemptUuid) {
  return request(
    'crm/mp/tasks/' + uuid + '/attempt/' + attemptUuid + '/',
    'DELETE',
    tenantPayload({})
  );
}

function mpTaskComplete(uuid, data) {
  return request(
    'crm/mp/tasks/' + uuid + '/complete/',
    'POST',
    tenantPayload(data || {})
  );
}

function mpTaskStatus(uuid, data) {
  return request(
    'crm/mp/tasks/' + uuid + '/status/',
    'POST',
    tenantPayload(data || {})
  );
}

function mpTaskSuggest(uuid, data) {
  return request(
    'crm/mp/tasks/' + uuid + '/suggest/',
    'POST',
    tenantPayload(data || {}),
    60000
  );
}

function mpTimeline(params) {
  return request('crm/mp/timeline/', 'GET', tenantPayload(params || {}));
}

function mpTimelineCreate(data) {
  return request('crm/mp/timeline/', 'POST', tenantPayload(data || {}));
}

function mpVipSearch(keyword) {
  return request(
    'crm/mp/vip-search/',
    'GET',
    tenantPayload({ keyword: keyword || '' })
  );
}

function mpVipDetail(uuid) {
  return new Promise(function (resolve, reject) {
    wx.request({
      url: app.globalData.host + 'crm/vip/' + uuid + '/',
      method: 'GET',
      header: { 'content-type': 'application/json' },
      timeout: 30000,
      data: tenantPayload({}),
      success: function (res) {
        if (res.statusCode === 200 && res.data && res.data.uuid) {
          resolve(res.data);
          return;
        }
        reject({
          error:
            (res.data && (res.data.error || res.data.detail)) ||
            'HTTP ' + res.statusCode,
          statusCode: res.statusCode,
          raw: res,
        });
      },
      fail: function (res) {
        reject({ error: (res && res.errMsg) || '网络请求失败', raw: res });
      },
    });
  });
}

function todayStr() {
  var d = new Date();
  var month = d.getMonth() + 1;
  var day = d.getDate();
  return (
    d.getFullYear() +
    '-' +
    (month < 10 ? '0' + month : '' + month) +
    '-' +
    (day < 10 ? '0' + day : '' + day)
  );
}

// 把页面筛选键翻译成后端参数：today/overdue/in_progress/completed。
function mpTaskFilterParams(key) {
  var params = {};
  key = key || '';
  if (key === 'today') {
    params.due_date = todayStr();
  } else if (key === 'overdue') {
    params.overdue = '1';
  } else if (key === 'in_progress') {
    params.status = '20';
  } else if (key === 'completed') {
    params.status = '30';
  }
  return params;
}

module.exports = {
  mpTaskSummary: mpTaskSummary,
  mpTaskList: mpTaskList,
  mpTaskDetail: mpTaskDetail,
  mpTaskAttempt: mpTaskAttempt,
  mpTaskAttemptDelete: mpTaskAttemptDelete,
  mpTaskComplete: mpTaskComplete,
  mpTaskStatus: mpTaskStatus,
  mpTaskSuggest: mpTaskSuggest,
  mpTimeline: mpTimeline,
  mpTimelineCreate: mpTimelineCreate,
  mpVipSearch: mpVipSearch,
  mpVipDetail: mpVipDetail,
  mpTaskFilterParams: mpTaskFilterParams,
};
