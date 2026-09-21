import io
import re
import pandas as pd
from pathlib import Path

folder_path = '../raw_files'
output_folder = Path('../cleaned_files')
output_folder.mkdir(exist_ok=True)

# US state/territory codes that can start an EPA_ID, e.g. AK4170024323, ALD004022448
STATE_CODES = {
    "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL",
    "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT",
    "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI",
    "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY", "DC", "PR",
    "VI", "GU", "AS", "MP",
}
NEW_ROW_RE = re.compile(r"^([A-Z]{2})[A-Z]{0,4}\d{6,},")


def is_new_row(line):
    match = NEW_ROW_RE.match(line)
    return bool(match) and match.group(1) in STATE_CODES


def repair_multiline_rows(csv_path):
    """Collapse fields (e.g. Contaminants) with embedded literal newlines
    back into a single physical line per record, so each row is one line."""
    with open(csv_path, "r", encoding="utf-8", errors="replace") as f:
        raw_lines = f.readlines()

    fixed_lines = [raw_lines[0].rstrip("\n")]  # header is always its own line
    buffer = None

    for line in raw_lines[1:]:
        line = line.rstrip("\n")
        if is_new_row(line):
            if buffer is not None:
                fixed_lines.append(buffer)
            buffer = line
        elif buffer is None:
            buffer = line
        else:
            buffer += " " + line

    if buffer is not None:
        fixed_lines.append(buffer)

    return "\n".join(fixed_lines) + "\n"


# Get a list of all the csvs in the Joined Files folder, skipping ones we already filtered
csv_files = [f for f in Path(folder_path).glob("*.csv") if "_filtered" not in f.stem]

# Iterate through each one

for csv_file in csv_files:
    print(csv_file)
    # For each file, load it in, repairing multi-line quoted fields first

    fixed_text = repair_multiline_rows(csv_file)
    df = pd.read_csv(io.StringIO(fixed_text))

    first_col = df.columns[0]
    is_numeric = pd.to_numeric(df[first_col], errors="coerce").notna()
    df = df[~is_numeric]

    output_path = output_folder / f"{csv_file.stem}_filtered{csv_file.suffix}"
    df.to_csv(output_path, index=False)

    # geometry (WKT MULTIPOLYGON) can be 100k+ chars, well past Excel's
    # 32,767-char cell limit, so also save a version without it for Excel use
    no_geom_path = output_folder / f"{csv_file.stem}_filtered_no_geometry{csv_file.suffix}"
    df.drop(columns=["geometry"]).to_csv(no_geom_path, index=False)

# next file


