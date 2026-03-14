"""preprocessing.py — CICIDS2017 data loading, cleaning, and split generation.

Authority: DATA_CONTRACT.md §4-6
Seed protocol: EXPERIMENT_CONTRACT.md §3 — seeds [42, 123, 456, 789, 1024]
"""

import hashlib
import json
from pathlib import Path
from typing import Optional

import random

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler


def set_seed(seed: int):
    """Set all random seeds for reproducibility (ENVIRONMENT_CONTRACT §8)."""
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch
        torch.manual_seed(seed)
        torch.use_deterministic_algorithms(True)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
            torch.backends.cudnn.deterministic = True
            torch.backends.cudnn.benchmark = False
    except ImportError:
        pass

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_RAW = PROJECT_DIR / "data" / "raw"
DATA_PROCESSED = PROJECT_DIR / "data" / "processed"
DATA_SPLITS = PROJECT_DIR / "data" / "splits"

# CICIDS2017 CSV files (8 files, one per capture session)
CSV_FILES = [
    "Monday-WorkingHours.pcap_ISCX.csv",
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
]

# Features an attacker CAN control (from TRADEOFF_LOG.md)
# These are the only features that adversarial perturbations should modify
# in constrained attack mode.
ATTACKER_CONTROLLABLE_FEATURES = [
    # Packet-level features attacker can manipulate
    "Flow Duration",
    "Total Fwd Packets",
    "Total Backward Packets",
    "Total Length of Fwd Packets",
    "Total Length of Bwd Packets",
    "Fwd Packet Length Max",
    "Fwd Packet Length Min",
    "Fwd Packet Length Mean",
    "Fwd Packet Length Std",
    "Bwd Packet Length Max",
    "Bwd Packet Length Min",
    "Bwd Packet Length Mean",
    "Bwd Packet Length Std",
    "Flow Bytes/s",
    "Flow Packets/s",
    "Flow IAT Mean",
    "Flow IAT Std",
    "Flow IAT Max",
    "Flow IAT Min",
    "Fwd IAT Total",
    "Fwd IAT Mean",
    "Fwd IAT Std",
    "Fwd IAT Max",
    "Fwd IAT Min",
    "Bwd IAT Total",
    "Bwd IAT Mean",
    "Bwd IAT Std",
    "Bwd IAT Max",
    "Bwd IAT Min",
    "Fwd Header Length",
    "Bwd Header Length",
    "Fwd Packets/s",
    "Bwd Packets/s",
    "Min Packet Length",
    "Max Packet Length",
    "Packet Length Mean",
    "Packet Length Std",
    "Packet Length Variance",
    # Payload features attacker controls
    "Average Packet Size",
    "Avg Fwd Segment Size",
    "Avg Bwd Segment Size",
    "Subflow Fwd Packets",
    "Subflow Fwd Bytes",
    "Subflow Bwd Packets",
    "Subflow Bwd Bytes",
    "Init_Win_bytes_forward",
    "Init_Win_bytes_backward",
    "act_data_pkt_fwd",
    "min_seg_size_forward",
    "Active Mean",
    "Active Std",
    "Active Max",
    "Active Min",
    "Idle Mean",
    "Idle Std",
    "Idle Max",
    "Idle Min",
]

# Features attacker CANNOT control (set by OS/network stack/protocol)
# These should NOT be perturbed in constrained adversarial attacks.
DEFENDER_OBSERVABLE_ONLY = [
    "Destination Port",  # Set by service, not attacker choice in most scenarios
    "Fwd PSH Flags",
    "Bwd PSH Flags",
    "Fwd URG Flags",
    "Bwd URG Flags",
    "FIN Flag Count",
    "SYN Flag Count",
    "RST Flag Count",
    "PSH Flag Count",
    "ACK Flag Count",
    "URG Flag Count",
    "CWE Flag Count",
    "ECE Flag Count",
    "Down/Up Ratio",
]


