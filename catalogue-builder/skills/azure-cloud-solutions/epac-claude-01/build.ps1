<#
.SYNOPSIS
  Packages the epac skill into dist/epac.skill (a zip with SKILL.md at the root).
  Only the skill files are included — the dev harness (evals, build scripts, CI,
  CONTRIBUTING, README, .git) is deliberately excluded so it never ships to users.

.EXAMPLE
  pwsh ./build.ps1
  pwsh ./build.ps1 -Version 1.2.0
#>
param(
  [string]$Version = ""
)

$ErrorActionPreference = "Stop"
$SkillName = "epac"
$Root      = $PSScriptRoot
$Dist      = Join-Path $Root "dist"
$Staging   = Join-Path ([System.IO.Path]::GetTempPath()) ("epac-skill-build-" + [Guid]::NewGuid())

# Files/folders that make up the SKILL itself (everything else is dev-only).
$Include = @("SKILL.md", "references")

Write-Host "Building $SkillName skill..." -ForegroundColor Cyan

# Fresh staging dir
New-Item -ItemType Directory -Force -Path $Staging | Out-Null
foreach ($item in $Include) {
  $src = Join-Path $Root $item
  if (-not (Test-Path $src)) { throw "Required skill item not found: $item" }
  Copy-Item -Path $src -Destination $Staging -Recurse -Force
}

# Validate SKILL.md has frontmatter name matching the skill
$skillMd = Get-Content (Join-Path $Staging "SKILL.md") -Raw
if ($skillMd -notmatch "(?ms)^---\s.*?\bname:\s*$SkillName\b.*?^---") {
  throw "SKILL.md frontmatter must declare 'name: $SkillName'"
}

# Package
New-Item -ItemType Directory -Force -Path $Dist | Out-Null
$Zip   = Join-Path $Dist "$SkillName.zip"
$Skill = Join-Path $Dist "$SkillName.skill"
if (Test-Path $Zip)   { Remove-Item $Zip -Force }
if (Test-Path $Skill) { Remove-Item $Skill -Force }

Compress-Archive -Path (Join-Path $Staging "*") -DestinationPath $Zip -Force
Move-Item -Path $Zip -Destination $Skill -Force
Remove-Item -Recurse -Force $Staging

if ($Version) { Write-Host "Version: $Version (remember to bump it where you track it)" -ForegroundColor Yellow }
Write-Host "Built: $Skill" -ForegroundColor Green
