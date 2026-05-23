# DENSITY-001: AI Agent 信息密度衰减观测实验

> **关键词**：信息密度 · AI Agent · 长期运行 · Shannon 信息论 · 制度空间搜索 · 自动科研

## 这是什么？

DENSITY-001 是一个观测实验：给一个独立运行的 AI Agent（端点星）装上**信息密度仪表盘**，量化追踪它在长期运行中是"变聪明了"还是"变笨了"。

这不是调参实验，是**制度空间搜索**——优化的是 Agent 的行为制度（钢印、基因模组、裁决策略），不是模型权重。

## 核心发现（Phase 1）

1. **ρ 估计器存在系统性上修偏压（+0.51 intercept）**：Agent 在 88.5% 的情况下高估了信息的实际效用
2. **行为模式不是缓慢漂移的，而是跳变的**：PELT 变点检测发现 C10/C14/C26 三个结构性跳变点
3. **引用网络在集中化但关联在瓦解**："宽而不深"的引用结构——权威节点聚集，但节点间的直接关联在稀疏化
4. **高密度信息的一次性悖论**：越被判定为"重要"的信息，事后越被证明不重要（ρ_estimated 系数 = -0.974）

## 方法论创新

### 双轨并行

| 轨道 | 做什么 | 能验证什么 |
|------|--------|-----------|
| **先验轨道** | 用 Shannon 信息密度公式评分，Ridge 回归校正 | 框架准不准 |
| **涌现式轨道** | 零预设，只记录行为事实 | 框架遗漏了什么 |

两条轨道交叉验证：一致→高置信，不一致→发现盲区。

### v1.1 新增追踪指标

- **BDI（行为多样性指数）**：每轮 action_type 的 Shannon 熵，检测系统趋同化
- **RCD（引用链深度）**：引用图最长路径，检测级联失效风险
- **SDE（S 衰减有效性）**：衰减模型是否正确识别了过时信息

## 仓库结构

```
├── README.md                           # 本文件
├── EXPERIMENT_DESIGN.md                # 完整实验设计方案
├── SHANNON_DENSITY.md                  # Shannon 信息密度理论框架
├── DENSITY_MODEL.md                    # 数学模型（ρ=S·λ·R·C, 阈值迭代, 收敛性）
├── DENSITY_OBSERVATORY.md              # 持久观测计划（v1.1, 含 BDI/RCD/SDE）
├── DENSITY_001_PHASE1_REPORT.md        # Phase 1 科学报告
├── DENSITY_001_REVIEW.md               # 外部评审（Claude GLM-5.1）
├── DENSITY_001_METHODOLOGY_NOTES.md    # 方法论注脚（vs Karpathy 自动科研范式）
├── KNOWLEDGE_ARCHIVE.md                # 知识归档（v3.0, 可复用方法论）
├── METHODOLOGY.md                      # 问题框架与双轨方法论
├── RESIDUAL_PIPELINE.md                # 残差采集管道设计
├── BEHAVIOR_LOG.md                     # 行为记录层设计
├── density_corrector.py                # 密度校正模型（零外部依赖 Ridge 回归）
├── density-log.jsonl                   # 35+ 轮裁决汇总日志
├── residual-series.jsonl               # 153+ 条逐块残差记录
├── residual-summary.jsonl              # 累积统计
├── behavior-log.jsonl                  # 122+ 条涌现式轨道行为记录
├── model/
│   └── density_corrector_current.json  # v1 部署模型
└── TASK-archive-*.md                   # 历史裁决归档
```

## 为什么这很重要？

| 维度 | Karpathy autoresearch | DENSITY-001 |
|------|----------------------|-------------|
| 搜索空间 | 参数空间（模型权重） | 制度空间（行为规则） |
| 反馈延迟 | 秒级 | 天级 |
| Ground truth | 有（val_bpb） | 无 |
| 信号密度 | 密集 | 稀疏 |
| 方法论价值 | 解决容易的问题 | **解决更难的问题** |

在稀疏信号、长延迟、无 ground truth 的约束下做科学实验——这套方法论适用于任何需要量化评估 AI Agent 长期运行质量的场景。

## 技术栈

- **零外部依赖**：Ridge 回归用纯 Python math 模块实现解析解
- **自动化采集**：OpenClaw cron 每 6 小时自动执行裁决
- **分析工具**：PELT 变点检测、PCA 降维、引用图拓扑演化分析

## 运行要求

- Python 3.10+（标准库即可）
- 数据文件（`density-log.jsonl`, `residual-series.jsonl`, `behavior-log.jsonl`）

## 许可

MIT License

---

*DENSITY-001 | 观自在·闻声 | 2026-05*  
*端点星信息密度持久观测实验*
