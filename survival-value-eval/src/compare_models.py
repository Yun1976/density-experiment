# -*- coding: utf-8 -*-
"""
数据质量 + 混合方案③可行性分析。
对比 LLM(predictions.json) vs 回归(TF-IDF+Ridge) 在同一 61 条测试集:
- 各自 ρ / MAE / 预测分布
- 一致 vs 分歧(分歧时谁更接近人工分)
- ensemble 效果(判断混合是否有增益)
- 潜在标签噪声(两者都大错 >=2 档, 很可能是标签本身错)
=> 判断 "LLM 校准回归" 是否有数据支撑。
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
import json
import numpy as np
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import Ridge
from scipy.stats import spearmanr
from split import get_splits

all_rows, train_rows, test_rows = get_splits(balance=False)

# ---- 回归 ----
Xtr = [r['input'] for r in train_rows]
ytr = np.array([int(r['output']) for r in train_rows])
Xte = [r['input'] for r in test_rows]
yte = np.array([int(r['output']) for r in test_rows])
vec = TfidfVectorizer(analyzer='char_wb', ngram_range=(2, 4),
                      max_features=30000, min_df=2, sublinear_tf=True)
Xtr_v = vec.fit_transform(Xtr)
Xte_v = vec.transform(Xte)
ridge = Ridge(alpha=10.0).fit(Xtr_v, ytr)
reg_cont = ridge.predict(Xte_v)
reg_int = np.array([max(1, min(5, int(round(p)))) for p in reg_cont])

# ---- LLM (predictions.json, 顺序与 test_rows 一致) ----
llm_data = json.load(open('predictions.json', encoding='utf-8'))
llm_int = np.array([d['llm_pred'] for d in llm_data])
yte2 = np.array([d['human'] for d in llm_data])
assert (yte == yte2).all(), 'test 顺序不匹配!'
yte = yte2


def mae(p):
    return np.mean(np.abs(p - yte))


print(f'测试集 {len(yte)} 条')
print(f'人工分布: {dict(sorted(Counter(yte).items()))}')
print(f'\n回归 Ridge: ρ={spearmanr(reg_cont, yte)[0]:.3f}  MAE={mae(reg_int):.2f}  dist={dict(sorted(Counter(reg_int).items()))}')
print(f'LLM QLoRA:  ρ={spearmanr(llm_int, yte)[0]:.3f}  MAE={mae(llm_int):.2f}  dist={dict(sorted(Counter(llm_int).items()))}')

# ---- 一致 / 分歧 ----
agree = reg_int == llm_int
dis = ~agree
print(f'\n回归与LLM 一致: {int(agree.sum())}/{len(yte)} ({agree.mean()*100:.0f}%)   分歧: {int(dis.sum())}')
if dis.sum():
    reg_closer = np.abs(reg_int[dis] - yte[dis]) < np.abs(llm_int[dis] - yte[dis])
    llm_closer = np.abs(llm_int[dis] - yte[dis]) < np.abs(reg_int[dis] - yte[dis])
    tie = dis.sum() - int(reg_closer.sum()) - int(llm_closer.sum())
    print(f'分歧时: 回归MAE={np.mean(np.abs(reg_int[dis]-yte[dis])):.2f}  LLM MAE={np.mean(np.abs(llm_int[dis]-yte[dis])):.2f}')
    print(f'  分歧中 回归更近人工: {int(reg_closer.sum())}   LLM更近: {int(llm_closer.sum())}   等距: {tie}')

# ---- ensemble ----
ens = (reg_cont + llm_int) / 2
ens_w = 0.7 * reg_cont + 0.3 * llm_int
ens_int = np.array([max(1, min(5, int(round(p)))) for p in ens])
print(f'\nEnsemble(等权平均):        ρ={spearmanr(ens, yte)[0]:.3f}  MAE={mae(ens_int):.2f}')
print(f'Ensemble(0.7回归+0.3LLM):  ρ={spearmanr(ens_w, yte)[0]:.3f}')

# ---- 潜在标签噪声 ----
both_bad = (np.abs(reg_int - yte) >= 2) & (np.abs(llm_int - yte) >= 2)
print(f'\n潜在标签噪声(回归和LLM都错>=2档): {int(both_bad.sum())} 条')
for i in np.where(both_bad)[0]:
    print(f'  {llm_data[i]["filename"]}: human={yte[i]}  reg={reg_int[i]}  llm={llm_int[i]}')

# ---- 混合方案可行性结论 ----
reg_rho = spearmanr(reg_cont, yte)[0]
llm_rho = spearmanr(llm_int, yte)[0]
ens_rho = spearmanr(ens, yte)[0]
print(f'\n=== 混合方案③(LLM校准回归)可行性 ===')
print(f'  回归单模型 ρ={reg_rho:.3f}   LLM单模型 ρ={llm_rho:.3f}   等权ensemble ρ={ens_rho:.3f}')
if ens_rho > max(reg_rho, llm_rho) + 0.01:
    print(f'  → ensemble 明显超过单模型({ens_rho-max(reg_rho,llm_rho):+.3f}), 混合有增益, 方案③有数据支撑')
else:
    print(f'  → ensemble 没明显超过单模型, 混合增益有限')
if dis.sum():
    if llm_closer.sum() > reg_closer.sum():
        print(f'  → 分歧中 LLM 更近人工({int(llm_closer.sum())} vs {int(reg_closer.sum())}), LLM 校准有价值')
    else:
        print(f'  → 分歧中 回归 更准({int(reg_closer.sum())} vs {int(llm_closer.sum())}), LLM 校准价值有限, 可能反而拉低')
