from app.pii.presidio_custom import analyze


def test_cnic_and_student_id_mask():
    text = "My CNIC is 35202-1234567-1 and student ID is FA21BCS-123."
    entities, masked = analyze(text)
    types = {e["type"] for e in entities}
    assert "CNIC" in types or "STUDENT_ID" in types
    assert masked and ("<CNIC>" in masked or "<STUDENT_ID>" in masked)


def test_email_masked():
    text = "My email is ali.khan@example.com. Summarize this message."
    entities, masked = analyze(text)
    assert any(e["type"] == "EMAIL_ADDRESS" for e in entities)
    assert "<EMAIL>" in masked
