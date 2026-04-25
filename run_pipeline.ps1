param(
    [Parameter(Mandatory = $true)]
    [string]$DocxPath
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

Write-Host "1/2 先执行 docx 转 md..."
python (Join-Path $workspace "docx_to_md.py") $docxFull $mdPath

$prompt = @"
使用 requirement-to-testcases-pipeline：
基于 @$mdPath 自动按顺序完成以下任务并写入文件：
1) 生成核心用例到 @$corePath（仅p0/p1）
2) 基于core补齐扩展到 @$fullPath（p2/p3 + UI验证/浮层场景/网络相关/机型兼容）
3) 生成审计报告到 @$auditPath（完整性检查报告）
"@

Write-Host ""
Write-Host "2/2 已生成一键提示词（已复制到剪贴板），粘贴到 Cursor 对话框即可："
Write-Host "------------------------------------------------------------"
Write-Host $prompt
Write-Host "------------------------------------------------------------"

try {
    Set-Clipboard -Value $prompt
    Write-Host "提示词已复制到剪贴板。"
} catch {
    Write-Host "复制剪贴板失败，请手动复制上方提示词。"
}
