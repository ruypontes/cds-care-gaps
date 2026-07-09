# cds-care-gaps

A small clinical decision support engine that reads a FHIR patient bundle and flags guideline care gaps, each with the resources that triggered it. Every recommendation is traceable back to the data. Standard library only.

A recommendation a clinician cannot trace is a recommendation they will not trust. So each gap carries an `evidence` list of `ResourceType/id` references.

## Rules shipped

- Active diabetes with no documented HbA1c.
- HbA1c at or above 9%, poor glycemic control.
- Diabetic patient not on a statin.
- Hypertension with no documented blood pressure.
- Metformin prescribed alongside chronic kidney disease (a safety check).

## Quickstart

```bash
python caregaps_cli.py --bundle data/bundles/case_metformin_ckd.json
```

As a library:

```python
from caregaps import find_care_gaps, load_bundle
find_care_gaps(load_bundle("data/bundles/case_poor_control.json"))
```

Gaps come back sorted high severity first.

## Scope

The rules are simple and illustrative, not a validated guideline set, and they read a fixed subset of FHIR (Condition, MedicationRequest, Observation). The design is what to reuse: rules are plain functions of a parsed summary, each returning a gap with traceable evidence, so adding a rule or wiring these into CDS Hooks is straightforward. Bundles under `data/bundles/` are synthetic.

## Tests

```bash
python -m pytest
```

## License

MIT. See [LICENSE](LICENSE).
