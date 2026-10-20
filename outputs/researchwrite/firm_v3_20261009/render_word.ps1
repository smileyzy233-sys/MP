param([string]$InputDocx,[string]$RenderDirectory)
$ErrorActionPreference='Stop'
$taskInput=(Resolve-Path -LiteralPath $InputDocx).Path
New-Item -ItemType Directory -Force -Path $RenderDirectory | Out-Null
$taskRender=(Resolve-Path -LiteralPath $RenderDirectory).Path
$taskPdf=Join-Path $taskRender 'document.pdf'
$taskWord=$null
$taskDoc=$null
$taskIsolated=$false
try {
  $taskWord=New-Object -ComObject Word.Application
  if ($taskWord.Documents.Count -ne 0) { throw 'Word instance contains other documents; no document was changed.' }
  $taskIsolated=$true
  $taskWord.Visible=$false
  $taskWord.DisplayAlerts=0
  $taskWord.AutomationSecurity=3
  $taskDoc=$taskWord.Documents.Open($taskInput,$false,$true,$false)
  $taskDoc.Repaginate()
  $taskPages=$taskDoc.ComputeStatistics(2)
  $taskDoc.ExportAsFixedFormat($taskPdf,17)
  @{input=$taskInput;pdf=$taskPdf;pages=$taskPages;engine='Microsoft Word isolated read-only PDF export';footnotes=$taskDoc.Footnotes.Count;tables=$taskDoc.Tables.Count;math=$taskDoc.OMaths.Count} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $taskRender 'render_meta.json') -Encoding utf8
  Write-Output "Rendered $taskPages pages to $taskPdf"
} finally {
  if ($null -ne $taskDoc) { $taskDoc.Close(0);[void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskDoc) }
  if ($taskIsolated -and $null -ne $taskWord) { $taskWord.Quit(0) }
  if ($null -ne $taskWord) { [void][Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskWord) }
  [GC]::Collect()
  [GC]::WaitForPendingFinalizers()
}
