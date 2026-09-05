#!/usr/bin/env bash
# ============================================================
#  WatchLog launcher (macOS / Linux)
#  Run this to start watching your WoW combat log.
#  Leave the terminal open while you play. Close it (or press
#  Ctrl+C) when you're done.
# ============================================================
#
# On macOS, WatchLog will usually auto-detect your WoW Logs
# folder automatically if it's installed in the default
# /Applications/World of Warcraft location -- no editing needed.
#
# On Linux (Wine/Lutris/Proton), auto-detection isn't attempted,
# since every setup places WoW in a different prefix folder.
# Uncomment the second line below and fill in your actual path.

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 "$DIR/watchlog.py"
# python3 "$DIR/watchlog.py" --logs-dir "/path/to/World of Warcraft/_retail_/Logs"

read -p "Press Enter to close..."
