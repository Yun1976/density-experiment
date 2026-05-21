$resp = Invoke-WebRequest -Uri 'http://192.168.1.5:8090/03-ops/logs/snapshot-20260520-084300.json' -UseBasicParsing
Write-Host $resp.Content
