param([string]$InputDocx,[string]$OutputDir)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
$pdfPath=Join-Path $OutputDir 'document.pdf'
$wordApp=$null; $wordDocument=$null; $isolated=$false
try {
    $wordApp=New-Object -ComObject Word.Application
    if($wordApp.Documents.Count -ne 0){throw 'Existing documents in Word instance; stop without touching them'}
    $isolated=$true
    $wordApp.Visible=$false; $wordApp.DisplayAlerts=0; $wordApp.AutomationSecurity=3
    $wordDocument=$wordApp.Documents.Open($InputDocx,$false,$true,$false)
    $wordDocument.Repaginate()
    $pageCount=$wordDocument.ComputeStatistics(2)
    $wordDocument.ExportAsFixedFormat($pdfPath,17)
    @{input=$InputDocx;pdf=$pdfPath;pages=$pageCount;engine='Isolated Word read-only export'} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $OutputDir 'render_meta.json') -Encoding utf8
    Write-Output "PAGES=$pageCount"
} finally {
    if($null -ne $wordDocument){$wordDocument.Close(0);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordDocument)}
    if($isolated -and $null -ne $wordApp){$wordApp.Quit(0)}
    if($null -ne $wordApp){[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($wordApp)}
    [GC]::Collect();[GC]::WaitForPendingFinalizers()
}
