# WatchLog

Splits your WoW combat log into separate files, one per dungeon/raid,
automatically and in real time — so each run is a clean, ready-to-upload
chunk for Archon instead of one giant mixed-together log.

Works on **Windows** and **macOS** out of the box. Works on **Linux**
too, with one extra manual step (see below) since WoW isn't natively
supported there.

---

## What this actually does

WoW writes everything you log — every dungeon, every raid, every trip
back to town — into one growing log file for the session. There's no
built-in way to split that by instance; the game only knows "logging is
on" or "logging is off."

WatchLog fixes that by watching the log file live and reacting to a
specific event WoW writes every time you zone: ZONE_CHANGE. That event
tells us which zone you entered, and whether it's an actual instance or
just a city/open-world zone. Using that:

- Enter a dungeon or raid: WatchLog starts a brand new file for it.
- Enter another instance right after: the previous file is closed and
  finalized, a new one starts.
- Zone into a city or the open world: whatever file was open gets
  closed. No new file starts. This also means if you forget to toggle
  /combatlog off before leaving an instance, the overworld tail just
  gets dropped instead of contaminating the dungeon's file.
- You relog or the game crashes mid-run: WoW starts a brand-new
  timestamped log file for the new session. WatchLog notices this
  automatically, cleanly finalizes whatever was open, and picks up the
  new session file without you doing anything.

Each resulting file is a self-contained, valid combat log chunk — drag
it straight into the Archon Uploader.

What it does NOT do: it doesn't toggle /combatlog for you. Use an
auto-logging addon (or type it manually) so logging is actually running
when you enter content — WatchLog can only split what WoW is already
recording.

---

## Folder layout

WatchLog keeps its own files completely separate from WoW's:

WatchLog/
  watchlog.py            (the script)
  run_watchlog.bat        (Windows launcher)
  run_watchlog.sh          (macOS/Linux launcher)
  SplitLogs/                (output goes here, created automatically)
      Halls_of_Atonement_20260714_201251.txt
      Spires_of_Ascension_20260714_201305.txt
      ...

It only ever READS from WoW's actual Logs folder — it never writes to
it or modifies anything there. On Windows that's typically:
...\World of Warcraft\_retail_\Logs\
On macOS:
/Applications/World of Warcraft/_retail_/Logs

You can place the WatchLog folder anywhere convenient — it doesn't need
to be inside the WoW installation, and shouldn't be (that folder often
needs admin/elevated rights to write into).

---

## Requirements

WatchLog needs Python 3 installed. Nothing else — no extra libraries to
install, it only uses Python's built-in modules.

Check if you already have it:
- Windows: open a terminal (Command Prompt or PowerShell) and run
  python --version
- macOS/Linux: open Terminal and run python3 --version

If that prints a version number (e.g. Python 3.12.4), you're set — skip
to Setup below.

If it's not installed:
- Windows: download the installer from python.org/downloads. During
  install, make sure to check "Add python.exe to PATH" — this is
  unchecked by default and is the most common reason python isn't
  recognized afterward.
- macOS: download from python.org/downloads, or if you have Homebrew
  installed, run brew install python3.
- Linux: almost always already installed as python3. If not, use your
  distro's package manager, e.g. sudo apt install python3 on
  Debian/Ubuntu, sudo dnf install python3 on Fedora.

---

## Setup

### 1. Get the files in place
Put all the files from this download into one folder together, e.g.
Documents\WatchLog\ (Windows) or ~/WatchLog/ (macOS/Linux).

### 2. Make sure combat logging will actually run
WatchLog only splits what's being logged — it doesn't start logging
itself. In-game, either:
- Type /combatlog yourself each session, or
- Use an auto-logging addon that toggles it for you on instance entry

### 3. Run it

Windows: double-click run_watchlog.bat.

macOS: open Terminal, cd into the WatchLog folder, then:
chmod +x run_watchlog.sh      (only needed once)
./run_watchlog.sh

Linux: see the Linux section below first — you'll need one extra step
before running it.

WatchLog will try to auto-detect your WoW Logs folder automatically. If
it can't (a non-default install location, an unusual drive letter,
etc.), it'll tell you so — open the launcher script and uncomment the
line with --logs-dir, filling in your actual path.

Once running, it either finds your current session's log file
immediately, or — if WoW isn't open yet — waits patiently until it
detects one. You can start WatchLog before launching WoW if you like.

### 4. When you're done
Close the window, or click into it and press Ctrl+C. If a dungeon file
was still open, it gets finalized cleanly before exiting.

---

## Linux setup (extra step)

WoW isn't officially supported on Linux — people run it through Wine,
Lutris, or Proton, and each of those places the install inside its own
"prefix" folder, in a location that's different for everyone. Because
of that, WatchLog does NOT attempt to auto-detect your Logs folder on
Linux — you'll need to find and specify it yourself, once.

Finding your Logs folder:
find ~ -iname "WoWCombatLog*.txt" 2>/dev/null

This searches your home directory for any WoW combat log files already
created (you'll need to have typed /combatlog in-game at least once
first). The result will show you the full path to the Logs folder,
something like:
/home/you/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_retail_/Logs/WoWCombatLog-...txt

Take everything up to and including Logs — that's the folder to use.

Using it: open run_watchlog.sh in a text editor, and uncomment / edit
the line with --logs-dir, pasting in the folder path you found. Then
run it the same way as macOS:
chmod +x run_watchlog.sh
./run_watchlog.sh

---

## Using the output

Every file in SplitLogs/ is named <Instance>_<timestamp>.txt and is
ready to upload individually to Archon / Warcraft Logs — no further
editing needed.

SplitLogs/ isn't cleaned up automatically, so old files will accumulate
over time. Feel free to delete ones you've already uploaded and
analyzed.

---

## Troubleshooting

"Couldn't auto-detect your WoW Logs folder" — your install isn't in one
of the common default locations WatchLog checks (a non-default
drive/folder on Windows, a non-default location on macOS, or any Linux
setup). Pass --logs-dir explicitly, as described above.

"No WoWCombatLog*.txt found yet" — WatchLog found (or was given) the
right folder, but no log file exists in it yet. Either WoW hasn't been
launched, or /combatlog hasn't been typed yet this session. This isn't
an error — it'll keep waiting and pick the file up automatically once
it appears.

A dungeon didn't get split out — double check logging was actually on
(/combatlog) while you were inside it. WatchLog can't split what was
never recorded.

The Windows window closes instantly when double-clicked — this usually
means Python isn't on your PATH, or the --logs-dir line has a typo. Try
running it from a terminal instead (cd into the WatchLog folder, then
python watchlog.py) so you can read the actual error message.

Output landed somewhere unexpected — by default, SplitLogs/ is created
next to watchlog.py itself, regardless of where your Logs folder is.
Pass --out "<some folder>" to override this.
