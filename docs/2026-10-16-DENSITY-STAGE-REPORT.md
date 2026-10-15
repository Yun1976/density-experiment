# 密度实验阶段性报告 — 2026-10-16

| 项 | 值 |
|---|---|
| 作者角色 | 端点星-工程师（后台执行器） |
| 机器 | DESKTOP-QTG76OM (`456e7e2e-5e77-4e16-a59c-a97643accba9`) |
| 时区 | Asia/Shanghai (UTC+8) |
| 落盘 | 2026-10-16 |
| 栏 | **已证 / SIM / 未证** 分栏；**禁止**把 SIM 写成 LIVE |
| 受众 | 创始人 snow 过目 → 再交观自在 / 验收（本文件**不伪造签收**） |

---

## 1. 本阶段目标与范围

### 含
- 密度判据 v0、DENSITY-NEXT-PROTOCOL-v0（设计门禁）、P1 SIM 消融（三 seed）证据整理
- Token ledger **主源决议**落盘（只定来源，**不接线**）
- 论文栈 ModularRSI / ReHarness 在 precipitation-staging 的镜像/摘要指针
- 本报告同步 GitHub 密度仓（若权限允许）

### 不含（硬红线）
- 不改 `merge_j`；不建 `token_ledger.jsonl`；不开 `measurable_cost=true`
- 不宣称 A4 / LIVE / ρ′
- 不碰肘站 `E:\elbow-expert`；不 push 肘站远端；不碰氢离子
- NylonME DSH ≠ 端点星 DSH（禁止混称）
- 不发明数字；SIM≠LIVE 必须标明

---

## 2. 已过门禁（分栏）

