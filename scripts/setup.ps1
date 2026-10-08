# T1 one-line setup for Windows. In PowerShell:
#
#   irm https://raw.githubusercontent.com/DIOKai/T1/main/scripts/setup.ps1 | iex
#
# Clones (or updates) T1 into %USERPROFILE%\T1, then runs install_local.py --all --auto-update:
# skills, rules, plugins, MCP servers, Remotion skills, and a SessionStart hook that pulls T1
# each time Claude Code starts so every computer stays in sync.
# Set $env:T1_DIR first to use another folder. Safe to run again.

$ErrorActionPreference = 'Stop'
$T1 = if ($env:T1_DIR) { $env:T1_DIR } else { Join-Path $HOME 'T1' }
$Repo = if ($env:T1_REPO) { $env:T1_REPO } else { "https://github.com/DIOKai/T1" }
$missing = @()

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { $missing += 'Git    -> winget install --id Git.Git -e' }

# Prefer the py launcher; plain "python" may be the Microsoft Store stub.
$py = $null
if (Get-Command py -ErrorAction SilentlyContinue) { $py = @('py', '-3') }
elseif (Get-Command python -ErrorAction SilentlyContinue) {
    try { $v = & python --version 2>&1; if ("$v" -match 'Python 3') { $py = @('python') } } catch {}
}
if (-not $py) { $missing += 'Python -> winget install --id Python.Python.3.12 -e' }

if ($missing.Count -gt 0) {
    Write-Host 'Missing tools. Install them, reopen PowerShell, then run this line again:' -ForegroundColor Yellow
    $missing | ForEach-Object { Write-Host "  $_" }
    return
}
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host 'Note: the claude CLI is not on PATH, so plugins/MCP will be skipped (skills and rules still install).' -ForegroundColor Yellow
    Write-Host '      Install Claude Code CLI, then run this line again to add them.'
}
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host 'Note: Node.js (npx) not found: Remotion skills and the fivem MCP need it -> winget install --id OpenJS.NodeJS.LTS -e' -ForegroundColor Yellow
}

if (Test-Path (Join-Path $T1 '.git')) {
    Write-Host "Updating $T1"
    git -C $T1 pull --ff-only
} else {
    Write-Host "Downloading T1 into $T1"
    git clone $Repo $T1
}

$exe = $py[0]
$pyArgs = @()
if ($py.Count -gt 1) { $pyArgs += $py[1..($py.Count - 1)] }
& $exe @pyArgs (Join-Path $T1 'scripts\install_local.py') --all --auto-update
Write-Host 'Done. Restart Claude Code (desktop app or CLI).' -ForegroundColor Green
