#!/usr/bin/env python3
"""
binder_trace_parser.py - Educational Binder IPC log analyzer.
Parses standard `logcat -b binder` or `logcat | grep binder` output.
"""
import re
import sys
import json
from collections import Counter
from pathlib import Path

# Matches common Android binder transaction log lines
BINDER_TXN_RE = re.compile(
    r"binder:\s+(?P<pid>\d+):(?P<tid>\d+)\s+transaction\s+(?P<txn_id>\d+)\s+from\s+(?P<src>\d+:\d+)\s+to\s+(?P<dst>\d+:\d+)"
)

def parse_log(path: Path):
    txns = []
    dst_counter = Counter()
    src_counter = Counter()
    warnings = []

    with open(path, encoding="utf-8", errors="ignore") as f:
        for i, line in enumerate(f, 1):
            m = BINDER_TXN_RE.search(line)
            if not m:
                continue
            txns.append(m.groupdict())
            dst_counter[m.group("dst")] += 1
            src_counter[m.group("src")] += 1
            if i % 5000 == 0 and len(txns) > i * 0.8:
                warnings.append(f"⚠️ High binder volume at line {i} ({len(txns)} transactions)")

    return txns, dst_counter, src_counter, warnings

def main():
    if len(sys.argv) < 2:
        print("Usage: binder_trace_parser.py <log_file> [--json]")
        sys.exit(1)

    log_path = Path(sys.argv[1])
    if not log_path.exists():
        print(f"❌ File not found: {log_path}")
        sys.exit(1)

    txns, dsts, srcs, warns = parse_log(log_path)
    json_mode = "--json" in sys.argv

    if json_mode:
        print(json.dumps({
            "total_transactions": len(txns),
            "top_targets": dsts.most_common(10),
            "top_sources": srcs.most_common(10),
            "warnings": warns
        }, indent=2))
        return

    print(f"📊 Binder IPC Analysis: {len(txns)} transactions parsed")
    print("\n🔝 Top Target PIDs (most called):")
    for pid, count in dsts.most_common(8):
        print(f"  {pid} → {count} calls")
    print("\n🔙 Top Source PIDs (most active):")
    for pid, count in srcs.most_common(8):
        print(f"  {pid} → {count} calls")
    if warns:
        print("\n⚠️ Warnings:")
        for w in warns: print(f"  {w}")
    print("\n💡 Tip: Map PIDs to services using `adb shell ps -A` or `dumpsys binder`")

if __name__ == "__main__":
    main()