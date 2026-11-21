from __future__ import annotations

from pathlib import Path

import pytest

from zi.char_table import build_char_table, write_char_table

TESTS_ROOT = Path(__file__).resolve().parent
FIXTURES = TESTS_ROOT / "fixtures" / "char_table"
GOLDEN = TESTS_ROOT / "golden" / "char_table"
STANDARD_CHARS = FIXTURES / "standard-chars.tsv"
RIME_WUBI_DICT = FIXTURES / "rime-wubi.sample.dict.yaml"
OFFICIAL_STANDARD_CHARS = (
    TESTS_ROOT.parent / "src" / "zi" / "data" / "standard-chars.tsv"
)


def _standard_rows(path: Path) -> list[tuple[str, int]]:
    rows: list[tuple[str, int]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        text, tier = line.split("\t")
        rows.append((text, int(tier)))
    return rows


def _write_rime_dict(path: Path, rows: list[tuple[str, str]]) -> None:
    lines = ["---", "name: wubi86", "..."]
    lines.extend(f"{text}\t{code}\t1" for text, code in rows)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def test_char_table_matches_golden(tmp_path: Path) -> None:
    table = build_char_table(STANDARD_CHARS, RIME_WUBI_DICT)
    output = tmp_path / "wubi86.zi.dict.yaml"

    write_char_table(output, table)

    assert output.read_text(encoding="utf-8") == (
        GOLDEN / "wubi86.zi.dict.yaml"
    ).read_text(encoding="utf-8")
    assert table.tier_counts == (7, 9, 3)
    assert table.augmentation_chars == 2
    assert table.total_chars == 21


def test_full_standard_charset_is_complete(tmp_path: Path) -> None:
    standard = _standard_rows(OFFICIAL_STANDARD_CHARS)
    rows = [(text, "aaaa") for text, _tier in standard]
    rows.append(("㐀", "bbbb"))
    rime_dict = tmp_path / "wubi86.dict.yaml"
    _write_rime_dict(rime_dict, rows)

    table = build_char_table(OFFICIAL_STANDARD_CHARS, rime_dict)

    assert table.tier_counts == (3500, 3000, 1605)
    assert table.standard_chars == 8105
    assert table.augmentation_chars == 1
    assert table.total_chars == 8106
    assert len(table.entries) == 8106
    assert len({text for text, _code in table.entries}) == 8106
    assert len(set(table.entries)) == len(table.entries)
    assert table.entries[0] == ("一", "aaaa")
    assert table.entries[-1] == ("㐀", "bbbb")


def test_missing_standard_char_is_reported(tmp_path: Path) -> None:
    rows = [
        (text, "aaaa")
        for text, _tier in _standard_rows(STANDARD_CHARS)
        if text != "蠼"
    ]
    rime_dict = tmp_path / "wubi86.dict.yaml"
    _write_rime_dict(rime_dict, rows)

    with pytest.raises(ValueError, match="缺少 1 个国标单字.*蠼"):
        build_char_table(STANDARD_CHARS, rime_dict)
