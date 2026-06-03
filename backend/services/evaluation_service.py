"""
Model evaluation utilities for Football BDA.

This module builds a supervised evaluation dataset from the raw Wyscout event
logs, trains a lightweight baseline on a train/test split, and returns
reproducible metrics for both classification and regression tasks.
"""

from __future__ import annotations

import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestRegressor
from sklearn.metrics import (
    accuracy_score,
    f1_score,
    mean_absolute_error,
    mean_squared_error,
    precision_score,
    r2_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
EVENT_FILES = [
    DATA_DIR / "events_European_Championship.json",
    DATA_DIR / "events_World_Cup.json",
]
TEAMS_FILE = DATA_DIR / "teams.json"
DEFAULT_REPORT_PATH = DATA_DIR / "model_evaluation.json"


MATCH_EVENT_TYPES = ["Pass", "Shot", "Foul", "Duel", "Free Kick", "Offside"]


def _load_json(path: Path):
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _goal_event(event: Dict) -> bool:
    if event.get("eventName") != "Shot":
        return False
    return any(tag.get("id") == 101 for tag in event.get("tags", []) if isinstance(tag, dict))


def _count_tag(event: Dict, tag_id: int) -> int:
    return int(any(tag.get("id") == tag_id for tag in event.get("tags", []) if isinstance(tag, dict)))


def _team_match_stats(events: Iterable[Dict]) -> Dict[str, float]:
    stats = {f"match_{event_type.lower().replace(' ', '_')}": 0 for event_type in MATCH_EVENT_TYPES}
    stats["match_accurate_passes"] = 0
    stats["match_shots_on_target"] = 0
    stats["match_total_events"] = 0

    for event in events:
        event_name = event.get("eventName")
        if event_name in MATCH_EVENT_TYPES:
            key = f"match_{event_name.lower().replace(' ', '_')}"
            stats[key] += 1
            stats["match_total_events"] += 1

            if event_name == "Pass":
                stats["match_accurate_passes"] += _count_tag(event, 1801)
            elif event_name == "Shot":
                stats["match_shots_on_target"] += _count_tag(event, 201)

    passes = stats.get("match_pass", 0)
    shots = stats.get("match_shot", 0)

    stats["match_pass_accuracy_rate"] = stats["match_accurate_passes"] / passes if passes else 0.0
    stats["match_shot_accuracy_rate"] = stats["match_shots_on_target"] / shots if shots else 0.0
    return stats


def _history_snapshot(history: Dict[str, float]) -> Dict[str, float]:
    matches = max(history["matches"], 1)
    return {
        "matches": history["matches"],
        "wins": history["wins"],
        "draws": history["draws"],
        "losses": history["losses"],
        "goals_for_pm": history["goals_for"] / matches,
        "goals_against_pm": history["goals_against"] / matches,
        "goal_diff_pm": (history["goals_for"] - history["goals_against"]) / matches,
        "shots_pm": history["shots"] / matches,
        "passes_pm": history["passes"] / matches,
        "fouls_pm": history["fouls"] / matches,
    }


def _team_goal_count(events: Iterable[Dict]) -> int:
    return sum(1 for event in events if _goal_event(event))


def _build_match_rows() -> Tuple[pd.DataFrame, Dict[str, int]]:
    teams = _load_json(TEAMS_FILE)
    team_names = {int(team["wyId"]): team.get("name") for team in teams if team.get("wyId") is not None}

    match_groups: Dict[int, List[Dict]] = defaultdict(list)
    for event_file in EVENT_FILES:
        for event in _load_json(event_file):
            match_groups[int(event["matchId"])] += [event]

    rows: List[Dict[str, float]] = []
    source_counts: Counter = Counter()
    history = defaultdict(lambda: Counter())

    for match_id, events in sorted(match_groups.items()):
        team_ids = sorted({int(event["teamId"]) for event in events if event.get("teamId") is not None})
        if len(team_ids) != 2:
            continue

        team1_id, team2_id = team_ids
        team1_all = [event for event in events if int(event["teamId"]) == team1_id]
        team2_all = [event for event in events if int(event["teamId"]) == team2_id]
        team1_stats = _history_snapshot(history[team1_id])
        team2_stats = _history_snapshot(history[team2_id])
        team1_goals = _team_goal_count(team1_all)
        team2_goals = _team_goal_count(team2_all)

        if team1_goals > team2_goals:
            outcome_label = 1
            source_counts["team1_win"] += 1
        elif team2_goals > team1_goals:
            outcome_label = 2
            source_counts["team2_win"] += 1
        else:
            outcome_label = 0
            source_counts["draw"] += 1

        row = {
            "match_id": match_id,
            "team1_id": team1_id,
            "team2_id": team2_id,
            "team1_name": team_names.get(team1_id, str(team1_id)),
            "team2_name": team_names.get(team2_id, str(team2_id)),
            "team1_goals": team1_goals,
            "team2_goals": team2_goals,
            "goal_difference": team1_goals - team2_goals,
            "outcome_label": outcome_label,
            "outcome_name": {0: "draw", 1: "team1_win", 2: "team2_win"}[outcome_label],
        }

        for key in team1_stats:
            row[f"home_{key}"] = team1_stats[key]
            row[f"away_{key}"] = team2_stats[key]
            row[f"diff_{key}"] = team1_stats[key] - team2_stats[key]

        rows.append(row)

        def _update_history(team_id: int, goals_for: int, goals_against: int, team_events: List[Dict]) -> None:
            history[team_id]["matches"] += 1
            history[team_id]["goals_for"] += goals_for
            history[team_id]["goals_against"] += goals_against
            history[team_id]["shots"] += sum(1 for event in team_events if event.get("eventName") == "Shot")
            history[team_id]["passes"] += sum(1 for event in team_events if event.get("eventName") == "Pass")
            history[team_id]["fouls"] += sum(1 for event in team_events if event.get("eventName") == "Foul")
            if goals_for > goals_against:
                history[team_id]["wins"] += 1
            elif goals_against > goals_for:
                history[team_id]["losses"] += 1
            else:
                history[team_id]["draws"] += 1

        _update_history(team1_id, team1_goals, team2_goals, team1_all)
        _update_history(team2_id, team2_goals, team1_goals, team2_all)

    frame = pd.DataFrame(rows)
    return frame, dict(source_counts)


def run_evaluation(test_size: float = 0.25, random_state: int = 42, report_path: Path | None = None) -> Dict:
    """Train and evaluate baseline models on a holdout split."""
    frame, outcome_counts = _build_match_rows()
    if frame.empty:
        raise RuntimeError("Could not build an evaluation dataset from the event logs")

    feature_columns = [
        column
        for column in frame.columns
        if column.startswith(("home_", "away_", "diff_"))
    ]

    X = frame[feature_columns].fillna(0.0)
    y_class = frame["outcome_label"]
    y_reg = frame["goal_difference"]

    X_train, X_test, y_class_train, y_class_test, y_reg_train, y_reg_test = train_test_split(
        X,
        y_class,
        y_reg,
        test_size=test_size,
        random_state=random_state,
        stratify=y_class,
    )

    classifier = GradientBoostingClassifier(
        random_state=random_state,
        n_estimators=200,
        learning_rate=0.05,
        max_depth=2,
    )
    classifier.fit(X_train, y_class_train)
    class_predictions = classifier.predict(X_test)
    class_probabilities = classifier.predict_proba(X_test)

    regressor = RandomForestRegressor(
        n_estimators=800,
        random_state=random_state,
    )
    regressor.fit(X_train, y_reg_train)
    reg_predictions = regressor.predict(X_test)

    classification_metrics = {
        "accuracy": round(float(accuracy_score(y_class_test, class_predictions)), 6),
        "precision_macro": round(float(precision_score(y_class_test, class_predictions, average="macro", zero_division=0)), 6),
        "recall_macro": round(float(recall_score(y_class_test, class_predictions, average="macro", zero_division=0)), 6),
        "f1_macro": round(float(f1_score(y_class_test, class_predictions, average="macro", zero_division=0)), 6),
        "roc_auc_ovr_macro": round(float(roc_auc_score(y_class_test, class_probabilities, multi_class="ovr", average="macro")), 6),
    }

    regression_metrics = {
        "mae": round(float(mean_absolute_error(y_reg_test, reg_predictions)), 6),
        "rmse": round(float(math.sqrt(mean_squared_error(y_reg_test, reg_predictions))), 6),
        "r2": round(float(r2_score(y_reg_test, reg_predictions)), 6),
    }

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": {
            "sources": [path.name for path in EVENT_FILES],
            "matches": int(len(frame)),
            "features": int(len(feature_columns)),
            "feature_columns": feature_columns,
            "outcome_distribution": outcome_counts,
            "train_rows": int(len(X_train)),
            "test_rows": int(len(X_test)),
        },
        "classification": {
            "model": "GradientBoostingClassifier",
            "target": "match_outcome (draw/team1_win/team2_win)",
            "metrics": classification_metrics,
        },
        "regression": {
            "model": "RandomForestRegressor",
            "target": "goal_difference",
            "metrics": regression_metrics,
        },
    }

    output_path = report_path or DEFAULT_REPORT_PATH
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=2)

    return report
