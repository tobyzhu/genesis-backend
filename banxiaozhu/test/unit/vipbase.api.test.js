/**
 * 与 vip/viputils.js getVipBaseInfo、commitHung 的 wx.request 形状保持一致。
 * 若 viputils.js 修改请求格式，请同步更新本文件。
 */
const util = require('../../utils/util.js');

function normalizeVipUuid(optionVipuuid) {
  if (optionVipuuid.length > 32) {
    return optionVipuuid.split('-').join('');
  }
  return optionVipuuid;
}

function buildGetVipBaseInfoRequest(globalData, options) {
  let optionVipuuid = '';
  if (options.uuid) {
    optionVipuuid = options.uuid;
  }
  if (options.vipuuid) {
    optionVipuuid = options.vipuuid;
  }
  const vipuuid_s = normalizeVipUuid(optionVipuuid);
  const vipuuid_u = util.strtouuid(vipuuid_s);
  return {
    method: 'GET',
    url: globalData.host + 'baseinfo/vip/' + vipuuid_u,
    header: {
      'content-type': 'application/json',
    },
    vipuuid_s,
    vipuuid_u,
  };
}

function buildCommitHungRequest(globalData, options) {
  const param = options;
  return {
    method: 'POST',
    url: globalData.host + 'adviser/addhung/?param=' + JSON.stringify(param),
    header: {
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8',
    },
  };
}

describe('getVipBaseInfo & commitHung API contract', () => {
  const globalData = {
    host: 'http://192.168.1.6:8030/',
    company: 'demo',
    storecode: '88',
    ecode: '888',
  };

  test('buildGetVipBaseInfoRequest formats UUID in URL path', () => {
    const raw = '0123456789abcdef0123456789abcdef';
    const req = buildGetVipBaseInfoRequest(globalData, { vipuuid: raw });
    expect(req.method).toBe('GET');
    expect(req.url).toBe(
      'http://192.168.1.6:8030/baseinfo/vip/' + util.strtouuid(raw)
    );
    expect(req.vipuuid_u).toBe('01234567-89ab-cdef-0123-456789abcdef');
  });

  test('buildGetVipBaseInfoRequest strips dashes from long uuid input', () => {
    const dashed =
      '01234567-89ab-cdef-0123-456789abcdef';
    const req = buildGetVipBaseInfoRequest(globalData, { uuid: dashed });
    expect(req.vipuuid_s).toBe('0123456789abcdef0123456789abcdef');
    expect(req.url).toContain(util.strtouuid(req.vipuuid_s));
  });

  test('buildCommitHungRequest POSTs param in query string', () => {
    const hungParam = {
      company: 'demo',
      storecode: '88',
      ecode: '888',
      vipuuid: 'vip-001',
      itemuuid: 'item-001',
      qty: 1,
    };
    const req = buildCommitHungRequest(globalData, hungParam);
    expect(req.method).toBe('POST');
    expect(req.url).toBe(
      'http://192.168.1.6:8030/adviser/addhung/?param=' +
        JSON.stringify(hungParam)
    );
    expect(req.header['content-type']).toContain('x-www-form-urlencoded');
  });
});

module.exports = {
  buildGetVipBaseInfoRequest,
  buildCommitHungRequest,
  normalizeVipUuid,
};
