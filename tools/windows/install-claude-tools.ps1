# install-claude-tools.ps1
# Sets up Claude Code on a Windows server and installs:
#   Claude-Mem, OmniRoute, claude-code-setup, Task Observer, Headroom.
# Safe to run again: steps that are already done are skipped.
#
# Run in PowerShell as Administrator (one line):
#   Set-ExecutionPolicy Bypass -Scope Process -Force; [Net.ServicePointManager]::SecurityProtocol = 'Tls12'; irm https://raw.githubusercontent.com/mikhailtimokhov-beep/gpt/claude/wizardly-knuth-lt4dww/tools/windows/install-claude-tools.ps1 | iex
#
# Messages are ASCII on purpose: Windows PowerShell 5.1 mangles UTF-8 piped through iex.

function Install-ClaudeTools {
    $ErrorActionPreference = 'Continue'
    $ProgressPreference = 'SilentlyContinue'   # Invoke-WebRequest is very slow with the progress bar on
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    $log = Join-Path $env:TEMP ("install-claude-tools-{0:yyyyMMdd-HHmmss}.log" -f (Get-Date))
    Start-Transcript -Path $log -Force | Out-Null
    $results = [ordered]@{}

    function Step($text) { Write-Host ""; Write-Host "==> $text" -ForegroundColor Cyan }
    function Ok($text) { Write-Host "    OK  $text" -ForegroundColor Green }
    function Warn($text) { Write-Host "    !!  $text" -ForegroundColor Yellow }

    function Update-SessionPath {
        $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
        $user = [Environment]::GetEnvironmentVariable('Path', 'User')
        $extra = @(
            (Join-Path $env:USERPROFILE '.local\bin'),
            (Join-Path $env:APPDATA 'npm'),
            (Join-Path $env:USERPROFILE '.bun\bin'),
            'C:\Program Files\Git\cmd',
            'C:\Program Files\nodejs'
        )
        $env:Path = (@($machine, $user) + $extra | Where-Object { $_ }) -join ';'
    }

    function Add-UserPath($dir) {
        $user = [Environment]::GetEnvironmentVariable('Path', 'User')
        $parts = @($user -split ';' | Where-Object { $_ })
        if ($parts -notcontains $dir) {
            [Environment]::SetEnvironmentVariable('Path', (($parts + $dir) -join ';'), 'User')
        }
    }

    function Test-Command($name) { [bool](Get-Command $name -ErrorAction SilentlyContinue) }

    function Test-Winget { Test-Command 'winget' }

    function Invoke-Download($url, $file) {
        $path = Join-Path $env:TEMP $file
        Invoke-WebRequest -Uri $url -OutFile $path -UseBasicParsing
        return $path
    }

    $isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) { Warn 'Not running as Administrator: Git/Node installs may fail. Re-run PowerShell "As Administrator".' }

    Update-SessionPath

    # ---------------------------------------------------------------- Git
    Step 'Git for Windows (Claude Code on Windows needs Git Bash)'
    if (Test-Command 'git') {
        Ok (git --version)
    } else {
        try {
            if (Test-Winget) {
                winget install --id Git.Git -e --silent --accept-package-agreements --accept-source-agreements
            } else {
                $rel = Invoke-RestMethod 'https://api.github.com/repos/git-for-windows/git/releases/latest' -UseBasicParsing
                $asset = $rel.assets | Where-Object { $_.name -match '^Git-[\d\.]+-64-bit\.exe$' } | Select-Object -First 1
                $exe = Invoke-Download $asset.browser_download_url 'git-setup.exe'
                Start-Process $exe -ArgumentList '/VERYSILENT', '/NORESTART', '/NOCANCEL', '/SP-', '/SUPPRESSMSGBOXES' -Wait
            }
            Update-SessionPath
            if (Test-Command 'git') { Ok (git --version) } else { Warn 'Git did not install' }
        } catch { Warn "Git install failed: $_" }
    }
    $results['Git'] = if (Test-Command 'git') { (git --version) } else { 'MISSING' }

    # ---------------------------------------------------------------- Node.js
    Step 'Node.js LTS (needed by OmniRoute, Claude-Mem, MCP servers)'
    $nodeOk = $false
    if (Test-Command 'node') {
        # OmniRoute needs Node >= 22.22.2 (or 24+)
        $ver = [version]((node -v).TrimStart('v'))
        $nodeOk = ($ver.Major -ge 24) -or ($ver -ge [version]'22.22.2' -and $ver.Major -eq 22)
        if (-not $nodeOk) { Warn "Node $(node -v) is too old, need 22.22.2+ or 24+" }
    }
    if (-not $nodeOk) {
        try {
            if (Test-Winget) {
                winget install --id OpenJS.NodeJS.LTS -e --silent --accept-package-agreements --accept-source-agreements
            } else {
                $index = Invoke-RestMethod 'https://nodejs.org/dist/index.json' -UseBasicParsing
                $lts = $index | Where-Object { $_.lts -and $_.files -contains 'win-x64-msi' } | Select-Object -First 1
                $msi = Invoke-Download "https://nodejs.org/dist/$($lts.version)/node-$($lts.version)-x64.msi" 'node-lts.msi'
                Start-Process msiexec.exe -ArgumentList '/i', "`"$msi`"", '/qn', '/norestart' -Wait
            }
            Update-SessionPath
        } catch { Warn "Node.js install failed: $_" }
    }
    $results['Node.js'] = if (Test-Command 'node') { (node -v) } else { 'MISSING' }
    if (Test-Command 'node') { Ok "node $(node -v), npm $(npm.cmd -v)" }

    # ---------------------------------------------------------------- Claude Code
    Step 'Claude Code CLI'
    if (-not (Test-Command 'claude')) {
        try {
            Invoke-RestMethod 'https://claude.ai/install.ps1' -UseBasicParsing | Invoke-Expression
        } catch { Warn "Claude Code install failed: $_" }
        Add-UserPath (Join-Path $env:USERPROFILE '.local\bin')
        Update-SessionPath
    }
    $results['Claude Code'] = if (Test-Command 'claude') { (claude --version) } else { 'MISSING' }
    if (Test-Command 'claude') { Ok $results['Claude Code'] } else { Warn 'claude command not found' }

    # ---------------------------------------------------------------- uv (Python runner for Headroom)
    Step 'uv (Python tool manager, brings its own Python for Headroom)'
    if (-not (Test-Command 'uv')) {
        try {
            Invoke-RestMethod 'https://astral.sh/uv/install.ps1' -UseBasicParsing | Invoke-Expression
        } catch { Warn "uv install failed: $_" }
        Add-UserPath (Join-Path $env:USERPROFILE '.local\bin')
        Update-SessionPath
    }
    if (Test-Command 'uv') { Ok (uv --version) }

    # ---------------------------------------------------------------- Plugins
    function Install-Plugin($marketplaceRepo, $pluginId) {
        & claude plugin marketplace add $marketplaceRepo 2>&1 | Out-Host
        & claude plugin install $pluginId --scope user -y 2>&1 | Out-Host
        $installed = (& claude plugin list 2>&1 | Out-String) -match [regex]::Escape($pluginId.Split('@')[0])
        if ($installed) { Ok "$pluginId installed" } else { Warn "$pluginId not found in 'claude plugin list'" }
        return $installed
    }

    if (Test-Command 'claude') {
        Step 'claude-code-setup (official Anthropic plugin)'
        $results['claude-code-setup'] = Install-Plugin 'anthropics/claude-plugins-official' 'claude-code-setup@claude-plugins-official'

        Step 'Claude-Mem (memory between sessions)'
        $results['Claude-Mem'] = Install-Plugin 'thedotmack/claude-mem' 'claude-mem@thedotmack'

        Step 'Task Observer (skill that proposes improvements to your skills)'
        $results['Task Observer'] = Install-Plugin 'rebelytics/one-skill-to-rule-them-all' 'task-observer@one-skill-to-rule-them-all'

        # Task Observer only works reliably with an activation line in CLAUDE.md.
        $claudeDir = Join-Path $env:USERPROFILE '.claude'
        $workspace = Join-Path $claudeDir 'task-observer'
        New-Item -ItemType Directory -Force -Path $workspace | Out-Null
        $claudeMd = Join-Path $claudeDir 'CLAUDE.md'
        $marker = '<!-- task-observer activation -->'
        $existing = if (Test-Path $claudeMd) { Get-Content $claudeMd -Raw } else { '' }
        if ($existing -notmatch [regex]::Escape($marker)) {
            $block = @"

$marker
## Task Observer
At the start of every session that will use tools, invoke the task-observer skill
and run its Session Start Protocol before the first tool call.
The task-observer workspace is: $($workspace -replace '\\', '/')
After each task, list the observation records written this session in one line
(ids and titles, or "none logged and why").
"@
            [IO.File]::AppendAllText($claudeMd, $block, (New-Object Text.UTF8Encoding $false))
            Ok "activation added to $claudeMd"
        } else {
            Ok 'activation already in CLAUDE.md'
        }
    } else {
        Warn 'Skipping plugins: Claude Code is not installed'
    }

    # ---------------------------------------------------------------- Headroom
    Step 'Headroom (compresses context, saves tokens)'
    if (-not (Test-Command 'headroom') -and (Test-Command 'uv')) {
        & uv tool install --python 3.13 'headroom-ai[all]' 2>&1 | Out-Host
        if ($LASTEXITCODE -ne 0) {
            Warn 'Full install failed, trying the lighter [proxy] variant'
            & uv tool install --python 3.13 'headroom-ai[proxy]' 2>&1 | Out-Host
        }
        Update-SessionPath
    }
    $results['Headroom'] = if (Test-Command 'headroom') { (headroom --version 2>&1 | Out-String).Trim() } else { 'MISSING' }
    if (Test-Command 'headroom') { Ok $results['Headroom'] } else { Warn 'headroom command not found' }

    # ---------------------------------------------------------------- OmniRoute
    Step 'OmniRoute (local AI gateway, dashboard on http://localhost:20128)'
    if (-not (Test-Command 'omniroute') -and (Test-Command 'node')) {
        # npm 11+ blocks install scripts unless allowed; older npm ignores the flag.
        & npm.cmd install -g omniroute --allow-scripts=omniroute,keytar,onnxruntime-node,@parcel/watcher,@swc/core,protobufjs,esbuild 2>&1 | Out-Host
        Update-SessionPath
    }
    $results['OmniRoute'] = if (Test-Command 'omniroute') {
        $v = (& npm.cmd ls -g omniroute --depth=0 2>&1 | Out-String) -replace '(?s).*omniroute@([\w\.\-]+).*', '$1'
        "omniroute $($v.Trim())"
    } else { 'MISSING' }
    if (Test-Command 'omniroute') { Ok $results['OmniRoute'] } else { Warn 'omniroute command not found' }

    # ---------------------------------------------------------------- Report
    Step 'Summary'
    foreach ($k in $results.Keys) {
        $v = $results[$k]
        $good = ($v -is [bool] -and $v) -or ($v -is [string] -and $v -ne 'MISSING')
        $shown = if ($v -is [bool]) { if ($v) { 'installed' } else { 'NOT installed' } } else { $v }
        $color = if ($good) { 'Green' } else { 'Red' }
        Write-Host ("    {0,-18} {1}" -f $k, $shown) -ForegroundColor $color
    }
    if (Test-Command 'claude') {
        Write-Host ""
        Write-Host '    claude plugin list:'
        & claude plugin list 2>&1 | Out-Host
    }

    Write-Host ""
    Write-Host 'Next steps:' -ForegroundColor Cyan
    Write-Host '  1. Close this window and open a NEW PowerShell, so PATH updates apply.'
    Write-Host '  2. Restart Claude (desktop app or CLI) so the plugins load.'
    Write-Host '  3. Headroom (token savings): start Claude through it with   headroom wrap claude'
    Write-Host '     Undo with   headroom unwrap claude'
    Write-Host '  4. OmniRoute (optional gateway): run   omniroute   then open http://localhost:20128'
    Write-Host '     Claude keeps talking to Anthropic directly unless you point it at OmniRoute yourself.'
    Write-Host "Log: $log"

    Stop-Transcript | Out-Null
}

Install-ClaudeTools