def load_raw_data(sample_frac: Optional[float] = None, seed: int = 42) -> pd.DataFrame:
    """Load all 8 CICIDS2017 CSV files into a single DataFrame.

    Args:
        sample_frac: If set, randomly sample this fraction of data (for development).
        seed: Random seed for sampling.

    Returns:
        Combined DataFrame with all flows.
    """
    frames = []
    for csv_file in CSV_FILES:
        path = DATA_RAW / csv_file
        if not path.exists():
            raise FileNotFoundError(f"Missing: {path}. Run scripts/download_data.sh")
        df = pd.read_csv(path, low_memory=False)
        df.columns = df.columns.str.strip()  # CICIDS2017 has leading spaces in column names
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    if sample_frac is not None:
        combined = combined.sample(frac=sample_frac, random_state=seed)

    return combined


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean CICIDS2017 data: handle inf, NaN, and encode labels.

    Known issues in CICIDS2017:
    - Flow Bytes/s and Flow Packets/s contain inf values
    - Some rows have NaN values
    - Label column has inconsistent spacing
    """
    # Strip label whitespace
    df["Label"] = df["Label"].str.strip()

    # Replace inf with NaN, then drop NaN rows
    df = df.replace([np.inf, -np.inf], np.nan)
    n_before = len(df)
    df = df.dropna()
    n_dropped = n_before - len(df)
    if n_dropped > 0:
        print(f"  Dropped {n_dropped:,} rows with inf/NaN ({n_dropped/n_before*100:.2f}%)")

    return df


def encode_labels(df: pd.DataFrame) -> tuple[pd.DataFrame, LabelEncoder, dict]:
    """Encode string labels to integers. Returns df, encoder, and label mapping."""
    le = LabelEncoder()
    df = df.copy()
    df["label_encoded"] = le.fit_transform(df["Label"])

    label_map = {label: int(idx) for idx, label in enumerate(le.classes_)}
    return df, le, label_map


def create_splits(
    df: pd.DataFrame,
    seed: int = 42,
    train_ratio: float = 0.6,
    val_ratio: float = 0.2,
    test_ratio: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Create stratified train/val/test splits.

    Per EXPERIMENT_CONTRACT §3: Fixed splits, stratified by attack class.
    """
    assert abs(train_ratio + val_ratio + test_ratio - 1.0) < 1e-6

    # Drop classes with fewer than 7 members — need ≥2 per split after 70/15/15
    # (with 3 samples, the val+test portion can get only 1, breaking stratified split)
    class_counts = df["label_encoded"].value_counts()
    min_members = 7
    small_classes = class_counts[class_counts < min_members].index.tolist()
    if small_classes:
        n_dropped = df["label_encoded"].isin(small_classes).sum()
        print(f"  Dropping {len(small_classes)} classes with <{min_members} samples "
              f"({n_dropped} rows): {small_classes}")
        df = df[~df["label_encoded"].isin(small_classes)].copy()
        # Re-encode to contiguous labels (XGBoost requires 0..N-1)
        unique_labels = sorted(df["label_encoded"].unique())
        remap = {old: new for new, old in enumerate(unique_labels)}
        df["label_encoded"] = df["label_encoded"].map(remap)

    # First split: train vs (val+test)
    train_df, temp_df = train_test_split(
        df,
        test_size=(val_ratio + test_ratio),
        random_state=seed,
        stratify=df["label_encoded"],
    )

    # Second split: val vs test
    relative_test_ratio = test_ratio / (val_ratio + test_ratio)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=relative_test_ratio,
        random_state=seed,
        stratify=temp_df["label_encoded"],
    )

    return train_df, val_df, test_df


def get_feature_columns(df: pd.DataFrame) -> list[str]:
    """Get numeric feature columns (excluding label columns)."""
    exclude = {"Label", "label_encoded"}
    return [c for c in df.select_dtypes(include=[np.number]).columns if c not in exclude]


def scale_features(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    feature_cols: list[str],
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, StandardScaler]:
    """Fit scaler on train ONLY, transform all splits.

    Per DATA_CONTRACT: LT-1 — preprocessing fit on train only.
    """
    scaler = StandardScaler()

    train_df = train_df.copy()
    val_df = val_df.copy()
    test_df = test_df.copy()

    train_df[feature_cols] = scaler.fit_transform(train_df[feature_cols])
    val_df[feature_cols] = scaler.transform(val_df[feature_cols])
    test_df[feature_cols] = scaler.transform(test_df[feature_cols])

    return train_df, val_df, test_df, scaler


