#!/usr/bin/env python3
"""Search the chinese-poetry/chinese-poetry JSON corpus without loading it all."""

from __future__ import annotations

import argparse
import json
import os
import random
import sys
from pathlib import Path
from typing import Any, Iterable


GENRES: dict[str, dict[str, Any]] = {
    "tang": {
        "label": "唐诗",
        "dirs": ["全唐诗"],
        "patterns": ["poet.tang.*.json"],
    },
    "song-poetry": {
        "label": "宋诗",
        "dirs": ["全唐诗"],
        "patterns": ["poet.song.*.json"],
    },
    "ci": {
        "label": "宋词",
        "dirs": ["宋词"],
        "patterns": ["ci.song.*.json"],
    },
    "yuanqu": {
        "label": "元曲",
        "dirs": ["元曲"],
        "patterns": ["*.json"],
    },
    "shijing": {
        "label": "诗经",
        "dirs": ["诗经"],
        "patterns": ["shijing.json"],
    },
    "chuci": {
        "label": "楚辞",
        "dirs": ["楚辞"],
        "patterns": ["chuci.json"],
    },
    "nalan": {
        "label": "纳兰性德",
        "dirs": ["纳兰性德"],
        "patterns": ["*.json"],
    },
    "five-dynasties": {
        "label": "五代诗词",
        "dirs": ["五代诗词"],
        "patterns": ["*.json"],
    },
    "caocao": {
        "label": "曹操诗集",
        "dirs": ["曹操诗集"],
        "patterns": ["*.json"],
    },
    "shuimo-tang": {
        "label": "水墨唐诗",
        "dirs": ["水墨唐诗"],
        "patterns": ["*.json"],
    },
    "analects": {
        "label": "论语",
        "dirs": ["论语"],
        "patterns": ["*.json"],
    },
}

DEFAULT_GENRES = [
    "tang",
    "song-poetry",
    "ci",
    "yuanqu",
    "shijing",
    "chuci",
    "nalan",
    "five-dynasties",
    "caocao",
    "shuimo-tang",
]


def expand_user(path: str) -> Path:
    return Path(path).expanduser().resolve()


def find_dataset(explicit: str | None) -> Path:
    candidates: list[Path] = []
    if explicit:
        candidates.append(expand_user(explicit))
    if os.environ.get("CHINESE_POETRY_PATH"):
        candidates.append(expand_user(os.environ["CHINESE_POETRY_PATH"]))

    candidates.extend(
        [
            expand_user("~/.claude/chinese-poetry-cache"),
            expand_user("~/.cache/chinese-poetry"),
            Path.cwd(),
        ]
    )

    for path in candidates:
        if (path / "全唐诗").is_dir() and (path / "宋词").is_dir():
            return path

    searched = "\n".join(f"  - {path}" for path in candidates)
    raise SystemExit(
        "Could not find the chinese-poetry dataset.\n"
        "Set CHINESE_POETRY_PATH or pass --dataset.\n"
        "Searched:\n"
        f"{searched}"
    )


def iter_json_files(dataset: Path, genre: str) -> Iterable[tuple[str, Path]]:
    if genre == "all":
        for key in DEFAULT_GENRES:
            yield from iter_json_files(dataset, key)
        return

    config = GENRES[genre]
    for dirname in config["dirs"]:
        root = dataset / dirname
        if not root.exists():
            continue
        for pattern in config["patterns"]:
            for path in sorted(root.glob(pattern)):
                if path.is_file() and "error" not in path.parts:
                    yield config["label"], path


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def iter_records(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, list):
        for item in value:
            yield from iter_records(item)
    elif isinstance(value, dict):
        if any(key in value for key in ("paragraphs", "content", "para", "title", "rhythmic")):
            yield value
        else:
            for item in value.values():
                yield from iter_records(item)


def as_lines(record: dict[str, Any]) -> list[str]:
    for key in ("paragraphs", "content", "para"):
        value = record.get(key)
        if isinstance(value, list):
            return [str(item) for item in value]
        if isinstance(value, str):
            return [value]
    return []


