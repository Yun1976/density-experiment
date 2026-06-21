# -*- coding: utf-8 -*-
"""
分层 train/test 切分 —— 让 train.py 的训练集 与 predict.py 的测试集 互斥且可复现。

为什么需要: 原 predict.py 在全部 241 条(=训练集)上评估, ρ 是 in-sample 的, 偏乐观,
跟回归模型 0.69 的对比也不公平。现在固定 seed 分层切出 20% 作纯测试集。

小样本类别(如 分1 仅 6 篇)至少留 1 条到测试集, 避免某分数完全缺席测试。
"""
import json
import random
from collections import defaultdict, Counter

DATA_FILE = 'train_data.jsonl'
SEED = 42
TEST_RATIO = 0.2


def load_rows(path=DATA_FILE):
    with open(path, encoding='utf-8') as f:
        return [json.loads(line) for line in f]


def stratified_split(rows, test_ratio=TEST_RATIO, seed=SEED):
    """按 output 分数分层切分, 返回 (train_rows, test_rows)。"""
    groups = defaultdict(list)
    for r in rows:
        groups[r['output']].append(r)
    train_rows, test_rows = [], []
    rnd = random.Random(seed)
    for score in sorted(groups):
        bucket = groups[score][:]
        rnd.shuffle(bucket)
        n_test = max(1, round(len(bucket) * test_ratio))  # 每类至少 1 条进测试
        test_rows.extend(bucket[:n_test])
        train_rows.extend(bucket[n_test:])
    return train_rows, test_rows


# 类别平衡: 每类设上限 CAP, 多数类欠采样到 CAP, 少数类全保留(不过采样, 避免过拟合)。
# 教训: A 标签 v3 把分2 压到 28 太狠, 伤了测试集中分2(最大类)的判断 -> 这次只轻微压制。
BALANCE_CAP = 80


def balance_train(train_rows, seed=SEED):
    """多数类欠采样到 BALANCE_CAP, 少数类全保留。不做过采样。"""
    rnd = random.Random(seed)
    groups = defaultdict(list)
    for r in train_rows:
        groups[r['output']].append(r)
    balanced = []
    for score in sorted(groups):
        bucket = groups[score][:]
        rnd.shuffle(bucket)
        balanced.extend(bucket[:BALANCE_CAP])  # 不足 CAP 全保留, 超过则截断
    rnd.shuffle(balanced)
    return balanced


def get_splits(balance=True):
    """返回 (all_rows, train_rows, test_rows), 供 train.py / predict.py 共用。
    balance=True 时对训练集做类别平衡(只影响 train_rows, test_rows 保持原样)。"""
    rows = load_rows()
    # 按内容去重: 原始数据可能有跨目录重复文件(如不同 source_dir 的 MEMORY.md),
    # 若不去重, 一份进训练一份进测试会造成泄漏。
    seen, dedup = set(), []
    for r in rows:
        if r['input'] in seen:
            continue
        seen.add(r['input'])
        dedup.append(r)
    if len(dedup) < len(rows):
        print(f'[split] 去重 {len(rows)} -> {len(dedup)} (移除 {len(rows) - len(dedup)} 条内容重复)')
    train_rows, test_rows = stratified_split(dedup)
    if balance:
        before = dict(sorted(Counter(r['output'] for r in train_rows).items()))
        train_rows = balance_train(train_rows)
        after = dict(sorted(Counter(r['output'] for r in train_rows).items()))
        print(f'[split] 平衡训练集: {before} -> {after} (共 {len(train_rows)} 条)')
    return dedup, train_rows, test_rows


if __name__ == '__main__':
    # 自检: 看切分结果与分布
    all_rows, train_rows, test_rows = get_splits()
    print(f'total {len(all_rows)} -> train {len(train_rows)} / test {len(test_rows)}')
    print(f'train dist: {dict(sorted(Counter(r["output"] for r in train_rows).items()))}')
    print(f'test  dist: {dict(sorted(Counter(r["output"] for r in test_rows).items()))}')
    # 记录级互斥校验: 用 input 内容(因为 filename 可能跨目录重名, 不能作唯一键)
    tr_keys = {r['input'] for r in train_rows}
    te_keys = {r['input'] for r in test_rows}
    print(f'record overlap (should be 0): {len(tr_keys & te_keys)}')
    dup = {k: v for k, v in Counter(r['filename'] for r in all_rows).items() if v > 1}
    if dup:
        print(f'note: {len(dup)} filename(s) reused across dirs (harmless): {list(dup)[:5]}')
