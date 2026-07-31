/**
 * Jest 全局 mock：wx API 与 getApp（须在 require util.js 之前生效）。
 */

const mockGlobalData = {
  host: 'http://127.0.0.1:8030/',
  appcode: '100',
  company: 'testco',
  storecode: '99',
  ecode: '888',
  openid: 'test-openid',
  networkenable: true,
};

const storage = {};

global.wx = {
  request: jest.fn(),
  login: jest.fn((opts) => opts && opts.success && opts.success({ code: 'mock-code' })),
  getStorageSync: jest.fn((key) => storage[key]),
  setStorageSync: jest.fn((key, val) => {
    storage[key] = val;
  }),
  setStorage: jest.fn(),
  getStorage: jest.fn(),
  reLaunch: jest.fn(),
  showModal: jest.fn(),
  getRealtimeLogManager: jest.fn(() => null),
  getNetworkType: jest.fn((opts) => opts && opts.success && opts.success({ networkType: 'wifi' })),
};

global.getApp = jest.fn(() => ({
  globalData: mockGlobalData,
  userInfoReadyCallback: null,
}));

global.getCurrentPages = jest.fn(() => []);

global.Page = jest.fn((config) => config);
global.App = jest.fn((config) => config);

beforeEach(() => {
  jest.clearAllMocks();
  Object.keys(storage).forEach((k) => delete storage[k]);
});
