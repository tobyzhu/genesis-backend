## Summary

- 添加 GitHub Actions 工作流 `.github/workflows/tests.yml`（banxiaozhu Jest + 可选 backend pytest）
- 补充 assistant 集成测试：VIP 工具、search_vips、readonly_sql、table catalog、assistant API（含导出）
- 补充 banxiaozhu API 契约测试（login、viputils、vipbase、checkout）
- 修复 `assistant/context_pack.py` 缩进错误
- 添加 CI / Secrets 说明文档 `scripts/CI.md`

## Test plan

- [ ] 在 GitHub 仓库 Settings → Secrets 配置 `GENESIS_DB_*`（见 `scripts/CI.md`）
- [ ] 本地：`bash scripts/test-all.sh`
- [ ] 推送分支后确认 Actions 中 **banxiaozhu (Jest)** 通过
- [ ] 配置 Secrets 后确认 **genesis_backend (pytest)** 通过

## Secrets（首次启用 backend CI）

| Secret | 说明 |
|--------|------|
| `GENESIS_DB_HOST` | MySQL 主机 |
| `GENESIS_DB_USER` | 数据库用户 |
| `GENESIS_DB_PASSWORD` | 密码 |
| `GENESIS_DB_NAME` | 源库名（如 `genesis_dev`） |
| `GENESIS_DB_PORT` | 可选，默认 3306 |
