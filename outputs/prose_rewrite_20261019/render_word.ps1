param([string]$InputDoc,[string]$OutputDir)
$ErrorActionPreference='Stop'
$null=New-Item -ItemType Directory -Path $OutputDir -Force
$before=(Get-FileHash -LiteralPath $InputDoc -Algorithm SHA256).Hash
$wordApp=New-Object -ComObject Word.Application
$wordApp.Visible=$false
$wordApp.DisplayAlerts=0
try {
 $wordDoc=$wordApp.Documents.Open($InputDoc,$false,$true,$false)
 $null=$wordDoc.Fields.Update()
 $wordDoc.Repaginate()
 $record=[ordered]@{path=$InputDoc;pages=$wordDoc.ComputeStatistics(2);math=$wordDoc.OMaths.Count;tables=$wordDoc.Tables.Count;footnotes=$wordDoc.Footnotes.Count;sha256=$before;headings=@()}
 foreach($para in $wordDoc.Paragraphs) {
  $t=$para.Range.Text.Trim()
  if($t -match '^A\.|^表A|^图A|^参考文献') {
   $record.headings+=@{text=$t;page=$para.Range.Information(3);y=$para.Range.Information(6)}
  }
 }
 $wordDoc.ExportAsFixedFormat((Join-Path $OutputDir 'qa.pdf'),17)
 $wordDoc.Close($false)
 $wordDoc=$null
 $record|ConvertTo-Json -Depth 5|Set-Content -LiteralPath (Join-Path $OutputDir 'word_open.json') -Encoding UTF8
 $record|ConvertTo-Json -Depth 5
} finally {
 if($wordDoc){$wordDoc.Close($false)}
 $wordApp.Quit()
 [void][System.Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp)
}
if((Get-FileHash -LiteralPath $InputDoc -Algorithm SHA256).Hash -ne $before){throw 'Read-only rendering modified input'}
