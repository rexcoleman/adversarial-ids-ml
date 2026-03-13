#!/usr/bin/env bash
# download_data.sh — Download CICIDS2017 dataset
#
# The CICIDS2017 dataset consists of 8 CSV files (one per day of capture).
# Total size: ~6.5 GB uncompressed.
#
# Source: https://www.unb.ca/cic/datasets/ids-2017.html
# Mirror: The dataset files are hosted on UNB's AWS infrastructure.
#
# After download, run check_data_ready.py to verify checksums.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
DATA_DIR="${PROJECT_DIR}/data/raw"

mkdir -p "$DATA_DIR"

# CICIDS2017 files — MachineLearningCSV format (pre-extracted flow features)
# These are the CICFlowMeter-generated CSV files, not raw PCAPs.
BASE_URL="https://iscxdownloads.cs.unb.ca/iscxdownloads/CIC-IDS-2017/CSVs"

FILES=(
    "Monday-WorkingHours.pcap_ISCX.csv"
    "Tuesday-WorkingHours.pcap_ISCX.csv"
    "Wednesday-workingHours.pcap_ISCX.csv"
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv"
    "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv"
    "Friday-WorkingHours-Morning.pcap_ISCX.csv"
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv"
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv"
)

echo "=== CICIDS2017 Dataset Download ==="
echo "Target: $DATA_DIR"
echo "Files: ${#FILES[@]}"
echo ""

FAILED=0
for file in "${FILES[@]}"; do
    TARGET="${DATA_DIR}/${file}"
    if [[ -f "$TARGET" ]]; then
        echo "SKIP: $file (already exists)"
        continue
    fi

    echo "DOWNLOADING: $file ..."
    if curl -L -f -o "$TARGET" "${BASE_URL}/${file}" 2>/dev/null; then
        SIZE=$(stat --printf="%s" "$TARGET" 2>/dev/null || stat -f%z "$TARGET" 2>/dev/null)
        echo "  OK: $(( SIZE / 1024 / 1024 )) MB"
    else
        echo "  FAIL: Download failed for $file"
        echo "  Try manual download from: https://www.unb.ca/cic/datasets/ids-2017.html"
        rm -f "$TARGET"
        FAILED=$((FAILED + 1))
    fi
done

echo ""
if [[ $FAILED -gt 0 ]]; then
    echo "WARNING: $FAILED file(s) failed to download."
    echo "The CICIDS2017 dataset may require manual download from the UNB website."
    echo "Alternative: Download the MachineLearningCSV.zip from the dataset page."
    echo ""
    echo "Manual download steps:"
    echo "  1. Visit https://www.unb.ca/cic/datasets/ids-2017.html"
    echo "  2. Download 'MachineLearningCSV.zip' or individual CSV files"
    echo "  3. Extract to: $DATA_DIR/"
    exit 1
else
    echo "=== All files downloaded ==="
    echo "Next: python scripts/check_data_ready.py"
fi
