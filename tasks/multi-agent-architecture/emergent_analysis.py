#!/usr/bin/env python3
"""
Emergent-track analysis for DENSITY-001.
Zero-prior: change point detection, PCA, graph topology evolution.
Input: behavior-log.jsonl, residual-series.jsonl
Output: emergent_analysis_report.md
"""

import json
import math
import os
from collections import Counter

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BEHAVIOR_LOG = os.path.join(SCRIPT_DIR, "behavior-log.jsonl")
RESIDUAL_SERIES = os.path.join(SCRIPT_DIR, "residual-series.jsonl")
OUTPUT = os.path.join(SCRIPT_DIR, "EMERGENT_ANALYSIS_REPORT.md")

# ── Helpers (zero external deps) ──────────────────────────

def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0

def variance(xs, mu=None):
    if mu is None:
        mu = mean(xs)
    return sum((x - mu) ** 2 for x in xs) / len(xs) if len(xs) > 1 else 0.0

def std(xs):
    return math.sqrt(variance(xs))

def cumsum(xs):
    s, out = 0, []
    for x in xs:
        s += x
        out.append(s)
    return out


# ── 1. PELT Change Point Detection ──────────────────────

def pelt_change_points(series, penalty=3.0, min_span=3):
    """
    Simple PELT (Pruned Exact Linear Time) for change point detection.
    segment cost = within-segment variance
    """
    n = len(series)
    if n < min_span * 2:
        return []

    # cost[i][j] = variance of series[i:j+1] (inclusive)
    F = [0.0] * (n + 1)  # F[t] = min cost segmenting [0:t)
    cp = [0] * (n + 1)  # last change point before t

    for t in range(1, n + 1):
        F[t] = float('inf')
        best_s = -1
        for s in range(max(0, t - 30), t):  # limited lookback for efficiency
            if t - s < min_span and s > 0:
                continue
            seg = series[s:t]
            seg_cost = variance(seg) * (t - s) if len(seg) > 1 else 0.0
            cost = F[s] + seg_cost + penalty
            if cost < F[t]:
                F[t] = cost
                best_s = s
        cp[t] = best_s

    # Backtrack
    changes = []
    t = n
    while t > 0:
        t = cp[t]
        if t > 0:
            changes.append(t)

    changes.reverse()
    # Deduplicate very close change points (within min_span)
    deduped = []
    for c in changes:
        if not deduped or c - deduped[-1] >= min_span:
            deduped.append(c)
    return deduped


# ── 2. PCA (simple power iteration for 2D) ──────────────

def pca_2d(matrix):
    """Simple PCA via covariance -> eigen decomposition (2 components)."""
    if not matrix or not matrix[0]:
        return [], []

    m = len(matrix)
    k = len(matrix[0])
    # Center
    means = [sum(col) / m for col in zip(*matrix)]
    centered = [[row[i] - means[i] for i in range(k)] for row in matrix]

    # Covariance matrix (k x k)
    cov = [[0.0] * k for _ in range(k)]
    for row in centered:
        for i in range(k):
            for j in range(k):
                cov[i][j] += row[i] * row[j]
    for i in range(k):
        for j in range(k):
            cov[i][j] /= (m - 1) if m > 1 else 1.0

    # Power iteration for top 2 eigenvectors
    def power_iterate(A, n_iter=30):
        d = len(A)
        v = [1.0 / math.sqrt(d)] * d
        for _ in range(n_iter):
            Av = [sum(A[i][j] * v[j] for j in range(d)) for i in range(d)]
            norm = math.sqrt(sum(x * x for x in Av))
            if norm < 1e-10:
                break
            v = [x / norm for x in Av]
        # Rayleigh quotient for eigenvalue
        Av = [sum(A[i][j] * v[j] for j in range(d)) for i in range(d)]
        lam = sum(v[i] * Av[i] for i in range(d))
        return lam, v

    lam1, v1 = power_iterate(cov)
    # Deflate for second component
    cov_deflated = [[0.0] * k for _ in range(k)]
    for i in range(k):
        for j in range(k):
            cov_deflated[i][j] = cov[i][j] - lam1 * v1[i] * v1[j]
    lam2, v2 = power_iterate(cov_deflated)

    # Project
    pc1 = [sum(row[i] * v1[i] for i in range(k)) for row in centered]
    pc2 = [sum(row[i] * v2[i] for i in range(k)) for row in centered]

    return pc1, pc2, lam1, lam2, v1, v2


# ── 3. Graph Topology ────────────────────────────────────

