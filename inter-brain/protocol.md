# 观自在三系统通信协议

> 左右脑通信层 — OpenClaw / Hermes / Claude Code 一体联动

---

## 系统角色分工

| 系统 | 角色 | 身份 | 职责 |
|------|------|------|------|
| **OpenClaw** | **任务编排 / 调度** | 观自在·闻声 | Cron 调度、任务分析、定时编排维护、系统监控、心跳检测 |
| **Hermes Agent** | **通讯+深度思考** | 观自在·千手 | 飞书通讯（lark-cli）、深度推理、多维分析、科学日报、第二视角、复杂问题求解 |
| **Claude Code** | **右脑 / 系统维护** | 观自在·净瓶 | 编程开发、基础设施维护、记忆系统守护、技术实现 |

### 角色隐喻

- **闻声**（OpenClaw）：任务调度与编排中心，Cron 调度与系统监控
- **千手**（Hermes）：飞书通讯入口（lark-cli），千手千眼的多维感知，深度分析
- **净瓶**（Claude Code）：净瓶甘露涤荡障碍，修复系统，维护基础设施

---

## 通信方式

### 文件通信（inter-brain）

任务通过 JSON 文件在 `inter-brain/` 目录中传递：

```
inter-brain/
├── inbox-hermes/    # → Hermes（右脑-深度思考）任务队列
├── inbox-claude/    # → Claude Code（右脑-系统维护）任务队列
├── outbox/          # ← 完成任务的结果
├── archive/         # ← 已归档任务
├── state.json       # 三系统共享状态
└── protocol.md      # 本文件
```

### 直接调用

```bash
# 分派给 Hermes（深度思考）
hermes --yolo --accept-hooks -z "深度分析任务内容"

# 分派给 Claude Code（系统维护）
claude -p "修复这个配置问题"

# 通过 OpenClaw 调度
openclaw agent run "任务描述"
```

---

## 任务消息格式

```json
{
  "id": "ib-YYYYMMDD-HHMMSS-RR",
  "from": "openclaw|hermes|claude",
  "to": "openclaw|hermes|claude",
  "type": "think|challenge|code|dispatch|report|health",
  "priority": "critical|high|normal|low",
  "status": "pending|processing|done|failed",
  "created": "ISO-8601",
  "timeout": 300,
  "payload": {
    "prompt": "任务描述",
    "context": {},
    "constraints": []
  },
  "result": null
}
```

### 任务类型

| type | 说明 | 典型执行者 |
|------|------|-----------|
| `think` | 深度思考/分析 | Hermes |
| `challenge` | P/non-P 挑战 | Hermes |
| `code` | 编程/技术实现 | Claude Code |
| `dispatch` | 任务分派 | OpenClaw |
| `report` | 报告生成 | Hermes |
| `health` | 健康检查 | OpenClaw |

---

## 调度流程

### 标准流程

```
用户请求 → OpenClaw（左脑/闻声）接收
  ↓
判断任务类型
  ├── 日常事务 → OpenClaw 自行处理
  ├── 深度分析 → 写入 inbox-hermes/ → Hermes 执行 → 结果写入 outbox/
  ├── 编程任务 → 写入 inbox-claude/ → Claude Code 执行 → 结果写入 outbox/
  └── 复杂任务 → OpenClaw 拆分 → 分派给多个系统 → 汇总结果
  ↓
结果回传用户
```

### 降级策略

```
Hermes 不可用 → OpenClaw 回退到自行执行（v2 模式）
Claude Code 不可用 → OpenClaw 临时接管系统维护任务
OpenClaw 不可用 → Claude Code 兜底监控（L3 防护）
```

---

## 定时任务

| 时间 | 任务 | 执行系统 | 频率 |
|------|------|---------|------|
| 03:00 | 健康巡检 | OpenClaw | 每天 |
| 08:00 | 晨间检查 | OpenClaw | 每天 |
| 09:00 | 科学日报 | Hermes（OpenClaw 调度） | 每天 |
| 19:00 | 失败经验总结 | OpenClaw | 每天 |
| 22:00 | 系统维护 | Claude Code（OpenClaw 调度） | 每天 |
| 心跳 | 三系统健康巡检 | OpenClaw | 每 30min |

---

## 共享知识库

**obsidian-vault/ 是三系统的共识层。**

- OpenClaw 回答问题前先查 wiki
- Claude Code 写代码时查询 wiki 了解技术决策上下文
- Hermes 执行任务时通过 wiki 获取项目状态和历史教训

---

## 教训来源

- 2026-05-06：自愈巡检失控 — 不自动修复，只检测+通知
- 2026-05-08：Gateway 宕机 — Gateway 是单点故障，必须有守护
- 2026-05-08：hermes-dispatch 通道脆弱 — .sh 在 cmd 中找不到 bash，.bat 中文编码炸裂

---

*观自在通信协议 | 2026-05-09*
