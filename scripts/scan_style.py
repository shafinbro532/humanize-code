#!/usr/bin/env python3
"""Humanize Code style scanner CLI.

Usage:
    python scripts/scan_style.py [PATH] --out humanize-out
    python scripts/scan_style.py . --lang python,javascript --exclude vendor,dist
    python scripts/scan_style.py . --json-only
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from humanize_scan import __version__
from humanize_scan.report import parse_excludes, parse_languages, scan_path, write_reports


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="scan_style.py",
        description="Scan code for human-vs-generated style signals.",
    )
    parser.add_argument("path", nargs="?", default=".", help="file or directory to scan")
    parser.add_argument(
        "--out", default="humanize-out",
        help="output directory (default: humanize-out)",
    )
    parser.add_argument(
        "--lang", default="all",
        help="comma-separated languages: python, javascript, php, c, cpp, java, generic",
    )
    parser.add_argument(
        "--exclude", default="",
        help="comma-separated paths or glob patterns to skip",
    )
    parser.add_argument(
        "--max-file-size", type=int, default=1024,
        help="maximum file size in KB (default: 1024)",
    )
    parser.add_argument(
        "--json-only", action="store_true",
        help="write scan.json but not scan.md",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress the summary")
    parser.add_argument("--version", action="version", version=f"humanize-code {__version__}")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    root = Path(args.path)
    if not root.exists():
        parser.error(f"path does not exist: {root}")
    try:
        languages = parse_languages(args.lang)
    except ValueError as exc:
        parser.error(str(exc))
    excludes = parse_excludes(args.exclude)

    scan = scan_path(
        root,
        languages=languages,
        excludes=excludes,
        max_file_size_kb=args.max_file_size,
    )
    out_dir = Path(args.out)
    json_path, md_path = write_reports(scan, out_dir, json_only=args.json_only)

    if not args.quiet:
        summary = scan["summary"]
        print(f"Humanize Code {__version__}")
        print(
            f"Scanned {summary['files']} files ({summary['loc']} LOC) in "
            f"{summary['duration_seconds']}s"
        )
        print(f"Score {summary['score']:.1f}/100 ({summary['class']})")
        print(
            f"AI-shaped: {summary['ai_shaped']} | mixed: {summary['mixed']} | "
            f"human-shaped: {summary['human_shaped']}"
        )
        if summary["skipped"]:
            print(f"Skipped: {summary['skipped']} files")
        if summary["errors"]:
            print(f"Errors: {summary['errors']} files (see scan.json)")
        print(f"JSON: {json_path}")
        if not args.json_only:
            print(f"Report: {md_path}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        sys.exit(0)
