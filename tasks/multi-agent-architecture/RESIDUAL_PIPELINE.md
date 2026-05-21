# 残差数列采集管道 — Residual Pipeline

> 闻声（观自在系统）2026-05-14
> 目标：采集 e_t(x) = u_t(x) - ρ_t(x) 时间序列，构建训练数据集

---

## 一、观测对象定义

### 1.1 观测域

观测对象**不是**某个智能体的行为，而是**裁决框架（judge agent）的密度估计器本身**。

```
                    ┌─────────────────────┐
                    │   智能体运行产出      │
                    │  (对话/tool call/    │
                    │   系统日志)           │
                    └──────┬──────────────┘
                           │ 信息块分割
                           ▼
              ┌─────────────────────────┐
              │   JUDGE 密度估计器       │ ← 观测对象
              │   ρ(x) = S·λ·R·C       │
              └────────┬────────────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
       保留         压缩         丢弃
       │            │            │
       └────────────┼────────────┘
                    │ 下一轮回证
                    ▼
              ┌─────────────┐
              │ u_t(x) 实际  │  ← 真实效用
              │ 效用观测     │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │ e_t(x) =    │  ← 残差
              │ u_t - ρ_t   │
              └─────────────┘
```

### 1.2 为什么观测估计器而非智能体

- 智能体行为是**被估计对象**，噪声太大
- 密度估计器的 ρ(x) → 保留/丢弃 → 后悔/冗余 形成**闭合反馈环**
- 残差 e_t 直接反映估计器质量，是信息密度滑移的**最小充分统计量**
- 训练出的模型可以直接替换/校准 ρ(x) 估计器

### 1.3 观测范围

观测覆盖**整个裁决管道**，不仅限于三系统中的某一个：
- 闻声（本机 OpenClaw）：自身对话的裁决
- 千手（Hermes）：深度推理产出
- 净瓶（Claude Code）：系统维护操作
- 端点星：远程业务执行

---

## 二、残差数列数据结构

### 2.1 单条残差记录

```json
{
  "id": "res_001",
  "cycle": 8,
  "timestamp": "2026-05-14T10:26:00+08:00",
  "block_id": "A",
  "source": "端点星双node同时离线",
  
  // 估计值（裁决时）
  "rho_estimated": 0.65,
  "S_estimated": 2.32,
  "R_estimated": 0.70,
  "C_estimated": 0.40,
  "lambda": 1.0,
  
  // 裁决动作
  "decision": "compressed",
  
  // 实际效用（后续回证）
  "u_observed": null,
  "u_source": null,
  "u_round": null,
  
  // 残差
  "residual": null,
  
  // 回证窗口状态
  "validation_status": "pending",
  "validation_deadline": 11
}
```

### 2.2 完整残差数列

文件：`tasks/multi-agent-architecture/residual-series.jsonl`

每行一条残差记录，包含从估计到回证的完整生命周期。

### 2.3 残差汇总

文件：`tasks/multi-agent-architecture/residual-summary.jsonl`

每轮一条，汇总统计量：
```json
{
  "cycle": 8,
  "timestamp": "2026-05-14T10:26:00+08:00",
  "n_blocks": 2,
  "residual_mean": -0.58,
  "residual_var": 1.01,
  "residual_acf1": null,
  "residual_skew": -0.32,
  "theta": 1.02,
  "regret_rate": 0.0,
  "redundancy_rate": 0.17,
  "drift_level": "orange",
  "estimator_bias": "overestimate",
  "n_pending_validation": 12,
  "n_validated_this_cycle": 2
}
```

---

## 三、采集流程

### 3.1 每轮裁决时（写入估计值）

```
Cycle t 裁决:
  for each block x:
    → 计算 S, R, C, λ → ρ
    → 写入 residual-series.jsonl（rho_estimated, decision）
    → validation_status = "pending"
```

### 3.2 每轮回证时（写入实际效用）

