---
name: genesis-vip-crm-runtime
description: >-
  Genesis assistant 运行时客户管理助手（profile_id=vip_crm）的领域说明与工具索引。
  供维护 assistant 模块时参考；Cursor 开发 skill 见仓库 .cursor/skills/genesis-vip-agent/。
---

# 客户管理助手（vip_crm）运行时说明

本目录描述 Django `assistant` 应用中 **profile_id = vip_crm** 的客户管理专用助手。

## 与通用助手的区别

- **通用助手**（`profile_id=general`）：营业、交易、挂单、报表等全量工具。
- **客户管理助手**（`profile_id=vip_crm`）：聚焦 `vip` 表及 CRM，工具子集 + VIP 专用工具。

## 配置入口

- Profile 定义：`assistant/agent_profiles.py` → `PROFILE_VIP_CRM`
- VIP 工具：`assistant/vip_tools.py`
- 对话路由：`assistant/views.py` → `assistant_chat_api`

## 数据约定

- 客户主键：vip 表列 `uuid`（口语称 vipuuid 指该 UUID 值）
- 外键列：expvstoll.vipuuid、cardinfo.vipuuid 等指向 vip.uuid
- 会员号：`vcode`；手机：`mtcode` / `telph`
- 有效交易：`expvstoll.valiflag = 'Y'`
- 软删除：`flag = 'N'` 的记录不应返回

## 新增工具检查清单

- [ ] 函数签名含 `company`, `storecode`
- [ ] 结果行数 ≤ 80（或工具内显式 limit）
- [ ] 已加入 `VIP_ONLY_REGISTRY` 与 catalog 文本
- [ ] 客户画像/流失风险：`vip_profile`、`vip_churn_risk`（支持 telph/vipuuid/vcode）
- [ ] 沉睡预警需说明 `inactive_days` / `risk_level` 口径
- [ ] 批量导出走 `assistant_vip_batch_export_api`（上限 5000 行）
- [ ] 新工具须加 `assistant/tests/test_<tool>.py`；先 `bash scripts/setup-test-db.sh`，再 `GENESIS_USE_TEST_DB=1 pytest assistant/tests`

详细开发指南见项目根目录 `.cursor/skills/genesis-vip-agent/SKILL.md`。
