$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSCommandPath
$meta = Get-Content -LiteralPath (Join-Path $taskRoot 'build_meta.json') -Raw -Encoding utf8 | ConvertFrom-Json
$renderDir = Join-Path $taskRoot 'qa_render'
New-Item -ItemType Directory -Path $renderDir -Force | Out-Null
$pdfPath = Join-Path $renderDir 'proposal_final.pdf'
$wordApp = $null
$wordDocument = $null
$createdIsolated = $false
try {
    $wordApp = New-Object -ComObject Word.Application
    if ($wordApp.Documents.Count -ne 0) { throw 'Word instance already has documents; stop without touching them.' }
    $createdIsolated = $true
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    $wordDocument = $wordApp.Documents.Open([string]$meta.output_path, $false, $true, $false)
    $wordDocument.Repaginate()
    $pages = $wordDocument.ComputeStatistics(2)
    $wordDocument.ExportAsFixedFormat($pdfPath,17)
    @{pdf_path=$pdfPath; pages=$pages; engine='Isolated Microsoft Word read-only PDF export'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRoot 'render_meta.json') -Encoding utf8
    Write-Output "WORD_PAGES=$pages"
    Write-Output "PDF_PATH=$pdfPath"
} finally {
    if ($null -ne $wordDocument) { $wordDocument.Close(0); [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordDocument) }
    if ($createdIsolated -and $null -ne $wordApp) { $wordApp.Quit(0) }
    if ($null -ne $wordApp) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordApp) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