def graph_metrics(behavior_records):
    """Extract graph metrics from reference chains."""
    # Build adjacency: event -> set of events it references
    nodes = {}
    for r in behavior_records:
        eid = r.get("id", "")
        refs = r.get("references_to", [])
        if eid:
            nodes[eid] = refs

    if not nodes:
        return {}

    n = len(nodes)
    # In-degree distribution
    indeg = Counter()
    for refs in nodes.values():
        for ref in refs:
            indeg[ref] += 1
    
    indeg_values = [indeg[nid] for nid in nodes] if nodes else [0]
    avg_indeg = mean(indeg_values) if indeg_values else 0.0

    # Components (undirected connected)
    adj = {nid: set(refs) for nid, refs in nodes.items()}
    for nid in nodes:
        for ref in nodes.get(nid, []):
            if ref in adj:
                adj[ref].add(nid)

    visited = set()
    components = []
    for nid in nodes:
        if nid in visited:
            continue
        stack = [nid]
        comp = set()
        while stack:
            cur = stack.pop()
            if cur in comp:
                continue
            comp.add(cur)
            visited.add(cur)
            for nb in adj.get(cur, []):
                if nb not in comp:
                    stack.append(nb)
        components.append(comp)

    comp_sizes = sorted([len(c) for c in components], reverse=True)

    # Clustering coefficient (simplified)
    # C = avg(2*edges_among_neighbors / (k*(k-1)))
    cluster_coeffs = []
    for nid, refs in nodes.items():
        neighbors = set(refs)
        if not refs:
            continue
        for ref in refs:
            if ref in adj:
                neighbors.update(adj[ref])
        neighbors.discard(nid)
        k = len(neighbors)
        if k < 2:
            continue
        edges = 0
        nlist = list(neighbors)
        for i in range(len(nlist)):
            for j in range(i + 1, len(nlist)):
                if nlist[j] in adj.get(nlist[i], set()) or nlist[i] in adj.get(nlist[j], set()):
                    edges += 1
        cluster_coeffs.append(2 * edges / (k * (k - 1)) if k > 1 else 0)

    avg_cluster = mean(cluster_coeffs) if cluster_coeffs else 0.0

    return {
        "n_nodes": n,
        "n_edges": sum(len(refs) for refs in nodes.values()),
        "avg_indegree": round(avg_indeg, 3),
        "n_components": len(components),
        "largest_component_size": comp_sizes[0] if comp_sizes else 0,
        "largest_component_pct": round(comp_sizes[0] / n * 100, 1) if comp_sizes and n > 0 else 0,
        "n_isolates": sum(1 for c in comp_sizes if c == 1),
        "component_sizes": comp_sizes[:10],
        "avg_clustering": round(avg_cluster, 3),
    }


# ── Main Analysis ────────────────────────────────────────

