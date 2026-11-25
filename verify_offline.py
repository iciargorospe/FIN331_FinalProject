
# FIN331: Offline reproduction and hand-check verification

from pathlib import Path
import csv
import gzip
import math
import shutil
import subprocess
import sys
import tempfile

import pandas as pd

ROOT = Path(__file__).resolve().parent
ARCHIVE = ROOT / "outputs/full_sample_analysis.csv.gz"

assert ARCHIVE.exists(), "Compressed dataset not found."

scripts = [
    ("full_sample_summary.py", "full_sample_summary.csv"),
    ("full_sample_tests.py", "full_sample_tests.csv"),
    ("full_sample_regression.py", "full_sample_regression.csv"),
    ("full_sample_categories.py", "full_sample_categories.csv"),
    ("full_sample_robustness.py", "full_sample_robustness.csv"),
    ("full_sample_economic.py", "full_sample_economic.csv"),
    (
        "full_sample_winsorized_regression.py",
        "full_sample_winsorized_regression.csv"
    ),
    (
        "full_sample_two_way_clustering.py",
        "full_sample_two_way_clustering.csv"
    ),
]

# Use a temporary directory so the verification does not
# overwrite our committed results or read the existing raw CSV.
with tempfile.TemporaryDirectory() as temporary:
    work = Path(temporary)
    output_dir = work / "outputs"
    output_dir.mkdir()

    # Step 1: Restore the underlying dataset
    with gzip.open(ARCHIVE, "rb") as source:
        with (output_dir / "full_sample_analysis.csv").open("wb") as dest:
            shutil.copyfileobj(source, dest)

    data = pd.read_csv(output_dir / "full_sample_analysis.csv")

    assert len(data) == 135466
    assert data["signalname"].nunique() == 209
    assert not data.duplicated(["signalname", "month"]).any()

    print("PASS: Compressed dataset restored")
    print("Observations:", len(data))
    print("Anomalies:", data["signalname"].nunique())

    # Step 2: Run each analysis using only the restored dataset
    print("\nREPRODUCING FULL-SAMPLE RESULTS")

    for script, filename in scripts:
        result = subprocess.run(
            [sys.executable, str(ROOT / script)],
            cwd=work,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(result.stdout)
            print(result.stderr)
            raise RuntimeError(f"Failed: {script}")

        generated = pd.read_csv(output_dir / filename)
        committed = pd.read_csv(ROOT / "outputs" / filename)

        pd.testing.assert_frame_equal(
            generated,
            committed,
            check_dtype=False,
            check_exact=False,
            rtol=1e-7,
            atol=1e-9
        )

        print(f"PASS: {filename} ({len(generated)} rows)")

    # Step 3: Independent hand calculation for Accruals
    count = 0
    total = 0.0

    with (output_dir / "full_sample_analysis.csv").open() as f:
        reader = csv.DictReader(f)

        for row in reader:
            if (
                row["signalname"] == "Accruals"
                and row["period"] == "Original Sample"
            ):
                total += float(row["ret"])
                count += 1

    assert count >= 24

    hand_mean = total / count

    summary = pd.read_csv(
        output_dir / "full_sample_summary.csv"
    )

    accruals = summary.loc[
        summary["signalname"] == "Accruals"
    ].iloc[0]

    assert count == accruals["original_months"]

    assert math.isclose(
        hand_mean,
        accruals["original_mean_pct"],
        rel_tol=1e-10,
        abs_tol=1e-10
    )

    print("\nINDEPENDENT HAND CHECK")
    print("Anomaly: Accruals")
    print("Original-sample observations:", count)
    print("Mean calculated using loop:", round(hand_mean, 6))
    print("Mean in summary:", round(accruals["original_mean_pct"], 6))

    print("\nSUCCESS: ALL OFFLINE VERIFICATION CHECKS PASSED!")
