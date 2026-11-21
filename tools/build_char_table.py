"""构建 `wubi86.zi` 字表：国标 8,105 单字三档 + rime-wubi 表外增广。

输入是仓库内的 8,105 分档单字清单与一份官方 rime-wubi `wubi86.dict.yaml`。
输出只含 `text`/`code` 两列，不含权重与来源。
单字码按 rime-wubi 单字条目原样保留简码与全码。
表外增广只收汉字，按码点排序。
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from zi.char_table import TIER_COUNTS, build_char_table, write_char_table

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_STANDARD_CHARS = ROOT / "src" / "zi" / "data" / "standard-chars.tsv"
DEFAULT_OUTPUT = ROOT / "var" / "char_table" / "wubi86.zi.dict.yaml"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--standard-chars",
        type=Path,
        default=DEFAULT_STANDARD_CHARS,
        help="国标 8,105 分档单字清单（char/tier TSV）",
    )
    parser.add_argument(
        "--rime-wubi-dict",
        type=Path,
        required=True,
        help="官方 rime-wubi `wubi86.dict.yaml`",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="输出字表路径",
    )
    arguments = parser.parse_args()

    table = build_char_table(
        arguments.standard_chars, arguments.rime_wubi_dict
    )
    if table.tier_counts != TIER_COUNTS:
        print(
            f"分档计数为 {table.tier_counts}，预期 {TIER_COUNTS}",
            file=sys.stderr,
        )
        return 1

    write_char_table(arguments.output, table)
    print(
        f"字表：{arguments.output}\n"
        f"一级 {table.tier_counts[0]} / 二级 {table.tier_counts[1]} / "
        f"三级 {table.tier_counts[2]}；增广 {table.augmentation_chars}；"
        f"条目 {len(table.entries)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
