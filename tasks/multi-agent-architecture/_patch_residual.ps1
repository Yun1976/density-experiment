$f = Get-Content 'tasks/multi-agent-architecture/residual-series.jsonl' -Encoding UTF8
for ($i = 0; $i -lt $f.Length; $i++) {
    if ($f[$i] -like '*b28_A_protocol*') {
        $f[$i] = $f[$i] -replace '"u_observed":null', '"u_observed":1.0'
        $f[$i] = $f[$i] -replace '"u_source":null', '"u_source":"direct_citation_C29_oscillation_contrast_evidence"'
        $f[$i] = $f[$i] -replace '"u_round":null', '"u_round":29'
        $f[$i] = $f[$i] -replace '"residual":null', '"residual":0.065'
        $f[$i] = $f[$i] -replace '"pending"', '"validated"'
    }
    if ($f[$i] -like '*b28_B_version*') {
        $f[$i] = $f[$i] -replace '"u_observed":null', '"u_observed":1.0'
        $f[$i] = $f[$i] -replace '"u_source":null', '"u_source":"direct_citation_C29_oscillation_strengthens_causal_chain"'
        $f[$i] = $f[$i] -replace '"u_round":null', '"u_round":29'
        $f[$i] = $f[$i] -replace '"residual":null', '"residual":-0.350'
        $f[$i] = $f[$i] -replace '"pending"', '"validated"'
    }
    if ($f[$i] -like '*b28_C_snapshot*') {
        $f[$i] = $f[$i] -replace '"u_observed":null', '"u_observed":0.0'
        $f[$i] = $f[$i] -replace '"u_source":null', '"u_source":"not_cited_C29_format_change_irrelevant"'
        $f[$i] = $f[$i] -replace '"u_round":null', '"u_round":29'
        $f[$i] = $f[$i] -replace '"residual":null', '"residual":-0.010'
        $f[$i] = $f[$i] -replace '"pending"', '"validated"'
    }
}
$f | Out-File 'tasks/multi-agent-architecture/residual-series.jsonl' -Encoding UTF8
Write-Output "Done"