def save_splits(
    train_df: pd.DataFrame,
    val_df: pd.DataFrame,
    test_df: pd.DataFrame,
    label_map: dict,
    seed: int = 42,
) -> None:
    """Save splits to data/splits/ with metadata."""
    DATA_SPLITS.mkdir(parents=True, exist_ok=True)

    train_df.to_csv(DATA_SPLITS / "train.csv", index=False)
    val_df.to_csv(DATA_SPLITS / "val.csv", index=False)
    test_df.to_csv(DATA_SPLITS / "test.csv", index=False)

    metadata = {
        "seed": seed,
        "train_rows": len(train_df),
        "val_rows": len(val_df),
        "test_rows": len(test_df),
        "label_map": label_map,
        "n_features": len(get_feature_columns(train_df)),
        "split_ratio": "60/20/20",
    }

    with open(DATA_SPLITS / "split_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"  Saved: train={len(train_df):,}, val={len(val_df):,}, test={len(test_df):,}")
    print(f"  Metadata: {DATA_SPLITS / 'split_metadata.json'}")


def get_controllable_feature_mask(feature_cols: list[str]) -> np.ndarray:
    """Return boolean mask: True for attacker-controllable features.

    Used by adversarial attack code to constrain perturbations.
    """
    controllable_set = set(ATTACKER_CONTROLLABLE_FEATURES)
    return np.array([col in controllable_set for col in feature_cols])


def run_preprocessing_pipeline(seed: int = 42, sample_frac: Optional[float] = None) -> dict:
    """Run full preprocessing pipeline. Returns metadata dict."""
    print(f"=== Preprocessing Pipeline (seed={seed}) ===\n")

    print("Step 1: Loading raw data...")
    df = load_raw_data(sample_frac=sample_frac, seed=seed)
    print(f"  Loaded {len(df):,} flows, {len(df.columns)} columns")

    print("\nStep 2: Cleaning...")
    df = clean_data(df)
    print(f"  Clean: {len(df):,} flows")

    print("\nStep 3: Encoding labels...")
    df, le, label_map = encode_labels(df)
    print(f"  Classes: {len(label_map)}")
    for label, idx in sorted(label_map.items(), key=lambda x: x[1]):
        count = (df["label_encoded"] == idx).sum()
        print(f"    [{idx}] {label}: {count:,} ({count/len(df)*100:.1f}%)")

    print("\nStep 4: Creating splits...")
    train_df, val_df, test_df = create_splits(df, seed=seed)

    feature_cols = get_feature_columns(df)
    print(f"  Features: {len(feature_cols)}")

    print("\nStep 5: Scaling features (fit on train only)...")
    train_df, val_df, test_df, scaler = scale_features(train_df, val_df, test_df, feature_cols)

    print("\nStep 6: Saving splits...")
    save_splits(train_df, val_df, test_df, label_map, seed=seed)

    # Feature controllability summary
    mask = get_controllable_feature_mask(feature_cols)
    print(f"\nFeature controllability:")
    print(f"  Attacker-controllable: {mask.sum()}/{len(mask)}")
    print(f"  Defender-observable only: {(~mask).sum()}/{len(mask)}")

    print("\n=== Preprocessing complete ===")

    # Extract arrays for downstream use
    X_train = train_df[feature_cols].values
    X_val = val_df[feature_cols].values
    X_test = test_df[feature_cols].values
    y_train = train_df["label_encoded"].values
    y_val = val_df["label_encoded"].values
    y_test = test_df["label_encoded"].values

    # Build label names ordered by new encoded index
    # After create_splits may remap labels, rebuild from actual data
    unique_encoded = sorted(set(y_train) | set(y_val) | set(y_test))
    # Use Label column which survived preprocessing
    enc_to_name = {}
    for split_df in [train_df, val_df, test_df]:
        for enc_val in split_df["label_encoded"].unique():
            name = split_df.loc[split_df["label_encoded"] == enc_val, "Label"].iloc[0]
            enc_to_name[int(enc_val)] = name
    label_names = [enc_to_name[i] for i in unique_encoded]

    return {
        "X_train": X_train,
        "X_val": X_val,
        "X_test": X_test,
        "y_train": y_train,
        "y_val": y_val,
        "y_test": y_test,
        "feature_cols": feature_cols,
        "label_names": label_names,
        "label_map": label_map,
        "scaler": scaler,
        "controllable_mask": mask,
        "total_flows": len(df),
        "n_classes": len(label_map),
        "n_features": len(feature_cols),
        "n_controllable": int(mask.sum()),
    }


if __name__ == "__main__":
    run_preprocessing_pipeline(seed=42)
