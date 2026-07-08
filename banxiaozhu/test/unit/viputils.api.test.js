/**
 * 与 vip/viputils.js 中 getHung、get_shoppingcart_ttype 的 wx.request 形状保持一致。
 * 若 viputils.js 修改请求格式，请同步更新本文件。
 */
function buildGetHungRequest(globalData) {
  return {
    method: 'GET',
    url: globalData.host + 'adviser/get_hung_byvipuuid/',
    data: {
      company: globalData.company,
      storecode: globalData.storecode,
      ecode: globalData.ecode,
      vipuuid: globalData.currentvip.uuid,
    },
  };
}

function buildShoppingcartTtypeRequest(globalData, options) {
  const param = {
    company: globalData.company,
    storecode: globalData.storecode,
    ecode: globalData.ecode,
    vipuuid: options.vipuuid,
    ttype: options.ttype,
  };
  return {
    method: 'POST',
    url:
      globalData.host +
      'adviser/get_shoppingcart/?param=' +
      JSON.stringify(param),
    header: {
      'content-type': 'application /x-www-form-urlencoded;charset=utf-8',
    },
  };
}

describe('viputils API contract', () => {
  const globalData = {
    host: 'http://192.168.1.6:8030/',
    company: 'demo',
    storecode: '88',
    ecode: '888',
    currentvip: { uuid: 'abc123vipuuid' },
  };

  test('buildGetHungRequest matches getHung URL and params', () => {
    const req = buildGetHungRequest(globalData);
    expect(req.method).toBe('GET');
    expect(req.url).toBe(
      'http://192.168.1.6:8030/adviser/get_hung_byvipuuid/'
    );
    expect(req.data).toEqual({
      company: 'demo',
      storecode: '88',
      ecode: '888',
      vipuuid: 'abc123vipuuid',
    });
  });

  test('buildShoppingcartTtypeRequest serializes param in query string', () => {
    const req = buildShoppingcartTtypeRequest(globalData, {
      vipuuid: 'abc123vipuuid',
      ttype: 'S',
    });
    expect(req.method).toBe('POST');
    expect(req.url).toBe(
      'http://192.168.1.6:8030/adviser/get_shoppingcart/?param=' +
        JSON.stringify({
          company: 'demo',
          storecode: '88',
          ecode: '888',
          vipuuid: 'abc123vipuuid',
          ttype: 'S',
        })
    );
    expect(req.header['content-type']).toContain('x-www-form-urlencoded');
  });

  test('get_shoppingcart_ttype G type uses same endpoint with ttype G', () => {
    const req = buildShoppingcartTtypeRequest(globalData, {
      vipuuid: 'abc123vipuuid',
      ttype: 'G',
    });
    expect(req.url).toContain('"ttype":"G"');
  });
});

module.exports = {
  buildGetHungRequest,
  buildShoppingcartTtypeRequest,
};
