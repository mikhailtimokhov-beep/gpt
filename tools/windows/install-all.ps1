# install-all.ps1
# One-shot setup of everything configured in this repository on a Windows PC:
#   1. Claude tools: Git, Node.js, Claude Code, uv, Claude-Mem, claude-code-setup,
#      Task Observer, Headroom, OmniRoute (install-claude-tools.ps1)
#   2. Economy rules + economy-scout agent        -> %USERPROFILE%\.claude
#   3. 32 agents for design, 3D, marketing, social, business (install-agents.ps1)
#   4. Graphify CLI and skill
#   5. All skills from this repository             -> %USERPROFILE%\.claude\skills
#   6. Free plugins: Omni Captions, Claude Video Vision
#   7. AI Memory (akitaonrails/ai-memory): long-term memory shared across agents
# Safe to run again: finished steps are skipped or refreshed.
#
# Run in PowerShell as Administrator (one line):
#   Set-ExecutionPolicy Bypass -Scope Process -Force; [Net.ServicePointManager]::SecurityProtocol = 'Tls12'; irm https://raw.githubusercontent.com/mikhailtimokhov-beep/gpt/main/tools/windows/install-all.ps1 | iex
#
# Messages are ASCII on purpose: Windows PowerShell 5.1 mangles UTF-8 piped through iex.

