# 字表 Zi

为 [rime-wubi](https://github.com/rime-wubi/rime-wubi) 生成 `wubi86.zi.dict.yaml`：国标《[通用规范汉字表](https://www.gov.cn/zhengce/zhengceku/2013-08/19/content_1289.htm)》8,105 单字三档加官方字表外的汉字增广。字表只含 `text`/`code` 两列，沿用官方 [rime-wubi](https://github.com/rime/rime-wubi) 的单字简码与全码。

本仓库只负责基础项目的字表层；Ci 词表由[词合 CiHe](https://github.com/chinese-ci/cihe) 生成，[rime-wubi](https://github.com/rime-wubi/rime-wubi) 仓库负责组装与发布。

## 运行

```bash
uv sync
uv run python tools/build_char_table.py \
  --rime-wubi-dict ../rime-wubi/wubi86.dict.yaml \
  --output ../rime-wubi/wubi86.zi.dict.yaml
```

- 默认标准字表：`src/zi/data/standard-chars.tsv`。
- 输出为 UTF-8、LF、`sort: original`、`columns: text/code`。
- 同一输入重复运行逐字节一致。

## 开发

```bash
uv run pytest
uv run pyright
```

## 许可

[MIT](https://opensource.org/license/mit)，见 [LICENSE](LICENSE)。
