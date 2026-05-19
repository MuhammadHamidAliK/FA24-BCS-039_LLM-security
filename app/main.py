from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.gateway import analyze_input

app = FastAPI(title="LLM Security Gateway", version="1.0.0")


class AnalyzeRequest(BaseModel):
    text: str = Field(..., min_length=1)
    input_id: str | None = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    return analyze_input(req.text, req.input_id)
