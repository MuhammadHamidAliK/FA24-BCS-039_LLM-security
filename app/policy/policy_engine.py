from dataclasses import dataclass

from app.utils.config import load_config


@dataclass
class PolicyResult:
    decision: str
    final_risk: float
    safe_text: str | None
    reason_codes: list[str]


def decide(
    rule_score: float,
    semantic_score: float,
    rule_reasons: list[str],
    semantic_reasons: list[str],
    pii_entities: list[dict],
) -> PolicyResult:
    cfg = load_config()
    w, t = cfg["weights"], cfg["thresholds"]
    pii_risk = w["pii"] if pii_entities else 0.0
    secret_risk = w["secret"] if any(e["type"] == "API_KEY" for e in pii_entities) else 0.0
    base = max(rule_score, semantic_score)
    final_risk = round(base + pii_risk + secret_risk, 3)
    reasons = list(dict.fromkeys(rule_reasons + semantic_reasons))

    attack = (
        rule_score >= t["rule_block"]
        or semantic_score >= t["semantic_block"]
        or final_risk >= t["final_block"]
        or bool(semantic_reasons)
    )
    if attack:
        if "SYSTEM_PROMPT_EXTRACTION" in reasons or any("SYSTEM_PROMPT" in r for r in reasons):
            reasons.append("SYSTEM_PROMPT_EXTRACTION")
        return PolicyResult("BLOCK", final_risk, None, list(dict.fromkeys(reasons)))

    if pii_entities:
        return PolicyResult("MASK", final_risk, None, reasons + ["PII_DETECTED"])

    return PolicyResult("ALLOW", final_risk, None, reasons or ["SAFE"])
