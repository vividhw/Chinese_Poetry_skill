---
name: chinese-poetry
description: >
  Search, retrieve, and cite Chinese classical poetry from the
  chinese-poetry/chinese-poetry dataset. Use when the user asks to find Tang
  poems, Song poems, Song Ci, Yuan Qu, Shijing, Chuci, Analects passages, or
  other classical Chinese texts by author, title, content, rhythmic pattern,
  genre, or when composing new Chinese poetry after first grounding the style
  in authentic retrieved works.
---

# Chinese Poetry Skill

Use the `chinese-poetry/chinese-poetry` JSON corpus as the source of truth for
classical Chinese poetry retrieval and grounded style imitation. Do not rely on
memory for exact poem text when the dataset is available.

## Preferred Workflow

1. Locate the dataset root. Prefer an explicit user path, then
   `CHINESE_POETRY_PATH`, then `~/.claude/chinese-poetry-cache`, then
   `~/.cache/chinese-poetry`.
2. Search with `scripts/search_poetry.py` from this skill. It reads one JSON
   file at a time, returns complete works, separates Tang poems from Song poems,
   skips `error/` data, and works on Windows/macOS/Linux.
3. Show at most 5 works unless the user asks for more.
4. Cite the source file returned by the script when presenting retrieved text.
5. For style imitation, retrieve 3-5 relevant works first, analyze imagery,
   form, diction, and emotional tone, then compose. Name the source works used.

## Search Script

Run the script with Python 3:

```bash
python scripts/search_poetry.py --dataset "$CHINESE_POETRY_PATH" --genre tang --author 李白 --limit 5
```

Useful examples:

```bash
# Search Tang poems by author
python scripts/search_poetry.py --genre tang --author 李白 --limit 5

# Search Song Ci by author
python scripts/search_poetry.py --genre ci --author 苏轼 --limit 5

# Search Song Ci by rhythmic pattern
python scripts/search_poetry.py --genre ci --rhythmic 水调歌头 --limit 5

# Search for text across the main corpora
python scripts/search_poetry.py --genre all --text 明月 --limit 5

# Search Shijing by title/content
python scripts/search_poetry.py --genre shijing --title 关雎 --limit 1

# Return structured JSON for further processing
python scripts/search_poetry.py --genre yuanqu --author 关汉卿 --limit 5 --json

# See supported genre keys
python scripts/search_poetry.py --list-genres
```

If the script cannot find the dataset, ask the user to set `CHINESE_POETRY_PATH`
or pass `--dataset <path-to-chinese-poetry>`. If network and filesystem access
are available, the dataset can be installed with:

```bash
git clone --depth 1 https://github.com/chinese-poetry/chinese-poetry.git ~/.cache/chinese-poetry
```

## Genre Keys

| Key | Corpus | Notes |
| --- | --- | --- |
| `tang` | `全唐诗/poet.tang.*.json` | Tang poems only |
| `song-poetry` | `全唐诗/poet.song.*.json` | Song poems only |
| `ci` | `宋词/ci.song.*.json` | Song Ci; use `--rhythmic` for 词牌名 |
| `yuanqu` | `元曲/*.json` | Yuan Qu |
| `shijing` | `诗经/shijing.json` | Uses `content` lines |
| `chuci` | `楚辞/chuci.json` | Uses `content` lines |
| `nalan` | `纳兰性德/*.json` | Uses `para` in some records |
| `five-dynasties` | `五代诗词/*.json` | Five Dynasties poetry |
| `caocao` | `曹操诗集/*.json` | Cao Cao poems |
| `shuimo-tang` | `水墨唐诗/*.json` | Tang poem subset |
| `analects` | `论语/*.json` | Analects passages |
| `all` | Main poetry corpora | Excludes non-literary helper folders |

## Output Format

For retrieved works, use this compact format:

```text
《标题》 — 作者

诗句内容（每行一句）

体裁；来源：path/to/file.json
```

For style imitation:

```text
## 风格分析
- 意象：...
- 句式：...
- 情感：...

## 创作
...

参考原作：《...》《...》《...》
```

## Fallback Grep

Use grep only if Python cannot run. Keep searches narrow, never read the whole
dataset into context, and avoid `全唐诗/error/`.

```bash
grep -rn '"author": "李白"' "$CP/全唐诗"/poet.tang.*.json | head -20
grep -rn '"rhythmic": "水调歌头"' "$CP/宋词"/ci.song.*.json | head -20
grep -rn '明月' "$CP/全唐诗"/poet.tang.*.json | head -20
```

After a grep hit, read only the surrounding local JSON object or rerun the
Python script to print complete works.

## Rules

- Do not fabricate exact poem text when the dataset can be searched.
- Do not load the full 345 MB dataset into context.
- Prefer the Python script over ad hoc shell pipelines.
- Limit displayed results by default.
- Mention when a result came from a subset such as `水墨唐诗` rather than the main corpus.
- For creative writing, make the new poem clearly separate from retrieved source text.
