# install-agents.ps1
# Installs the 32 agents from tools/agents/my-agents.txt into %USERPROFILE%\.claude\agents.
# Files come from msitarzewski/agency-agents at the commit that was reviewed for
# safety, and each download is checked against its SHA-256 before it is saved.
#
# Run in PowerShell (one line):
#   irm https://raw.githubusercontent.com/mikhailtimokhov-beep/gpt/main/tools/agents/install-agents.ps1 | iex
#
# Messages are ASCII on purpose: Windows PowerShell 5.1 mangles UTF-8 piped through iex.

function Install-Agents {
    $ErrorActionPreference = 'Stop'
    $ProgressPreference = 'SilentlyContinue'
    [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

    $commit = 'b37b5bb33b78f2c1d6567d98e25ca818e3259219'
    $base = "https://raw.githubusercontent.com/msitarzewski/agency-agents/$commit"
    $dest = Join-Path $env:USERPROFILE '.claude\agents'
    New-Item -ItemType Directory -Force -Path $dest | Out-Null

    $agents = @(
    @('design/design-brand-guardian.md', 'd1d5c78af85d4d35be94b93d5c011d17e3cf5dcb69b2037a3ebf3059803b893e'),
    @('design/design-image-prompt-engineer.md', '63a564d01dc5812c494cd8aa034ce1217031d8fe8b3eca1323316879769ff13f'),
    @('design/design-persona-walkthrough.md', '8def8c73df7f79a61704e7353b85b915afa31c4a9fa1100fbb9220c50d6a1c55'),
    @('design/design-ui-designer.md', '4dc51255ffcb47e2bf4289a7d49a7cc224238af759f9e6e3c56771c698575d6d'),
    @('design/design-ui-finish-gate-reviewer.md', 'cc2cc803782a791797b63530bfd46ee676148f05bc1db7c614c8860f9798bc86'),
    @('design/design-ux-architect.md', '7d373da3fd204db3c830f28e03cdf85bcacd3858e38fbdad58489953f811c296'),
    @('design/design-ux-researcher.md', '25f59c4333df2d0f1170ff7a1b11ea8415fd3d0ef80c3e0985209aeb4018680f'),
    @('design/design-visual-storyteller.md', 'f4950c9d65b5d105ec48ebce4b7621154e3bf89871dbbf07af245476930eb4dd'),
    @('design/design-whimsy-injector.md', 'b1cc9abd37723ff12b508717e4f7f9621aafd8c20014894d93a8d6e2bc5657a4'),
    @('engineering/engineering-frontend-developer.md', '71eeb60cbeedd94b41b2e5852d8986c909e8d150c324b4bb99e3b184ae202094'),
    @('game-development/blender/blender-addon-engineer.md', 'e9a778fb9a78c31b6c2e2d8a0912cccd32652c1627be4794ae70f5ceb0021076'),
    @('game-development/technical-artist.md', '9b7e75b629b7b1c87a0bc37e6abaec91e0ad7ae02e8a091c5a876e2bea817742'),
    @('marketing/marketing-ai-citation-strategist.md', '1d23c94aced61beb0e7a3151ad4c14ccb8205a95e48d4bc6c0fda6739c2e356d'),
    @('marketing/marketing-content-creator.md', '26ddce44f057068a3935c13d53becd3c57385fb47fcdcfdd891b80269070b3d5'),
    @('marketing/marketing-email-strategist.md', '605c98066a4a1b5538d76476a11316247316ecb8da88beda68a21f2c8918f19b'),
    @('marketing/marketing-growth-hacker.md', '6938b4fccaf4447e8c4b8fd071ce383a484cd3fb72583d87ac9835fa9741a7c7'),
    @('marketing/marketing-instagram-curator.md', 'bab95910975a95409eca10e28c44cf762cd46f9d8b7d551bcb347ef0f39e68fd'),
    @('marketing/marketing-pr-communications-manager.md', 'e255a9ebf00a0db0dc12e72fe2a647195ceacf3c0e63f38788e077966d69b800'),
    @('marketing/marketing-seo-specialist.md', 'cfa35eb3626230e1bc96ab3d434b42005b092fd4de8f517efe4a4b3f8fca60d0'),
    @('marketing/marketing-short-video-editing-coach.md', '4634520ab5e84b26bb6658f4f8c0f737ed7dd0b5c631b9211482a4cf4037ccbf'),
    @('marketing/marketing-social-media-strategist.md', '7c698a9280872666b2726b7ca305c6d4890fcb95a098c7c316beb9bf5fdb4274'),
    @('marketing/marketing-tiktok-strategist.md', '980ca09138f63ec2d934e111af4fa59d76a483bb23220a5f862aa4e9f0c9124a'),
    @('marketing/marketing-video-optimization-specialist.md', '9cf82969be8898c96192617becf5e38e8de6b79650c362d840c53d2c10f2e8b9'),
    @('paid-media/paid-media-creative-strategist.md', 'a24a303228178eb23d514fee63831cf7e1a3d7e5276c54ce5b58dce566700c41'),
    @('paid-media/paid-media-paid-social-strategist.md', 'c8004c7f640dfef9c7c698f69c4c3712d063df06c8d391c809df92ba420af3db'),
    @('product/product-trend-researcher.md', '69c8e54a9413ba411195e8d5274ee3cd88fa8cda18486db70c0f19ce374550a2'),
    @('sales/sales-offer-lead-gen-strategist.md', '75a12987fb2a205ac029c2ebf43d1ae1a1502d1707ab4921923928489ff3778c'),
    @('sales/sales-outbound-strategist.md', '4f6c8abf9c936fbe5f4b66fc8044096e3dd5199f8f8ae9d0309ad92bc0653174'),
    @('sales/sales-proposal-strategist.md', '84c42e0ae7e11e6b239b7f921bdb0c33398102f94998c2eaa41114a3a46dc4c9'),
    @('spatial-computing/xr-immersive-developer.md', 'a9aa13187bfb774f3eb734ae9869ef249ec3290674f0bb3c1368b69bfa25a2b0'),
    @('specialized/business-strategist.md', '9314906805d8dee81c3e2d10cb93513a391731d9fceb2e4c936257005a144b92'),
    @('specialized/specialized-pricing-analyst.md', 'fb8a63681615666bb2efe45b7fd2d9ad8a072ab9066efae6b61d454a58039f85')
    )

    $ok = 0; $failed = @()
    foreach ($a in $agents) {
        $path = $a[0]; $hash = $a[1]
        $name = Split-Path $path -Leaf
        $tmp = Join-Path $env:TEMP $name
        try {
            Invoke-WebRequest -Uri "$base/$path" -OutFile $tmp -UseBasicParsing
            $got = (Get-FileHash -Algorithm SHA256 $tmp).Hash.ToLower()
            if ($got -ne $hash) { throw "checksum mismatch" }
            Move-Item -Force $tmp (Join-Path $dest $name)
            $ok++
        } catch {
            Remove-Item -ErrorAction SilentlyContinue $tmp
            $failed += "$name ($_)"
        }
    }

    Write-Host ""
    Write-Host "Installed $ok of $($agents.Count) agents into $dest" -ForegroundColor Green
    if ($failed.Count) {
        Write-Host "Failed:" -ForegroundColor Red
        $failed | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
    }
    Write-Host "Restart Claude so it loads the agents."
}

Install-Agents
