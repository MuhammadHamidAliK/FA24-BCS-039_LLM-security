"""Evaluate gateway on data/final_eval.csv; writes results/ metrics."""
import json
from pathlib import Path

import pandas as pd
from sklearn.metrics import classification_report, precision_recall_fscore_support

from app.gateway import analyze_input

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data" / "final_eval.csv"
OUT = ROOT / "results"


def main():
    if not DATA.exists():
        import subprocess
        import sys

        subprocess.run([sys.executable, str(ROOT / "scripts" / "generate_eval_csv.py")], check=True)
    df = pd.read_csv(DATA)
    rows = []
    for _, r in df.iterrows():
        res = analyze_input(str(r["prompt"]), str(r["id"]))
        rows.append({**res, "expected_policy": r["expected_policy"], "match": res["decision"] == r["expected_policy"]})

    out_df = pd.DataFrame(rows)
    OUT.mkdir(exist_ok=True)
    out_df.to_csv(OUT / "evaluation_results.csv", index=False)

    y_true, y_pred = df["expected_policy"], out_df["decision"]
    p, r, f1, _ = precision_recall_fscore_support(y_true, y_pred, average="weighted", zero_division=0)
    metrics = {
        "policy_accuracy": float(out_df["match"].mean()),
        "weighted_precision": float(p),
        "weighted_recall": float(r),
        "weighted_f1": float(f1),
        "mean_latency_ms": float(out_df["latency_ms"].mean()),
        "p95_latency_ms": float(out_df["latency_ms"].quantile(0.95)),
        "per_class": classification_report(y_true, y_pred, zero_division=0, output_dict=True),
    }
    (OUT / "metrics_summary.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print(f"Accuracy: {metrics['policy_accuracy']:.3f} | Mean latency: {metrics['mean_latency_ms']:.0f}ms")


if __name__ == "__main__":
    main()