```
Cycle t+1 开始:
  for each pending block x from past W=3 cycles:
    → 检查是否被引用（u=1）、压缩摘要被引用（u=0.5）、未被引用（u=0）
    → 更新 residual-series.jsonl（u_observed, residual = u - ρ）
    → validation_status = "validated"
```

### 3.3 效用值定义

| u 值 | 含义 | 触发条件 |
|------|------|---------|
| 0 | 无用 | W 轮内从未被引用/依赖/压缩摘要引用 |
| 0.5 | 部分有用 | 压缩摘要被引用（原信息已丢弃但摘要存活） |
| 0.3 | 隐式依赖 | file-transfer 路径确认、架构假设间接依赖 |
| 1.0 | 有用 | 被明确引用/重复发现需要/信息缺口自纠错涉及 |
| -0.5 | 负效用 | 保留该信息导致错误推理（罕见，仅限误判保留） |

---

## 四、数据采集自动化

### 4.1 现有裁决框架的改造点

当前 Cycle 裁决结束后需要额外执行：

1. **residual-series.jsonl 追加**：将每个信息块的 ρ 估计写入
2. **回证扫描**：扫描本轮裁决中引用的历史信息块，找到其原始 residual-series 条目，写入 u_observed
3. **residual-summary.jsonl 追加**：计算本轮汇总统计量

### 4.2 裁决者 prompt 增强

在 JUDGE_CRITERIA.md 中增加"残差记录"步骤：

```
### 步骤 5（新增）：残差记录

对每个信息块 x：
  - 记录 ρ(x) 的四因子分解 (S, R, C, λ)
  - 标记 validation_status = "pending"
  - 设定 validation_deadline = current_cycle + 3

对 W=3 窗口内 pending 块：
  - 若被引用 → u = 1.0 → residual = 1.0 - ρ
  - 若压缩摘要被引用 → u = 0.5 → residual = 0.5 - ρ
  - 若未被引用 → u = 0 → residual = -ρ
  - 标记 validated
```

---

## 五、数据集格式（供模型训练）

### 5.1 训练样本

每个经过完整回证周期的信息块是一条训练样本：

```json
{
  "features": {
    "S_surprise": 2.32,
    "R_relevance": 0.70,
    "C_novelty": 0.40,
    "lambda_decay": 1.0,
    "cycle_index": 8,
    "block_source_type": "system_status",
    "decision": "compressed",
    "theta_at_decision": 1.02,
    "num_active_hypotheses": 12,
    "cycles_since_first_seen": 0,
    "source_agent": "endpointstar",
    "drift_level_at_decision": "yellow"
  },
  "label": {
    "u_observed": 0.0,
    "residual": -0.65,
    "validation_cycle": 11
  }
}
```

### 5.2 特征工程

| 特征 | 类型 | 说明 |
|------|------|------|
| S, R, C, λ | 连续 | 四因子原始值 |
| f_rho | 连续 | ρ = S·λ·R·C |
| f_cycle_pos | 连续 | 归一化轮次位置 |
| f_block_type | 类别 | system_status/tool_output/reasoning/observation |
| f_theta | 连续 | 判定时的阈值 |
| f_active_hypotheses | 连续 | 活跃假设数量 |
| f_age | 连续 | 距首次观察的轮次数 |
| f_source | 类别 | wensheng/qianshou/jingping/endpointstar |
| f_drift | 类别 | green/yellow/orange/red |
| f_decision | 类别 | kept/compressed/dropped |

### 5.3 标签

| 标签 | 类型 | 说明 |
|------|------|------|
| u_observed | 连续 [0,1] | 真实效用（回证后） |
| residual | 连续 | e = u - ρ |
| is_regret | 布尔 | e < -|ρ| (低估到丢弃了重要信息) |
| is_inflated | 布尔 | S<0.1 ∧ C<0.1 (膨胀型输出) |

---

## 六、模型训练路线图

### Phase 1: 残差采集（当前）
- 从 Cycle 9 开始，每轮裁决同步写入 residual-series.jsonl
- 目标：收集 ≥ 100 条完整回证的残差样本
- 预计时间：~10 轮裁决（含 W=3 回证窗口滞后）

