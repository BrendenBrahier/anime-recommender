param([Parameter(ValueFromRemainingArguments=$true)][string[]]$PythonArgs)
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path $PSScriptRoot -Parent
$bundledPython = Join-Path $env:USERPROFILE '.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe'
if (Test-Path (Join-Path $repoRoot '.venv/Scripts/python.exe')) {
    $pythonExe = Join-Path $repoRoot '.venv/Scripts/python.exe'
} elseif (Test-Path $bundledPython) {
    $pythonExe = $bundledPython
} else {
    $pythonExe = 'python'
}
Push-Location $repoRoot
try {
    & $pythonExe @PythonArgs
    if ($LASTEXITCODE -ne 0) { throw "Python exited with code $LASTEXITCODE" }
} finally { Pop-Location }
