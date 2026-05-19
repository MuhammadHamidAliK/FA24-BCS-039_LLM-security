import time
import uuid
from typing import Any

from app.detectors import rule_detector, semantic_detector
from app.pii import presidio_custom
from app.policy import policy_engine
from app.utils import language
from app.utils.logging import audit_log


def analyze_input(text: str, input_id: str | None = None) -> dict[str, Any]:
    t0 = time.perf_counter()
    input_id = input_id or f"req_{uuid.uuid4().hex[:8]}"

    rule = rule_detector.analyze(text)
    sem = semantic_detector.analyze(text)
    pii_entities, masked = presidio_custom.analyze(text)
    policy = policy_engine.decide(rule.score, sem.score, rule.reason_codes, sem.reason_codes, pii_entities)

    safe_text = masked if policy.decision == "MASK" else (text if policy.decision == "ALLOW" else None)
    latency_ms = int((time.perf_counter() - t0) * 1000)

    out = {
        "input_id": input_id,
        "language": language.detect_language(text),
        "rule_score": round(rule.score, 3),
        "semantic_score": round(sem.score, 3),
        "pii_entities": pii_entities,
        "final_risk": policy.final_risk,
        "decision": policy.decision,
        "safe_text": safe_text,
        "reason_codes": policy.reason_codes,
        "latency_ms": latency_ms,
    }
    audit_log(out)
    return out
