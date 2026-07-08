/**
 * 与 my/login/login.js userLogin 中 wx.request 形状保持一致。
 * 若 login.js 修改请求格式，请同步更新本文件。
 */
function buildCheckUserpwdRequest(globalData, pageData) {
  return {
    method: 'GET',
    url: globalData.host + 'common/check_userpwd',
    data: {
      company: pageData.company,
      storecode: pageData.storecode,
      usercode: pageData.usercode,
      password: pageData.password,
    },
  };
}

function handleLoginSuccess(res, app, pageData, hooks) {
  if (res.data == 200) {
    app.globalData.company = pageData.company;
    app.globalData.storecode = pageData.storecode;
    app.globalData.usercode = pageData.usercode;
    app.globalData.ecode = pageData.usercode;
    app.globalData.network_allow_flag = true;
    app.globalData.network_disallow_flag = false;
    hooks.saveLocal();
    hooks.reLaunch('/index/index');
    return true;
  }
  if (res.data == 500) {
    hooks.openAlert({ content: '用户名/密码不对!' });
    return false;
  }
  return false;
}

describe('login API contract', () => {
  const globalData = {
    host: 'http://192.168.1.6:8030/',
  };
  const pageData = {
    company: 'demo',
    storecode: '88',
    usercode: '888',
    password: 'secret',
  };

  test('buildCheckUserpwdRequest matches login.js URL and params', () => {
    const req = buildCheckUserpwdRequest(globalData, pageData);
    expect(req.method).toBe('GET');
    expect(req.url).toBe('http://192.168.1.6:8030/common/check_userpwd');
    expect(req.data).toEqual({
      company: 'demo',
      storecode: '88',
      usercode: '888',
      password: 'secret',
    });
  });

  test('handleLoginSuccess on 200 updates globalData and navigates', () => {
    const app = { globalData: { ...globalData } };
    const hooks = {
      saveLocal: jest.fn(),
      reLaunch: jest.fn(),
      openAlert: jest.fn(),
    };
    const ok = handleLoginSuccess({ data: 200 }, app, pageData, hooks);
    expect(ok).toBe(true);
    expect(app.globalData.company).toBe('demo');
    expect(app.globalData.ecode).toBe('888');
    expect(app.globalData.network_allow_flag).toBe(true);
    expect(hooks.reLaunch).toHaveBeenCalledWith('/index/index');
  });

  test('handleLoginSuccess on 500 shows alert', () => {
    const app = { globalData: { ...globalData } };
    const hooks = {
      saveLocal: jest.fn(),
      reLaunch: jest.fn(),
      openAlert: jest.fn(),
    };
    const ok = handleLoginSuccess({ data: 500 }, app, pageData, hooks);
    expect(ok).toBe(false);
    expect(hooks.openAlert).toHaveBeenCalledWith(
      expect.objectContaining({ content: '用户名/密码不对!' })
    );
  });
});

module.exports = { buildCheckUserpwdRequest, handleLoginSuccess };