def main():
    # Load behavior log
    behaviors = []
    with open(BEHAVIOR_LOG, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            behaviors.append(json.loads(line))

    # Load residual series
    residuals = []
    with open(RESIDUAL_SERIES, encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            r = json.loads(line)
            if r.get("residual") is not None and r.get("validation_status") == "validated":
                residuals.append(r)

    n_beh = len(behaviors)
    print(f"Behavior records: {n_beh}")
    print(f"Validated residuals: {len(residuals)}")

    # ── 1. Change Point Detection ──
    # Use residual values as signal
    if len(residuals) >= 6:
        # Sort by cycle, take residual values
        r_sorted = sorted(residuals, key=lambda r: r.get("cycle", 0))
        # Group by cycle for smoother signal
        cycle_residuals = {}
        for r in r_sorted:
            cyc = r.get("cycle", 0)
            cycle_residuals.setdefault(cyc, []).append(r["residual"])
        cycles = sorted(cycle_residuals.keys())
        cycle_means = [mean(cycle_residuals[c]) for c in cycles]
        cp_indices = pelt_change_points(cycle_means, penalty=3.0, min_span=3)
        cp_cycles = [cycles[i] for i in cp_indices] if cp_indices else []
        print(f"Change points detected at cycles: {cp_cycles}")
    else:
        cycles, cycle_means, cp_cycles = [], [], []
        print("Not enough residual data for change point detection")

    # ── 2. Behavior drift via token length & compressibility ──
    # Build per-cycle aggregates
    cycle_stats = {}
    for b in behaviors:
        cyc = b.get("cycle", 0)
        if cyc not in cycle_stats:
            cycle_stats[cyc] = {
                "token_lengths": [],
                "compressibilities": [],
                "n_refs": [],
            }
        cycle_stats[cyc]["token_lengths"].append(b.get("raw_length_tokens", 0))
        cycle_stats[cyc]["compressibilities"].append(b.get("compressibility_gzip", 0))
        cycle_stats[cyc]["n_refs"].append(len(b.get("references_to", [])))

    behavior_cycles = sorted(cycle_stats.keys())
    if behavior_cycles:
        comp_series = [mean(cycle_stats[c]["compressibilities"]) for c in behavior_cycles]
        token_series = [mean(cycle_stats[c]["token_lengths"]) for c in behavior_cycles]
        ref_series = [mean(cycle_stats[c]["n_refs"]) for c in behavior_cycles]

        # Change points in compressibility
        comp_cp = pelt_change_points(comp_series, penalty=2.0, min_span=3)
        comp_cp_cycles = [behavior_cycles[i] for i in comp_cp] if comp_cp else []
        print(f"Compressibility change points: {comp_cp_cycles}")

        # Change points in reference density
        ref_cp = pelt_change_points(ref_series, penalty=2.0, min_span=3)
        ref_cp_cycles = [behavior_cycles[i] for i in ref_cp] if ref_cp else []
        print(f"Reference density change points: {ref_cp_cycles}")

    # ── 3. PCA ──
    if behavior_cycles and len(behavior_cycles) >= 5:
        # Feature matrix: [token_length, compressibility, n_refs] per cycle
        feat_matrix = []
        for c in behavior_cycles:
            feat_matrix.append([
                mean(cycle_stats[c]["token_lengths"]),
                mean(cycle_stats[c]["compressibilities"]),
                mean(cycle_stats[c]["n_refs"]),
            ])
        pc1, pc2, lam1, lam2, v1, v2 = pca_2d(feat_matrix)
        var_explained = [lam1 / (lam1 + lam2) * 100, lam2 / (lam1 + lam2) * 100]
        print(f"PCA: PC1={var_explained[0]:.1f}%, PC2={var_explained[1]:.1f}%")
    else:
        pc1, pc2, lam1, lam2, v1, v2 = [], [], 0, 0, [], []
        var_explained = [0, 0]

    # ── 4. Graph Topology ──
    gmetrics = graph_metrics(behaviors)
    print(f"Graph: {gmetrics.get('n_nodes', 0)} nodes, {gmetrics.get('n_components', 0)} components")

    # ── 5. Temporal graph evolution ──
    # Split by cycle groups (early 1-10, mid 11-20, late 21+)
    time_windows = {}
    for b in behaviors:
        cyc = b.get("cycle", 0)
        if cyc <= 10:
            w = "early_c1_c10"
        elif cyc <= 20:
            w = "mid_c11_c20"
        else:
            w = "late_c21_plus"
        time_windows.setdefault(w, []).append(b)

    window_metrics = {}
    for w, recs in time_windows.items():
        window_metrics[w] = graph_metrics(recs)

    # ── Generate Report ──
    lines = [
        "# DENSITY-001 涌现式分析报告",
        "",
        f"分析时间：自动生成",
        f"行为记录：{n_beh} 条",
        f"已验证残差：{len(residuals)} 条",
        "",
        "## 1. 变点检测 (PELT)",
        "",
    ]
    if cp_cycles:
        lines.append(f"残差均值变点：**C{cp_cycles}**")
        lines.append(f"解读：在这些轮次附近，信息密度估计偏差发生了结构性变化。")
    else:
        lines.append("未检测到显著变点——残差均值未出现突变。")
    lines.append("")

    if behavior_cycles:
        lines.append(f"压缩率变点（gzip）：C{comp_cp_cycles if comp_cp_cycles else '无'}")
        lines.append(f"引用密度变点：C{ref_cp_cycles if ref_cp_cycles else '无'}")
        lines.append("")

    lines.extend([
        "## 2. PCA 行为模式降维",
        "",
    ])
    if pc1:
        lines.append(f"- PC1（{var_explained[0]:.1f}% 方差）：主特征 = [token_length: {v1[0]:.3f}, compressibility: {v1[1]:.3f}, n_refs: {v1[2]:.3f}]")
        lines.append(f"- PC2（{var_explained[1]:.1f}% 方差）：次特征 = [token_length: {v2[0]:.3f}, compressibility: {v2[1]:.3f}, n_refs: {v2[2]:.3f}]")
        lines.append("")
        lines.append("行为模式漂移评估：")
        # Check if PC1 drifts over time
        if len(pc1) >= 5:
            early_pc1 = mean(pc1[:len(pc1)//3])
            late_pc1 = mean(pc1[2*len(pc1)//3:])
            drift = late_pc1 - early_pc1
            if abs(drift) > std(pc1) * 0.5:
                lines.append(f"  ⚠️ 存在显著漂移：PC1 从 {early_pc1:.3f} → {late_pc1:.3f}（Δ={drift:.3f}）")
            else:
                lines.append(f"  ✅ 漂移不显著：PC1 从 {early_pc1:.3f} → {late_pc1:.3f}（Δ={drift:.3f}）")
        lines.append("")

    lines.extend([
        "## 3. 引用图拓扑演化",
        "",
        "### 全量图",
        f"- 节点：{gmetrics.get('n_nodes', '?')}",
        f"- 边：{gmetrics.get('n_edges', '?')}",
        f"- 连通分量：{gmetrics.get('n_components', '?')}（最大分量 {gmetrics.get('largest_component_pct', '?')}%）",
        f"- 平均入度：{gmetrics.get('avg_indegree', '?')}",
        f"- 平均聚类系数：{gmetrics.get('avg_clustering', '?')}",
        "",
        "### 时间窗口对比",
        "",
    ])

    for wname, wdata in window_metrics.items():
        lines.append(f"**{wname}**：{wdata.get('n_nodes', '?')} 节点, {wdata.get('n_components', '?')} 分量, "
                     f"最大分量 {wdata.get('largest_component_pct', '?')}%, "
                     f"聚类 {wdata.get('avg_clustering', '?')}")

    lines.extend([
        "",
        "### 图演化趋势判断",
        "",
    ])

    # Check fragmentation trend
    comp_trend = []
    for wname in ["early_c1_c10", "mid_c11_c20", "late_c21_plus"]:
        if wname in window_metrics:
            comp_trend.append(window_metrics[wname].get("n_components", 0))
    if len(comp_trend) >= 2 and comp_trend[0] > 0:
        if comp_trend[-1] > comp_trend[0] * 1.5:
            lines.append("⚠️ 连通分量数量上升 → **存在碎片化趋势**")
        else:
            lines.append("✅ 连通分量数量相对稳定 → 引用网络未明显碎片化")

    cluster_trend = []
    for wname in ["early_c1_c10", "mid_c11_c20", "late_c21_plus"]:
        if wname in window_metrics:
            cluster_trend.append(window_metrics[wname].get("avg_clustering", 0))
    if len(cluster_trend) >= 2 and cluster_trend[0] > 0:
        if cluster_trend[-1] < cluster_trend[0] * 0.7:
            lines.append("⚠️ 聚类系数下降 → 信息关联在瓦解（熵增的图论信号）")
        else:
            lines.append("✅ 聚类系数相对稳定 → 信息关联未明显瓦解")

    lines.extend([
        "",
        "## 4. 双轨交叉验证",
        "",
        "先验轨道（残差校正模型）与涌现式发现对照：",
    ])

    # Cross-validation logic
    fragmentation = comp_trend[-1] > comp_trend[0] * 1.5 if len(comp_trend) >= 2 else False
    clustering_drop = cluster_trend[-1] < cluster_trend[0] * 0.7 if len(cluster_trend) >= 2 else False
    residual_drift = abs(mean(cycle_means[-5:]) - mean(cycle_means[:5])) > 0.3 if len(cycle_means) >= 10 else False

    if fragmentation or clustering_drop:
        if residual_drift:
            lines.append("✅ 一致：先验轨道检测到残差趋势变化，涌现式轨道检测到图结构变化 → 可信")
        else:
            lines.append("⚠️ 部分一致：涌现式轨道检测到图结构变化，但先验轨道残差稳定 → 值得深究")
    else:
        if residual_drift:
            lines.append("⚠️ 部分一致：先验轨道检测到残差趋势变化，但涌现式轨道图结构稳定 → 值得深究")
        else:
            lines.append("✅ 一致：两条轨道均未检测到显著模式变化 → 端点星当前处于稳定期")

    lines.extend([
        "",
        "## 5. 假设检验",
        "",
        f"Hδ（残差数列收敛→估计器无偏）：{'✅ 支持' if len(cycle_means) >= 5 and abs(mean(cycle_means[-5:])) < 0.3 else '⏳ 待验证'}",
        f"Hτ（端点星行为模式发生结构性变化）：{'⚠️ 部分支持' if fragmentation or clustering_drop else '✅ 不支持（当前稳定）'}",
        f"Hγ（引用网络拓扑随时间演化）：{'⚠️ 提示碎片化' if fragmentation else '⚠️ 提示聚类瓦解' if clustering_drop else '✅ 未显著变化'}",
    ])

    # Write report
    report = "\n".join(lines)
    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"\nReport written to {OUTPUT}")


if __name__ == "__main__":
    main()
