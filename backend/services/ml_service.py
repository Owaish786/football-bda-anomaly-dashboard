"""
ML services for football analytics.
Currently provides IsolationForest-based anomaly detection on team statistics.
"""

from typing import Dict, List

import pandas as pd
from sklearn.ensemble import IsolationForest

from backend.services.data_provider import REAL_DATA


def detect_team_anomalies(contamination: float = 0.2, top_n: int = 5) -> Dict:
    """Detect anomalous teams using IsolationForest on aggregated team stats."""
    if not REAL_DATA or not REAL_DATA.get("team_stats"):
        return {
            "success": False,
            "error": "No processed real data available for anomaly detection",
            "data": [],
        }

    rows: List[Dict] = REAL_DATA["team_stats"]
    df = pd.DataFrame(rows)

    required_cols = ["teamName", "shots", "passes", "fouls", "total_events", "matches"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        return {
            "success": False,
            "error": f"Missing columns for ML model: {', '.join(missing)}",
            "data": [],
        }

    features = df[["shots", "passes", "fouls", "total_events", "matches"]].fillna(0)

    # Clamp contamination to valid sklearn range (0, 0.5]
    contamination = max(min(contamination, 0.5), 0.01)

    model = IsolationForest(
        n_estimators=200,
        contamination=contamination,
        random_state=42,
    )
    model.fit(features)

    preds = model.predict(features)  # -1 anomaly, 1 normal
    scores = model.decision_function(features)  # lower => more anomalous

    out = df[["teamName", "shots", "passes", "fouls", "total_events", "matches"]].copy()
    out["anomaly_label"] = ["anomaly" if p == -1 else "normal" for p in preds]
    out["anomaly_score"] = scores

    anomalies = (
        out[out["anomaly_label"] == "anomaly"]
        .sort_values("anomaly_score", ascending=True)
        .head(top_n)
    )

    return {
        "success": True,
        "model": "IsolationForest",
        "contamination": contamination,
        "total_teams": int(len(out)),
        "detected_anomalies": int((out["anomaly_label"] == "anomaly").sum()),
        "data": anomalies.to_dict(orient="records"),
    }
