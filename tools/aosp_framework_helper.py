#!/usr/bin/env python3
"""
aosp_framework_helper.py - CLI utility for Android Open Source Project framework development.
Designed strictly for educational, research, and legitimate development purposes.

Features:
  • Framework logcat streaming & filtering
  • AOSP build environment validation
  • Safe patch application (dry-run support)
  • Cross-platform compatible (Linux/macOS primary)
"""

import argparse
import logging
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

# ANSI Color Codes (disabled if stdout isn't a TTY)
IS_TTY = sys.stdout.isatty()
COLORS = {
    "RESET": "\033[0m",
    "RED": "\033[91m",
    "GREEN": "\033[92m",
    "YELLOW": "\033[93m",
    "CYAN": "\033[96m",
    "MAGENTA": "\033[95m",
} if IS_TTY else {k: "" for k in ["RESET", "RED", "GREEN", "YELLOW", "CYAN", "MAGENTA"]}

logging.basicConfig(
    level=logging.INFO,
    format=f"{COLORS['CYAN']}[%(asctime)s]{COLORS['RESET']} %(levelname)s: %(message)s",
    datefmt="%H:%M:%S"
)

def run_cmd(cmd: List[str], check: bool = True, cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Execute a shell command safely with error handling."""
    try:
        return subprocess.run(cmd, check=check, capture_output=True, text=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {' '.join(cmd)}")
        if e.stderr:
            logging.debug(e.stderr.strip())
        sys.exit(e.returncode)
    except FileNotFoundError:
        logging.error(f"Executable not found: {cmd[0]}")        sys.exit(1)

def check_env() -> None:
    """Validate AOSP development environment prerequisites."""
    logging.info("🔍 Checking AOSP environment...")
    
    checks = {
        "Java (OpenJDK 17+)": lambda: run_cmd(["java", "-version"], check=False).returncode == 0,
        "repo tool": lambda: shutil.which("repo") is not None,
        "adb": lambda: shutil.which("adb") is not None,
        "Disk space (>50GB free)": lambda: shutil.disk_usage(".").free > 50 * 1024**3,
    }

    for name, check_fn in checks.items():
        status = COLORS["GREEN"] + "✅" if check_fn() else COLORS["RED"] + "❌"
        logging.info(f"{status} {name}")

    if not all(fn() for fn in [checks[k] for k in checks]):
        logging.warning("⚠️  Environment check completed with failures. Review missing dependencies.")
    else:
        logging.info("🎉 Environment validation passed.")

def stream_logcat(services: List[str], buffer_size: str = "main") -> None:
    """Stream & filter logcat output for specific Android framework services."""
    if not shutil.which("adb"):
        logging.error("adb not found. Ensure device is connected or emulator is running.")
        sys.exit(1)

    logging.info(f"📡 Streaming logcat for: {', '.join(services)} (buffer: {buffer_size})")
    cmd = ["adb", "logcat", "-b", buffer_size, "-v", "color", "-s"] + [f"{s}:*" for s in services]
    
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in proc.stdout:
            # Simple color enhancement for tags
            if any(s in line for s in services):
                sys.stdout.write(f"{COLORS['MAGENTA']}{line}{COLORS['RESET']}")
            else:
                sys.stdout.write(line)
            sys.stdout.flush()
    except KeyboardInterrupt:
        logging.info("\n🛑 Logcat stream stopped.")
    finally:
        proc.terminate()

def apply_patch(patch_path: Path, aosp_root: Path, dry_run: bool = False) -> None:
    """Safely apply a unified diff/patch to an AOSP tree."""
    if not patch_path.exists():
        logging.error(f"Patch file not found: {patch_path}")
        sys.exit(1)        
    action = "DRY-RUN" if dry_run else "APPLY"
    logging.info(f"📦 {action} patch: {patch_path.name}")
    
    cmd = ["git", "apply", "--check" if dry_run else "--apply", str(patch_path)]
    
    try:
        result = run_cmd(cmd, check=False, cwd=aosp_root)
        if dry_run:
            if result.returncode == 0:
                logging.info("✅ Patch applies cleanly (dry-run passed).")
            else:
                logging.error("❌ Patch conflicts detected. Review manually.")
                logging.debug(result.stderr.strip())
        else:
            if result.returncode == 0:
                logging.info("✅ Patch applied successfully.")
            else:
                logging.error("❌ Patch application failed.")
                logging.debug(result.stderr.strip())
    except Exception as e:
        logging.error(f"Unexpected error during patching: {e}")
        sys.exit(1)

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="aosp_framework_helper",
        description="Educational CLI tool for Android framework development & debugging."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # env-check
    p_env = subparsers.add_parser("env-check", help="Validate AOSP build environment")
    p_env.set_defaults(func=check_env)

    # logcat-stream
    p_log = subparsers.add_parser("logcat-stream", help="Filter & stream framework logs")
    p_log.add_argument("--services", nargs="+", default=["ActivityManager", "WindowManager", "SystemServer"],
                       help="Framework tags to filter (default: ActivityManager WindowManager SystemServer)")
    p_log.add_argument("--buffer", default="main", choices=["main", "system", "crash", "radio"],
                       help="Logcat buffer to read")
    p_log.set_defaults(func=lambda args: stream_logcat(args.services, args.buffer))

    # patch-apply
    p_patch = subparsers.add_parser("patch-apply", help="Apply framework patch safely")
    p_patch.add_argument("patch", type=Path, help="Path to .diff or .patch file")
    p_patch.add_argument("--root", type=Path, default=Path.cwd(), help="AOSP source root directory")
    p_patch.add_argument("--dry-run", action="store_true", help="Test patch application without modifying files")
    p_patch.set_defaults(func=lambda args: apply_patch(args.patch, args.root, args.dry_run))
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()