def text_value(value: Any) -> str:
    return "" if value is None else str(value)


def record_matches(record: dict[str, Any], args: argparse.Namespace) -> bool:
    author = text_value(record.get("author"))
    title = text_value(record.get("title") or record.get("rhythmic") or record.get("chapter"))
    rhythmic = text_value(record.get("rhythmic"))
    lines = "\n".join(as_lines(record))

    checks = [
        (args.author, author),
        (args.title, title),
        (args.text, "\n".join([title, rhythmic, lines])),
        (args.rhythmic, rhythmic),
    ]
    return all(query in target for query, target in checks if query)


def normalize(record: dict[str, Any], genre_label: str, path: Path, dataset: Path) -> dict[str, Any]:
    title = text_value(record.get("title") or record.get("rhythmic") or record.get("chapter") or "无题")
    author = text_value(record.get("author") or "佚名")
    return {
        "title": title,
        "author": author,
        "rhythmic": text_value(record.get("rhythmic")),
        "chapter": text_value(record.get("chapter")),
        "section": text_value(record.get("section")),
        "dynasty": text_value(record.get("dynasty")),
        "genre": genre_label,
        "lines": as_lines(record),
        "source": str(path.relative_to(dataset)),
    }


def search(dataset: Path, args: argparse.Namespace) -> list[dict[str, Any]]:
    matches: list[dict[str, Any]] = []
    for genre_label, path in iter_json_files(dataset, args.genre):
        try:
            data = load_json(path)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"Warning: skipped {path}: {exc}", file=sys.stderr)
            continue

        for record in iter_records(data):
            if record_matches(record, args):
                matches.append(normalize(record, genre_label, path, dataset))
                if not args.random and len(matches) >= args.limit:
                    return matches

    if args.random and len(matches) > args.limit:
        return random.sample(matches, args.limit)
    return matches


def format_markdown(results: list[dict[str, Any]]) -> str:
    if not results:
        return "No matching poems found."

    blocks: list[str] = []
    for item in results:
        heading = f"《{item['title']}》 — {item['author']}"
        meta = [item["genre"]]
        if item.get("rhythmic"):
            meta.append(f"词牌：{item['rhythmic']}")
        if item.get("section"):
            meta.append(f"篇章：{item['section']}")
        if item.get("chapter"):
            meta.append(f"卷/章：{item['chapter']}")
        meta.append(f"来源：{item['source']}")
        lines = "\n".join(item["lines"]) if item["lines"] else "(no poem lines found)"
        blocks.append(f"{heading}\n\n{lines}\n\n{'；'.join(meta)}")
    return "\n\n---\n\n".join(blocks)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Search chinese-poetry/chinese-poetry JSON files and print complete works."
    )
    parser.add_argument("--dataset", help="Path to chinese-poetry dataset root.")
    parser.add_argument(
        "--genre",
        default="all",
        choices=["all", *GENRES.keys()],
        help="Corpus to search. Use all for the main poetry corpora.",
    )
    parser.add_argument("--author", help="Author name substring, e.g. 李白.")
    parser.add_argument("--title", help="Title substring.")
    parser.add_argument("--text", help="Substring to search in title, rhythmic name, and poem lines.")
    parser.add_argument("--rhythmic", help="Song Ci rhythmic pattern substring, e.g. 水调歌头.")
    parser.add_argument("--limit", type=int, default=5, help="Maximum number of results to print.")
    parser.add_argument("--random", action="store_true", help="Randomly sample matches after scanning.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of Markdown.")
    parser.add_argument("--list-genres", action="store_true", help="List supported genre keys and exit.")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.list_genres:
        for key, config in GENRES.items():
            print(f"{key}\t{config['label']}")
        return 0

    if args.limit < 1:
        parser.error("--limit must be at least 1")
    if not any([args.author, args.title, args.text, args.rhythmic, args.random]):
        parser.error("Provide at least one search option: --author, --title, --text, --rhythmic, or --random")

    dataset = find_dataset(args.dataset)
    results = search(dataset, args)
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(format_markdown(results))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
