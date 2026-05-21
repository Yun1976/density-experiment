# 行为记录层 — Behavior Log

> 涌现式观测轨道核心数据文件
> 原则：只记录行为，不记录价值判断

## 文件

`tasks/multi-agent-architecture/behavior-log.jsonl`

## 单条记录 Schema

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

## 字段定义

| 字段 | 类型 | 说明 | 为什么零先验 |
|------|------|------|-------------|
| id | string | 事件唯一标识 | 只标记身份，不评判内容 |
| timestamp | ISO8601 | 事件发生时间 | 只记录时间 |
| cycle | int | 裁决轮次 | 只记录周期位置 |
| agent | string | 来源智能体 | 只记录来源 |
| action_type | enum | output/decision/error/self_modify | 只记录动作类型 |
| triggered_by | string | 触发源 | 只记录因果链 |
| raw_content_hash | string | SHA256 内容指纹 | 不存原文，不评判内容 |
| raw_length_tokens | int | 原始 token 长度 | 纯度量，无价值 |
| references_to | list | 引用了之前哪些事件 | 只记录引用行为，不评判"该引用" |
| referenced_by | list | 被之后哪些事件引用 | 只记录引用事实 |
| downstream_actions | list | 引发了什么后续行为 | 只记录结果链 |
| compressibility_gzip | float | gzip 压缩比 (0..1) | 纯数学量，无语义 |

## 采集流程

每轮裁决时，对每个信息块：
1. 计算 `raw_content_hash`（SHA256，不存原文）
2. 计算 `raw_length_tokens`（tokenizer估数）
3. 计算 `compressibility_gzip`（gzip 压缩比）
4. 提取 `references_to`（信息块中引用/提及的先前事件 ID）
5. 在回证扫描时回填 `referenced_by` 和 `downstream_actions`

## 与 residual-series 的关系

```
                    ┌─────────────────────────┐
端点星/智能体产出 ──┤                         │
                    │   同一信息块同时写入两条轨道  │
                    ├─────────────────────────┤
                    │ 行为记录层（零先验）     │ behavior-log.jsonl
                    │ raw_content_hash,       │
                    │ raw_length_tokens,      │
                    │ compressibility_gzip,   │
                    │ references_to,          │
                    │ referenced_by,          │
                    │ downstream_actions      │
                    ├─────────────────────────┤
                    │ 密度估计层（先验框架）    │ residual-series.jsonl
                    │ S, R, C, λ, ρ,          │
                    │ u_observed, residual     │
                    └─────────────────────────┘
```

## 涌现式分析触发条件

- 累积 ≥ 50 条 → 首次涌现式分析（变点检测 + PCA + 图拓扑）
- 后续每累积 50 条 → 增量分析
- 不做预测，只做观察报告

---

*行为记录层 v1.0 | 2026-05-14*
