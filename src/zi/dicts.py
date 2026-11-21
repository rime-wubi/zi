"""写出 Rime `.dict.yaml`，并读取单字表。"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence

DICT_VERSION = "0.1.0"


def write_dict_yaml(
    path: Path,
    name: str,
    entries: Sequence[tuple[str, str]],
    import_tables: Sequence[str] = (),
) -> None:
    lines = [
        "# Rime dictionary",
        "# encoding: utf-8",
        "---",
        f"name: {name}",
        f'version: "{DICT_VERSION}"',
        "sort: original",
        "columns:",
        "  - text",
        "  - code",
    ]
    if import_tables:
        lines.append("import_tables:")
        for table in import_tables:
            lines.append(f"  - {table}")
    lines.append("...")
    for text, code in entries:
        if not text or not code or "\t" in text or "\t" in code:
            raise ValueError(f"非法词条：{text!r} / {code!r}")
        lines.append(f"{text}\t{code}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def parse_tsv_entries(
    lines: Iterable[str], source: str
) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    for line in lines:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        columns = line.split("\t")
        if len(columns) < 2:
            raise ValueError(f"{source} 行不符合契约：{line!r}")
        entries.append((columns[0], columns[1]))
    return entries


def read_char_table(path: Path) -> list[tuple[str, str]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "...":
            start = index + 1
            break
    if start is None:
        raise ValueError(f"字表缺少 YAML 文档结束标记：{path}")
    return parse_tsv_entries(lines[start:], str(path))
