# 端点星信息密度衰减观测实验

> AI Agent长期运行后，信息密度是否必然衰减？衰减的数学签名是什么？

## 在线预览

📄 [实验方案卡片化渲染](http://47.101.59.225/cards/template.html?md=EXPERIMENT_DESIGN.md)

## 项目简介

本实验通过**残差数列**（Residual Series）观测 AI Agent 长期运行中信息密度的变化规律。

核心思路：
- 估计器对每个信息块给出密度评分 ρ
- 回证机制追踪信息的实际效用 u
- 残差 e = u - ρ 揭示估计器的系统性偏差
- 累积足够残差后，训练密度校正模型 ρ̂ = ρ + ê

## Phase 1 实验状态（更新：2026-05-21）

```
裁决轮次: 35 轮 (C1-C35) | 先验轨道: 153 条残差记录 (100 条已验证)
涌现式轨道: 122 条行为记录 | 时间跨度: 8 天
Ridge v1 模型: R²=0.875, TS-CV +50.1%
```

### 核心发现

1. **ρ 估计器系统性上修偏压 (+0.51)**：88.5% 的残差为负，平均高估 0.37 效用单位
2. **三个结构性跳变点** — C10 (首闪断) / C14 (Guardian出现) / C26 (Guardian单调重复)
3. **引用网络集中化但关联瓦解** — 最大分量 12%→73%，聚类 0.44→0.21
4. **高密度信息一次性悖论** — ρ=-0.974 系数，Guardian退役事件 e=-2.639

👉 [完整 Phase 1 科学报告](DENSITY_001_PHASE1_REPORT.md)

## 文件结构

```
EXPERIMENT_DESIGN.md              — 完整实验方案（统一基底）
DENSITY_001_PHASE1_REPORT.md     — Phase 1 科学报告 (2026-05-21)
DENSITY_001_REVIEW.md            — 外部评审意见 (Claude GLM-5.1)
SHANNON_DENSITY.md               — 香农信息密度理论框架
DENSITY_MODEL.md                 — 数学模型
RESIDUAL_PIPELINE.md             — 残差采集管道设计
EMERGENT_ANALYSIS_REPORT.md     — 涌现式分析报告
THEORY_OF_COLLAPSE.md            — 通用解释框架
template.html                    — Markdown→卡片渲染模板（纯前端）
density_corrector.py             — 密度校正模型 (纯Python, 零外部依赖)
emergent_analysis.py             — 涌现式分析 (PELT + PCA + 图拓扑)
train_and_deploy.py              — 模型训练与部署脚本
batch_backfill.py                — 批量回证脚本
residual-series.jsonl            — 残差序列 (先验轨道)
behavior-log.jsonl               — 行为记录 (涌现式轨道)
density-log.jsonl                — 35轮裁决日志
model/density_corrector_current.json — v1 部署模型
README.md                        — 本文件
```

## 关键概念

| 概念 | 定义 |
|------|------|
| 信息密度 ρ | S·λ·R·C 四因子乘积（香农惊喜度×衰减×相关性×新颖性） |
| 残差 e | 实际效用 - 估计密度 |
| 回证 u | 信息块在后续轮次中被引用/依赖的程度 |
| 密度校正模型 | Ridge回归，100条门槛，TS-CV验证 |
| 先验轨道 | 有预设框架的数据采集（residual-series.jsonl） |
| 涌现式轨道 | 零先验纯行为记录（behavior-log.jsonl） |

## 实验阶段

1. ✅ **数据累积**（~7天）— 残差从26条增长到100+条
2. 🔵 **基线模型**（~30天）— 首次模型训练与部署（v1 已训练, TS-CV +50.1%）
3. ⬜ **模式识别**（~90天）— 衰减模式分类
4. ⬜ **泛化验证**（~180天）— 跨智能体验证

## 许可证

MIT License

## 关联项目

- [endpointstar-framework](https://github.com/Yun1976/endpointstar-framework) — AI Agent 配置框架
- [knowledge-constitution](https://github.com/Yun1976/knowledge-constitution) — 知识库方法论
- [ai-agent-incidents](https://github.com/Yun1976/ai-agent-incidents) — 运维事故报告
