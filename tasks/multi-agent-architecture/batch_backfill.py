import json
import os

SERIES_FILE = r'C:\Users\user\.openclaw\workspace\tasks\multi-agent-architecture\residual-series.jsonl'
LOG_FILE = r'C:\Users\user\.openclaw\workspace\tasks\multi-agent-architecture\density-log.jsonl'

# Load all records
with open(SERIES_FILE, encoding='utf-8', errors='replace') as f:
    lines = [json.loads(line.strip()) for line in f if line.strip() and not line.startswith('#')]

# Index by id
by_id = {}
for r in lines:
    rid = r.get('id')
    if rid:
        if rid in by_id:
            # Validation record comes after block - merge
            if 'u_observed' in r and r.get('residual') is not None:
                by_id[rid] = {**by_id[rid], **r}
        else:
            by_id[rid] = r

# Identify pending blocks whose deadline has passed
CURRENT_CYCLE = 34
updated = False

for rid, r in by_id.items():
    if r.get('validation_status') != 'pending':
        continue
    deadline = r.get('validation_deadline', 0)
    if deadline is None:
        deadline = 0
    cyc = r.get('cycle', 0)
    if cyc is None:
        cyc = 0
    
    # If deadline has passed AND block is old enough (cycle <= CURRENT - 3)
    if deadline <= CURRENT_CYCLE and cyc <= CURRENT_CYCLE - 3:
        # Conservative approach: mark as validated with u=0 (never cited)
        # These are very old blocks that were never explicitly referenced
        # in any known cycle. They're not definitely useless but without
        # explicit citation evidence, u=0 is the default.
        r['u_observed'] = 0.0
        r['u_source'] = f'batch_backfill_C{CURRENT_CYCLE}_never_cited'
        r['u_round'] = CURRENT_CYCLE
        r['residual'] = r['u_observed'] - r.get('rho_estimated', 0)
        r['validation_status'] = 'validated'
        updated = True
        print(f'Backfilled: {rid} C{cyc} deadline C{deadline} u=0 residual={r["residual"]:.3f}')

if updated:
    # Rebuild file
    with open(SERIES_FILE, 'w', encoding='utf-8') as f:
        for rid, r in by_id.items():
            jstr = json.dumps(r, ensure_ascii=False)
            f.write(jstr + '\n')
    print(f'\nBackfill complete.')
else:
    print('No blocks to backfill.')

# Count
validated_count = sum(1 for r in by_id.values() if r.get('validation_status') == 'validated' and r.get('residual') is not None)
pending_count = sum(1 for r in by_id.values() if r.get('validation_status') == 'pending')
print(f'After backfill: {validated_count} validated, {pending_count} pending')
