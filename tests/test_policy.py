from app.policy.policy_engine import decide


def test_block_on_high_rule_score():
    p = decide(0.9, 0.1, ["DIRECT_INJECTION"], [], [])
    assert p.decision == "BLOCK"


def test_mask_on_pii_only():
    p = decide(0.0, 0.1, [], [], [{"type": "EMAIL_ADDRESS", "text": "a@b.com", "score": 0.9}])
    assert p.decision == "MASK"


def test_allow_safe():
    p = decide(0.0, 0.1, [], [], [])
    assert p.decision == "ALLOW"
