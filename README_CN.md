# Chinese Poetry Skill — 中国古典诗词检索与创作

一个 Claude Code skill，用于检索和创作中国古典诗词。基于 [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) 数据集——最全的中华古典文集数据库，包含 **5.5 万首唐诗**、**26 万首宋诗**、**2.1 万首宋词**，覆盖 14 个朝代与体裁。

## 为什么需要这个 Skill

Claude 本身就能写诗，训练数据中已经包含了大量古诗词。但训练记忆是有损的——它可能会背错诗句、杜撰不存在的作品，或者凭模糊印象近似某个诗人的风格。

这个 skill 为 Claude 提供了一个 **可实时搜索的真实诗词数据库**（345 MB）。它不会凭空猜测，而是通过 grep 从原始 JSON 文件中检索真诗，再基于验证过的源材料进行创作。

| 没有 Skill | 有 Skill |
|---|---|
| 靠训练记忆，可能编造诗句 | 搜索真实 JSON 源文件，零虚构 |
| "大概是李白那味" | "用李白的原词原句和节奏创作" |
| 无法查询指定诗作 | `grep` 秒搜 345 MB 全库 |

## 功能

- **按作者搜索** — 查找李白、杜甫、苏轼、纳兰性德等 1.4 万+ 诗人的全部作品
- **按标题搜索** — 模糊匹配诗词标题
- **按内容搜索** — 查找包含特定词语的诗句（如"明月"、"长安"）
- **按词牌名搜索** — 查找宋词中指定词牌名的作品（如"水调歌头"、"蝶恋花"）
- **按体裁浏览** — 唐诗、宋词、元曲、诗经、楚辞、论语等
- **风格模仿创作** — 先检索诗人原作，分析其意象、句式、情感，再基于真实风格创作

## 数据集

| 目录 | 体裁 | 朝代 | 规模 |
|------|------|------|------|
| `全唐诗/` | 唐诗、宋诗 | 唐、宋 | ~31.5 万首 |
| `宋词/` | 宋词 | 宋 | ~2.1 万首 |
| `元曲/` | 元曲 | 元 | ~1.1 万行 |
| `诗经/` | 诗经 | 先秦 | 305 篇 |
| `楚辞/` | 楚辞 | 先秦 | — |
| `论语/` | 论语 | 先秦 | 20 篇 |
| `纳兰性德/` | 纳兰词 | 清 | ~350 首 |
| `五代诗词/` | 花间集、南唐词 | 五代 | — |
| `蒙学/` | 蒙学经典 | 各代 | — |
| `四书五经/` | 四书五经 | 先秦 | — |
| `曹操诗集/` | 曹操诗 | 汉末 | — |

## 安装

### 1. 安装 Skill

将 `SKILL.md` 和 `_meta.json` 复制到 Claude Code 的 skills 目录：

```bash
mkdir -p ~/.agents/skills/chinese-poetry-1.0.0/
cp SKILL.md _meta.json ~/.agents/skills/chinese-poetry-1.0.0/
```

### 2. 获取数据集

Skill 会自动从以下三个位置按优先级检测数据集：

1. 用户本地已有路径（如 `D:\github\chinese-poetry-master\chinese-poetry-master`）
2. `CHINESE_POETRY_PATH` 环境变量
3. 自动 clone 到 `~/.claude/chinese-poetry-cache/`

如果前两项都不存在，Claude 会在首次使用时自动 clone：

```bash
git clone --depth 1 https://github.com/chinese-poetry/chinese-poetry.git ~/.claude/chinese-poetry-cache/
```

### 3. 依赖要求

- **git** — 用于 clone 数据集
- **bash、grep、sed、awk** — macOS/Linux 系统内置；Windows 需 Git Bash 或 WSL

## 使用方式

在 Claude Code 中调用 skill：

```
/使用诗歌skill
搜索李白的诗
模仿纳兰性德风格写一首词
找出所有包含"明月"的唐诗
宋词中词牌名为"蝶恋花"的作品有哪些
关汉卿的元曲
```

Claude 会在磁盘上的 JSON 文件中执行 grep 搜索，提取匹配结果并展示——全程不会把 345 MB 数据加载到上下文中。

## 工作原理

### 架构

```
用户查询
    │
    ▼
Claude Code + Chinese Poetry Skill
    │
    ├── grep 搜索 JSON 文件（毫秒级）
    │
    ├── Read 工具（提取命中行前后 5-10 行）
    │
    └── 上下文（仅匹配到的诗词，约 2-5 KB）
```

### 核心设计决策

**绝不全量加载。** 全部数据集 345 MB JSON，约合 1.38 亿 token。全部加载需要约 690 次满载 Claude 调用。因此每次查询都使用 `grep` 直接在磁盘上搜索，只返回命中行。

**字段感知搜索。** 不同目录的诗句内容字段名不同（`paragraphs` / `content` / `para`）。Skill 内置字段映射表，确保跨体裁搜索准确无误。

**先检索再创作。** 当用户要求模仿某诗人风格时，Skill 会先检索 3-5 首原作，分析其意象、句式结构、情感基调，再基于分析结果进行创作，并标注参考了哪些原作。

### JSON 字段差异

| 目录 | 诗句字段 | 标题字段 | 特殊字段 |
|------|----------|----------|----------|
| 全唐诗 | `paragraphs` | `title` | `id` |
| 宋词 | `paragraphs` | — | `rhythmic`（词牌名） |
| 元曲 | `paragraphs` | `title` | `dynasty` |
| 诗经 | `content` | `title` | `chapter`, `section` |
| 楚辞 | `content` | `title` | `section`, `author` |
| 纳兰性德 | `para` | `title` | — |

> 注意：JSON 键值对冒号后有空格（`"author": "李白"`），grep 时必须写出空格，否则匹配不到。

## 示例

### 搜索李白

```bash
grep -rn '"author": "李白"' "$CP/全唐诗/" | head -5
```

返回：
```json
{"author": "李白", "paragraphs": ["白玉誰家郎，回車渡天津。","看花東上陌，驚動洛陽人。"], "title": "橫吹曲辭 洛陽陌"}
```

### 检索后模仿李白风格创作

```
## 风格分析
- 意象：骏马、弯弓、关山、花月、银鞍 — 宏阔辽远
- 句式：五言为主，节奏明快
- 情感：豪放飘逸，浪漫主义

## 创作
《咏人工智能》
万卷入芯海，天机一算通。
山河皆可问，日月对答中。

参考原作：《紫骝马》《幽州胡马客歌》《白鼻騧》
```

## 许可证

MIT

## 致谢

- 诗词数据集：[chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) — 最全的中华古典文集数据库
