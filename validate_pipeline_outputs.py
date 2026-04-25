import argparse
import re
import sys
from pathlib import Path


TC_RE = re.compile(r"^\s*-\s*tc-(p[0-3])(?:-(\d{3}))?\s*[:：]")
TC_STYLE_SHORT_RE = re.compile(r"^\s*-\s*tc-p[0-3]\s*[:：]", re.M)
TC_STYLE_FULL_RE = re.compile(r"^\s*-\s*tc-p[0-3]-\d{3}\s*[:：]", re.M)
AUDIT_SECTIONS = [
    "### 1. 需求覆盖统计",
    "### 2. 用例覆盖度检查",
    "### 3. 维度覆盖检查",
    "### 4. 关键信息提取确认",
    "### 5. 待澄清问题汇总",
    "### 6. 生成质量评估",
]


def read_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {path}")
    return path.read_text(encoding="utf-8")


def parse_tc_levels(text: str):
    levels = []
    ids = []
    section = ""
    for line in text.splitlines():
        if line.startswith("### "):
            section = line.strip()
        m = TC_RE.match(line)
        if m:
            level = m.group(1)
            num = m.group(2) or "000"
            levels.append(level)
            ids.append((section, f"{level}-{num}"))
    return levels, ids


def extract_headings(text: str, prefix: str) -> list[str]:
    return [line.strip() for line in text.splitlines() if line.startswith(prefix)]


def detect_tc_style(text: str) -> str:
    has_full = bool(TC_STYLE_FULL_RE.search(text))
    has_short = bool(TC_STYLE_SHORT_RE.search(text))
    if has_full and not has_short:
        return "full"
    if has_short and not has_full:
        return "short"
    if has_full and has_short:
        return "mixed"
    return "none"


def check_core(core_text: str, errors: list[str]):
    levels, ids = parse_tc_levels(core_text)
    if not levels:
        errors.append("core 未识别到任何 tc 用例。")
        return
    if any(level not in {"p0", "p1"} for level in levels):
        errors.append("core 存在非 p0/p1 用例。")
    if len(ids) != len(set(ids)):
        errors.append("core 在同一功能块内存在重复编号。")
    if "#### 正常流程功能" not in core_text or "#### 关键分支（顺序）" not in core_text:
        errors.append("core 缺少标准维度标题（正常流程功能/关键分支（顺序））。")


def check_full(full_text: str, errors: list[str], warnings: list[str], template_mode: bool = False):
    levels, ids = parse_tc_levels(full_text)
    if not levels:
        errors.append("full 未识别到任何 tc 用例。")
        return
    if not any(level == "p0" for level in levels):
        warnings.append("full 未包含 p0 用例（非阻塞，模板模式下可按模板决定）。")
    if not any(level == "p1" for level in levels):
        warnings.append("full 未包含 p1 用例（非阻塞，模板模式下可按模板决定）。")
    if not any(level == "p2" for level in levels):
        errors.append("full 缺少 p2 用例。")
    if not any(level == "p3" for level in levels):
        errors.append("full 缺少 p3 用例。")
    if (not template_mode) and len(ids) != len(set(ids)):
        errors.append("full 在同一功能块内存在重复编号。")

    if template_mode:
        # 模板模式下允许维度以独立章节出现，不强制每个功能块都挂在 #### 下
        dim_keywords = ["UI验证", "浮层场景", "网络相关", "机型兼容"]
        for kw in dim_keywords:
            if kw not in full_text:
                errors.append(f"full 缺少专项维度关键词: {kw}")
    else:
        for dim in ["#### UI验证", "#### 浮层场景", "#### 网络相关", "#### 机型兼容"]:
            if dim not in full_text:
                errors.append(f"full 缺少专项维度: {dim}")


def check_audit(audit_text: str, errors: list[str]):
    if "## 完整性检查报告" not in audit_text:
        errors.append("audit 缺少“## 完整性检查报告”。")
    for sec in AUDIT_SECTIONS:
        if sec not in audit_text:
            errors.append(f"audit 缺少章节: {sec}")
    if "统计口径说明" not in audit_text:
        errors.append("audit 缺少“统计口径说明”。")


