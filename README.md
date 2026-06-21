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

## 文件结构

```
EXPERIMENT_DESIGN.md   — 完整实验方案（统一基底）
template.html          — Markdown→卡片渲染模板（纯前端）
survival-value-eval/   — 笔记存活价值评估子项目（LLM vs 回归）
README.md              — 本文件
```

## 子项目

### [survival-value-eval](survival-value-eval/) — 笔记存活价值评估（LLM vs 回归）

信息密度实验的下游应用：用机器学习自动评估笔记的「信息存活价值」(1–5 分)，对比 **LLM QLoRA 微调 / TF-IDF 回归 / 混合模型**三条路线。

**核心发现**：小数据(~300 条)下，简单 TF-IDF + Ridge 回归 (ρ=0.778) 显著优于 3B LLM 微调 (0.466)；混合需门控，简单 ensemble 反被拖累(0.65)。详见 [survival-value-eval/README.md](survival-value-eval/README.md) 与 [survival-value-eval/docs/lessons.md](survival-value-eval/docs/lessons.md)。

## 关键概念

| 概念 | 定义 |
|------|------|
| 信息密度 ρ | S·λ·R·C 四因子乘积（香农惊喜度×衰减×相关性×新颖性） |
| 残差 e | 实际效用 - 估计密度 |
| 回证 u | 信息块在后续轮次中被引用/依赖的程度 |
| 密度校正模型 | Ridge回归，100条门槛，TS-CV验证 |

## 实验阶段

1. **数据累积**（~7天）— 残差从26条增长到100+条
2. **基线模型**（~30天）— 首次模型训练与部署
3. **模式识别**（~90天）— 衰减模式分类
4. **泛化验证**（~180天）— 跨智能体验证

## 许可证

MIT License

## 关联项目

- [endpointstar-framework](https://github.com/Yun1976/endpointstar-framework) — AI Agent 配置框架
- [knowledge-constitution](https://github.com/Yun1976/knowledge-constitution) — 知识库方法论
- [ai-agent-incidents](https://github.com/Yun1976/ai-agent-incidents) — 运维事故报告
