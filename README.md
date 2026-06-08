# Chinese Poetry Skill

A Claude Code skill for searching, retrieving, and composing Chinese classical poetry. Backed by the [chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) dataset — the most comprehensive open-source collection of classical Chinese literature, containing **55,000 Tang poems**, **260,000 Song poems**, and **21,000 Song Ci** across 14 dynasties and genres.

## Why

Claude can already write poetry from its training data. However, training memory is lossy — it can misquote lines, invent nonexistent poems, or approximate a poet's style from faded impressions.

This skill gives Claude a **real-time searchable database** of over 345 MB of authentic classical Chinese poetry. Instead of guessing, it retrieves actual poems via grep and composes new works grounded in verified source material.

| Without Skill | With Skill |
|---|---|
| Relies on training memory, may hallucinate lines | Searches exact source JSON, zero fabrication |
| "Roughly Li Bai" | "Li Bai, with his actual vocabulary and cadence" |
| Can't look up specific poems on demand | `grep` across 345 MB in seconds |

## Features

- **Search by author** — Find all works by 李白, 杜甫, 苏轼, 纳兰性德, and ~14,000+ other poets
- **Search by title** — Fuzzy-match poem titles across the entire corpus
- **Search by content** — Find every poem containing a specific word or phrase (e.g., 明月, 长安)
- **Search by rhythmic pattern** — Find Song Ci by 词牌名 (e.g., 水调歌头, 蝶恋花)
- **Browse by genre** — Tang poems, Song Ci, Yuan Qu, Shijing, Chuci, Analects, and more
- **Style imitation** — Retrieve a poet's actual works first, then compose new poems in their verified style

## Supported Corpora

| Directory | Genre | Dynasty | Poems |
|-----------|-------|---------|-------|
| `全唐诗/` | Tang & Song poems | 唐, 宋 | ~315,000 |
| `宋词/` | Song Ci (lyrics) | 宋 | ~21,000 |
| `元曲/` | Yuan Qu (drama) | 元 | ~11,000 lines |
| `诗经/` | Book of Songs | 先秦 | 305 |
| `楚辞/` | Songs of Chu | 先秦 | — |
| `论语/` | Analects | 先秦 | 20 chapters |
| `纳兰性德/` | Nalan Xingde | 清 | ~350 |
| `五代诗词/` | Five Dynasties | 五代 | — |
| `蒙学/` | Elementary classics | Various | — |
| `四书五经/` | Four Books & Five Classics | 先秦 | — |
| `曹操诗集/` | Cao Cao poems | 汉末 | — |

## Installation

### 1. Install the skill

Copy `SKILL.md` and `_meta.json` into your Claude Code skills directory:

```bash
mkdir -p ~/.agents/skills/chinese-poetry-1.0.0/
cp SKILL.md _meta.json ~/.agents/skills/chinese-poetry-1.0.0/
```

### 2. Get the dataset

The skill auto-detects the dataset from three locations (checked in order):

1. A local path you already have (e.g., `D:\github\chinese-poetry-master\chinese-poetry-master`)
2. The `CHINESE_POETRY_PATH` environment variable
3. Auto-clone to `~/.claude/chinese-poetry-cache/`

If none exist, Claude will clone it automatically on first use:

```bash
git clone --depth 1 https://github.com/chinese-poetry/chinese-poetry.git ~/.claude/chinese-poetry-cache/
```

### 3. Requirements

- **git** — for cloning the dataset
- **bash, grep, sed, awk** — system built-ins on macOS/Linux; available via Git Bash or WSL on Windows

## Usage

Invoke the skill in Claude Code:

```
/使用诗歌skill
搜索李白的诗
模仿纳兰性德风格写一首词
找出所有包含"明月"的唐诗
宋词中词牌名为"蝶恋花"的作品有哪些
```

Claude will grep the JSON files on disk, extract matching results, and present them — without loading the entire 345 MB dataset into context.

## How It Works

### Architecture

```
User Query
    │
    ▼
Claude Code + Chinese Poetry Skill
    │
    ├── grep on JSON files (searches in ~100ms)
    │
    ├── Read tool (extracts 5-10 lines around hit)
    │
    └── Context (only the matching poem, ~2-5 KB)
```

### Key Design Decisions

**Never load the entire dataset.** The full corpus is 345 MB of JSON — approximately 138 million tokens. Loading it all would require ~690 Claude calls at maximum context. Instead, every query uses `grep` to search directly on disk, returning only matching lines.

**Field-aware searching.** Different directories use different JSON field names for poem content (`paragraphs` vs `content` vs `para`). The skill maps these so searches work correctly across all genres.

**Retrieve then compose.** When asked to write in a poet's style, the skill always retrieves 3-5 genuine works first, analyzes their imagery, structure, and tone, then composes — citing which original poems informed the result.

## Example

### Search for Li Bai

```bash
grep -rn '"author": "李白"' "$CP/全唐诗/" | head -5
```

Returns:
```json
{"author": "李白", "paragraphs": ["白玉誰家郎，回車渡天津。","看花東上陌，驚動洛陽人。"], "title": "橫吹曲辭 洛陽陌"}
```

### Compose in Li Bai's style (after retrieval)

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

## License

MIT

## Credits

- Poetry dataset: [chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry) — the most comprehensive Chinese classical poetry database
- Inspired by the open-source Chinese poetry community
