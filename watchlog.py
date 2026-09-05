"""
WatchLog: WoW Combat Log Watcher & Splitter
--------------------------------------------
READS from your WoW Logs folder (never modifies anything there). Modern
WoW writes a fresh, timestamped file each session
(WoWCombatLog-MMDDYY-HHMMSS.txt) rather than one fixed WoWCombatLog.txt,
so this script auto-detects whichever one is currently active and
switches to a new one automatically if you relog mid-session.

WRITES split, per-instance log files into a "SplitLogs" folder next to
this script (e.g. Documents\\WatchLog\\SplitLogs), completely separate
from WoW's own Logs folder.

Every time you zone into a new dungeon/raid (a ZONE_CHANGE event with a
nonzero difficultyID), it starts a brand-new output file for that
instance. Zoning anywhere else (a city, the open world, or a different
instance) closes whatever chunk was open -- so an overworld tail never
bleeds into a dungeon file, even if you forgot to toggle /combatlog
before leaving.

Each output file is a valid combat log chunk, ready to be dragged into
the Archon Uploader / Warcraft Logs client for parsing.

USAGE:
    python watchlog.py
    python watchlog.py --logs-dir "D:\\Games\\World of Warcraft\\_retail_\\Logs"

With no --logs-dir given, WatchLog tries to auto-detect your WoW
install on Windows and macOS by checking common install locations.
This isn't attempted on Linux (Wine/Lutris/Proton prefixes vary too
much to guess) -- pass --logs-dir explicitly there.

Leave it running in a terminal while you play. Stop with Ctrl+C.
"""

import argparse
import os
import platform
import re
import string
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional

DEFAULT_OUTPUT_SUBDIR = "SplitLogs"
POLL_INTERVAL_SECONDS = 1.0
LOG_GLOB = "WoWCombatLog*.txt"
# Retail only for now -- Classic support (_classic_, _classic_era_,
# _classic_ptr_) is planned but not yet handled here.
VERSION_FOLDERS = ["_retail_"]

ZONE_CHANGE_RE = re.compile(r'ZONE_CHANGE,(\d+),"([^"]+)",(\d+)')


def candidate_install_roots() -> list[Path]:
    """Likely 'World of Warcraft' install folders to check, based on OS.

    Windows and macOS both install to a small, predictable set of
    locations, so it's worth checking them automatically. Linux isn't
    included here on purpose: WoW isn't natively supported there, and
    people run it through Wine/Lutris/Proton, each of which places the
    install inside its own "prefix" folder with a location that varies
    per person's setup -- there's no small set of paths worth guessing.
    """
    system = platform.system()
    roots: list[Path] = []

    if system == "Windows":
        program_dirs = ["Program Files (x86)", "Program Files"]
        bare_dirs = ["World of Warcraft", "Games\\World of Warcraft"]
        for letter in string.ascii_uppercase:
            drive = Path(f"{letter}:\\")
            if not drive.exists():
                continue
            for pf in program_dirs:
                roots.append(drive / pf / "World of Warcraft")
            for bare in bare_dirs:
                roots.append(drive / bare)

    elif system == "Darwin":  # macOS
        roots.append(Path("/Applications/World of Warcraft"))
        roots.append(Path.home() / "Applications" / "World of Warcraft")

    return roots


def find_logs_dirs_under(install_root: Path) -> list[Path]:
    """Given a 'World of Warcraft' folder, return any Logs folders inside it."""
    found = []
    if not install_root.exists():
        return found
    for version in VERSION_FOLDERS:
        candidate = install_root / version / "Logs"
        if candidate.exists():
            found.append(candidate)
    return found


def auto_detect_logs_dir() -> Optional[Path]:
    """Search common install locations for a WoW Logs folder.

    Returns the single match if exactly one is found. If none or
    multiple are found, returns None -- the caller decides how to
    report that.
    """
    all_found: list[Path] = []
    for root in candidate_install_roots():
        all_found.extend(find_logs_dirs_under(root))

    if len(all_found) == 1:
        return all_found[0]
    if len(all_found) > 1:
        print("Found multiple possible WoW Logs folders:")
        for p in all_found:
            print(f"  - {p}")
        print('Re-run with --logs-dir "<the one you want>" to pick one.')
    return None


def sanitize(name: str) -> str:
    """Turn a zone name into a safe filename fragment."""
    return re.sub(r"[^A-Za-z0-9_-]+", "_", name).strip("_")


def find_latest_log(logs_dir: Path) -> Optional[Path]:
    """Return the most recently modified WoWCombatLog*.txt file, or None."""
    candidates = list(logs_dir.glob(LOG_GLOB))
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def open_new_chunk(output_dir: Path, zone_name: str, header_lines: list[str]):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_zone = sanitize(zone_name)
    out_path = output_dir / f"{safe_zone}_{timestamp}.txt"
    fh = open(out_path, "w", encoding="utf-8")
    for h in header_lines:
        fh.write(h)
    return fh, out_path


