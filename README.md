# WatchLog

Splits your WoW combat log into separate files, one per dungeon/raid,
automatically and in real time — so each run is a clean, ready-to-upload
chunk for Archon instead of one giant mixed-together log.

**Retail only, for now.** Classic support (`_classic_`, `_classic_era_`,
etc.) is planned but not yet implemented — if you have a Classic install
alongside Retail, WatchLog ignores it and auto-detects Retail only.

---

## Which version do I need?

- **Windows, no Python installed:** use `watchlog.exe` — just download
  and double-click, nothing else to set up.
- **Windows with Python already installed, or macOS/Linux:** use
  `watchlog.py` with the launcher for your OS (`run_watchlog.bat` or
  `run_watchlog.sh`). See Requirements below.

Both versions behave identically — the `.exe` is just the script
bundled together with its own copy of Python, so people without Python
installed can still run it.

---

## Before you start: make sure combat logging will actually run

**WatchLog only splits what's already being logged — it doesn't turn
logging on itself.** This is the single most common setup mistake, so
read this section before assuming something's broken.

You have two options:

**Option A: Type `/combatlog` yourself.** Simple and reliable. Type it
once when you queue or enter content, type it again when you're done
if you want to stop. No addon required.

**Option B: Use an addon that auto-toggles it for you** on instance
entry/exit, so you never have to remember. This is convenient, but
**worth a word of caution**: not every auto-logging addon handles this
cleanly. During testing, **AutoCombatLogger** was found to sometimes
turn logging on a moment too late (missing the exact instant you enter
an instance), and to occasionally re-toggle logging while just standing
around in a city for no clear reason — both of which mean WatchLog
never sees the event it needs and won't create a split file for that
run. If you use an auto-toggle addon and notice a dungeon isn't getting
split, this kind of timing issue is the first thing to suspect —
try disabling it and using `/combatlog` manually to confirm.

Either way: if a dungeon isn't in `SplitLogs\` afterward, the most
likely cause is that combat logging simply wasn't running (or was
toggled at the wrong moment), not a bug in WatchLog itself.

---

## What this actually does

WoW writes everything you log — every dungeon, every raid, every trip
back to town — into one growing log file for the session. There's no
built-in way to split that by instance; the game only knows "logging is
on" or "logging is off."

WatchLog fixes that by watching the log file live and reacting to a
specific event WoW writes every time you zone: `ZONE_CHANGE`. That event
tells us which zone you entered, and whether it's an actual instance or
just a city/open-world zone. Using that:

- **Enter a dungeon or raid** → WatchLog starts a brand new file for it.
- **Enter another instance right after** → the previous file is closed
  and finalized, a new one starts.
- **Zone into a city or the open world** → whatever file was open gets
  closed. No new file starts. This also means if you forget to toggle
  `/combatlog` off before leaving an instance, the overworld tail just
  gets dropped instead of contaminating the dungeon's file.
- **You relog or the game crashes mid-run** → WoW starts a brand-new
  timestamped log file for the new session. WatchLog notices this
  automatically, cleanly finalizes whatever was open, and picks up
  the new session file without you doing anything.

Each resulting file is a self-contained, valid combat log chunk — drag
it straight into the Archon Uploader.

**A quirk worth knowing about, not a bug:** WoW doesn't always write
your own actions to disk the instant they happen — outside of active
group combat, it can buffer them and only flush after a delay or once
enough events queue up. This means WatchLog's terminal output can
sometimes lag a couple of minutes behind what you actually did in-game
if you were mostly idle. The data itself is still accurate once it
does write — this only affects how promptly you see confirmation on
screen, not the correctness of the split files.

---

## Folder layout

WatchLog keeps its own files completely separate from WoW's:

```
WatchLog/
  watchlog.exe            <- Windows, no Python needed (use this OR watchlog.py)
  watchlog.py              <- the script (all platforms, requires Python)
  run_watchlog.bat          <- Windows launcher for watchlog.py
  run_watchlog.sh             <- macOS/Linux launcher
  SplitLogs/                    <- output goes here, created automatically
      Halls_of_Atonement_20260714_201251.txt
      Spires_of_Ascension_20260714_201305.txt
      ...
```

It only ever **reads** from WoW's actual Logs folder — it never writes
to it or modifies anything there. On Windows that's typically:
```
...\World of Warcraft\_retail_\Logs\
```
On macOS:
```
/Applications/World of Warcraft/_retail_/Logs
```

You can place the `WatchLog` folder anywhere convenient — it doesn't
need to be inside the WoW installation, and shouldn't be (that folder
often needs admin/elevated rights to write into).

---

## Requirements

**Using `watchlog.exe` (Windows):** none — it's fully self-contained.
Just download it and double-click. Skip straight to Setup below.

**Using `watchlog.py` (Windows without the `.exe`, macOS, or Linux):**
you'll need **Python 3** installed. Nothing else — no extra libraries,
it only uses Python's built-in modules.

Check if you already have it:
- Windows: open a terminal (Command Prompt or PowerShell) and run
  `python --version`
- macOS/Linux: open Terminal and run `python3 --version`

If that prints a version number (e.g. `Python 3.12.4`), you're set.

