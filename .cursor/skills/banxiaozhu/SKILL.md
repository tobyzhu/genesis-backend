---
name: banxiaozhu
description: >-
  Genesis 帮小主微信小程序开发助手：启动与登录流程、globalData、
  wx.request API 约定、util.js/viputils.js 扩展、本地联调。
  在 banxiaozhu/ 下新增/修改页面、对接 genesis_backend API 时使用。
disable-model-invocation: true
---

# 帮小主（banxiaozhu）微信小程序

## 概述

**帮小主** 是 Genesis 美业 ERP 的微信小程序，供门店员工使用：VIP 客户、开单/挂单/结账、CRM、店务报表。

| 概念 | 说明 |
|------|------|
| `appcode` | `'100'` = 帮小主（`app.js` globalData） |
| `company` / `storecode` / `ecode` | 租户、门店、员工工号 — 几乎每个 API 必传 |
| 认证 | WiFi 门店绑定 + 员工密码，**非 JWT** |
| 后端 | [`genesis_backend/`](../genesis_backend/)，开发默认 `http://<LAN-IP>:8030/` |

**分工**：本 skill 管小程序 UI 与请求；后端 AI 助手见 [`genesis-vip-agent`](../genesis-vip-agent/SKILL.md)（`assistant/vip_crm` 只读工具）。

## 应用入口

启动顺序（[`banxiaozhu/app.json`](../../banxiaozhu/app.json)）：`checknetwork` → `login` → `index`。

Tab 栏：首页 / 客户 / 店务 / 我的。

```
banxiaozhu/
├── app.js, app.json          # 全局配置、globalData、wx.login
├── utils/util.js             # 通用 API、网络检测、主数据加载
├── vip/viputils.js           # VIP、卡项、挂单、购物车
├── index/                    # 首页、在店客人
├── vip/                      # 客户 tab（最大模块）
├── query/                    # 店务 tab
├── todolist/                 # CRM 待办
└── my/                       # 登录、网络、我的
```

## 认证与 globalData 生命周期

1. `wx.login` → `GET wechat/wechatlogin/?appcode=100&code=...` → `openid`, `session_key`, `user_uuid`
2. WiFi BSSID → `GET common/check_wifilist/?networktype=wifi&bssid=...` → `company`, `storecode`
3. 员工登录 → `GET common/check_userpwd?company&storecode&usercode&password` → `'200'` 或 `'500'`
4. 写入 `app.globalData.company / storecode / ecode`

**关键 globalData 字段**（[`banxiaozhu/app.js`](../../banxiaozhu/app.js)）：

| 字段 | 用途 |
|------|------|
| `host` | API 根地址 |
| `company`, `storecode`, `ecode` | 租户上下文 |
| `openid`, `appcode` | 微信身份 |
| `currentvip`, `currentvipuuid_s/u` | 当前选中客户 |
| `currentvip_*cardlist` | 卡项缓存 |
| `shoppingcart_item_*` | 购物车 |
| `isDev` | `true` 时 WiFi 失败 fallback 到 demo 公司 |

## API 调用约定

- 几乎全部为 **GET + query params**
- 业务请求带 `company`, `storecode`, `ecode`（常还有 `appcode`, `openid`）
- 复杂写入：`?param=` + `JSON.stringify(...)`（如 `adviser/addshoppingcart/`）
- UUID：REST 路径用 `util.strtouuid()`；storage 常用无连字符格式
- **新 API 封装位置**：
  - 通用 → [`banxiaozhu/utils/util.js`](../../banxiaozhu/utils/util.js)
  - VIP/开单 → [`banxiaozhu/vip/viputils.js`](../../banxiaozhu/vip/viputils.js)
  - 避免在 page `.js` 内重复 `wx.request`

完整接口对照见 [references/api-map.md](references/api-map.md)。

## 本地联调

1. 改 [`banxiaozhu/app.js`](../../banxiaozhu/app.js) 中 `globalData.host` 为电脑局域网 IP，例如 `http://192.168.1.8:8030/`
2. 或控制台执行：`wx.setStorageSync('genesis_api_host', 'http://192.168.1.8:8030/')` 后重启小程序
3. 后端：`cd genesis_backend && python manage.py runserver 0.0.0.0:8030`
4. 微信开发者工具：详情 → 本地设置 → 勾选「不校验合法域名…」
5. [`banxiaozhu/project.config.json`](../../banxiaozhu/project.config.json) 中 `urlCheck: false`
6. **真机不能用 127.0.0.1** — 必须 LAN IP；手机与电脑同一 WiFi