function Install-All {
    $ErrorActionPreference = 'Continue'
    $ProgressPreference = 'SilentlyContinue'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    $raw = 'https://raw.githubusercontent.com/mikhailtimokhov-beep/gpt/main'
    $claudeDir = Join-Path $env:USERPROFILE '.claude'
    $results = [ordered]@{}

    function Step($text) { Write-Host ""; Write-Host "==> $text" -ForegroundColor Cyan }
    function Ok($text) { Write-Host "    OK  $text" -ForegroundColor Green }
    function Warn($text) { Write-Host "    !!  $text" -ForegroundColor Yellow }
    function Test-Command($name) { [bool](Get-Command $name -ErrorAction SilentlyContinue) }
    function Update-SessionPath {
        $machine = [Environment]::GetEnvironmentVariable('Path', 'Machine')
        $user = [Environment]::GetEnvironmentVariable('Path', 'User')
        $extra = @((Join-Path $env:USERPROFILE '.local\bin'), (Join-Path $env:APPDATA 'npm'),
                   'C:\Program Files\Git\cmd', 'C:\Program Files\nodejs')
        $env:Path = (@($machine, $user) + $extra | Where-Object { $_ }) -join ';'
    }

    # 1 -------------------------------------------------------------- tools
    Step '1/7 Claude tools (Git, Node.js, Claude Code, plugins, Headroom, OmniRoute)'
    try {
        Invoke-RestMethod "$raw/tools/windows/install-claude-tools.ps1" -UseBasicParsing | Invoke-Expression
        $results['Claude tools'] = 'done (see the summary above)'
    } catch { Warn "tools step failed: $_"; $results['Claude tools'] = 'FAILED' }
    Update-SessionPath

    # 2 -------------------------------------------------------------- economy
    Step '2/7 Economy rules and economy-scout agent'
    try {
        foreach ($f in 'rules/economy.md', 'agents/economy-scout.md') {
            $dest = Join-Path $claudeDir ($f -replace '/', '\')
            New-Item -ItemType Directory -Force -Path (Split-Path $dest) | Out-Null
            Invoke-WebRequest "$raw/.claude/$f" -OutFile $dest -UseBasicParsing
        }
        Ok 'economy.md and economy-scout.md installed'
        $results['Economy rules'] = 'installed'
    } catch { Warn "economy step failed: $_"; $results['Economy rules'] = 'FAILED' }

    # 3 -------------------------------------------------------------- agents
    Step '3/7 Agents (design, 3D, marketing, social, business)'
    try {
        Invoke-RestMethod "$raw/tools/agents/install-agents.ps1" -UseBasicParsing | Invoke-Expression
        $n = @(Get-ChildItem (Join-Path $claudeDir 'agents') -Filter *.md -ErrorAction SilentlyContinue).Count
        $results['Agents'] = "$n files in .claude\agents"
    } catch { Warn "agents step failed: $_"; $results['Agents'] = 'FAILED' }

    # 4 -------------------------------------------------------------- graphify
    Step '4/7 Graphify (code knowledge graph)'
    if (-not (Test-Command 'graphify')) {
        if (Test-Command 'uv') { & uv tool install graphifyy 2>&1 | Out-Host }
        elseif (Test-Command 'py') { & py -3 -m pip install --user graphifyy 2>&1 | Out-Host }
        Update-SessionPath
    }
    if (Test-Command 'graphify') {
        & graphify install --platform claude 2>&1 | Select-Object -Last 3 | Out-Host
        $results['Graphify'] = (& graphify --version 2>&1 | Out-String).Trim()
    } else { Warn 'graphify not found after install'; $results['Graphify'] = 'MISSING' }

    # 5 -------------------------------------------------------------- skills
    Step '5/7 Skills from the repository (design, animation, 3D, video)'
    if (Test-Command 'git') {
        $repo = Join-Path $env:USERPROFILE 'gpt'
        if (Test-Path (Join-Path $repo '.git')) {
            & git -C $repo pull --quiet --ff-only origin main 2>&1 | Out-Host
        } else {
            & git clone --quiet --depth 1 https://github.com/mikhailtimokhov-beep/gpt.git $repo 2>&1 | Out-Host
        }
        $src = Join-Path $repo '.claude\skills'
        if (Test-Path $src) {
            $dst = Join-Path $claudeDir 'skills'
            New-Item -ItemType Directory -Force -Path $dst | Out-Null
            Get-ChildItem $src -Directory | ForEach-Object {
                Copy-Item $_.FullName -Destination $dst -Recurse -Force
            }
            $n = @(Get-ChildItem $src -Directory).Count
            Ok "$n skill folders copied to $dst"
            $results['Skills'] = "$n folders"
        } else { Warn 'repository has no .claude\skills'; $results['Skills'] = 'FAILED' }
    } else { Warn 'git not found, skipping skills'; $results['Skills'] = 'SKIPPED (no git)' }

    # 6 -------------------------------------------------------------- plugins
    Step '6/7 Free plugins: Omni Captions, Claude Video Vision'
    if (Test-Command 'claude') {
        foreach ($p in @(@('lattifai/omni-captions-skills', 'omnicaptions@omni-captions-skills'),
                         @('jordanrendric/claude-video-vision', 'claude-video-vision@claude-video-vision'))) {
            & claude plugin marketplace add $p[0] 2>&1 | Out-Null
            & claude plugin install $p[1] --scope user -y 2>&1 | Out-Host
        }
        $list = (& claude plugin list 2>&1 | Out-String)
        $results['Plugins'] = (@('omnicaptions', 'claude-video-vision') | ForEach-Object {
            if ($list -match $_) { "$_ ok" } else { "$_ MISSING" } }) -join ', '
    } else { Warn 'claude not found, skipping plugins'; $results['Plugins'] = 'SKIPPED (no claude)' }

    # 7 -------------------------------------------------------------- ai-memory
    Step '7/7 AI Memory (memory between sessions and agents)'
    if (-not (Test-Command 'ai-memory')) {
        try {
            # Official installer: checks the release zip against its SHA-256, no admin needed.
            Invoke-RestMethod 'https://github.com/akitaonrails/ai-memory/releases/latest/download/install.ps1' -UseBasicParsing | Invoke-Expression
        } catch { Warn "ai-memory install failed: $_" }
        $env:Path += ';' + (Join-Path $env:LOCALAPPDATA 'Programs\ai-memory')
    }
    if (Test-Command 'ai-memory') {
        & ai-memory setup --yes --agent claude-code 2>&1 | Select-Object -Last 5 | Out-Host
        $results['AI Memory'] = (& ai-memory --version 2>&1 | Out-String).Trim()
    } else { Warn 'ai-memory not found after install'; $results['AI Memory'] = 'MISSING' }

    # ---------------------------------------------------------------- summary
    Step 'Summary'
    foreach ($k in $results.Keys) {
        $v = $results[$k]
        $color = if ($v -match 'FAILED|MISSING|SKIPPED') { 'Red' } else { 'Green' }
        Write-Host ("    {0,-16} {1}" -f $k, $v) -ForegroundColor $color
    }
    Write-Host ""
    Write-Host 'Close this window, open a new PowerShell and restart Claude so everything loads.'
    Write-Host 'Token savings: start Claude with   headroom wrap claude'
}

Install-All
