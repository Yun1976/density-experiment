# TOKEN LEDGER CANDIDATES — 2026-10-15

- **Status**: P0 scan for founder批 — source decision draft（交拍）
- **Protocol**: passes `DENSITY-NEXT-PROTOCOL-v0` discipline
- **Hard constraints observed**: `measurable_cost` 未批前不改 `merge_j` 默认；不装 NylonME；不改肘站；不含氢离子；不 push；ρ′不做；A4/LIVE 未批；**不改生产代码**
- **Scan host**: DESKTOP-QTG76OM (`machineId=456e7e2e-5e77-4e16-a59c-a97643accba9`)
- **Scan time**: 2026-10-15 20:44:37 +08:00 (Asia/Shanghai)
- **Scope**: read-only under `anti-entropy-runtime` / `docs` / `logs` / `work` / related entropy-transfer + harness + `~/.claude` / `~/.dsh`

---

## 0. Non-negotiable（协议红线）

| Rule | Implication |
|------|-------------|
| **char/4 不能解锁 `measurable_cost=true`** | C1 `forced_injection_char_div4` 仅可作粗代理；**禁止**据此让 e 进入 LIVE J |
| e 进 J 仅当 | `measurable_cost=true` **且** `|\Delta C| > \epsilon` |
| 今日动作 | 只定 ledger **来源建议**；**不**翻 merge 默认；**不**写 LIVE |

---

## 1. 候选路径表

