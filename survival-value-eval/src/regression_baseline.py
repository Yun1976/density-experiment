# -*- coding: utf-8 -*-
"""
B 标签回归基线: TF-IDF + Ridge。
- 用 split.py 的同一 train/test split, 保证和 LLM 在同一个 61 条测试集上对比
- 用笔记全文(input 字段)做字符级 TF-IDF, 和 LLM 同信息源(都只看文本, 不吃 metadata)
- 目的: 算出 B 标签的回归基线 ρ, 才能判断 LLM 的 0.466 算赢没赢
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # Windows GBK 防 ρ 崩
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from sklearn.svm import LinearSVR
from scipy.stats import spearmanr
from split import get_splits

# 回归用全量训练(不 balance)——回归对不平衡的鲁棒性比 SFT 好, 这是它的优势
all_rows, train_rows, test_rows = get_splits(balance=False)
print(f'训练 {len(train_rows)} / 测试 {len(test_rows)}  (与 LLM 同一测试集)')
print(f'训练分布: {dict(sorted(Counter(int(r["output"]) for r in train_rows).items()))}')
print(f'测试分布: {dict(sorted(Counter(int(r["output"]) for r in test_rows).items()))}')

Xtr_text = [r['input'] for r in train_rows]
ytr = np.array([int(r['output']) for r in train_rows])
Xte_text = [r['input'] for r in test_rows]
yte = np.array([int(r['output']) for r in test_rows])

# 字符级 TF-IDF (中文友好, 不需分词; char_wb 边界感知)
vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4),
                      max_features=30000, min_df=2, sublinear_tf=True)
Xtr = vec.fit_transform(Xtr_text)
Xte = vec.transform(Xte_text)
print(f'TF-IDF 特征维度: {Xtr.shape[1]}')


def eval_model(name, pred_cont):
    rho, _ = spearmanr(pred_cont, yte)
    pred_int = np.array([max(1, min(5, int(round(p)))) for p in pred_cont])
    mae = np.mean(np.abs(pred_int - yte))
    exact = np.mean(pred_int == yte)
    print(f'  {name:18s} ρ={rho:.3f}   MAE={mae:.3f}   完全一致={exact*100:.0f}%   pred dist={dict(sorted(Counter(pred_int).items()))}')
    return rho


print('\n=== B 标签回归基线 (同信息源: 笔记全文) ===')
ridge = Ridge(alpha=10.0).fit(Xtr, ytr)
eval_model('TF-IDF + Ridge', ridge.predict(Xte))

svr = LinearSVR(C=0.1, max_iter=5000).fit(Xtr, ytr)
eval_model('TF-IDF + LinearSVR', svr.predict(Xte))

print('\n=== 对比 LLM (B版) ===')
print('  LLM (QLoRA)        ρ=0.466   MAE=0.770   完全一致=57%')
print('\n结论:')
print('  - 回归 ρ > 0.466  → LLM 没赢, 回归在纯文本上就更强')
print('  - 回归 ρ < 0.466  → LLM 赢了, 语义理解优于词频统计')
print('  - 回归 ρ ≈ 0.466  → 两者持平, LLM 没明显优势')
