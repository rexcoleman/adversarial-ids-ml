#!/usr/bin/env python3
"""check_data_ready.py — Phase 0 gate: verify CICIDS2017 data is present and valid.

Checks:
1. All expected CSV files exist in data/raw/
2. Each file has expected minimum row count (sanity check)
3. Label column (' Label') exists in each file
4. Computes and stores SHA-256 checksums for reproducibility
"""

import hashlib
import sys
from pathlib import Path

import pandas as pd

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data" / "raw"
CHECKSUM_FILE = PROJECT_DIR / "data" / "checksums.sha256"

# Expected files and minimum row counts (approximate, for sanity checking)
EXPECTED_FILES = {
    "Monday-WorkingHours.pcap_ISCX.csv": 529918,
    "Tuesday-WorkingHours.pcap_ISCX.csv": 445909,
    "Wednesday-workingHours.pcap_ISCX.csv": 692703,
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv": 170366,
    "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv": 288602,
    "Friday-WorkingHours-Morning.pcap_ISCX.csv": 191033,
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv": 225745,
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv": 286467,
}

# Tolerance: allow 10% fewer rows (different CSV parsers may handle edge cases differently)
ROW_TOLERANCE = 0.10


def compute_sha256(filepath: Path) -> str:
    """Compute SHA-256 of a file."""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def main():
    print("=== CICIDS2017 Data Validation ===\n")

    if not DATA_DIR.exists():
        print(f"FAIL: Data directory does not exist: {DATA_DIR}")
        print("  Run: bash scripts/download_data.sh")
        sys.exit(1)

    failures = []
    checksums = {}

    for filename, expected_rows in EXPECTED_FILES.items():
        filepath = DATA_DIR / filename

        # Check existence
        if not filepath.exists():
            print(f"FAIL: Missing file: {filename}")
            failures.append(filename)
            continue

        # Check readability and row count
        try:
            df = pd.read_csv(filepath, low_memory=False)
            actual_rows = len(df)
            min_rows = int(expected_rows * (1 - ROW_TOLERANCE))

            if actual_rows < min_rows:
                print(f"FAIL: {filename} — {actual_rows} rows (expected ≥{min_rows})")
                failures.append(filename)
                continue

            # Check label column exists
            label_col = " Label"  # CICIDS2017 has a leading space
            if label_col not in df.columns:
                # Try without space
                if "Label" in df.columns:
                    label_col = "Label"
                else:
                    print(f"FAIL: {filename} — no 'Label' column found")
                    print(f"  Columns: {list(df.columns[:5])} ... ({len(df.columns)} total)")
                    failures.append(filename)
                    continue

            n_classes = df[label_col].nunique()
            print(f"PASS: {filename} — {actual_rows:,} rows, {n_classes} classes")

        except Exception as e:
            print(f"FAIL: {filename} — read error: {e}")
            failures.append(filename)
            continue

        # Compute checksum
        sha = compute_sha256(filepath)
        checksums[filename] = sha

    # Write checksums
    if checksums:
        CHECKSUM_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(CHECKSUM_FILE, "w") as f:
            for fname, sha in sorted(checksums.items()):
                f.write(f"{sha}  {fname}\n")
        print(f"\nChecksums written to: {CHECKSUM_FILE}")

    # Summary
    print(f"\n=== {len(EXPECTED_FILES) - len(failures)}/{len(EXPECTED_FILES)} files validated ===")

    if failures:
        print(f"\nFailed files: {failures}")
        print("Run: bash scripts/download_data.sh")
        sys.exit(1)
    else:
        print("All data files ready.")


if __name__ == "__main__":
    main()
