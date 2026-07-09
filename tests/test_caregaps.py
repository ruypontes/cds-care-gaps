from pathlib import Path

from caregaps import find_care_gaps, load_bundle

BUNDLES = Path(__file__).resolve().parents[1] / "data" / "bundles"


def _gaps(name):
    return find_care_gaps(load_bundle(BUNDLES / name))


def _ids(gaps):
    return {g["rule_id"] for g in gaps}


def test_poor_control_case():
    ids = _ids(_gaps("case_poor_control.json"))
    assert "diabetes_poor_control" in ids
    assert "diabetes_no_statin" in ids
    assert "diabetes_no_hba1c" not in ids  # an HbA1c is present


def test_no_hba1c_case():
    ids = _ids(_gaps("case_no_hba1c.json"))
    assert "diabetes_no_hba1c" in ids


def test_metformin_ckd_safety_gap():
    gaps = _gaps("case_metformin_ckd.json")
    ids = _ids(gaps)
    assert "metformin_in_ckd" in ids
    gap = next(g for g in gaps if g["rule_id"] == "metformin_in_ckd")
    assert "Condition/c3-ckd" in gap["evidence"]
    assert "MedicationRequest/m3-met" in gap["evidence"]


def test_high_severity_sorted_first():
    gaps = _gaps("case_metformin_ckd.json")
    assert gaps[0]["severity"] == "high"


def test_every_gap_carries_evidence():
    for name in ("case_poor_control.json", "case_no_hba1c.json", "case_metformin_ckd.json"):
        for gap in _gaps(name):
            assert gap["evidence"], f"{gap['rule_id']} has no evidence"