| # | 路径 | 存在? | 样例字段 | 能否支撑 `|\Delta C| > \epsilon` | 风险 |
|---|------|-------|----------|--------------------------------|------|
| A | `D:\AI WORK\entropy-transfer\anti-entropy-runtime\token_pairs.json` | **是** (735 B, mtime 2026-07-26) | `pairs[].code/name/ip_whitelist/usage_count/last_used_at` — **API 配对登记**，无 `prompt_tokens` / `input_tokens` | **否**（无 LLM token 数值；`usage_count` 是调用次数） | 名称误导：`metrics_c1_c5` 仍将其列为 `token_proxy_files` 首选；若未来误写入带 `*token*` 数字字段会**错误**置 `measurable_cost=True` |
| B | `D:\AI WORK\anti-entropy-runtime\token_pairs.json` | **否** | — | 否 | 文档/README 常写「token_pairs」但本树无副本 |
| C | C1 fallback `forced_injection_char_div4`（GENES + 思维印章 + active SKILL.md） | **是**（代码路径；E0 实测） | `chars`, `tokens_proxy=chars/4`, `measurable_cost:false`；E0: C1=49779 | **否**（协议明示 char/4 ≠ measurable） | 今日 LIVE 现状；误把其当真成本会破 e–token 绑定 |
| D | `D:\AI WORK\entropy-transfer\anti-entropy-runtime\remote-cache\sessions\*.jsonl` | **是**（3 文件；mtime ~2026-09-08） | `message.usage.input_tokens`, `output_tokens`, `cache_read_input_tokens`, `cache_creation_input_tokens`, `thinking_tokens`；样例一文件 usage_rows=228 | **是** | 样本少、偏缓存镜像；同 `msg_id` 多行重复；非专用账本 |
| E | `%USERPROFILE%\.claude\projects\**\*.jsonl` | **是**（本机 17 jsonl，全部含 usage；最新至 2026-10-14） | 同 D；样例 usage_rows=59，单行 `input_tokens=147699` | **是**（活源） | 在用户主目录非 runtime 树；需去重；跨机不一致 |
| F | `D:\AI WORK\deepseek-harness\packages\llm\token-meter\`（`TurnTokenUsage`） | **是**（库代码） | `uncachedInputTokens`, `outputTokens`, `totalTokens`, `cacheReadTokens?`, `cacheWriteTokens?`, `reasoningTokens?`, `routes[]` | **条件是**：从 DSH session event 投影后落盘；今日无独立 ledger 文件 | schema 最干净；接入需另批 |
| G | `%USERPROFILE%\.dsh\endpoint-star\strategy-usage.json` + `strategy-ledger.jsonl` | **是** | `counts[strategy_id]`, `uses/success/fail` | **否**（策略命中次数） | 名称含 usage/ledger 易混 |
| H | `D:\AI WORK\entropy-transfer\anti-entropy-runtime\residuals\summary-v5.jsonl` | **是** | `keep/observe/prune`, `residual_mean` | **否** | C3 源，非 C1 |
| I | `D:\AI WORK\anti-entropy-runtime\strategy_usage.py` → 写出 G | **是** | 扫 `state.db` 计 strategy_id | **否** | 与 token 无关 |
| J | `D:\AI WORK\work\aihot-src\` admin SQL / tests | **是**（出域） | `usage->>'prompt_tokens'`, `completion_tokens` | 理论是，非密度运行域 | 不可作密度主源 |
| K | `D:\AI WORK\docs\DENSITY_RRSI_ABLATION_RESULTS_20261010.json` SIM `delta_c` | **是** | `delta_c`, `mean_delta_C` | **否**（SIM 合成） | 不可解锁 LIVE measurable |
| L | **拟建** `D:\AI WORK\anti-entropy-runtime\bloat_meter\state\token_ledger.jsonl` | **否** | 见 §3 | **是**（由 E/D/F 抽取写入后） | 今日不存在；创建/接线另批 |
| M | tiktoken / `n_tokens` 本地实现 | **未发现**密度栈内实现 | — | 本地估词仍属代理 | 即使引入也不应单独解锁 measurable |

**关键词扫描摘要**: `token_pairs` / `measurable_cost` / `delta_c` / `char/4` / `C1` 集中在 `bloat_meter` + `docs` 协议；真 `input_tokens`/`output_tokens` 在 Claude / remote-cache session jsonl；OpenAI 形 `prompt_tokens`/`completion_tokens` 主要在 `work\aihot-src`（出域）与 DSH 测试夹具。

**候选条数**: 13（A–M）

---

## 2. 推荐主源 + 备选

### 主源（推荐）

**`%USERPROFILE%\.claude\projects\**\*.jsonl`（本机 Claude Code / CC session 日志）**

- 理由：提供方上报的 `input_tokens` / `output_tokens` / cache 桶；本机 17/17 已有 usage；可算 turn/session `\Delta C`，支撑 `|\Delta C| > \epsilon`。
- 落地建议（**仅建议，本日不实施**）：只读抽取 → 规范化写入拟建 `bloat_meter\state\token_ledger.jsonl`；去重键建议 `(session_id, message.id)` 取最后一条含 usage 的 assistant 行。
- **不**把现有 `token_pairs.json` 当主源（实为配对登记）。

### 备选 1

**`D:\AI WORK\entropy-transfer\anti-entropy-runtime\remote-cache\sessions\*.jsonl`** — 同构字段；离线夹具；样本少偏旧。

### 备选 2

**DSH `token-meter` `TurnTokenUsage`** — schema 最规范；适合 DSH evolve-set；需确认 persistence 落盘后再挂。

### 明确否决

`token_pairs.json`；char/4；`strategy-usage` / `strategy-ledger`；residuals；SIM `delta_c`；tiktoken 本地估词。

---

## 3. 建议 schema（拟建 `token_ledger.jsonl` 每行一条）

| Field | 中文 | Type | Notes |
|-------|------|------|-------|
| `timestamp` | 时间戳 | ISO-8601 string | 事件自身 ts |
| `run_id` | 运行/会话 ID | string | `sessionId` 或 evolve run id |
| `msg_id` | 消息 ID | string | provider `message.id`；去重 |
| `prompt_tokens` | 提示/输入 token | int | 自 `input_tokens` 或 OpenAI `prompt_tokens` |
| `completion_tokens` | 补全/输出 token | int | 自 `output_tokens` / `completion_tokens` |
| `cache_read_tokens` | 缓存读 | int? | `cache_read_input_tokens` |
| `cache_write_tokens` | 缓存写 | int? | `cache_creation_input_tokens` |
| `reasoning_tokens` | 推理子桶 | int? | `thinking_tokens` |
| `total` | 合计 | int | 须写清是否含 cache |
| `delta_c` | 成本差 | float? | 相对基线/上一 run；供 `|\Delta C|>\epsilon` |
| `model` | 模型 | string | |
| `source` | 来源 | string | e.g. `claude_projects_jsonl` |
| `path` | 原始路径 | string | 溯源 |
| `notes` | 备注 | string? | 去重/计费约定 |

**C1 接线原则（未来批，非本日）**: 仅当 ledger 提供数值性 provider token 且 `source` ∈ 白名单时，才允许 `measurable_cost=true`；char/4 必须保持 `false`。

---

## 4. 明确声明：char/4 **不能**解锁 `measurable_cost=true`

依据：

1. `merge_scalar.py`：Estimated char/4 proxies are **NOT** measurable cost.
2. `DENSITY-NEXT-PROTOCOL-v0` §4.2 / 停止条件：**用 char/4 开 measurable_cost** = 违反 e–token 绑定。
3. E0 实测：`source=forced_injection_char_div4`, `C1_measurable_cost=false`。

**任何「用 char/4 把 e 放进 J」的提案一律否决。**

---

## 5. 今日未做 / 边界

- 未改 `merge_j` / `metrics_c1_c5` / 任何生产代码
- 未创建 `token_ledger.jsonl`（仅路径建议）
- 未装 NylonME；未改肘站；未 push；未做 ρ′；未开 A4/LIVE
- `measurable_cost` 默认保持 false，直至创始人另批

---

## 6. 创始人决议（2026-10-15 · Asia/Shanghai）

| 项 | 决议 |
|---|---|
| **主源** | Claude projects jsonl：`%USERPROFILE%\.claude\projects\**\*.jsonl` |
| **备选** | `D:\AI WORK\entropy-transfer\anti-entropy-runtime\remote-cache\sessions\*.jsonl` |
| **否决** | `token_pairs.json`；char/4；`strategy-usage` / `strategy-ledger` |
| **接线** | **另批** — 本日不改 `merge_j`、不建 `token_ledger.jsonl`、不开 `measurable_cost=true` |
| **来源** | 创始人已定（房间 snow 转达） |

**注**：本决议只定来源优先级；**不等于**已接线或已开 LIVE measurable。SIM≠LIVE。

---

## 7. SHA256

```
07698ad0b5f6b45c2a7dbfaa368cf09b9cde89feb37337f4a22a4b8daba564be
```

- **Absolute path**: `D:\AI WORK\docs\2026-10-15-TOKEN-LEDGER-CANDIDATES.md`
- **Candidate rows**: 13 (A–M)
- **Hash scope (fence)**: SHA256 of UTF-8 bytes from start of file through the newline before this fenced block (`## 7. SHA256` section header included).
- **Encoding**: UTF-8 (no BOM); §6 中文已重写可读。
- **Prior corrupt §6**: replaced 2026-10-16 (P0 hygiene); founder decision unchanged.
- **SHA256 of full md file (after previous bullets)**: `cc56211e07d666c9fa897942c6876868e69b152da6df25242dd4b21e2e828adf`