## 改代码 Checklist

1. 确认模块：`vip` / `query` / `todolist` / `my`
2. 查 `util.js` / `viputils.js` 是否已有封装
3. 新后端接口：同时改 `genesis_backend/<app>/urls.py` 与对应 view
4. 新页面：四文件 `.js` / `.wxml` / `.wxss` / `.json`，并在 `app.json` 注册
5. 动态菜单：后端 `WechatAppFunctions` + 前端 merge（`util.mergeInstoreVipGridItem` 等）
6. Tab 快捷入口：改 `getWechatFunction` 返回的 grids，或 `app.json` tabBar / 页面内导航

## 开单 / 结账数据流

| 状态 | 后端表 | 小程序入口 |
|------|--------|-----------|
| 未结账（挂单） | `expvstoll_hung`, `expense_hung` | `vip/kaidan`, `vip/shoppingcar` |
| 已结账 | `expvstoll`, `expense`, `toll` | `vip/checkout/checkout.js` |

结账关键接口：`get_hung_byvipuuid/` → `get_checkout_shortfall/` → `checkout_hungs/`（均 `?param=JSON` 或 query params）。

**PC 手工开单（genesis_pc）**：完整流程、储值卡定价规则、后端校验与测试见 [pc-manual-billing.md](pc-manual-billing.md)。**营销活动/活动设定**（特价/折扣走活动分组主从、组合销售走活动明细）见 [pc-promotions.md](pc-promotions.md)。PC **全站**业务色必须用 `--g-color-*` 语义 token（layouts/views/components），禁止新增业务裸十六进制；顶栏可切换 azure/salon/moss。

## 常见陷阱

- 无统一 HTTP client，错误处理各页不一致 — 优先复用 util 封装
- 安全依赖 query params + WiFi，不是 Bearer token — 勿漏 `company/storecode/ecode`
- `check_userpwd` 返回字符串 `'200'`/`'500'`，比较用 `res.data == 200`
- `isDev` + WiFi 失败会走 demo 公司（`yiren` / `01`）
- 勿改 `lib/regenerator-runtime/` 等 vendored 目录
- URL 拼接注意双斜杠（如 `host + '/crm/...'`）

## 关键文件

| 用途 | 路径 |
|------|------|
| 全局配置 | `banxiaozhu/app.js` |
| 页面注册 | `banxiaozhu/app.json` |
| 共享 API | `banxiaozhu/utils/util.js` |
| VIP 业务 | `banxiaozhu/vip/viputils.js` |
| 微信登录/手机 | `banxiaozhu/utils/wxutils.js` |
| 网络检测 | `banxiaozhu/my/checknetwork/checknetwork.js` |
| 员工登录 | `banxiaozhu/my/login/login.js` |
| 主数据预加载 | `banxiaozhu/index/index.js` |
| 结账 | `banxiaozhu/vip/checkout/checkout.js` |
| 客户 tab 入口 | `banxiaozhu/vip/vipindex/vipindex.js` |
| 后端路由 | `genesis_backend/genesis/urls.py` |
| 微信 API | `genesis_backend/wechat/views.py` |
| 登录/WiFi | `genesis_backend/common/views.py` |
| 开单/购物车 | `genesis_backend/adviser/urls.py` |

## 验证场景（skill 自检）

| 场景 | skill 应指引 |
|------|-------------|
| 客户 tab 加快捷入口 | `getWechatFunction` + merge 函数，或 `vipindex` 页面导航 |
| checkout 报错 | 查 `checkout.js` 三个 adviser 接口 + `?param=` 格式 |
| 真机连不上后端 | `host` / `genesis_api_host` + `runserver 0.0.0.0:8030` |

## 测试

```bash
cd banxiaozhu && npm test
```

约定：

- 新 API 封装须加 `test/unit/*.test.js`（mock `wx.request`）
- 修改 `util.js` 纯函数后跑 `npm test`
- 登录请求契约见 `test/unit/login.api.test.js`（与 `my/login/login.js` 保持同步）
- VIP/挂单/购物车契约见 `test/unit/viputils.api.test.js`、`test/unit/vipbase.api.test.js`
- 结账契约见 `test/unit/checkout.api.test.js`

全仓库：`bash scripts/test-all.sh`（含 genesis_backend pytest）。

CI：GitHub Actions 工作流 `.github/workflows/tests.yml`（Jest 必跑；后端 pytest 需配置仓库 Secrets，见 [`scripts/CI.md`](../../scripts/CI.md)）。
