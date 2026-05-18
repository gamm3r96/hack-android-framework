#!/usr/bin/env python3
"""
soong_build_inspector.py - Static analyzer for Android.bp Soong files.
Educational use only. Not a replacement for `soong` or `bpfmt`.
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

MODULE_START_RE = re.compile(r"^(\w[\w_]*)\s*\{\s*$")
NAME_RE = re.compile(r'name:\s*"([^"]+)"')
DEP_KEYS = ["static_libs", "shared_libs", "deps", "java_libs", "header_libs"]
DEP_RE = re.compile(r"(" + "|".join(DEP_KEYS) + r"):\s*\[(.*?)\]", re.DOTALL)

def parse_bp(content: str):
    modules = []
    current = None
    in_block = False
    depth = 0

    for line in content.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("//"):
            continue
        if not in_block and MODULE_START_RE.match(stripped):
            current = {"type": MODULE_START_RE.match(stripped).group(1), "name": "", "deps": [], "srcs": []}
            in_block = True
            depth = 1
            continue
        if in_block:
            depth += stripped.count("{") - stripped.count("}")
            if depth <= 0:
                if current and current["name"]:
                    modules.append(current)
                current = None
                in_block = False
                continue
            nm = NAME_RE.search(stripped)
            if nm: current["name"] = nm.group(1)
            dm = DEP_RE.search(stripped)
            if dm:
                deps = [d.strip().strip('",') for d in dm.group(2).split(",") if d.strip()]
                current["deps"].extend(deps)
            # Optional: extract srcs if needed
    return modules

def main():
    if len(sys.argv) < 2:
        print("Usage: soong_build_inspector.py <Android.bp> or <directory>")
        sys.exit(1)

    target = Path(sys.argv[1])
    files = list(target.rglob("Android.bp")) if target.is_dir() else [target]
    
    dep_freq = defaultdict(int)
    mod_count = 0
    skipped = 0

    for f in files:
        try:
            mods = parse_bp(f.read_text())
            mod_count += len(mods)
            for m in mods:
                for d in m["deps"]:
                    dep_freq[d] += 1
        except Exception as e:
            skipped += 1

    print(f"📦 Parsed {mod_count} modules across {len(files)} files ({skipped} skipped)")
    print("\n🔗 Top 10 Dependencies:")
    for dep, count in sorted(dep_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {dep} → used {count} times")
    print("\n💡 Tip: Run `m graphviz` or `development/tools/make_build_graph.py` for full visualization.")

if __name__ == "__main__":
    main()