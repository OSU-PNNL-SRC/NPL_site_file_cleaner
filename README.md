# SRP File Cleaner

Cleans raw SRP CSV exports: repairs rows that got split across multiple
physical lines, strips stray numeric-only header/junk rows, and writes a
filtered copy of each file (plus an Excel-safe copy with the `geometry`
column dropped).

## Expected folder layout

Joined Files/
├── code/
│   └── srp_file_cleaner.py   <- run from here
├── raw_files/                 <- input CSVs go here
└── cleaned_files/              <- output is written here (created automatically if missing)



## Requirements

- Python 3
- pandas (`pip install pandas`)

## Usage

cd "Joined Files/code"
python srp_file_cleaner.py



Paths (`../raw_files`, `../cleaned_files`) are relative to the directory
you run the script from, not to the script's own location — always run it
from inside `code/`, or the input glob will silently find zero files.

## What it does, per file in `raw_files/`

1. **Repairs multi-line rows.** Some fields (e.g. `Contaminants`) contain
   literal embedded newlines, splitting one logical record across several
   physical lines. A new record is recognized by a line starting with a
   two-letter US state/territory code followed by up to 4 more letters and
   6+ digits (e.g. `AK4170024323,` or `ALD004022448,`) — any line that
   doesn't match gets glued onto the previous record with a space.
2. **Drops numeric-first-column rows** — these are treated as stray
   header/repeat rows, not real records.
3. **Writes `<name>_filtered.csv`** to `cleaned_files/` — the full cleaned
   file.
4. **Writes `<name>_filtered_no_geometry.csv`** to `cleaned_files/` — same
   data with the `geometry` column dropped, since WKT `MULTIPOLYGON`
   values can run past Excel's 32,767-character cell limit.

Files already ending in `_filtered` in `raw_files/` are skipped, so it's
safe to re-run without reprocessing already-cleaned output.
