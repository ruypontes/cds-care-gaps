"""Guideline care-gap rules over a parsed patient summary.

Each rule returns a gap dict with an evidence list of the FHIR references that
triggered it, so every recommendation is traceable to the data. The rules are
intentionally simple and illustrative, not a validated guideline engine.
"""
STATIN_TERMS = ("statin", "atorvastatin", "simvastatin", "rosuvastatin", "pravastatin")
LOINC_HBA1C = "4548-4"
BP_LOINCS = {"85354-9", "8480-6", "8462-4"}
SNOMED_DM2 = "44054006"
SNOMED_HTN = "59621000"
SNOMED_CKD = "709044004"


def _condition_ref(summary, code):
    for c, ref in summary["conditions"]:
        if c == code:
            return ref
    return None


def _statin_ref(summary):
    for display, ref in summary["meds"]:
        if any(term in display for term in STATIN_TERMS):
            return ref
    return None


def _med_ref(summary, term):
    for display, ref in summary["meds"]:
        if term in display:
            return ref
    return None


def _latest_obs(summary, loinc):
    hits = [o for o in summary["observations"] if o["code"] == loinc]
    return hits[-1] if hits else None


def _has_bp(summary):
    return any(o["code"] in BP_LOINCS for o in summary["observations"])


def rule_diabetes_no_hba1c(s):
    ref = _condition_ref(s, SNOMED_DM2)
    if ref and not _latest_obs(s, LOINC_HBA1C):
        return {
            "rule_id": "diabetes_no_hba1c",
            "severity": "high",
            "description": "Active diabetes without a documented HbA1c. Order HbA1c.",
            "evidence": [ref],
        }
    return None


def rule_diabetes_poor_control(s):
    ref = _condition_ref(s, SNOMED_DM2)
    obs = _latest_obs(s, LOINC_HBA1C)
    if ref and obs and obs["value"] is not None and obs["value"] >= 9.0:
        return {
            "rule_id": "diabetes_poor_control",
            "severity": "high",
            "description": f"HbA1c {obs['value']}% indicates poor glycemic control. Intensify therapy.",
            "evidence": [ref, obs["ref"]],
        }
    return None


def rule_diabetes_no_statin(s):
    ref = _condition_ref(s, SNOMED_DM2)
    if ref and not _statin_ref(s):
        return {
            "rule_id": "diabetes_no_statin",
            "severity": "medium",
            "description": "Diabetic patient not on a statin. Consider statin per guideline.",
            "evidence": [ref],
        }
    return None


def rule_htn_no_bp(s):
    ref = _condition_ref(s, SNOMED_HTN)
    if ref and not _has_bp(s):
        return {
            "rule_id": "htn_no_bp",
            "severity": "medium",
            "description": "Hypertension without a documented blood pressure. Record BP.",
            "evidence": [ref],
        }
    return None


def rule_metformin_in_ckd(s):
    ckd = _condition_ref(s, SNOMED_CKD)
    met = _med_ref(s, "metformin")
    if ckd and met:
        return {
            "rule_id": "metformin_in_ckd",
            "severity": "high",
            "description": "Metformin with chronic kidney disease. Review dose or discontinue per eGFR.",
            "evidence": [ckd, met],
        }
    return None


RULES = [
    rule_diabetes_no_hba1c,
    rule_diabetes_poor_control,
    rule_diabetes_no_statin,
    rule_htn_no_bp,
    rule_metformin_in_ckd,
]
