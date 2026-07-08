# banxiaozhu API 对照表

小程序函数 / 页面 → HTTP 路径 → 后端 app。开发环境 base：`globalData.host`（如 `http://192.168.1.6:8030/`）。

**通用 query params**：`company`, `storecode`, `ecode`（多数接口还需 `appcode`, `openid`）。

---

## wechat/

| 调用方 | 方法 | 路径 | 主要参数 | 后端 |
|--------|------|------|----------|------|
| `app.js` onLaunch | GET | `wechat/wechatlogin/` | `appcode`, `code` | `wechat/views.py` WechatLogin |
| `wxutils.js` | GET | `wechat/getphone` | `encryptedData`, `iv`, `session_key` | getphone |
| `util.getWechatFunction` | GET | `wechat/get_wechatapp_function/` | `company`, `storecode`, `option` | Get_WechatApp_Function |

---

## common/

| 调用方 | 方法 | 路径 | 主要参数 | 后端 |
|--------|------|------|----------|------|
| `util.checkNetwork` | GET | `common/check_wifilist/` | `networktype`, `ssid`, `bssid` | check_WifiList |
| `my/login/login.js` | GET | `common/check_userpwd` | `company`, `storecode`, `usercode`, `password` | check_userpwd |

`check_userpwd` 成功返回 `'200'`，失败 `'500'`（非 JSON）。

---

## baseinfo/

| util 函数 | 方法 | 路径 | 说明 |
|-----------|------|------|------|
| `get_VipList` | GET | `baseinfo/get_viplist_byecode/` | 顾问名下 VIP 列表 |
| `get_Vip10List` 等 | GET | `adviser/get_vipList_byviptypeandecode/` | 按 viptype 筛选 |
| `get_VipInList` 等 | GET | `adviser/get_viplist_bylevel/` | 按等级筛选 |
| `get_cardtypelist` | GET | `baseinfo/get_cardtypelist` | 卡类型 |
| `get_empllist` | GET | `baseinfo/get_empllist/` | 员工列表 |
| `get_SrvList` / `get_GoodsList` | GET | `adviser/get_vip_itemlist` | 服务/商品（带 item 参数） |
| `get_appoption_byseg` | GET | `baseinfo/get_appoption_byseg/` | 选项字典 |
| `get_nextvcode` | GET | `baseinfo/get_nextvcode/` | 新会员号 |
| `get_RoomList` | GET | `baseinfo/get_roomlist/` | 房间 |
| `get_SalonList` | GET | `baseinfo/get_salonlist/` | 沙龙 |
| `viputils.getVipBaseInfo` | GET | `baseinfo/vip/{uuid}` | VIP 详情（uuid 用 strtouuid） |

---

## adviser/（开单 / 挂单 / 购物车 / 结账）

| 调用方 | 方法 | 路径 | param 说明 |
|--------|------|------|------------|
| `viputils.getVipCardList` | GET | `adviser/get_vip_cardlist/` | query: `vipuuid`, `suptype` |
| `viputils.newCardHung` | GET | `adviser/newcardhung/?param=` | JSON: 新卡挂单 |
| `viputils.commitHung` | GET | `adviser/addhung/?param=` | JSON: 提交挂单 |
| `viputils.getHung` | GET | `adviser/get_hung_byvipuuid/` | query: `vipuuid` |
| `viputils.getHungItem` | GET | `adviser/get_hungitem/` | 挂单明细 |
| `goods.js` / `serviece.js` 等 | GET | `adviser/addshoppingcart/?param=` | JSON: 加入购物车 |
| `shoppingcar.js` | GET | `adviser/modify_shoppingcartitem/?param=` | JSON: 改购物车项 |
| `shoppingcar.js` | GET | `adviser/shoppingcarthung/?param=` | JSON: 购物车转挂单 |
| `fillcard.js` | GET | `adviser/fillcardhung/?param=` | JSON: 充卡挂单 |
| `viputils.get_shoppingcart` | GET | `adviser/get_shoppingcart/?param=` | JSON |
| `viputils.get_ShoppingCartItem` | GET | `adviser/get_shoppingcartitem/?param=` | JSON |
| `util.getInstoreVipList` | GET | `adviser/get_instore_vips/` | 在店未结账客人 |
| `checkout.js` | GET | `adviser/get_hung_byvipuuid/` | 结账前拉挂单 |
| `checkout.js` | GET | `adviser/get_checkout_shortfall/` | 差额 |
| `checkout.js` | GET | `adviser/checkout_hungs/?param=` | JSON: 结账 |
| `util.get_emplarch_bymonth` | GET | `cashier/get_emplarch_bymonth/` | 员工业绩 |

---

## crm/

| viputils 函数 | 方法 | 路径 |
|---------------|------|------|
| `getVipConsume` | GET | `crm/get_vipconsumelist/` |
| `get_vipcasedetail_byvipuuid` | GET | `crm/get_vipcasedetail_byvipuuid` |
| `get_vipcasedetail` | GET | `crm/get_vipcasedetail` |
| `get_SalonVipList` | GET | `crm/get_salonvip_list/` |
| `get_SalonVipDetail` | GET | `crm/get_salonvip_detail/` |
| `get_viplist_bycrmrptid` | GET | `crm/get_viplist_bycrmrptid` |

---

## report/

| util 函数 | 方法 | 路径 |
|-----------|------|------|
| `get_VipcntList` | GET | `report/get_invipcnt` |
| `get_DailyStoreData` | GET | `report/get_dailystoredata` |

---

## 后端 URL 入口

| Django app | urls 文件 |
|------------|-----------|
| 顶层挂载 | `genesis_backend/genesis/urls.py` |
| wechat | `genesis_backend/wechat/urls.py` |
| common | `genesis_backend/common/urls.py` |
| baseinfo | `genesis_backend/baseinfo/urls.py` |
| adviser | `genesis_backend/adviser/urls.py` |
| crm | `genesis_backend/crm/urls.py` |
| report | `genesis_backend/report/urls.py` |
| cashier | `genesis_backend/cashier/urls.py` |
