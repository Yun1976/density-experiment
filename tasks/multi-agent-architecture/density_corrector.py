#!/usr/bin/env python3
"""
density_corrector.py — 密度校正模型 v0.1 (zero deps)

纯 Python 实现，零外部依赖（仅有 json, math, pathlib）。
用于观测端点星信息密度衰减，最终交付：一个可用的密度校正模型。

训练条件：
  累积 ≥ 100 条完整回证的残差样本时触发首次训练

验证方式：
  时间序列交叉验证 — 训练集=Cycle 1..N-1, 验证集=Cycle N

部署方式：
  保存为 JSON 文件，judge cron 加载后校正 ρ 估计
  ρ̂ = ρ + ê（仅在 |ê| > error_threshold 时启用）

Author: 闻声（观自在系统）
Created: 2026-05-14
"""

import json
import math
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent
SERIES_FILE = BASE_DIR / "residual-series.jsonl"
MODEL_DIR = BASE_DIR / "model"
MODEL_DIR.mkdir(exist_ok=True)

MIN_SAMPLES_ABSOLUTE = 100
MIN_SAMPLES_TRAIN = 50   # minimum for ts-cv evaluation


# ---- Vector math (pure python) ----

def mean(vals):
    n = len(vals)
    if n == 0:
        return 0.0
    return sum(vals) / n

def std(vals):
    n = len(vals)
    if n < 2:
        return 1.0
    m = mean(vals)
    return math.sqrt(sum((x - m)**2 for x in vals) / (n - 1))

def dot(a, b):
    return sum(ai * bi for ai, bi in zip(a, b))

def mat_vec_mul(A, v):
    return [dot(row, v) for row in A]

def transpose(A):
    if not A:
        return []
    return [[A[i][j] for i in range(len(A))] for j in range(len(A[0]))]

def mat_mul(A, B):
    """A: m×k, B: k×n → m×n"""
    Bt = transpose(B)
    return [[dot(row, col) for col in Bt] for row in A]

def add_identity_scaled(A, alpha):
    n = len(A)
    if n == 0:
        return A
    result = [row[:] for row in A]
    for i in range(n):
        result[i][i] += alpha
    return result

def solve_linear(A, b):
    """
    Solve Ax = b using Gaussian elimination with partial pivoting.
    A is n×n, b is n-vector.
    """
    n = len(A)
    # Augmented matrix
    M = [A[i][:] + [b[i]] for i in range(n)]
    
    for col in range(n):
        # Partial pivot
        max_row = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[max_row][col]) < 1e-12:
            continue  # singular, skip
        if max_row != col:
            M[col], M[max_row] = M[max_row], M[col]
        
        # Eliminate below
        pivot = M[col][col]
        for row in range(col + 1, n):
            factor = M[row][col] / pivot
            for j in range(col, n + 1):
                M[row][j] -= factor * M[col][j]
    
    # Back substitution
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        if abs(M[i][i]) < 1e-12:
            x[i] = 0.0
        else:
            x[i] = (M[i][n] - sum(M[i][j] * x[j] for j in range(i + 1, n))) / M[i][i]
    return x


# ---- Data loading ----

