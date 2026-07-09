#!/usr/bin/env python
"""Detect guideline care gaps for a FHIR patient bundle.

    python caregaps_cli.py --bundle data/bundles/case_metformin_ckd.json
"""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from caregaps import find_care_gaps, load_bundle  # noqa: E402


def main(argv=None):
    ap = argparse.ArgumentParser(description="FHIR care-gap detection (CDS)")
    ap.add_argument("--bundle", required=True)
    args = ap.parse_args(argv)
    gaps = find_care_gaps(load_bundle(args.bundle))
    print(json.dumps(gaps, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
