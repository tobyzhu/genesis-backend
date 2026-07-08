/**
 * 与 vip/checkout/checkout.js 中 loadHungItems、差额计算、结账 wx.request 形状保持一致。
 * 若 checkout.js 修改请求格式，请同步更新本文件。
 */
function buildLoadHungItemsRequest(globalData, pageData) {
  return {
    method: 'GET',
    url: globalData.host + 'adviser/get_hung_byvipuuid/',
    data: {
      company: globalData.company,
      storecode: globalData.storecode,
      vipuuid: pageData.vipuuid,
    },
  };
}

function buildCheckoutShortfallRequest(globalData, pageData, hunguuids) {
  return {
    method: 'GET',
    url: globalData.host + 'adviser/get_checkout_shortfall/',
    data: {
      company: globalData.company,
      storecode: globalData.storecode,
      vipuuid: pageData.vipuuid,
      hunguuids: JSON.stringify(hunguuids),
    },
  };
}

function buildCheckoutHungsRequest(globalData, pageData, hunguuids, extra) {
  return {
    method: 'POST',
    url: globalData.host + 'adviser/checkout_hungs/',
    data: {
      company: globalData.company,
      storecode: globalData.storecode,
      vipuuid: pageData.vipuuid,
      hunguuids: hunguuids,
      extra_paymode: extra.extraPaymode,
      extra_pay_amount: extra.extraDue,
      extra_payments: extra.extraPayments,
    },
    header: {
      'content-type': 'application/json',
    },
  };
}

describe('checkout API contract', () => {
  const globalData = {
    host: 'http://192.168.1.6:8030/',
    company: 'demo',
    storecode: '88',
  };
  const pageData = { vipuuid: 'vip-uuid-001' };

  test('buildLoadHungItemsRequest matches checkout.js loadHungItems', () => {
    const req = buildLoadHungItemsRequest(globalData, pageData);
    expect(req.method).toBe('GET');
    expect(req.url).toBe(
      'http://192.168.1.6:8030/adviser/get_hung_byvipuuid/'
    );
    expect(req.data).toEqual({
      company: 'demo',
      storecode: '88',
      vipuuid: 'vip-uuid-001',
    });
  });

  test('buildCheckoutShortfallRequest JSON-stringifies hunguuids', () => {
    const hids = ['h1', 'h2'];
    const req = buildCheckoutShortfallRequest(globalData, pageData, hids);
    expect(req.method).toBe('GET');
    expect(req.url).toBe(
      'http://192.168.1.6:8030/adviser/get_checkout_shortfall/'
    );
    expect(req.data.hunguuids).toBe(JSON.stringify(hids));
    expect(req.data.vipuuid).toBe('vip-uuid-001');
  });

  test('buildCheckoutHungsRequest POSTs JSON body with extra payments', () => {
    const hids = ['h1'];
    const req = buildCheckoutHungsRequest(globalData, pageData, hids, {
      extraPaymode: 'CASH',
      extraDue: 50,
      extraPayments: [{ pcode: 'CASH', amount: 50 }],
    });
    expect(req.method).toBe('POST');
    expect(req.url).toBe(
      'http://192.168.1.6:8030/adviser/checkout_hungs/'
    );
    expect(req.data).toEqual({
      company: 'demo',
      storecode: '88',
      vipuuid: 'vip-uuid-001',
      hunguuids: hids,
      extra_paymode: 'CASH',
      extra_pay_amount: 50,
      extra_payments: [{ pcode: 'CASH', amount: 50 }],
    });
    expect(req.header['content-type']).toBe('application/json');
  });
});

module.exports = {
  buildLoadHungItemsRequest,
  buildCheckoutShortfallRequest,
  buildCheckoutHungsRequest,
};
