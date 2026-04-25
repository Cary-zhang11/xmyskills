from __future__ import annotations

import argparse
import re
from pathlib import Path

from docx import Document
from docx.document import Document as _Document
from docx.table import Table
from docx.text.paragraph import Paragraph
from docx.oxml.text.paragraph import CT_P
from docx.oxml.table import CT_Tbl


def normalize(text: str) -> str:
    return text.replace("\u00a0", " ").strip()


def heading_level(style_name: str) -> int | None:
    if not style_name:
        return None
    style_name = style_name.lower()
    if "heading" in style_name:
        parts = style_name.split()
        for part in parts[::-1]:
            if part.isdigit():
                level = int(part)
                if 1 <= level <= 6:
                    return level
    return None


def infer_cn_heading_level(text: str) -> int | None:
    # Typical Chinese section titles in requirement docs.
    if re.match(r"^[一二三四五六七八九十]+、", text):
        return 2
    if re.match(r"^[（(][一二三四五六七八九十]+[)）]", text):
        return 3
    if re.match(r"^\d+[、.]", text):
        return 4
    return None


def para_is_list(paragraph) -> bool:
    p = paragraph._p
    ppr = p.pPr
    if ppr is None:
        return False
    return ppr.numPr is not None


def iter_blocks(doc: _Document):
    parent = doc.element.body
    for child in parent.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, doc)
        elif isinstance(child, CT_Tbl):
            yield Table(child, doc)


def table_to_markdown(table: Table) -> list[str]:
    rows: list[list[str]] = []
    for row in table.rows:
        cells = [normalize(cell.text).replace("\n", " / ") for cell in row.cells]
        if any(cells):
            rows.append(cells)
    if not rows:
        return []

    col_count = max(len(r) for r in rows)
    normalized_rows = [r + [""] * (col_count - len(r)) for r in rows]
    header = normalized_rows[0]
    lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(["---"] * col_count) + " |",
    ]
    for row in normalized_rows[1:]:
        lines.append("| " + " | ".join(row) + " |")
    return lines


def split_cell_lines(text: str) -> list[str]:
    text = normalize(text)
    if not text:
        return []
    parts = [normalize(part) for part in re.split(r"[;/；\n]+| / ", text)]
    return [p for p in parts if p]


def table_to_sections(table: Table) -> list[str]:
    # Optimized for requirement tables:
    # | 功能点 | 功能描述 | 示意图 | 埋点 |
    rows: list[list[str]] = []
    for row in table.rows:
        cells = [normalize(cell.text) for cell in row.cells]
        if any(cells):
            rows.append(cells)
    if len(rows) < 2:
        return table_to_markdown(table)

    lines: list[str] = []
    for row in rows[1:]:
        if not row:
            continue
        feature = row[0] if len(row) > 0 else ""
        desc = row[1] if len(row) > 1 else ""
        track = row[3] if len(row) > 3 else ""
        if feature:
            lines.append(f"## {feature}")
            lines.append("")
        if desc:
            lines.append("### 功能描述")
            for item in split_cell_lines(desc):
                lines.append(f"- {item}")
            lines.append("")
        if track:
            lines.append("### 埋点")
            for item in split_cell_lines(track):
                lines.append(f"- {item}")
            lines.append("")
    return lines or table_to_markdown(table)


def convert_docx_to_md(src_path: str, dst_path: str) -> None:
    doc = Document(src_path)
    lines: list[str] = []
    in_list = False
    table_index = 0

    for block in iter_blocks(doc):
        if isinstance(block, Paragraph):
            text = normalize(block.text)
            if not text:
                if lines and lines[-1] != "":
                    lines.append("")
                in_list = False
                continue

            level = heading_level(getattr(block.style, "name", ""))
            if level is None:
                level = infer_cn_heading_level(text)
            if level is not None:
                lines.append(f'{"#" * level} {text}')
                lines.append("")
                in_list = False
                continue

            if para_is_list(block):
                lines.append(f"- {text}")
                in_list = True
                continue

            if in_list and lines and lines[-1] != "":
                lines.append("")
            lines.append(text)
            lines.append("")
            in_list = False
            continue

        if isinstance(block, Table):
            table_index += 1
            # Usually the second table is feature details in requirement docs.
            if table_index == 2:
                table_lines = table_to_sections(block)
            else:
                table_lines = table_to_markdown(block)
            if table_lines:
                if lines and lines[-1] != "":
                    lines.append("")
                lines.extend(table_lines)
                lines.append("")
            in_list = False

    while lines and lines[-1] == "":
        lines.pop()

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert DOCX requirement document to Markdown."
    )
    parser.add_argument("input", help="Input .docx file path")
    parser.add_argument(
        "output",
        nargs="?",
        help="Output .md file path; defaults to same name as input",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    source = Path(args.input)
    target = Path(args.output) if args.output else source.with_suffix(".md")
    convert_docx_to_md(str(source), str(target))
    print(f"converted: {source} -> {target}")
