#!/usr/bin/env python3
"""Build a chaptered, screenshot-backed draft companion for a reviewed tutorial."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import math
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

from transcript_lookup import load_segments
from visual_transcript_index import digest, regular_file


VERSION = "tutorial_companion.v1"


def _record(path: Path) -> dict:
    return {"path": str(path), "sha256": digest(path), "size_bytes": path.stat().st_size}


def _probe_duration(video: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(video)],
        capture_output=True, text=True, check=True,
    )
    duration = float(result.stdout.strip())
    if not math.isfinite(duration) or duration <= 0:
        raise ValueError("video needs a finite positive duration")
    return duration


def _chapters(path: Path, duration: float) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("version") != "chapter_markers.v1":
        raise ValueError("chapters must come from chapter_markers.py")
    chapters = payload.get("chapters")
    if not isinstance(chapters, list) or not 1 <= len(chapters) <= 24:
        raise ValueError("chapters must contain 1–24 entries")
    previous_end = 0.0
    ids = set()
    for position, chapter in enumerate(chapters, 1):
        if not isinstance(chapter, dict):
            raise ValueError(f"chapter {position} must be an object")
        identifier, title = chapter.get("id"), chapter.get("title")
        if not isinstance(identifier, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,40}", identifier) or identifier in ids:
            raise ValueError(f"chapter {position} has an invalid or repeated id")
        ids.add(identifier)
        if not isinstance(title, str) or not title.strip() or len(title) > 120:
            raise ValueError(f"chapter {position} needs a short title")
        try:
            start, end = float(chapter["start"]), float(chapter["end"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"chapter {position} needs numeric start/end") from exc
        if not all(math.isfinite(x) for x in (start, end)) or start < previous_end - 0.001 or end <= start or end > duration + 0.1:
            raise ValueError(f"chapter {position} has invalid timing")
        previous_end = end
    return chapters


def _choices(values: list[str], chapters: list[dict]) -> dict[str, float]:
    ranges = {item["id"]: (float(item["start"]), float(item["end"])) for item in chapters}
    chosen = {}
    for value in values:
        identifier, separator, stamp = value.partition("=")
        if not separator or identifier not in ranges or identifier in chosen:
            raise ValueError("--at needs a unique existing CHAPTER_ID=SECONDS")
        second = float(stamp)
        start, end = ranges[identifier]
        if not math.isfinite(second) or not start <= second < end:
            raise ValueError(f"screenshot time for {identifier} must be inside its chapter")
        chosen[identifier] = second
    return chosen


def _safe(text: str) -> str:
    escaped = html.escape(text.replace("\n", " ").replace("\r", " ").strip(), quote=False)
    return re.sub(r"([\\`*_{}\[\]()#+!|>])", r"\\\1", escaped)


def _markdown(title: str, video: Path, rows: list[dict]) -> str:
    lines = [f"# {_safe(title)}", "", f"Video: `{video}`", "",
             "Draft companion. Check each screenshot and step against the video before sharing.", ""]
    for row in rows:
        image = quote(row["image"], safe="/")
        lines.extend([
            f"## {_safe(row['title'])} ({row['start']:.3f}–{row['end']:.3f}s)", "",
            f"![Video sample at {row['screenshot_at']:.3f}s]({image})", "",
            f"Screenshot sampled at {row['screenshot_at']:.3f}s. Check that it shows the intended step.", "",
        ])
        if row["description"]:
            lines.extend([_safe(row["description"]), ""])
        lines.extend(["Nearby spoken text:", ""])
        for segment in row["speech"]:
            lines.append(f"- {segment['start']:.3f}–{segment['end']:.3f}s: {_safe(segment['text'])}")
        if not row["speech"]:
            lines.append("- No transcript segment in this chapter.")
        if row["speech_omitted"]:
            lines.append(f"- {row['speech_omitted']} further transcript segments omitted; review the source transcript.")
        lines.append("")
    return "\n".join(lines)


def _extract(video: Path, second: float, destination: Path) -> None:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostdin", "-v", "error", "-i", str(video),
         "-ss", f"{second:.6f}", "-map", "0:v:0", "-frames:v", "1",
         "-vf", "scale='min(960,iw)':-2:flags=lanczos", "-threads", "1", str(destination)],
        capture_output=True, text=True,
    )
    if result.returncode or not destination.is_file() or not destination.stat().st_size:
        raise ValueError(f"could not extract screenshot at {second:.3f}s: {result.stderr[-300:]}")


def build(video: Path, chapters_path: Path, transcript_path: Path, output: Path,
          *, title: str, at: list[str]) -> dict:
    video = regular_file(video, "video")
    chapters_path = regular_file(chapters_path, "chapters")
    transcript_path = regular_file(transcript_path, "transcript")
    if not title.strip() or len(title) > 120:
        raise ValueError("title must contain 1–120 characters")
    if output.exists() or output.is_symlink():
        raise ValueError("output directory already exists")
    duration = _probe_duration(video)
    chapters = _chapters(chapters_path, duration)
    segments, _ = load_segments(transcript_path)
    if any(item["end"] > duration + 0.25 for item in segments):
        raise ValueError("transcript extends beyond video")
    chosen = _choices(at, chapters)
    before = [_record(path) for path in (video, chapters_path, transcript_path)]
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".tutorial-companion-", dir=output.parent) as temporary:
        bundle = Path(temporary)
        frames = bundle / "frames"
        frames.mkdir()
        rows = []
        for position, chapter in enumerate(chapters, 1):
            start, end = float(chapter["start"]), float(chapter["end"])
            second = chosen.get(chapter["id"], (start + end) / 2)
            image_name = f"frames/{position:02d}-{chapter['id']}.png"
            image_path = bundle / image_name
            _extract(video, second, image_path)
            speech = [item for item in segments if item["start"] < end and item["end"] > start]
            rows.append({
                "id": chapter["id"], "title": chapter["title"],
                "description": str(chapter.get("description", "")).strip()[:1000],
                "start": start, "end": end, "screenshot_at": second,
                "image": image_name, "image_sha256": digest(image_path),
                "speech": [{"start": item["start"], "end": item["end"], "text": item["text"][:300]}
                           for item in speech[:6]],
                "speech_omitted": max(0, len(speech) - 6),
            })
        if before != [_record(path) for path in (video, chapters_path, transcript_path)]:
            raise ValueError("source bytes changed during build")
        notes = _markdown(title, video, rows)
        (bundle / "companion.md").write_text(notes, encoding="utf-8")
        receipt = {"version": VERSION, "title": title, "sources": before,
                   "duration": duration, "choices": chosen, "rows": rows,
                   "markdown_sha256": digest(bundle / "companion.md")}
        receipt["receipt_sha256"] = hashlib.sha256(json.dumps(receipt, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
        (bundle / "receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        bundle.rename(output)
    return receipt


def verify(receipt_path: Path) -> dict:
    receipt_path = regular_file(receipt_path, "receipt")
    data = json.loads(receipt_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != VERSION:
        raise ValueError("unsupported companion receipt")
    claimed = data.pop("receipt_sha256", None)
    actual = hashlib.sha256(json.dumps(data, sort_keys=True, ensure_ascii=False).encode()).hexdigest()
    if claimed != actual:
        raise ValueError("receipt changed")
    source_paths = [regular_file(Path(item["path"]), "source") for item in data["sources"]]
    if [_record(path) for path in source_paths] != data["sources"]:
        raise ValueError("source bytes changed")
    video, chapters_path, transcript_path = source_paths
    if abs(_probe_duration(video) - data["duration"]) > 0.001:
        raise ValueError("video duration changed")
    chapters = _chapters(chapters_path, data["duration"])
    segments, _ = load_segments(transcript_path)
    if _choices([f"{key}={value}" for key, value in data["choices"].items()], chapters) != data["choices"]:
        raise ValueError("screenshot choices changed")
    if len(chapters) != len(data["rows"]):
        raise ValueError("chapter rows changed")
    for position, (chapter, row) in enumerate(zip(chapters, data["rows"]), 1):
        start, end = float(chapter["start"]), float(chapter["end"])
        speech = [item for item in segments if item["start"] < end and item["end"] > start]
        expected = {"id": chapter["id"], "title": chapter["title"],
                    "description": str(chapter.get("description", "")).strip()[:1000],
                    "start": start, "end": end,
                    "screenshot_at": data["choices"].get(chapter["id"], (start + end) / 2),
                    "image": f"frames/{position:02d}-{chapter['id']}.png",
                    "image_sha256": row["image_sha256"],
                    "speech": [{"start": item["start"], "end": item["end"], "text": item["text"][:300]}
                               for item in speech[:6]],
                    "speech_omitted": max(0, len(speech) - 6)}
        if row != expected:
            raise ValueError("chapter or transcript mapping changed")
        picture = regular_file(receipt_path.parent / row["image"], "screenshot")
        if digest(picture) != row["image_sha256"]:
            raise ValueError("screenshot bytes changed")
    notes = regular_file(receipt_path.parent / "companion.md", "Markdown companion")
    if notes.read_text(encoding="utf-8") != _markdown(data["title"], video, data["rows"]) or digest(notes) != data["markdown_sha256"]:
        raise ValueError("companion Markdown changed")
    return {"status": "ready_for_human_review", "chapters": len(chapters)}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    create = commands.add_parser("build")
    create.add_argument("video", type=Path)
    create.add_argument("chapters", type=Path)
    create.add_argument("transcript", type=Path)
    create.add_argument("--output", type=Path, required=True)
    create.add_argument("--title", required=True)
    create.add_argument("--at", action="append", default=[], metavar="CHAPTER_ID=SECONDS")
    check = commands.add_parser("verify")
    check.add_argument("receipt", type=Path)
    args = parser.parse_args()
    try:
        result = (build(args.video, args.chapters, args.transcript, args.output, title=args.title, at=args.at)
                  if args.command == "build" else verify(args.receipt))
        print(json.dumps(result if args.command == "verify" else {"status": "draft_created", "chapters": len(result["rows"])}))
    except (OSError, UnicodeError, KeyError, TypeError, ValueError, json.JSONDecodeError,
            subprocess.CalledProcessError) as exc:
        parser.exit(2, f"tutorial_companion: {exc}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