### 已证（门禁/决议）
| 项 | 状态 | 证据 |
|---|---|---|
| 判据 v0 | **PASS** | handoff `D:\AI WORK\docs\handoff-guanzizai-density-criteria-v0\` |
| DENSITY-NEXT-PROTOCOL-v0 | **PASS（设计门禁）** | `D:\AI WORK\docs\2026-10-15-DENSITY-NEXT-PROTOCOL-v0.md` |
| P0 主源决议 | **已定（未接线）** | 候选卡 §6：Claude projects jsonl 主源；remote-cache 备选；否决 token_pairs/char4 |
| 论文栈 staging | **摘要+PDF 已镜像** | box `/workspace/endpoint-star-docs/precipitation-staging/` ModularRSI / ReHarness digests |

### SIM（可复现算术栏；≠ LIVE）
| 项 | 状态 | 关键数字 |
|---|---|---|
| P1 SIM 消融 2026-10-15 | **PASS（label=SIM）** | 三 seed `[119, 2609, 1015]`：**A2 OOD 最优** 全一致；A2 gap < A1/A3；A2 leak=0 |
| script_sha256 | 签收沿用 | `D10BE0DFAF08E50B2B7C28DF12B3A4A01C4B81304CB71007314FCD7E8D90C5FD` |
| 与 2026-10-10 方向 | 一致（方向性） | 冻池 replay：A2 OOD best=True；原 10-10 runner 本机未找到 |

**Per-seed（摘自签收结果；未改消融逻辑）**

| Seed | Arm | Ŝ_ood | gap | leak |
|---:|---|---:|---:|---:|
| 119 | A2 RRSI-J | 0.6522 | 0.1491 | 0.00 |
| 2609 | A2 RRSI-J | 0.6455 | 0.1070 | 0.00 |
| 1015 | A2 RRSI-J | 0.6542 | 0.1336 | 0.00 |

（A1/A3 详见 `DENSITY_NEXT_RESULTS_20261015.md`；A1/A3 leak=0.50、gap 更大。）

### 未证 / 未做
| 项 | 状态 |
|---|---|
| ledger 接线 → `merge_j` / `measurable_cost=true` | **未做（另批）** |
| A4 / LIVE 消融 | **未批 · 未做** |
| ρ′ | **未批 · 未做** |
| 肘站 / 氢离子 | **冻结 · 未碰** |
| 本轮 SIM 加强（扩种子 20261016） | **未完成**（P1 可选；本报告优先落盘） |

---

## 3. 证据路径与 SHA256

| 文件 | SHA256（全文件） |
|---|---|
| `D:\AI WORK\docs\2026-10-15-DENSITY-NEXT-PROTOCOL-v0.md` | `18bb2e64d4858f47b7a025acc5a0ce7c55203391c43e9de49d5a159589cb494d` |
| `D:\AI WORK\docs\density_next_sim_ablation_20261015.py` | `d10be0dfaf08e50b2b7c28df12b3a4a01c4b81304cb71007314fcd7e8d90c5fd` |
| `D:\AI WORK\docs\DENSITY_NEXT_RESULTS_20261015.md` | `97c0a856a969483012c0cecf1ba851fb08825601811762464a846f30e59e7eca` |
| `D:\AI WORK\docs\DENSITY_NEXT_RESULTS_20261015.json` | `c145b11af218a73abfad850a00d9b2d5df5e38f319a11189d6ad4f60bfb9ab48` |
| `D:\AI WORK\docs\2026-10-15-TOKEN-LEDGER-CANDIDATES.md`（UTF-8 重写后） | `a9430380e6adec704a3af4d1a83f0f8da8d67f4fdc13b72a5c568561d3c21a4b` |
| box ModularRSI digest | `94f407d1fa8b98004b3dbc3c9822bcafc04daa56a53be2b466574f91db535d20` |
| box ReHarness digest | `416bfce52b61e0e507bae5752b0beec7500eeb17a54415ff96e206f82ac2ea06` |

Handoff（交验收摘要已存在；**本报告不伪造新签收**）：
- `handoff-guanzizai-density-criteria-v0`
- `handoff-guanzizai-density-next-protocol-v0`
- `handoff-guanzizai-density-sim-20261015`

---

## 4. 本轮优化与证据整理（2026-10-16）

1. **候选卡 UTF-8**：重写 `2026-10-15-TOKEN-LEDGER-CANDIDATES.md`，§6 创始人决议中文可读；乱码备份 `.bak-mojibake-20261016`；**未接线**。
2. **SIM 卫生**：确认签收脚本 SHA=`D10BE0DF…C5FD`、label=`SIM`、`measurable_cost=false`、禁 LIVE/A4 宣称仍在结果 md；**未改消融逻辑**（故未发新 script SHA）。
3. **论文栈指针**：ModularRSI(2609.14857) / ReHarness(2610.12668) 摘要在 box `precipitation-staging/`；本机 `D:\AI WORK\docs` **尚无**同名 digest 副本（仅指针见本报告 §3）；不覆写已签收卡。
4. **SIM 加强 20261016**：本回合优先报告落盘；扩种子复跑列为 P1 待续（不替代 20261015 签收栏）。

---

## 5. 明确未做

- 接线 / `token_ledger.jsonl` 创建 / `measurable_cost=true`
- A4 / LIVE / ρ′
- 肘站整线 / 氢离子 / NylonME 安装
- 伪造观自在或验收签收

---

## 6. 下一刀待批清单

1. **接线批**：主源 Claude jsonl → 拟建 ledger → 白名单 source → 才允许讨论 `measurable_cost`
2. **measurable_cost=true**（仅当 |\ΔC|>ε 可证）
3. **LIVE 消融 / A4 用语**（另批）
4. ρ′（另批）
5. （可选）SIM 扩种子稳健性，文件名带 `20261016`，**不替代** 20261015 签收栏

---

## 7. 风险与诚信门

- **SIM ≠ LIVE**：OOD 为 candidate-tagged proxies，非 held-out runner；禁止对外写成已 LIVE 选优。
- **Arm1 `mean_e` ≠ Ridge r² / L-FRAUD 0.778**：残差为 u−ρ，禁止与 Ridge/L-FRAUD 混引。
- **char/4 ≠ measurable**：不能解锁 e 进 J。
- **NylonME DSH ≠ 端点星 DSH**。
- **观自在**（不是「关自在」）。

---

## 8. 本文件 SHA

| 口径 | SHA256 |
|---|---|
| 验收权威快照（GitHub `627d940` · LF · 签收所用） | `76fda72528acbe56cdb4b2a4b5d6b3c0cc9d5f3c883b2e61eaffd6fd39110a05` |
| 旧自称 `eb6b56c4…` | **作废**（与实测不符） |

- **Absolute path**: `D:\AI WORK\docs\2026-10-16-DENSITY-STAGE-REPORT.md`
- **Hash scope**: 全文件 UTF-8；历史签收以验收闸 LF `76fda725…0a05` 为准。
- **本修订全文件 SHA256（LF）**: `dcc2b4aeb798580d5f45d16c309ddeaae3165bb64718a72b7396be0872b3b0a0`
