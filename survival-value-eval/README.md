# Note Survival Value Evaluator — LLM 微调 vs 回归 对比

> 评估知识库笔记的「信息存活价值」(1–5 分),对比 **LLM QLoRA 微调 / TF-IDF 回归 / 混合模型**三种方法。
> **核心发现:小数据(~300 条)下,简单 TF-IDF 回归 (ρ=0.778) 显著优于 3B LLM 微调 (0.466);混合需门控,简单 ensemble 反而更差。**

这是 [信息密度实验](https://github.com/topics/information-density) 的一部分——研究知识库笔记的熵增/反熵增评估。

---

## 背景

知识库随时间膨胀,哪些笔记值得保留(高存活价值)、哪些可删/归档(低)?本项目用机器学习自动评估笔记价值,对比三条路线。

**评分定义(信息存活价值):**

| 分数 | 含义 |
|---|---|
| 1 | 可删流水(日报/草稿) |
| 2 | 可合并归档 |
| 3 | 一般参考 |
| 4 | 压缩保留 |
| 5 | 必留核心(被反复引用) |

## 核心结果

| 方法 | Spearman ρ | MAE | 完全一致 |
|---|---|---|---|
| LLM QLoRA (Qwen2.5-3B) | 0.466 | 0.77 | 57% |
| **TF-IDF + Ridge** | **0.778** | 0.84 | 26% |
| TF-IDF + LinearSVR | 0.779 | 0.79 | 51% |
| Ensemble 等权平均 | 0.653 | — | — |
| Ensemble 0.7回归+0.3LLM | 0.688 | — | — |

> ρ 越高越好。回归在纯文本上就碾压 LLM;简单 ensemble 被 LLM 整体弱拖累,低于回归单模型。

## 三条关键发现

1. **小数据下简单模型赢** — 300 条训练样本,TF-IDF + 线性回归碾压 3B LLM。小数据 + 文本线性可分 = 简单模型的菜。别为用 LLM 而用 LLM。
2. **混合不是简单平均** — LLM 整体弱时,简单 ensemble 会被拖累(0.65 < 回归 0.78)。必须用门控/stacking,让弱模型只在它强的地方说话。分歧分析显示 LLM 在 34/58 个分歧 case 上比回归更接近人工分,有校准潜力,但要把这种局部优势提取出来。
3. **先算简单基线,再上大模型** — 5 秒跑个回归,避免几小时 LLM 调参弯路。这是本项目最大的方法论教训。

详见 [`docs/lessons.md`](docs/lessons.md)。

## 快速开始

```bash
pip install -r requirements.txt
```

**回归基线(推荐,秒级,无需 GPU):**
```bash
python src/regression_baseline.py
```

**用你自己的数据**(格式见 [`data/sample.jsonl`](data/sample.jsonl)):
- 每行一条 JSON:`instruction` + `input`(笔记全文) + `output`(1–5) + `filename`
- 放到 `train_data.jsonl`,`split.py` 会自动分层切分 + 去重 + 类别平衡

**LLM 微调(可选,需 GPU):**
```bash
python src/train.py     # QLoRA 微调 -> ./output/
python src/predict.py   # 在测试集上评估
python src/compare_models.py  # LLM vs 回归 vs 混合 对比
```

> 5060 Ti 等 Blackwell(sm_120)显卡需 cu128 torch:
> `pip install torch --index-url https://download.pytorch.org/whl/cu128`

## 目录结构

```
src/
  split.py                # 分层切分 + 去重 + CAP 类别平衡
  train.py                # LLM QLoRA 微调 (trl 1.x)
  predict.py              # LLM 测试集评估
  regression_baseline.py  # TF-IDF + Ridge/SVR 回归基线
  compare_models.py       # LLM vs 回归 vs ensemble 对比 + 混合可行性
data/
  sample.jsonl            # 数据格式示例(3 条 fake, 不含真实数据)
  README.md               # 数据格式说明
docs/
  lessons.md              # 完整经验教训
```

## 关于数据

**本项目不含原始数据**(原始笔记含私有知识库内容)。`data/sample.jsonl` 只展示格式。要复现,需自行构造同格式数据:
- 建议每个分数至少 30–50 条真实样本,总量 500+
- 注意类别平衡(本项目曾因分2 占 53% 导致 LLM 坍缩到全输出 2)
- 标签一致性:同一篇多人/跨天评分应一致,否则是天花板

## License

MIT — 见 [LICENSE](LICENSE)。
