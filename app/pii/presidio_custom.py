import re
from functools import lru_cache

from presidio_analyzer import AnalyzerEngine, Pattern, PatternRecognizer, RecognizerResult
from presidio_anonymizer import AnonymizerEngine
from presidio_anonymizer.entities import OperatorConfig

from app.utils.config import load_config

_CONTEXT = re.compile(
    r"\b(email|phone|cnic|student\s*id|api\s*key|password|token)\b", re.I
)
_COMPOSITE_PAIRS = {("PERSON", "PHONE_NUMBER"), ("STUDENT_ID", "EMAIL_ADDRESS"), ("PERSON", "API_KEY")}
_PLACEHOLDERS = {
    "PERSON": "<PERSON>",
    "EMAIL_ADDRESS": "<EMAIL>",
    "PHONE_NUMBER": "<PHONE>",
    "CNIC": "<CNIC>",
    "API_KEY": "<API_KEY>",
    "STUDENT_ID": "<STUDENT_ID>",
}


def _custom_recognizers():
    return [
        PatternRecognizer(
            supported_entity="CNIC",
            patterns=[Pattern("CNIC", r"\b\d{5}-\d{7}-\d\b", 0.85)],
            context=["cnic", "nic", "id card"],
        ),
        PatternRecognizer(
            supported_entity="STUDENT_ID",
            patterns=[Pattern("SID", r"\b[A-Z]{2}\d{2}[A-Z]{3}-\d{3,4}\b", 0.8)],
            context=["student", "registration", "roll"],
        ),
        PatternRecognizer(
            supported_entity="API_KEY",
            patterns=[
                Pattern("API", r"(?i)\b(sk-[a-zA-Z0-9]{20,}|api[_-]?key\s*[:=]\s*\S+)\b", 0.85)
            ],
            context=["api", "key", "token", "secret"],
        ),
    ]


@lru_cache
def _analyzer() -> AnalyzerEngine:
    engine = AnalyzerEngine()
    for rec in _custom_recognizers():
        engine.registry.add_recognizer(rec)
    return engine


def _boost(results: list[RecognizerResult], text: str) -> list[RecognizerResult]:
    cfg = load_config()["presidio"]
    ctx_near = bool(_CONTEXT.search(text))
    out = []
    for r in results:
        score = r.score
        if ctx_near and r.entity_type in ("EMAIL_ADDRESS", "PHONE_NUMBER", "CNIC", "STUDENT_ID", "API_KEY"):
            score = min(1.0, score + cfg["context_boost"])
        thr = cfg["entity_thresholds"].get(r.entity_type, 0.5)
        if score >= thr:
            out.append(RecognizerResult(r.entity_type, r.start, r.end, score))
    types = {r.entity_type for r in out}
    if any(a in types and b in types for a, b in _COMPOSITE_PAIRS):
        out = [
            RecognizerResult(
                r.entity_type,
                r.start,
                r.end,
                min(1.0, r.score + cfg["composite_boost"]),
            )
            if r.entity_type in {t for pair in _COMPOSITE_PAIRS for t in pair}
            else r
            for r in out
        ]
    return out


def analyze(text: str) -> tuple[list[dict], str | None]:
    raw = _analyzer().analyze(text=text, language="en")
    boosted = _boost(raw, text)
    entities = [
        {"type": r.entity_type, "text": text[r.start : r.end], "score": round(r.score, 3)}
        for r in boosted
    ]
    if not entities:
        return [], text
    ops = {e["type"]: OperatorConfig("replace", {"new_value": _PLACEHOLDERS.get(e["type"], f"<{e['type']}>")}) for e in entities}
    masked = AnonymizerEngine().anonymize(text=text, analyzer_results=boosted, operators=ops).text
    return entities, masked
