#!/usr/bin/env python3
"""
adb_framework_manager.py - Educational ADB automation for Android framework development.
Focus: Safe testing, backups, service control, and log collection.
"""
import argparse
import subprocess
import sys
import shutil
import time
from pathlib import Path

COLORS = {
    "RESET": "\033[0m", "RED": "\033[91m", "GREEN": "\033[92m",
    "YELLOW": "\033[93m", "CYAN": "\033[96m", "BOLD": "\033[1m"
}
IS_TTY = sys.stdout.isatty()

def log(msg, level="INFO"):
    prefix = {"INFO": f"{COLORS['CYAN']}ℹ️{COLORS['RESET']}", "WARN": f"{COLORS['YELLOW']}⚠️{COLORS['RESET']}", 
              "ERROR": f"{COLORS['RED']}❌{COLORS['RESET']}", "OK": f"{COLORS['GREEN']}✅{COLORS['RESET']}"}[level]
    print(f"{prefix} {msg}" if IS_TTY else f"[{level}] {msg}")

def run(cmd, check=True, silent=False):
    if not silent: log(f"🔧 {' '.join(cmd)}", "INFO")
    try:
        return subprocess.run(cmd, check=check, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        log(f"Command failed: {e.stderr.strip()}", "ERROR")
        sys.exit(e.returncode)
    except FileNotFoundError:
        log("adb not found. Install Android Platform Tools.", "ERROR")
        sys.exit(1)

def require_device():
    res = run(["adb", "devices"], silent=True)
    devices = [l for l in res.stdout.splitlines()[1:] if l.strip() and "device" in l]
    if not devices:
        log("No device connected or authorized.", "ERROR")
        sys.exit(1)
    return devices[0].split()[0]

def cmd_check(args):
    dev = require_device()
    log(f"Connected: {dev}", "OK")
    build_type = run(["adb", "shell", "getprop", "ro.build.type"], silent=True).stdout.strip()
    log(f"Build type: {build_type}", "OK")
    if build_type == "user":
        log("⚠️  USER builds restrict system modifications. Use USERDEBUG or ENG for framework work.", "WARN")
def cmd_pull(args):
    require_device()
    src = args.remote
    dst = Path(args.local) if args.local else Path(f"./pull_{Path(src).name}")
    backup = dst.with_suffix(dst.suffix + ".bak")
    
    if dst.exists() and not backup.exists():
        log("Creating backup before overwrite...", "WARN")
        shutil.copy2(dst, backup)
        
    log(f"Pulling {src} → {dst}")
    run(["adb", "pull", src, str(dst)])
    log("Pull complete.", "OK")

def cmd_push(args):
    require_device()
    src = Path(args.local)
    if not src.exists():
        log(f"Local file not found: {src}", "ERROR"); sys.exit(1)
        
    dst = args.remote
    log(f"Pushing {src} → {dst}")
    run(["adb", "root"])
    run(["adb", "remount"])
    run(["adb", "push", str(src), dst])
    log("Push complete. Restarting affected services...", "INFO")
    cmd_restart(args)

def cmd_restart(args):
    require_device()
    log("Restarting framework services (safe sequence)...")
    run(["adb", "shell", "stop"])
    time.sleep(1)
    run(["adb", "shell", "start"])
    log("Framework restarted. Monitor with: adb logcat | grep -E 'SystemServer|Zygote'", "OK")

def cmd_logcat(args):
    require_device()
    tags = args.services.split(",") if args.services else ["ActivityManager", "WindowManager", "SystemServer"]
    cmd = ["adb", "logcat", "-v", "color", "-s"] + [f"{t}:*" for t in tags]
    log(f"📡 Streaming logs for: {', '.join(tags)} (Ctrl+C to stop)")
    subprocess.run(cmd)

def cmd_props(args):
    require_device()
    if args.get:
        val = run(["adb", "shell", "getprop", args.get], silent=True).stdout.strip()
        log(f"{args.get} = {val or '(not set)'}", "OK")
    elif args.set and args.value:
        log(f"Setting {args.set}={args.value}")        run(["adb", "shell", "setprop", args.set, args.value])
    else:
        run(["adb", "shell", "getprop"])

def main():
    p = argparse.ArgumentParser(prog="adb_framework_manager", description="Educational ADB automation for framework dev.")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("check", help="Verify device connection & build type")
    sub.add_parser("restart", help="Safely restart Android framework services")
    
    p_pull = sub.add_parser("pull", help="Pull remote file (auto-backup)")
    p_pull.add_argument("remote")
    p_pull.add_argument("--local")
    
    p_push = sub.add_parser("push", help="Push local file to system (requires root)")
    p_push.add_argument("local")
    p_push.add_argument("remote")
    
    p_log = sub.add_parser("logcat", help="Stream framework logs")
    p_log.add_argument("--services", default="ActivityManager,WindowManager,SystemServer")
    
    p_prop = sub.add_parser("props", help="Get/set system properties")
    p_prop.add_argument("--get")
    p_prop.add_argument("--set")
    p_prop.add_argument("--value")
    
    args = p.parse_args()
    {"check": cmd_check, "restart": cmd_restart, "pull": cmd_pull, "push": cmd_push, 
     "logcat": cmd_logcat, "props": cmd_props}[args.cmd](args)

if __name__ == "__main__":
    main()