If it's not installed:
- **Windows:** download the installer from
  [python.org/downloads](https://www.python.org/downloads/). During
  install, make sure to check **"Add python.exe to PATH"** — this is
  unchecked by default and is the most common reason `python` isn't
  recognized afterward.
- **macOS:** download from
  [python.org/downloads](https://www.python.org/downloads/), or if you
  have [Homebrew](https://brew.sh/) installed, run `brew install python3`.
- **Linux:** almost always already installed as `python3`. If not, use
  your distro's package manager, e.g. `sudo apt install python3` on
  Debian/Ubuntu, `sudo dnf install python3` on Fedora.

---

## Setup

### 1. Get the files in place
Put all the files from this download/repo into one folder together,
e.g. `Documents\WatchLog\` (Windows) or `~/WatchLog/` (macOS/Linux).

### 2. Make sure combat logging will actually run
See "Before you start" above — either type `/combatlog` yourself, or
use an auto-toggle addon (with the caveat mentioned there).

### 3. Run it

**Windows, using the `.exe`:** double-click `watchlog.exe`. A console
window opens automatically — nothing else needed.

**Windows, using the script:** double-click `run_watchlog.bat`.

**macOS:** open Terminal, `cd` into the WatchLog folder, then:
```
chmod +x run_watchlog.sh      # only needed once
./run_watchlog.sh
```

**Linux:** see the Linux section below first — you'll need one extra
step before running it.

WatchLog will try to auto-detect your **Retail** WoW Logs folder. If it
can't (a non-default install location, an unusual drive letter, etc.),
it'll tell you so — open the launcher script (or, for the `.exe`, run
it from a terminal with `watchlog.exe --logs-dir "<path>"` instead of
double-clicking) and point it at your actual Logs folder.

Once running, it either finds your current session's log file
immediately, or — if WoW isn't open yet — waits patiently until it
detects one. You can start WatchLog *before* launching WoW if you like,
and it doesn't matter which order you open WoW vs. run it in.

### 4. When you're done
Close the window, or click into it and press `Ctrl+C`. If a dungeon
file was still open, it gets finalized cleanly before exiting. On
Windows you may see a `Terminate batch job (Y/N)?` prompt — type `Y`
and press Enter.

---

## Linux setup (extra step)

WoW isn't officially supported on Linux — people run it through Wine,
Lutris, or Proton, and each of those places the install inside its own
"prefix" folder, in a location that's different for everyone. Because
of that, WatchLog does **not** attempt to auto-detect your Logs folder
on Linux — you'll need to find and specify it yourself, once.

**Finding your Logs folder:**
```
find ~ -iname "WoWCombatLog*.txt" 2>/dev/null
```
This searches your home directory for any WoW combat log files already
created (you'll need to have typed `/combatlog` in-game at least once
first). The result will show you the full path to the `Logs` folder,
something like:
```
/home/you/Games/battlenet/drive_c/Program Files (x86)/World of Warcraft/_retail_/Logs/WoWCombatLog-...txt
```
Take everything up to and including `Logs` — that's the folder to use.

**Using it:** open `run_watchlog.sh` in a text editor, and uncomment /
edit the line with `--logs-dir`, pasting in the folder path you found.
Then run it the same way as macOS:
```
chmod +x run_watchlog.sh
./run_watchlog.sh
```

---

## Using the output

Every file in `SplitLogs/` is named `<Instance>_<timestamp>.txt` and is
ready to upload individually to Archon / Warcraft Logs — no further
editing needed.

`SplitLogs/` isn't cleaned up automatically, so old files will
accumulate over time. Feel free to delete ones you've already uploaded
and analyzed.

---

## Troubleshooting

**A dungeon didn't get split out at all** — by far the most common
cause is combat logging not actually running during that instance. See
"Before you start" above, especially the note about auto-toggle addons
misfiring. Double check `/combatlog` was on (or your addon actually
toggled it) while you were inside.

**"Found multiple possible WoW Logs folders"** — WatchLog only checks
Retail installs, but found more than one (e.g. Retail on two different
drives). Pass `--logs-dir` explicitly to pick the one you want.

**"Couldn't auto-detect your WoW Logs folder"** — your install isn't in
one of the common default locations WatchLog checks (a non-default
drive/folder on Windows, a non-default location on macOS, or any
Linux setup), or you only have a Classic install (not yet supported).
Pass `--logs-dir` explicitly, as described above.

**"No WoWCombatLog*.txt found yet"** — WatchLog found (or was given)
the right folder, but no log file exists in it yet. Either WoW hasn't
been launched, or `/combatlog` hasn't been typed yet this session. This
isn't an error — it'll keep waiting and pick the file up automatically
once it appears.

**The terminal seems delayed / took a while to show an update** — this
can be normal. WoW doesn't always flush your own actions to disk
instantly if you're mostly idle; see the note under "What this
actually does" above. The underlying data is still accurate.

**The Windows window closes instantly when double-clicked** — for the
script version, this usually means Python isn't on your `PATH`, or the
`--logs-dir` line has a typo. Try running it from a terminal instead
(`cd` into the WatchLog folder, then `python watchlog.py`) so you can
read the actual error message.

**Output landed somewhere unexpected** — by default, `SplitLogs/` is
created next to whichever file you ran (`watchlog.exe` or
`watchlog.py`), regardless of where your Logs folder is. Pass
`--out "<some folder>"` to override this.
