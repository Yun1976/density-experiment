# -*- coding: utf-8 -*-
"""
端点星 · 信息存活价值评估器 —— QLoRA 微调脚本
运行环境: Windows + NVIDIA 5060 Ti (16GB)
用法:
  1. 先装依赖:  pip install -r requirements.txt
  2. 运行:      python train.py
  3. 产出:      ./output/  (LoRA adapter, 拷回 U 盘带回)
模型: Qwen2.5-3B-Instruct, 4bit 量化 + LoRA 微调
"""
import os
import sys
import json
import torch

# Windows GBK 终端无法输出 ✓ 等字符, 强制 stdout 用 utf-8, 避免训练完成后 print 崩溃
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
from datasets import Dataset
from transformers import (
    AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
)
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from trl import SFTTrainer, SFTConfig
from split import get_splits   # 分层切分: 只用训练子集, 测试子集留给 predict.py

MODEL_NAME = 'Qwen/Qwen2.5-3B-Instruct'   # 首次会自动下载(约6GB), 国内可设 HF 镜像见 README
OUTPUT_DIR = './output'
MAX_SEQ = 1024

# ---------- 1. 加载训练数据 ----------
print('加载训练数据...')
all_rows, raw, test_rows = get_splits()   # 训练子集; test_rows 留给 predict.py
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
if tokenizer.pad_token is None:
    tokenizer.pad_token = tokenizer.eos_token

texts = []
for r in raw:
    msg = [
        {'role': 'system', 'content': r['instruction']},
        {'role': 'user', 'content': r['input']},
        {'role': 'assistant', 'content': r['output']},
    ]
    texts.append(tokenizer.apply_chat_template(msg, tokenize=False, add_generation_prompt=False))
ds = Dataset.from_dict({'text': texts})
print(f'  {len(ds)} 条训练样本 (共 {len(all_rows)} 条, 留 {len(test_rows)} 条作测试集)')

# ---------- 2. 4bit 量化加载模型 ----------
print('加载模型(4bit 量化, 首次需下载, 请耐心)...')
bnb = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_quant_type='nf4',
    bnb_4bit_compute_dtype=torch.bfloat16,
)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME, quantization_config=bnb, device_map='auto', trust_remote_code=True
)
model = prepare_model_for_kbit_training(model)
model.config.use_cache = False

# ---------- 3. LoRA 配置 ----------
peft_cfg = LoraConfig(
    r=16, lora_alpha=32, lora_dropout=0.05,
    target_modules=['q_proj', 'k_proj', 'v_proj', 'o_proj', 'gate_proj', 'up_proj', 'down_proj'],
    task_type='CAUSAL_LM',
)
model = get_peft_model(model, peft_cfg)
model.print_trainable_parameters()

# ---------- 4. 训练 ----------
print('开始训练(5060Ti 上约 5-15 分钟)...')
args = SFTConfig(
    output_dir=OUTPUT_DIR,
    num_train_epochs=3,
    per_device_train_batch_size=2,
    gradient_accumulation_steps=4,
    learning_rate=2e-4,
    logging_steps=10,
    save_strategy='epoch',
    bf16=True,                       # 5060 Ti 支持 bf16
    max_length=MAX_SEQ,
    dataset_text_field='text',
)
trainer = SFTTrainer(model=model, train_dataset=ds, args=args, processing_class=tokenizer)
trainer.train()
trainer.save_model(OUTPUT_DIR)
tokenizer.save_pretrained(OUTPUT_DIR)
print(f'\n✓ 训练完成! LoRA adapter 已存到 {OUTPUT_DIR}')
print('  把整个 output 文件夹拷回 U 盘, 带回给端点星。')