def load_series():
    """Load residual-series.jsonl. Merges block records with validation records."""
    raw_records = []
    with open(SERIES_FILE, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            raw_records.append(json.loads(line))
    
    # Separate blocks (have S,R,C) from validation rows (have u_observed,residual)
    blocks = {}
    validations = {}
    for r in raw_records:
        keys = set(r.keys())
        bid = r.get("id")
        if not bid:
            continue
        if "S" in keys and "R" in keys and "C" in keys:
            # Block record - keep as base
            blocks[bid] = r
        if "u_observed" in keys and r.get("residual") is not None:
            # Validation record - store separately
            validations[bid] = r
    
    # Merge: block + its validation
    validated = []
    pending = []
    for bid, block in blocks.items():
        if bid in validations:
            merged = {**block, **validations[bid]}
            merged["validation_status"] = "validated"
            validated.append(merged)
        else:
            block["validation_status"] = "pending"
            pending.append(block)
    
    all_records = validated + pending
    return validated, pending, all_records


# ---- Feature extraction ----

def encode_decision(v):
    m = {"kept": 0, "compressed": 1, "dropped": 2, "pending": 1, "unknown": 1}
    return m.get(v, 1)

def feature_vector(rec):
    """7 features: S, R, C, lambda, rho, cycle/100, decision_enc"""
    return [
        rec["S"],
        rec["R"],
        rec["C"],
        rec.get("lambda", 1.0),
        rec["rho_estimated"],
        rec["cycle"] / 100.0,
        encode_decision(rec["decision"]),
    ]

def extract_label(rec):
    return rec["residual"]


# ---- Ridge regression (analytical) ----

class DensityCorrector:
    def __init__(self, alpha=1.0, error_threshold=0.1):
        self.alpha = alpha
        self.error_threshold = error_threshold
        self.coef_ = None      # length 7
        self.intercept_ = None
        self.f_means_ = None   # length 7
        self.f_stds_ = None    # length 7
        self.n_samples_ = 0
        self.train_mse_ = None
        self.train_rmse_ = None
        self.train_r2_ = None
        self.timestamp_ = None
    
    def fit(self, records):
        """Train ridge regression on validated records."""
        n = len(records)
        X_raw = [feature_vector(r) for r in records]
        y = [extract_label(r) for r in records]
        
        # Standardize features
        n_feat = len(X_raw[0])
        self.f_means_ = [mean([X_raw[i][j] for i in range(n)]) for j in range(n_feat)]
        self.f_stds_ = [max(std([X_raw[i][j] for i in range(n)]), 1e-10) for j in range(n_feat)]
        
        X = [[(X_raw[i][j] - self.f_means_[j]) / self.f_stds_[j] 
              for j in range(n_feat)] for i in range(n)]
        
        # Augment X with intercept column
        X_aug = [row + [1.0] for row in X]
        p = n_feat + 1  # features + intercept
        
        # XTX
        XTX = mat_mul(transpose(X_aug), X_aug)  # p×p
        
        # Ridge: XTX + alpha*I (don't regularize intercept)
        XTX_reg = [row[:] for row in XTX]
        for i in range(n_feat):
            XTX_reg[i][i] += self.alpha
        
        # XTy
        XTy = [sum(X_aug[i][j] * y[i] for i in range(n)) for j in range(p)]
        
        # Solve (XTX + aI) β = XTy
        beta = solve_linear(XTX_reg, XTy)
        
        self.coef_ = beta[:n_feat]
        self.intercept_ = beta[n_feat]
        self.n_samples_ = n
        
        # In-sample metrics
        y_pred = [dot(X_aug[i], beta) for i in range(n)]
        self.train_mse_ = mean([(y[i] - y_pred[i])**2 for i in range(n)])
        self.train_rmse_ = math.sqrt(self.train_mse_)
        
        y_mean = mean(y)
        ss_res = sum((y[i] - y_pred[i])**2 for i in range(n))
        ss_tot = sum((yi - y_mean)**2 for yi in y)
        self.train_r2_ = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0
        
        self.timestamp_ = datetime.now().isoformat()
    
    def predict(self, record):
        """Predict residual for a record dict."""
        if self.coef_ is None:
            return 0.0
        x = feature_vector(record)
        x_scaled = [(x[j] - self.f_means_[j]) / self.f_stds_[j] for j in range(len(x))]
        x_aug = x_scaled + [1.0]
        return dot(x_aug, self.coef_ + [self.intercept_])
    
    def correct(self, record):
        """
        Correct density estimate. Only applies if |ê| > error_threshold.
        Returns (rho_corrected, e_hat, applied)
        """
        e_hat = self.predict(record)
        if abs(e_hat) > self.error_threshold:
            return record["rho_estimated"] + e_hat, e_hat, True
        return record["rho_estimated"], e_hat, False
    
    def to_dict(self):
        return {
            "alpha": self.alpha,
            "error_threshold": self.error_threshold,
            "coef": self.coef_,
            "intercept": self.intercept_,
            "feature_means": self.f_means_,
            "feature_stds": self.f_stds_,
            "n_samples": self.n_samples_,
            "train_mse": round(self.train_mse_, 6) if self.train_mse_ else None,
            "train_rmse": round(self.train_rmse_, 6) if self.train_rmse_ else None,
            "train_r2": round(self.train_r2_, 6) if self.train_r2_ else None,
            "timestamp": self.timestamp_,
            "feature_names": ["S", "R", "C", "lambda", "rho", "cycle_norm", "decision_enc"],
        }
    
    @classmethod
    def from_dict(cls, d):
        m = cls(alpha=d["alpha"], error_threshold=d.get("error_threshold", 0.1))
        m.coef_ = d["coef"]
        m.intercept_ = d["intercept"]
        m.f_means_ = d["feature_means"]
        m.f_stds_ = d["feature_stds"]
        m.n_samples_ = d["n_samples"]
        m.train_mse_ = d["train_mse"]
        m.train_rmse_ = d["train_rmse"]
        m.train_r2_ = d["train_r2"]
        m.timestamp_ = d["timestamp"]
        return m


# ---- Time-series cross validation ----

def ts_cross_validate(records):
    """
    Train on cycles 1..k, test on cycle k+1.
    No data leakage — simulates real deployment.
    """
    records = sorted(records, key=lambda r: r["cycle"])
    
    cycles = {}
    for r in records:
        cycles.setdefault(r["cycle"], []).append(r)
    
    cycle_ids = sorted(cycles.keys())
    if len(cycle_ids) < 2:
        return None
    
    results = []
    for i in range(1, len(cycle_ids)):
        train_cycles = cycle_ids[:i]
        test_cycle = cycle_ids[i]
        
        train_rec = [r for c in train_cycles for r in cycles[c]]
        test_rec = cycles[test_cycle]
        
        if len(train_rec) < MIN_SAMPLES_TRAIN:
            continue
        
        model = DensityCorrector()
        model.fit(train_rec)
        
        for r in test_rec:
            e_hat = model.predict(r)
            e_true = r["residual"]
            results.append({
                "test_cycle": test_cycle,
                "block_id": r["id"],
                "e_true": e_true,
                "e_pred": round(e_hat, 4),
                "squared_error": round((e_true - e_hat)**2, 6),
            })
    
    if len(results) < 5:
        return None  # too few test observations
    
    se = [r["squared_error"] for r in results]
    mse_val = mean(se)
    rmse_val = math.sqrt(mse_val)
    
    e_true_all = [r["e_true"] for r in results]
    baseline_rmse = math.sqrt(mean([e**2 for e in e_true_all]))
    
    improvement = (baseline_rmse - rmse_val) / baseline_rmse * 100 if baseline_rmse > 0 else 0
    
    return {
        "n_folds": len(results),
        "rmse": round(rmse_val, 4),
        "baseline_rmse": round(baseline_rmse, 4),
        "improvement_pct": round(improvement, 1),
        "reliable": improvement > 5 and len(results) >= 20,
        "per_fold": results,
    }


# ---- Persistence ----

def save_model(model):
    MODEL_DIR.mkdir(exist_ok=True)
    path = MODEL_DIR / "density_corrector_current.json"
    
    # Archive old
    if path.exists():
        import shutil
        ts = model.timestamp_[:10].replace("-", "") if model.timestamp_ else datetime.now().strftime("%Y%m%d")
        shutil.copy(path, MODEL_DIR / f"density_corrector_{ts}.json")
    
    model_dict = model.to_dict()
    model_dict["version"] = len(list(MODEL_DIR.glob("density_corrector_*.json"))) + 1
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(model_dict, f, indent=2, ensure_ascii=False)
    
    return path

def load_model():
    path = MODEL_DIR / "density_corrector_current.json"
    if not path.exists():
        return None
    with open(path, encoding="utf-8") as f:
        return DensityCorrector.from_dict(json.load(f))


# ---- Main ----

def main():
    print("=== 密度校正模型 v0.1 ===\n")
    
    validated, pending, all_records = load_series()
    print(f"数据状态:")
    print(f"  已验证残差: {len(validated)} 条")
    print(f"  待回证: {len(pending)} 条")
    
    if len(validated) < MIN_SAMPLES_ABSOLUTE:
        needed = MIN_SAMPLES_ABSOLUTE - len(validated)
        cycles_est = math.ceil(needed / 3)  # ~3 new validated/cycle
        days_est = math.ceil(cycles_est / 4)  # ~4 cycles/day
        print(f"\n❌ 未达到训练门槛: {len(validated)}/{MIN_SAMPLES_ABSOLUTE}")
        print(f"   预计还需 {days_est} 天 (约 {cycles_est} 轮裁决)")
    else:
        print(f"\n✅ 数据充足 ({len(validated)} ≥ {MIN_SAMPLES_ABSOLUTE})，可训练")
    
    # Always compute ts-CV
    print(f"\n--- 时间序列交叉验证（模拟部署）---")
    cv = ts_cross_validate(validated)
    if cv:
        print(f"  测试观测: {cv['n_folds']}")
        print(f"  TS-CV RMSE: {cv['rmse']:.4f}")
        print(f"  基线 RMSE (ê=0): {cv['baseline_rmse']:.4f}")
        print(f"  改进: {cv['improvement_pct']:.1f}%")
        print(f"  可靠性: {'✅ 可部署' if cv['reliable'] else '❌ 不可靠（改需进>5%且观测≥20）'}")
    else:
        print(f"  数据不足，无法做 TS-CV（需要 ≥2 个 cycle 且 ≥5 条测试观测）")
    
    # Only train if ready
    if len(validated) >= MIN_SAMPLES_ABSOLUTE:
        print(f"\n--- 训练 ---")
        model = DensityCorrector()
        model.fit(validated)
        path = save_model(model)
        
        print(f"  n_samples: {model.n_samples_}")
        print(f"  train_rmse: {model.train_rmse_:.4f}")
        print(f"  train_r2: {model.train_r2_:.4f}")
        print(f"  已保存: {path}")
        
        print(f"\n  特征系数:")
        names = model.to_dict()["feature_names"] + ["intercept"]
        vals = model.coef_ + [model.intercept_]
        for name, val in zip(names, vals):
            print(f"    {name:16s}: {val:+.4f}")
    else:
        print(f"\n⏳ 等待数据累积...模型文件未生成。")
    
    print(f"\n下次检查: judge cron 每 6h 自动累积残差。")

if __name__ == "__main__":
    main()
