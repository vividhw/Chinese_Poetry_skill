# Chinese Poetry Skill

A skill for searching, retrieving, citing, and composing Chinese classical
poetry with the [chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry)
dataset as the source of truth.

The skill now includes a cross-platform Python search script, so agents no
longer need to hand-roll fragile `grep` pipelines or read large JSON files into
context.

## What It Does

- Search by author, title, content, and Song Ci rhythmic pattern.
- Search specific corpora: Tang poems, Song poems, Song Ci, Yuan Qu, Shijing,
  Chuci, Nalan Xingde, Five Dynasties poetry, Cao Cao poems, and more.
- Return complete works with source file paths.
- Keep Tang poetry and Song poetry separate inside `全唐诗/`.
- Skip `error/` data in the upstream dataset.
- Retrieve real examples before composing in a poet's style.

## Files

```text
SKILL.md
scripts/search_poetry.py
_meta.json
README.md
README_CN.md
```

## Install

Copy the skill folder into your skills directory, keeping the `scripts/`
directory intact:

```bash
mkdir -p ~/.agents/skills/chinese-poetry-1.1.0/
cp -R SKILL.md scripts _meta.json ~/.agents/skills/chinese-poetry-1.1.0/
```

## Dataset

Download or clone the dataset separately:

```bash
git clone --depth 1 https://github.com/chinese-poetry/chinese-poetry.git ~/.cache/chinese-poetry
```

Then either set:

```bash
export CHINESE_POETRY_PATH=~/.cache/chinese-poetry
```

or pass the path explicitly:

```bash
python scripts/search_poetry.py --dataset ~/.cache/chinese-poetry --genre tang --author 李白 --limit 5
```

## Search Examples

```bash
# Tang poems by Li Bai
python scripts/search_poetry.py --genre tang --author 李白 --limit 5

# Song Ci by Su Shi
python scripts/search_poetry.py --genre ci --author 苏轼 --limit 5

# Song Ci by rhythmic pattern
python scripts/search_poetry.py --genre ci --rhythmic 水调歌头 --limit 5

# Text search across the main poetry corpora
python scripts/search_poetry.py --genre all --text 明月 --limit 5

# Structured JSON output
python scripts/search_poetry.py --genre shijing --title 关雎 --limit 1 --json
```

## Supported Genre Keys

| Key | Corpus |
| --- | --- |
| `tang` | Tang poems: `全唐诗/poet.tang.*.json` |
| `song-poetry` | Song poems: `全唐诗/poet.song.*.json` |
| `ci` | Song Ci: `宋词/ci.song.*.json` |
| `yuanqu` | Yuan Qu |
| `shijing` | Book of Songs |
| `chuci` | Songs of Chu |
| `nalan` | Nalan Xingde |
| `five-dynasties` | Five Dynasties poetry |
| `caocao` | Cao Cao poems |
| `shuimo-tang` | Shui Mo Tang poems subset |
| `analects` | Analects |
| `all` | Main poetry corpora |

## Design Notes

The upstream dataset is hundreds of MB of JSON. The skill should never load it
all into model context. `scripts/search_poetry.py` loads one JSON file at a
time, normalizes common fields (`paragraphs`, `content`, `para`, `rhythmic`),
and prints only the matching complete works.

## License

MIT. Dataset credit: [chinese-poetry/chinese-poetry](https://github.com/chinese-poetry/chinese-poetry).