def _coverage_ratio(expected: set[str], actual: set[str]) -> float:
    if not expected:
        return 1.0
    return len(expected & actual) / len(expected)


def check_template_alignment(
    template_text: str,
    full_text: str,
    errors: list[str],
    warnings: list[str],
):
    # 模板对比仅针对 full 结果；若模板包含审计章节，则截断到审计章节前
    audit_anchor = "\n## 完整性检查报告"
    if audit_anchor in template_text:
        template_text = template_text.split(audit_anchor, 1)[0]

    # 防呆：模板对齐模式下禁止直接模板拷贝充当full
    norm_template = "\n".join([l.rstrip() for l in template_text.strip().splitlines()])
    norm_full = "\n".join([l.rstrip() for l in full_text.strip().splitlines()])
    if norm_template == norm_full:
        errors.append("检测到 full 与模板正文完全一致，疑似模板直拷贝，判定为无效生成。")

    template_h2 = set(extract_headings(template_text, "## "))
    template_h3 = set(extract_headings(template_text, "### "))
    template_h4 = set(extract_headings(template_text, "#### "))

    result_text = full_text
    result_h2 = set(extract_headings(result_text, "## "))
    result_h3 = set(extract_headings(result_text, "### "))
    result_h4 = set(extract_headings(result_text, "#### "))

    h2_ratio = _coverage_ratio(template_h2, result_h2)
    h3_ratio = _coverage_ratio(template_h3, result_h3)
    h4_ratio = _coverage_ratio(template_h4, result_h4)

    if h2_ratio < 0.85:
        errors.append(f"模板对比二级标题覆盖率不足: {h2_ratio:.0%}（要求>=85%）")
    if h3_ratio < 0.80:
        errors.append(f"模板对比三级标题覆盖率不足: {h3_ratio:.0%}（要求>=80%）")
    if h4_ratio < 0.65:
        warnings.append(f"模板对比四级标题覆盖率偏低: {h4_ratio:.0%}（建议>=65%）")

    missing_h2 = sorted(h for h in template_h2 if h not in result_h2)
    missing_h3 = sorted(h for h in template_h3 if h not in result_h3)
    if missing_h2:
        warnings.append(f"模板未覆盖的二级标题示例: {', '.join(missing_h2[:5])}")
    if missing_h3:
        warnings.append(f"模板未覆盖的三级标题示例: {', '.join(missing_h3[:8])}")

    template_style = detect_tc_style(template_text)
    result_style = detect_tc_style(result_text)
    if template_style != "none" and result_style != "none" and template_style != result_style:
        warnings.append(f"编号风格不一致：模板为 {template_style}，结果为 {result_style}（非阻塞）")
    elif template_style == "none":
        warnings.append("模板未检测到 tc 编号样式，跳过编号风格比对。")


def main():
    parser = argparse.ArgumentParser(description="校验 docx-skill-md 产物是否符合通用契约")
    parser.add_argument("--core", required=True, help="core 文件路径")
    parser.add_argument("--full", required=True, help="full 文件路径")
    parser.add_argument("--audit", required=True, help="audit 文件路径")
    parser.add_argument("--template", required=False, help="可选：模板文件路径，仅与 full 做结构比对")
    args = parser.parse_args()

    core_text = read_text(Path(args.core))
    full_text = read_text(Path(args.full))
    audit_text = read_text(Path(args.audit))

    errors: list[str] = []
    warnings: list[str] = []
    check_core(core_text, errors)
    template_mode = bool(args.template)
    check_full(full_text, errors, warnings, template_mode=template_mode)
    check_audit(audit_text, errors)
    if args.template:
        template_text = read_text(Path(args.template))
        check_template_alignment(template_text, full_text, errors, warnings)

    if errors:
        print("校验失败：")
        for i, err in enumerate(errors, 1):
            print(f"{i}. {err}")
        if warnings:
            print("\n附加提示：")
            for i, warning in enumerate(warnings, 1):
                print(f"{i}. {warning}")
        sys.exit(1)

    if warnings:
        print("校验通过（有提示）：")
        for i, warning in enumerate(warnings, 1):
            print(f"{i}. {warning}")
    else:
        print("校验通过：core/full/audit 均满足通用契约。")


if __name__ == "__main__":
    main()
