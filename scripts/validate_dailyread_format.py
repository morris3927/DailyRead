#!/usr/bin/env python3
"""Validate DailyRead domain note entries keep the required explanatory headings."""
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path

REQUIRED = [
    "這篇在說什麼",
    "主要貢獻",
    "方法 / pipeline",
    "實驗設計",
    "かに讀後判斷",
]
DOMAINS = [
    "silicon-sampling-social-simulation",
    "harness-engineering",
    "agent-memory",
]
ENTRY_RE = re.compile(r"(?m)^##\s+\d+\.\s+.+$")

def entries(text: str):
    matches = list(ENTRY_RE.finditer(text))
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        yield m.group(0), text[start:end]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("date", help="YYYY-MM-DD")
    ap.add_argument("--root", default=".", help="DailyRead repo root")
    ap.add_argument("--domain", action="append", choices=DOMAINS, help="Validate only this domain; may be repeated")
    args = ap.parse_args()
    root = Path(args.root)
    errors: list[str] = []
    domains = args.domain or DOMAINS
    for domain in domains:
        path = root / domain / f"{args.date}.md"
        if not path.exists():
            errors.append(f"missing file: {path}")
            continue
        text = path.read_text(encoding="utf-8")
        found = list(entries(text))
        if not found:
            # Allow explicit no-candidate notes.
            if "無高品質候選" in text or "無強力新候選" in text:
                continue
            errors.append(f"{path}: no numbered paper/article entries found")
            continue
        for title, body in found:
            for heading in REQUIRED:
                if not re.search(rf"(?m)^###\s+{re.escape(heading)}\s*$", body):
                    errors.append(f"{path}: {title} missing heading: ### {heading}")
    if errors:
        print("DailyRead format validation FAILED", file=sys.stderr)
        for e in errors:
            print(f"- {e}", file=sys.stderr)
        return 1
    print(f"DailyRead format validation OK for {args.date}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
