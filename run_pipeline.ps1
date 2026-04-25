param(
    [Parameter(Mandatory = $true)]
    [string]$DocxPath,

    [Parameter(Mandatory = $false)]
    [string]$TemplatePath,

    [Parameter(Mandatory = $false)]
    [int]$MaxRounds = 5,

    [Parameter(Mandatory = $false)]
    [switch]$NonInteractive
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $DocxPath)) {
    throw "文件不存在: $DocxPath"
}

$workspace = Split-Path -Parent $MyInvocation.MyCommand.Path
$docxFull = (Resolve-Path -LiteralPath $DocxPath).Path
$baseName = [System.IO.Path]::GetFileNameWithoutExtension($docxFull)
$dir = Split-Path -Parent $docxFull

$mdPath = Join-Path $dir ($baseName + ".md")
$corePath = Join-Path $dir ($baseName + "测试用例-core.md")
$fullPath = Join-Path $dir ($baseName + "测试用例-full.md")
$auditPath = Join-Path $dir ($baseName + "测试用例-audit.md")
$reportPath = Join-Path $dir ($baseName + "测试用例-迭代报告.md")
$validatorPath = Join-Path $workspace "validate_pipeline_outputs.py"

if (-not (Test-Path -LiteralPath $validatorPath)) {
    throw "校验脚本不存在: $validatorPath"
}

Write-Host "0/3 先执行 docx 转 md..."
python (Join-Path $workspace "docx_to_md.py") $docxFull $mdPath

if (Test-Path -LiteralPath $reportPath) {
    Remove-Item -LiteralPath $reportPath -Force
}

$templateFull = $null
if ($TemplatePath) {
    if (-not (Test-Path -LiteralPath $TemplatePath)) {
        throw "模板文件不存在: $TemplatePath"
    }
    $templateFull = (Resolve-Path -LiteralPath $TemplatePath).Path
}

function Get-PromptText {
    param([int]$Round)

    $lines = @(
        ('使用 requirement-to-testcases-pipeline（第 {0} 轮）：' -f $Round),
        ('基于 @{0} 自动按顺序完成以下任务并写入文件：' -f $mdPath),
        ('1) 生成核心用例到 @{0}（仅p0/p1）' -f $corePath),
        ('2) 基于core补齐扩展到 @{0}（p2/p3 + UI验证/浮层场景/网络相关/机型兼容）' -f $fullPath),
        ('3) 生成审计报告到 @{0}（完整性检查报告）' -f $auditPath),
        '',
        '生成后请执行校验，目标是通过标准：',
        '- 通用校验通过（core/full/audit）',
        '- 严禁使用任何脚本直接生成或覆盖 core/full/audit（仅允许 skill 生成）'
    )

    if ($templateFull) {
        $lines += ('- 模板对比通过（仅 full vs @{0}）' -f $templateFull)
    }

    return ($lines -join "`r`n")
}

function Run-Validation {
    $args = @(
        $validatorPath,
        "--core", $corePath,
        "--full", $fullPath,
        "--audit", $auditPath
    )
    if ($templateFull) {
        $args += @("--template", $templateFull)
    }

    $output = & python @args 2>&1 | Out-String
    $ok = ($LASTEXITCODE -eq 0)
    $cmdText = "python `"$validatorPath`" --core `"$corePath`" --full `"$fullPath`" --audit `"$auditPath`""
    if ($templateFull) {
        $cmdText += " --template `"$templateFull`""
    }

    return [PSCustomObject]@{
        Success = $ok
        Output  = $output.TrimEnd()
        Cmd     = $cmdText
    }
}

for ($round = 1; $round -le $MaxRounds; $round++) {
    Write-Host ''
    Write-Host ('1/3 第 {0} 轮：生成提示词...' -f $round)
    $prompt = Get-PromptText -Round $round
    Write-Host '------------------------------------------------------------'
    Write-Host $prompt
    Write-Host '------------------------------------------------------------'
    try {
        Set-Clipboard -Value $prompt
        Write-Host '提示词已复制到剪贴板。'
    } catch {
        Write-Host '复制剪贴板失败，请手动复制。'
    }

    Write-Host ''
    if ($NonInteractive) {
        Write-Host '2/3 非交互模式：跳过人工确认，直接执行校验。'
    } else {
        Write-Host '2/3 请在 Cursor 对话中执行本轮生成。完成后回到此终端按回车继续校验。'
        [void](Read-Host ('按回车开始第 {0} 轮校验' -f $round))
    }

    Write-Host '3/3 执行校验...'
    $validation = Run-Validation
    Write-Host $validation.Output

    $statusText = if ($validation.Success) { '通过' } else { '未通过' }
    $reportLines = @(
        '# 迭代报告',
        '',
        ('## 第 {0} 轮' -f $round),
        ('- 校验命令：{0}' -f $validation.Cmd),
        ('- 校验结果：{0}' -f $statusText),
        '',
        '### 校验输出',
        '```text',
        $validation.Output,
        '```',
        ''
    )
    Add-Content -LiteralPath $reportPath -Value ($reportLines -join "`r`n") -Encoding UTF8

    if ($validation.Success) {
        Write-Host ''
        Write-Host ('已达标：第 {0} 轮校验通过。' -f $round)
        Write-Host ('迭代报告：{0}' -f $reportPath)
        exit 0
    }

    if ($round -lt $MaxRounds) {
        Write-Host ''
        Write-Host ('第 {0} 轮未通过，请根据上方失败项优化 skill 后进入下一轮。' -f $round)
    }
}

Write-Host ''
Write-Host ('达到最大轮次 {0} 仍未通过，请根据迭代报告继续修复。' -f $MaxRounds)
Write-Host ('迭代报告：{0}' -f $reportPath)
exit 1
