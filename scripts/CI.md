# Genesis 测试与 CI

GitHub：[tobyzhu](https://github.com/tobyzhu) · 推荐远程仓库 [`genesis-backend`](https://github.com/tobyzhu/genesis-backend)（本目录为 monorepo：`genesis_backend/` + `banxiaozhu/` + `scripts/`）。

本地一键跑测：

```bash
bash scripts/test-all.sh
```

## 首次推送到 GitHub

```bash
cd /path/to/Genesis
git init
git checkout -b feat/test-suite-and-ci
git add .
git commit -m "Add test suite, GitHub Actions CI, and CI documentation."
git remote add origin https://github.com/tobyzhu/genesis-backend.git
git push -u origin feat/test-suite-and-ci
```

在 GitHub 打开 **Compare & pull request**，正文可用 [`scripts/PR-test-suite.md`](PR-test-suite.md)。

若远程已有历史，先 `git pull origin main --rebase` 再 push。

## 本地后端测试（MySQL）

1. 在 `genesis_backend/.env` 配置源库（与开发环境相同）：

   ```env
   DB_HOST=101.200.55.5
   DB_PORT=3306
   DB_USER=...
   DB_PASSWORD=...
   DB_NAME=genesis_dev
   ```

2. 克隆表结构到 `test_<DB_NAME>`（不复制数据）：

   ```bash
   bash scripts/setup-test-db.sh
   ```

3. 运行 pytest：

   ```bash
   cd genesis_backend
   GENESIS_USE_TEST_DB=1 .venv/bin/pytest assistant/tests -q
   ```

## GitHub Actions

工作流：`.github/workflows/tests.yml`

| Job | 触发条件 | 说明 |
|-----|----------|------|
| `banxiaozhu` | 每次 push / PR | `npm ci && npm test`，无需 Secrets |
| `backend` | 配置了 DB Secrets 时 | `setup-test-db.sh` + `pytest assistant/tests` |

未配置 Secrets 时，backend job 会 **跳过**（显示 notice），PR 仍可合并；Jest 失败则 CI 失败。

## 仓库 Secrets 配置

路径：**GitHub 仓库 → Settings → Secrets and variables → Actions → New repository secret**

| Secret 名称 | 必填 | 说明 | 示例 |
|-------------|------|------|------|
| `GENESIS_DB_HOST` | 是 | MySQL 主机 | `101.200.55.5` |
| `GENESIS_DB_USER` | 是 | 数据库用户 | `sa` |
| `GENESIS_DB_PASSWORD` | 是 | 数据库密码 | （勿提交到代码库） |
| `GENESIS_DB_NAME` | 是 | **源库**名（非 test_ 前缀） | `genesis_dev` |
| `GENESIS_DB_PORT` | 否 | 端口，默认 `3306` | `3306` |

CI 会：

1. 用上述值写入 `genesis_backend/.env`（仅 runner 临时目录，不入库）
2. 执行 `scripts/setup-test-db.sh`，从 `DB_NAME` 克隆结构到 `test_<DB_NAME>`
3. 以 `GENESIS_USE_TEST_DB=1` 运行 pytest

### 权限与安全

- 测试库账号只需对 `test_*` 库及源库的 `CREATE`、`SELECT`（读 information_schema / `CREATE TABLE LIKE`）；**不要**给生产写权限。
- 建议使用只读或专用 CI 账号；密码仅放在 GitHub Secrets，不要写入 `.env` 提交。
- Fork 的 PR **无法**使用上游 Secrets；backend job 会自动跳过。

### 验证 Secrets 是否生效

推送任意分支后，在 Actions 页查看 **Tests** 工作流：

- `banxiaozhu (Jest)` 应为绿色
- `genesis_backend (pytest)` 若 Secrets 正确，应执行完整 pytest；若跳过，日志中有 `Skipping backend pytest` notice

## 本地小程序测试

```bash
cd banxiaozhu
npm install
npm test
```

契约测试文件见 `banxiaozhu/test/unit/*.test.js`；修改 `login.js` / `viputils.js` / `checkout.js` 请求格式时需同步更新对应 `*.api.test.js`。
