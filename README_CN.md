# Chinese Poetry Skill — 中国古典诗词检索与创作

一个用于检索、引用和创作中国古典诗词的 skill，数据源来自
[chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)。

新版加入了跨平台 Python 检索脚本，Agent 不再需要临时拼 `grep` 命令，也不用把大型
JSON 文件读进上下文。

## 功能

- 按作者、标题、正文、宋词词牌名检索。
- 按语料范围检索：唐诗、宋诗、宋词、元曲、诗经、楚辞、纳兰词、五代诗词、曹操诗集等。
- 返回完整作品，并标注来源文件。
- 区分 `全唐诗/` 里的唐诗 `poet.tang.*.json` 和宋诗 `poet.song.*.json`。
- 默认跳过上游数据集中的 `error/` 目录。
- 仿作前先检索真实原作，再分析风格并创作。

## 文件结构

```text
SKILL.md
scripts/search_poetry.py
_meta.json
README.md
README_CN.md
```

## 安装 Skill

复制整个 skill 文件夹到 skills 目录，注意保留 `scripts/`：

```bash
mkdir -p ~/.agents/skills/chinese-poetry-1.1.0/
cp -R SKILL.md scripts _meta.json ~/.agents/skills/chinese-poetry-1.1.0/
```

## 准备数据集

数据集单独下载：

```bash
git clone --depth 1 https://github.com/chinese-poetry/chinese-poetry.git ~/.cache/chinese-poetry
```

然后设置环境变量：

```bash
export CHINESE_POETRY_PATH=~/.cache/chinese-poetry
```

也可以每次显式传入路径：

```bash
python scripts/search_poetry.py --dataset ~/.cache/chinese-poetry --genre tang --author 李白 --limit 5
```

## 使用示例

```bash
# 搜索李白唐诗
python scripts/search_poetry.py --genre tang --author 李白 --limit 5

# 搜索苏轼宋词
python scripts/search_poetry.py --genre ci --author 苏轼 --limit 5

# 按词牌名搜索
python scripts/search_poetry.py --genre ci --rhythmic 水调歌头 --limit 5

# 在主要诗词语料中搜索“明月”
python scripts/search_poetry.py --genre all --text 明月 --limit 5

# 输出 JSON，便于后续处理
python scripts/search_poetry.py --genre shijing --title 关雎 --limit 1 --json
```

## 支持的体裁键

| 键 | 语料 |
| --- | --- |
| `tang` | 唐诗：`全唐诗/poet.tang.*.json` |
| `song-poetry` | 宋诗：`全唐诗/poet.song.*.json` |
| `ci` | 宋词：`宋词/ci.song.*.json` |
| `yuanqu` | 元曲 |
| `shijing` | 诗经 |
| `chuci` | 楚辞 |
| `nalan` | 纳兰性德 |
| `five-dynasties` | 五代诗词 |
| `caocao` | 曹操诗集 |
| `shuimo-tang` | 水墨唐诗子集 |
| `analects` | 论语 |
| `all` | 主要诗词语料 |

## 设计说明

上游数据集有数百 MB，skill 不应该把它整体读进上下文。`scripts/search_poetry.py`
会逐个 JSON 文件读取，统一处理 `paragraphs`、`content`、`para`、`rhythmic`
等字段，只输出命中的完整作品。

仿作时应先检索 3-5 首真实作品，分析意象、句式、用词和情绪基调，再单独给出新作，
并列出参考原作。

## 许可证

MIT。数据集来源：[chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)。