### Phase 2: 基线模型
- 用残差数列训练一个轻量回归模型
- 输入：特征向量（S, R, C, λ, ...）
- 输出：预测残差 ê(x)，等价于校正后的密度 ρ̂(x) = ρ(x) + ê(x)
- 训练目标：最小化 MSE(ê, e_true)

### Phase 3: 判定增强
- 用校正后的 ρ̂(x) 替代原始 ρ(x) 做保留/压缩/丢弃判定
- A/B 对比：原始 θ 校准 vs 模型增强 θ 校准
- 目标：r_t 和 d_t 同时降低

### Phase 4: 泛化
- 将模型输出的残差模式泛化为"信息密度健康指数"
- 可用于任何智能体的信息密度诊断
- 为"永久记忆形成"提供量化边界条件

---

## 七、与现有文档的关系

```
SHANNON_DENSITY.md       ← 香农信息论基础
        ↓
DENSITY_MODEL.md         ← 密度估计器数学模型
        ↓
JUDGE_CRITERIA.md        ← 可操作执行手册
        ↓
RESIDUAL_PIPELINE.md     ← 本文档：残差采集管道 ← 新增
        ↓
DENSITY_OBSERVATORY.md   ← 持久观测计划（ω̄, r, d 宏观指标）
```

---

## 八、启动条件

- [x] residual-series.jsonl 初始化
- [x] residual-summary.jsonl 初始化
- [x] 裁决者 prompt 更新（增加残差记录步骤）
- [x] Cycle 9 开始采集

---

## 九、涌现式轨道（v1.1 新增）

### 9.1 设计原则

在现有残差采集管道旁，增加一条平行的行为记录轨道：
- **不记录价值判断** — 不评判"有用/没用"
- **不预设框架** — 不计算 S·R·C·λ
- **只记录事实** — 引用链、压缩率、触发链、长度
- **让模式涌现** — 用无监督方法在原始数据中发现结构

### 9.2 行为记录文件

`behavior-log.jsonl` — 每条信息块一条，与 residual-series.jsonl 对应：

```json
{
  "id": "evt_0001",
  "timestamp": "2026-05-14T10:26:00+08:00",
  "cycle": 8,
  "agent": "endpoint_star",
  "action_type": "output",
  "triggered_by": "cron_a68cb58c_cycle_8",
  "raw_content_hash": "sha256:abc123...",
  "raw_length_tokens": 342,
  "references_to": ["evt_0138", "evt_0135"],
  "referenced_by": [],
  "downstream_actions": [],
  "compressibility_gzip": 0.38
}
```

### 9.3 residual-series.jsonl 新增字段

原 schema 增加两个零先验字段：

```json
{
  "compressibility_gzip": 0.38,
  "raw_length_tokens": 342
}
```

### 9.4 涌现式分析工具箱

| 方法 | 输入 | 输出 | 触发 |
|------|------|------|------|
| 变点检测 (PELT/CUSUM) | 产出长度、压缩率、引用密度 | "第 N 天发生了突变" | ≥50 条 |
| PCA 降维 | 多维行为向量 | 2D/3D 行为模式轨迹 | ≥50 条 |
| 图拓扑演化 | 引用网络 | 聚类系数、出度分布、连通分量变化 | ≥50 条 |

### 9.5 采集流程增量

在现有裁决流程中增加（不影响先验轨道）：
- 步骤 4a：计算 `compressibility_gzip`、`raw_length_tokens`
- 步骤 4b：提取 `references_to`（信息块中引用/提及的先前事件 ID）
- 步骤 4c：写入 `behavior-log.jsonl`
- 步骤 10a：回证时回填 `referenced_by`、`downstream_actions`

### 9.6 双轨交叉验证

两块分析最终对照：
- 涌现式分析发现的模式 ←→ 残差分析结论
- 一致 → 双向确证，结论可信
- 不一致 → 先验框架遗漏了什么，值得深究

---

*残差数列采集管道 v1.1 | 观自在·闻声 | 2026-05-14*
