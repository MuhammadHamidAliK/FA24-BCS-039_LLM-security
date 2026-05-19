import re
from dataclasses import dataclass

_LEET = str.maketrans("01345@$!", "oieaslsi")


@dataclass
class RuleResult:
    score: float
    reason_codes: list[str]


_PATTERNS: list[tuple[str, str, float]] = [
    (r"ignore\s+(all\s+)?(previous|prior|earlier)\s+instructions?", "DIRECT_INJECTION", 0.9),
    (r"reveal\s+(the\s+)?system\s+prompt", "SYSTEM_PROMPT_EXTRACTION", 0.92),
    (r"(jailbreak|bypass\s+(all\s+)?safety|unrestricted\s+assistant)", "JAILBREAK", 0.88),
    (r"(api\s*keys?|passwords?|tokens?).{0,40}(in|from|stored\s+in)\s+(your\s+)?context", "SECRET_EXTRACTION", 0.9),
    (r"پالیسی|نظرانداز", "MULTILINGUAL_INJECTION_UR", 0.78),
    (r"우회|안전\s*장치", "MULTILINGUAL_INJECTION_KO", 0.78),
    (r"override\s+(your\s+)?policy", "RAG_TOOL_OVERRIDE", 0.85),
    (r"پچھلی\s*ہدایات|پچھلی\s*ہدایت|پچھلے\s*اصول", "MULTILINGUAL_INJECTION_UR", 0.88),
    (r"سسٹم\s*پرومپٹ|نظام\s*پرامپٹ", "SYSTEM_PROMPT_EXTRACTION_UR", 0.9),
    (r"이전\s*지침|시스템\s*프롬프트", "MULTILINGUAL_INJECTION_KO", 0.88),
    (r"ign0re|instruct!ons|pr0mpt|sh0w\s+system", "OBFUSCATED_ATTACK", 0.82),
    (r"forget\s+(the\s+)?(earlier|previous)\s+rules", "PARAPHRASED_INJECTION", 0.8),
    (r"hidden\s+(configuration|prompt|instructions?)", "PARAPHRASED_INJECTION", 0.78),
    (r"pretend\s+you\s+are", "JAILBREAK", 0.75),
    (r"ignore\s+rules?\s+and\s+email", "MIXED_ATTACK_PII", 0.86),
]


def _normalize(text: str) -> str:
    t = text.lower().translate(_LEET)
    return re.sub(r"\s+", " ", t)


def analyze(text: str) -> RuleResult:
    norm = _normalize(text)
    score, reasons = 0.0, []
    for pattern, code, s in _PATTERNS:
        if re.search(pattern, norm, re.I | re.UNICODE) or re.search(pattern, text, re.I | re.UNICODE):
            score, reasons = max(score, s), reasons + [code]
    return RuleResult(score, list(dict.fromkeys(reasons)))
