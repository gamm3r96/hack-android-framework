#!/usr/bin/env python3
"""
framework_api_diff.py - Compare Android API dump files for educational tracking.
Expects standard AOSP `api/*.txt` format.
"""
import re
import sys
from pathlib import Path

API_LINE_RE = re.compile(r"^\s*(package|class|interface|enum|field|method|ctor)\b")

def parse_api(path: Path):
    api_set = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            if API_LINE_RE.match(line):
                api_set.add(line)
    return api_set

def main():
    if len(sys.argv) != 3:
        print("Usage: framework_api_diff.py <old_api.txt> <new_api.txt>")
        sys.exit(1)

    old_path, new_path = Path(sys.argv[1]), Path(sys.argv[2])
    if not old_path.exists() or not new_path.exists():
        print("❌ One or both API dump files not found.")
        sys.exit(1)

    old = parse_api(old_path)
    new = parse_api(new_path)

    added = new - old
    removed = old - new

    print(f"📊 API Surface Diff:")
    print(f"  ➕ Added:   {len(added)} entries")
    print(f"  ➖ Removed: {len(removed)} entries")
    print(f"  ↔️ Unchanged: {len(old & new)} entries")

    if added:
        print("\n📜 Sample Added (first 5):")
        for line in sorted(added)[:5]: print(f"  {line}")
    if removed:
        print("\n📜 Sample Removed (first 5):")
        for line in sorted(removed)[:5]: print(f"  {line}")

    print("\n💡 Tip: Use `development/tools/metalava` for official compatibility checks.")

if __name__ == "__main__":
    main()