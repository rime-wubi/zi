"""构建 `wubi86.zi` 字表：国标 8,105 单字三档 + rime-wubi 表外增广。

字表只写 `text`/`code` 两列，不含权重、词频或来源名。
单字码取自 rime-wubi 的单字条目，同一字的简码与全码按原顺序全部保留。
表外增广只取 rime-wubi 中存在的汉字，按码点排序。
表外增广默认由 schema 的 `extended_charset` 开关过滤。
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from zi.dicts import write_dict_yaml

TIER_COUNTS: tuple[int, int, int] = (3500, 3000, 1605)

_CODE_PATTERN = re.compile(r"[a-z]{1,4}")

# Unicode 统一汉字区段；兼容汉字（U+F900–U+FAFF 等）不算单字集。
_HAN_RANGES = (
    (0x3400, 0x4DBF),
    (0x4E00, 0x9FFF),
    (0x20000, 0x2A6DF),
    (0x2A700, 0x2B739),
    (0x2B740, 0x2B81D),
    (0x2B820, 0x2CEA1),
    (0x2CEB0, 0x2EBE0),
    (0x2EBF0, 0x2EE5D),
    (0x30000, 0x3134A),
    (0x31350, 0x323AF),
)


def _is_han_character(text: str) -> bool:
    if len(text) != 1:
        return False
    codepoint = ord(text)
    return any(start <= codepoint <= end for start, end in _HAN_RANGES)


@dataclass(frozen=True)
class _StandardChar:
    text: str
    tier: int


@dataclass(frozen=True)
class CharTable:
    entries: tuple[tuple[str, str], ...]
    tier_counts: tuple[int, int, int]
    augmentation_chars: int

    @property
    def standard_chars(self) -> int:
        return sum(self.tier_counts)

    @property
    def total_chars(self) -> int:
        return self.standard_chars + self.augmentation_chars


def _read_standard_chars(path: Path) -> tuple[_StandardChar, ...]:
    chars: list[_StandardChar] = []
    seen: set[str] = set()
    previous_tier = 1
    for number, line in enumerate(
        path.read_text(encoding="utf-8").splitlines(), 1
    ):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        columns = line.split("\t")
        if len(columns) != 2:
            raise ValueError(
                f"{path} 第 {number} 行不符合 char/tier 契约：{line!r}"
            )
        text, tier_text = columns[0].strip(), columns[1].strip()
        if not _is_han_character(text):
            raise ValueError(f"{path} 第 {number} 行不是单个汉字：{text!r}")
        if tier_text not in ("1", "2", "3"):
            raise ValueError(f"{path} 第 {number} 行档位非法：{tier_text!r}")
        tier = int(tier_text)
        if tier < previous_tier:
            raise ValueError(f"{path} 第 {number} 行档位倒退：{text}")
        if text in seen:
            raise ValueError(f"{path} 第 {number} 行单字重复：{text}")
        seen.add(text)
        previous_tier = tier
        chars.append(_StandardChar(text, tier))
    if not chars:
        raise ValueError(f"分档单字清单为空：{path}")
    return tuple(chars)


def _read_rime_char_codes(path: Path) -> dict[str, tuple[str, ...]]:
    lines = path.read_text(encoding="utf-8").splitlines()
    start = None
    for index, line in enumerate(lines):
        if line.strip() == "...":
            start = index + 1
            break
    if start is None:
        raise ValueError(f"rime-wubi 字典缺少 YAML 文档结束标记：{path}")

    codes: dict[str, list[str]] = {}
    for number, line in enumerate(lines[start:], start + 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        columns = line.split("\t")
        if len(columns) < 2:
            raise ValueError(f"{path} 第 {number} 行缺少编码：{line!r}")
        text, code = columns[0], columns[1]
        if not _is_han_character(text):
            continue
        if _CODE_PATTERN.fullmatch(code) is None:
            raise ValueError(f"{path} 第 {number} 行编码非法：{code!r}")
        entries = codes.setdefault(text, [])
        if code not in entries:
            entries.append(code)
    if not codes:
        raise ValueError(f"rime-wubi 字典没有单字条目：{path}")
    return {text: tuple(entries) for text, entries in codes.items()}


def build_char_table(
    standard_chars_path: Path, rime_wubi_dict_path: Path
) -> CharTable:
    standard = _read_standard_chars(standard_chars_path)
    codes = _read_rime_char_codes(rime_wubi_dict_path)

    missing = [char.text for char in standard if char.text not in codes]
    if missing:
        sample = "、".join(missing[:10])
        raise ValueError(
            f"rime-wubi 字表缺少 {len(missing)} 个国标单字：{sample}"
        )

    entries: list[tuple[str, str]] = []
    tier_counts = [0, 0, 0]
    for char in standard:
        tier_counts[char.tier - 1] += 1
        for code in codes[char.text]:
            entries.append((char.text, code))

    standard_set = {char.text for char in standard}
    augmentation = sorted(set(codes) - standard_set)
    for text in augmentation:
        for code in codes[text]:
            entries.append((text, code))

    return CharTable(
        entries=tuple(entries),
        tier_counts=(tier_counts[0], tier_counts[1], tier_counts[2]),
        augmentation_chars=len(augmentation),
    )


def write_char_table(path: Path, table: CharTable) -> None:
    write_dict_yaml(path, "wubi86.zi", table.entries)
