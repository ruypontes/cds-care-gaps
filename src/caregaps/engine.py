"""Parse a FHIR bundle into a patient summary and run the care-gap rules."""
import json
from pathlib import Path

from .rules import RULES

_SEVERITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def load_bundle(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _display(concept):
    if not concept:
        return ""
    codings = concept.get("coding", [])
    if codings:
        return codings[0].get("display") or codings[0].get("code") or ""
    return concept.get("text", "")


def _code(concept):
    if not concept:
        return None
    codings = concept.get("coding", [])
    return codings[0].get("code") if codings else None


def _is_active(resource):
    codings = resource.get("clinicalStatus", {}).get("coding", [])
    return (codings[0].get("code") if codings else "") == "active"


def summarize(bundle):
    conditions, meds, observations = set(), [], []
    for entry in bundle.get("entry", []):
        r = entry.get("resource", {})
        rt = r.get("resourceType")
        ref = f"{rt}/{r.get('id')}"
        if rt == "Condition" and _is_active(r):
            conditions.add((_code(r.get("code")), ref))
        elif rt == "MedicationRequest" and r.get("status") == "active":
            meds.append((_display(r.get("medicationCodeableConcept")).lower(), ref))
        elif rt == "Observation":
            observations.append({
                "code": _code(r.get("code")),
                "value": r.get("valueQuantity", {}).get("value"),
                "ref": ref,
            })
    return {"conditions": conditions, "meds": meds, "observations": observations}


def find_care_gaps(bundle):
    summary = summarize(bundle)
    gaps = [gap for gap in (rule(summary) for rule in RULES) if gap]
    gaps.sort(key=lambda g: _SEVERITY_ORDER.get(g["severity"], 9))
    return gaps
