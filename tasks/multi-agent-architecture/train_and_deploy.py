import json
import math
import os
from datetime import datetime

SCRIPT_DIR = r'C:\Users\user\.openclaw\workspace\tasks\multi-agent-architecture'
SERIES_FILE = os.path.join(SCRIPT_DIR, 'residual-series.jsonl')
MODEL_DIR = os.path.join(SCRIPT_DIR, 'model')

# ── Load & merge data ──
with open(SERIES_FILE, encoding='utf-8', errors='replace') as f:
    raw_records = [json.loads(line.strip()) for line in f if line.strip() and not line.startswith('#')]

blocks = {}
for r in raw_records:
    bid = r.get('id')
    if not bid:
        continue
    keys = set(r.keys())
    if 'S' in keys and 'R' in keys and 'C' in keys:
        blocks[bid] = r
    if 'u_observed' in keys and r.get('residual') is not None:
        if bid in blocks:
            blocks[bid] = {**blocks[bid], **r}
        else:
            blocks[bid] = r

# Filter to validated (have residual)
validated = []
for bid, r in blocks.items():
    if r.get('residual') is not None and r.get('rho_estimated') is not None:
        if 'S' not in r or 'R' not in r or 'C' not in r:
            continue  # skip validation-only rows without features
        validated.append(r)

print(f'Merged validated records: {len(validated)}')

# ── Feature extraction ──
def encode_decision(v):
    m = {'kept': 0, 'compressed': 1, 'dropped': 2}
    return m.get(v, 1)

def feature_vector(rec):
    return [
        rec['S'],
        rec['R'],
        rec['C'],
        rec.get('lambda', 1.0),
        rec['rho_estimated'],
        rec.get('cycle', 0) / 100.0,
        encode_decision(rec.get('decision', 'unknown')),
    ]

X = [feature_vector(r) for r in validated]
y = [r['residual'] for r in validated]
print(f'Feature vectors: {len(X)}, targets: {len(y)}')

# ── Ridge Regression (closed form) ──
# w = (X^T X + alpha*I)^(-1) X^T y
alpha = 1.0  # L2 regularization

n = len(X)
d = len(X[0]) + 1  # +1 for intercept (bias)

# Build design matrix with intercept column
A = [[1.0] + row for row in X]  # n x d

# A^T A + alpha*I (but don't regularize intercept)
ATA = [[0.0] * d for _ in range(d)]
for row in A:
    for i in range(d):
        for j in range(d):
            ATA[i][j] += row[i] * row[j]

# Add ridge penalty (skip intercept)
for i in range(1, d):
    ATA[i][i] += alpha

# A^T y
ATy = [0.0] * d
for row, yi in zip(A, y):
    for i in range(d):
        ATy[i] += row[i] * yi

