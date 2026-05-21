# H4 验证计划

## 目标
执行一个完整的"推理→实验→压缩→恢复→继续"循环，验证：
1. 密度模型在真实信息流中是否可操作
2. 后悔/冗余信号是否自然涌现
3. 跨 session 的持久注意力是否可恢复

## 循环设计

### Cycle 1 — 基线建立
**任务**: 探索端点星磁盘布局，定位 obsidian-vault 和 OpenClawNode 服务状态
**执行者**: main agent (自执行，不 spawn worker)
**产出**: 端点星系统画像 → 写入 TASK.md

### Cycle 2 — 压缩裁决
**任务**: 对 Cycle 1 的上下文做密度判定，保留高密度信息，丢弃冗余
**裁决者**: main agent 自裁决
**产出**: 密度校准日志 → 写入 TASK.md

### Cycle 3 — 恢复继续
**任务**: 从 TASK.md 恢复核心状态，基于 Cycle 1 发现做下一轮推进
**产出**: 验证"从 TASK.md 恢复后能否正确理解任务状态"

### Cycle 4 — 裁决回顾
**任务**: 回顾 Cycle 2 的裁决质量，检测后悔/冗余信号，校准 θ
**这是密度模型自我进化的核心环节**

## 基础设施
- 端点星 node: dec83393 (新 session, 1503219a 旧 session)
- 文件: TASK.md, DENSITY_MODEL.md, INTROSPECTION.md, JUDGE_CRITERIA.md
- 密度模型参数: θ₀=1.0, α=0.15, β=0.10

## 开始时间
2026-05-12 23:34 CST