def watch(logs_dir: Path, output_dir: Path):
    if not logs_dir.exists():
        print(f"ERROR: logs folder not found at: {logs_dir}")
        print('Pass the correct folder with --logs-dir "<path to Logs folder>"')
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    current_file = None
    current_out_path = None
    header_lines: list[str] = []

    active_log_path = find_latest_log(logs_dir)
    if active_log_path is None:
        print(f"No WoWCombatLog*.txt found yet in {logs_dir}")
        print("Waiting for you to log in and type /combatlog... (Ctrl+C to stop)")
        try:
            while active_log_path is None:
                time.sleep(POLL_INTERVAL_SECONDS)
                active_log_path = find_latest_log(logs_dir)
        except KeyboardInterrupt:
            print("\nStopping watcher.")
            sys.exit(0)
        print(f"Found log file: {active_log_path.name}\n")

    print(f"Watching folder: {logs_dir}")
    print(f"Active log file: {active_log_path.name}")
    print(f"Output dir: {output_dir.resolve()}")
    print("Waiting for you to zone into a dungeon/raid... (Ctrl+C to stop)\n")

    log_handle = open(active_log_path, "r", encoding="utf-8", errors="ignore")
    log_handle.seek(0, os.SEEK_END)  # only watch NEW lines from this point on

    try:
        while True:
            line = log_handle.readline()

            if not line:
                # Nothing new -- check whether a fresher log file has shown
                # up (e.g. you relogged or reloaded the UI after a crash).
                latest = find_latest_log(logs_dir)
                if latest is not None and latest != active_log_path:
                    print(f"\nDetected new session log: {latest.name}")
                    log_handle.close()
                    if current_file:
                        current_file.close()
                        print(f"  -> closed: {current_out_path.name}")
                        current_file, current_out_path = None, None
                    active_log_path = latest
                    log_handle = open(active_log_path, "r", encoding="utf-8", errors="ignore")
                    print(f"Now watching: {active_log_path.name}\n")
                    continue

                time.sleep(POLL_INTERVAL_SECONDS)
                continue

            if "COMBAT_LOG_VERSION" in line:
                header_lines = [line]

            match = ZONE_CHANGE_RE.search(line)
            if match:
                zone_name = match.group(2)
                difficulty_id = match.group(3)
                is_instance = difficulty_id != "0"

                # Any zone change ends whatever chunk was previously open,
                # whether we're moving into a new instance or back out to
                # a city/open world. This also cleanly handles the case
                # where you forget to toggle /combatlog before leaving an
                # instance -- the overworld tail just gets dropped instead
                # of bleeding into the dungeon's file.
                if current_file:
                    current_file.close()
                    print(f"  -> closed: {current_out_path.name}")
                    current_file, current_out_path = None, None

                if is_instance:
                    current_file, current_out_path = open_new_chunk(
                        output_dir, zone_name, header_lines
                    )
                    print(f"New instance detected: {zone_name}")
                    print(f"  -> writing: {current_out_path.name}")
                else:
                    print(f"Left instance, now in: {zone_name} (not logging)")

            if current_file:
                current_file.write(line)
                current_file.flush()

    except KeyboardInterrupt:
        print("\nStopping watcher.")
        if current_file:
            current_file.close()
            print(f"Final file saved: {current_out_path.name}")
        log_handle.close()


def main():
    parser = argparse.ArgumentParser(
        description="Split WoW combat logs live, per instance, across sessions."
    )
    parser.add_argument(
        "--logs-dir",
        type=str,
        default=None,
        help="Path to your WoW Logs folder (contains WoWCombatLog-*.txt files). "
        "If omitted, WatchLog tries to auto-detect it (Windows/macOS only).",
    )
    parser.add_argument(
        "--out",
        type=str,
        default=None,
        help="Folder to write split log files into "
        "(default: a 'SplitLogs' folder next to this script)",
    )
    args = parser.parse_args()

    if args.logs_dir:
        logs_dir = Path(args.logs_dir)
    else:
        detected = auto_detect_logs_dir()
        if detected is None:
            system = platform.system()
            print("Couldn't auto-detect your WoW Logs folder.")
            if system == "Linux":
                print(
                    "Auto-detection isn't attempted on Linux, since Wine/Lutris/"
                    "Proton installs each place WoW in their own prefix folder "
                    "with no common location to guess."
                )
                print(
                    "Find yours with something like:\n"
                    '  find ~ -iname "WoWCombatLog*.txt" 2>/dev/null'
                )
            print('Then pass it explicitly: --logs-dir "<path to your Logs folder>"')
            sys.exit(1)
        logs_dir = detected

    script_dir = Path(__file__).resolve().parent
    output_dir = Path(args.out) if args.out else script_dir / DEFAULT_OUTPUT_SUBDIR
    watch(logs_dir, output_dir)


if __name__ == "__main__":
    main()