# Solve via Gaussian elimination
def solve(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for col in range(n):
        # Pivot
        max_row = max(range(col, n), key=lambda r: abs(M[r][col]))
        if abs(M[max_row][col]) < 1e-12:
            continue
        M[col], M[max_row] = M[max_row], M[col]
        # Eliminate below
        for row in range(col + 1, n):
            factor = M[row][col] / M[col][col]
            for j in range(col, n + 1):
                M[row][j] -= factor * M[col][j]
    # Back-substitute
    x = [0.0] * n
    for i in range(n - 1, -1, -1):
        x[i] = M[i][n] / M[i][i] if abs(M[i][i]) > 1e-12 else 0.0
        for j in range(i - 1, -1, -1):
            M[j][n] -= M[j][i] * x[i]
    return x

w = solve(ATA, ATy)
intercept = w[0]
coef = w[1:]

# ── Training metrics ──
preds = [intercept + sum(c * f for c, f in zip(coef, row)) for row in X]
residuals = [y[i] - preds[i] for i in range(n)]
rmse = math.sqrt(sum(r * r for r in residuals) / n)

y_mean = sum(y) / n
ss_tot = sum((yi - y_mean) ** 2 for yi in y)
ss_res = sum(r * r for r in residuals)
r2 = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

print(f'Training RMSE: {rmse:.4f}')
print(f'Training R²: {r2:.4f}')
print()

feature_names = ['S', 'R', 'C', 'lambda', 'rho_estimated', 'cycle/100', 'decision_enc']
print('Feature coefficients:')
for name, val in zip(feature_names, coef):
    print(f'  {name:16s}: {val:+.4f}')
print(f'  {"intercept":16s}: {intercept:+.4f}')

# ── TS-CV ──
cycles = sorted(set(r['cycle'] for r in validated))
print(f'\nCycles: {min(cycles)}-{max(cycles)}, {len(cycles)} unique')

# Train on all-but-last, test on last
n_folds = min(5, len(cycles) - 1)
fold_results = []
for fold in range(n_folds):
    test_cycle = cycles[-(fold + 1)]
    train = [r for r in validated if r['cycle'] != test_cycle]
    test = [r for r in validated if r['cycle'] == test_cycle]
    
    if len(test) == 0:
        continue
    
    X_train = [feature_vector(r) for r in train]
    y_train = [r['residual'] for r in train]
    X_test = [feature_vector(r) for r in test]
    y_test = [r['residual'] for r in test]
    
    # Train ridge on train set
    n_train = len(X_train)
    d_train = len(X_train[0]) + 1
    A_train = [[1.0] + row for row in X_train]
    
    ATA_train = [[0.0] * d_train for _ in range(d_train)]
    ATy_train = [0.0] * d_train
    for row, yi in zip(A_train, y_train):
        for i in range(d_train):
            for j in range(d_train):
                ATA_train[i][j] += row[i] * row[j]
    for i in range(1, d_train):
        ATA_train[i][i] += alpha
    for row, yi in zip(A_train, y_train):
        for i in range(d_train):
            ATy_train[i] += row[i] * yi
    
    w_fold = solve(ATA_train, ATy_train)
    
    # Predict on test
    fold_preds = []
    for row in X_test:
        pred = w_fold[0]  # intercept
        for c, f in zip(w_fold[1:], row):
            pred += c * f
        fold_preds.append(pred)
    
    fold_residuals = [y_test[i] - fold_preds[i] for i in range(len(y_test))]
    fold_rmse = math.sqrt(sum(r * r for r in fold_residuals) / len(fold_residuals))
    
    # Baseline: always predict 0
    baseline_rmse = math.sqrt(sum(yi * yi for yi in y_test) / len(y_test))
    
    fold_results.append({
        'test_cycle': test_cycle,
        'n_test': len(test),
        'rmse': fold_rmse,
        'baseline_rmse': baseline_rmse,
    })

# Average TS-CV
cv_rmse = sum(f['rmse'] for f in fold_results) / len(fold_results)
cv_baseline = sum(f['baseline_rmse'] for f in fold_results) / len(fold_results)
improvement = (cv_baseline - cv_rmse) / cv_baseline * 100 if cv_baseline > 0 else 0

print(f'\n--- TS-CV ({len(fold_results)} folds) ---')
for fr in fold_results:
    imp = (fr['baseline_rmse'] - fr['rmse']) / fr['baseline_rmse'] * 100
    print(f'  C{fr["test_cycle"]}: n={fr["n_test"]} RMSE={fr["rmse"]:.4f} baseline={fr["baseline_rmse"]:.4f} imp={imp:.1f}%')
print(f'Average: RMSE={cv_rmse:.4f}, improvement={improvement:.1f}%')

# ── Save model ──
os.makedirs(MODEL_DIR, exist_ok=True)
model_dict = {
    'version': 1,
    'timestamp': datetime.now().isoformat(),
    'algorithm': 'ridge_regression',
    'alpha': alpha,
    'n_samples': n,
    'train_rmse': round(rmse, 4),
    'train_r2': round(r2, 4),
    'cv_rmse': round(cv_rmse, 4),
    'cv_improvement_pct': round(improvement, 1),
    'feature_names': ['intercept'] + feature_names,
    'coefficients': [intercept] + coef,
    'feature_stats': {
        'S': {'mean': sum(r['S'] for r in validated) / n, 'sd': math.sqrt(sum((r['S'] - sum(r2['S'] for r2 in validated)/n)**2 for r in validated)/n)},
        'R': {'mean': sum(r['R'] for r in validated) / n, 'sd': math.sqrt(sum((r['R'] - sum(r2['R'] for r2 in validated)/n)**2 for r in validated)/n)},
        'C': {'mean': sum(r['C'] for r in validated) / n, 'sd': math.sqrt(sum((r['C'] - sum(r2['C'] for r2 in validated)/n)**2 for r in validated)/n)},
    }
}

path = os.path.join(MODEL_DIR, 'density_corrector_current.json')
with open(path, 'w', encoding='utf-8') as f:
    json.dump(model_dict, f, indent=2, ensure_ascii=False)

print(f'\nModel saved to {path}')
print('Density corrector v1 deployed.')
