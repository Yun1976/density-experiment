# -*- coding: utf-8 -*-
"""
训练完后评估: 用微调好的模型给【测试集】笔记打分, 算和人工评分的一致性。
注意: 评估在训练时未见过的 20% 测试子集上进行(由 split.py 切分), 与训练集互斥,
      这样得到的 Spearman ρ 才能跟回归模型 0.69 公平对比。
在 5060 Ti 上训练完后接着跑:  python predict.py
产出 predictions.json (拷回 U 盘)
对比目标: 回归模型 ρ=0.69, LLM 要超过它
"""
import sys
import json
import re
import torch

# Windows GBK 终端无法输出 ρ 等字符, 强制 stdout 用 utf-8
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
from scipy.stats import spearmanr
from split import get_splits   # 只在测试子集上评估

MODEL = 'Qwen/Qwen2.5-3B-Instruct'
ADAPTER = './output'

print('加载微调模型...')
bnb = BitsAndBytesConfig(load_in_4bit=True, bnb_4bit_quant_type='nf4', bnb_4bit_compute_dtype=torch.bfloat16)
tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
base = AutoModelForCausalLM.from_pretrained(MODEL, quantization_config=bnb, device_map='auto', trust_remote_code=True)
model = PeftModel.from_pretrained(base, ADAPTER)
model.eval()

_all, _train, rows = get_splits()   # 取测试子集(与训练集互斥)
preds, humans = [], []
print(f'评估 {len(rows)} 条测试样本 (约2-5分钟)...')

for i, r in enumerate(rows):
    msg = [
        {'role': 'system', 'content': r['instruction']},
        {'role': 'user', 'content': r['input']},
    ]
    inp = tok.apply_chat_template(msg, tokenize=False, add_generation_prompt=True)
    ids = tok(inp, return_tensors='pt').to(model.device)
    with torch.no_grad():
        out = model.generate(**ids, max_new_tokens=8, do_sample=False, pad_token_id=tok.eos_token_id)
    text = tok.decode(out[0][ids.input_ids.shape[1]:], skip_special_tokens=True)
    m = re.search(r'[1-5]', text)
    pred = int(m.group()) if m else 3
    preds.append(pred)
    humans.append(int(r['output']))
    if (i + 1) % 50 == 0:
        print(f'  {i+1}/{len(rows)}')

rho, _ = spearmanr(preds, humans)
mae = sum(abs(p - h) for p, h in zip(preds, humans)) / len(preds)
exact = sum(1 for p, h in zip(preds, humans) if p == h)
print(f'\n=== 微调 LLM vs 人工评分 (测试集) ===')
print(f'  Spearman ρ = {rho:.3f}   (回归模型 0.69, LLM 要超过这个才算赢)')
print(f'  MAE        = {mae:.3f}')
print(f'  完全一致   = {exact}/{len(rows)} ({exact*100//len(rows)}%)')

json.dump(
    [{'filename': r['filename'], 'human': h, 'llm_pred': p} for r, h, p in zip(rows, humans, preds)],
    open('predictions.json', 'w', encoding='utf-8'),
    ensure_ascii=False, indent=2,
)
print('\n预测已存 predictions.json, 连同 output/ 一起拷回 U 盘')
