"""Rule-based clinical decision support: care-gap detection over FHIR."""
from .engine import find_care_gaps, load_bundle, summarize

__version__ = "0.1.0"
__all__ = ["find_care_gaps", "load_bundle", "summarize"]
