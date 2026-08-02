const fakeApp = {
  globalData: {
    host: 'http://x/',
    company: 'yiren',
    storecode: '01',
    ecode: '888',
  },
};

global.getApp = () => fakeApp;

let requests = [];
global.wx = {
  request: (opts) => {
    requests.push(opts);
    opts.success({ statusCode: 200, data: { ok: true, data: { result: 1 } } });
  },
  setClipboardData: () => {},
};

const crm = require('../crm.js');

describe('crm mp utils', () => {
  beforeEach(() => {
    requests = [];
  });

  test('mpTaskSummary sends tenant params', async () => {
    const res = await crm.mpTaskSummary({ limit: 5 });
    expect(res.data.result).toBe(1);
    const req = requests[0];
    expect(req.url).toBe('http://x/crm/mp/tasks/summary/');
    expect(req.method).toBe('GET');
    expect(req.data).toMatchObject({
      company: 'yiren',
      storecode: '01',
      ecode: '888',
      limit: 5,
    });
  });

  test('mpTaskAttempt posts payload', async () => {
    await crm.mpTaskAttempt('abc', { detail: 'x' });
    const req = requests[0];
    expect(req.method).toBe('POST');
    expect(req.data).toMatchObject({
      company: 'yiren',
      storecode: '01',
      ecode: '888',
      detail: 'x',
    });
  });

  test('rejects non-ok response', async () => {
    global.wx.request = (opts) =>
      opts.success({ statusCode: 200, data: { ok: false, error: 'boom' } });
    await expect(crm.mpTaskList({})).rejects.toMatchObject({ error: 'boom' });
  });

  test('mpTaskFilterParams maps filter keys', () => {
    expect(crm.mpTaskFilterParams('')).toEqual({});
    expect(crm.mpTaskFilterParams('overdue')).toEqual({ overdue: '1' });
    expect(crm.mpTaskFilterParams('in_progress')).toEqual({ status: '20' });
    expect(crm.mpTaskFilterParams('completed')).toEqual({ status: '30' });
    expect(crm.mpTaskFilterParams('today').due_date).toMatch(/^\d{4}-\d{2}-\d{2}$/);
  });

  test('mpVipDetail resolves vip object', async () => {
    global.wx.request = (opts) => {
      requests.push(opts);
      opts.success({
        statusCode: 200,
        data: { uuid: 'abc', vname: '张三', vcode: '0100594' },
      });
    };
    const vip = await crm.mpVipDetail('abc');
    expect(vip.vname).toBe('张三');
    const req = requests[0];
    expect(req.url).toBe('http://x/crm/vip/abc/');
    expect(req.data).toMatchObject({ company: 'yiren', storecode: '01', ecode: '888' });
  });

  test('mpTaskAttemptDelete sends DELETE', async () => {
    await crm.mpTaskAttemptDelete('task1', 'attempt1');
    const req = requests[0];
    expect(req.method).toBe('DELETE');
    expect(req.url).toBe('http://x/crm/mp/tasks/task1/attempt/attempt1/');
    expect(req.data).toMatchObject({ company: 'yiren', storecode: '01', ecode: '888' });
  });
});
