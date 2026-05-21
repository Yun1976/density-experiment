$taskPath = 'C:\Users\user\.openclaw\workspace\tasks\multi-agent-architecture\TASK.md'
$archivePath = 'C:\Users\user\.openclaw\workspace\tasks\multi-agent-architecture\TASK-archive-C24-C27.md'
$lines = Get-Content $taskPath -Encoding UTF8

$headerEnd = -1
$c24Start = -1
$c28Start = -1

for ($i = 0; $i -lt $lines.Count; $i++) {
    if ($lines[$i] -match '^## .*裁决记录') { $headerEnd = $i }
    if ($lines[$i] -match '^### Cycle 24') { $c24Start = $i }
    if ($lines[$i] -match '^### C28') { $c28Start = $i }
}

Write-Host "c24Start=$c24Start c28Start=$c28Start"

$archiveLines = $lines[$c24Start..($c28Start-1)]
Write-Host "Archive lines: $($archiveLines.Count)"

# Build archive with utf8 bom
$archiveContent = @()
$archiveContent += "# TASK Archive: Cycle C24-C27"
$archiveContent += ""
$archiveContent += "Date range: 2026-05-19 06:32 to 2026-05-19 20:21 (C24-C27, 4 rounds)"
$archiveContent += "Key events: Guardian second regression (tri-state model), D047 gene module decay, Guardian saga pulse decay, post-D047 plateau"
$archiveContent += ""
$archiveContent += "---"
$archiveContent += ""
$archiveContent += $archiveLines

$utf8bom = New-Object System.Text.UTF8Encoding $true
[System.IO.File]::WriteAllLines($archivePath, $archiveContent, $utf8bom)
Write-Host "Archive created"

# Build new TASK.md: keep lines before c24Start + add archive ref + lines from c28Start onward
$before = $lines[0..($c24Start-1)]
$after = $lines[$c28Start..($lines.Count-1)]

$archiveRef = '> History C24-C27 archived to [TASK-archive-C24-C27.md](./TASK-archive-C24-C27.md)'

$newContent = @()
$newContent += $before
$newContent += $archiveRef
$newContent += ""
$newContent += $after

[System.IO.File]::WriteAllLines($taskPath, $newContent, $utf8bom)

$newLines = Get-Content $taskPath -Encoding UTF8
Write-Host "New line count: $($newLines.Count)"
