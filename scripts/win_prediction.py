"""
IPL Win Prediction Model
========================
Logistic Regression classifier that predicts whether the batting team
will win, using match state features captured at ball 60 (midpoint of
the 2nd innings — i.e. 10 overs in).

Features (all computed at the 60-ball mark):
    runs_so_far     Cumulative 2nd-innings runs
    wickets_lost    Cumulative wickets fallen
    runs_required   Runs still needed (target - runs_so_far + 1)
    balls_remaining Balls left in the innings (120 - 60 = 60)
    rrr             Required run rate = runs_required * 6 / balls_remaining
    target          1st-innings total

Pipeline:
    StandardScaler → LogisticRegression (max_iter=1000)
    80/20 stratified train-test split (random_state=42)

Run from project root:
    python scripts/win_prediction.py
"""

import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score, classification_report

# ---------------------------------------------------
# LOAD CLEANED DATASETS
# ---------------------------------------------------

matches = pd.read_csv("data/processed/matches_clean.csv")
deliveries = pd.read_csv("data/processed/deliveries_clean.csv")

print("\n===== IPL WIN PREDICTION MODEL =====\n")

# ---------------------------------------------------
# FEATURE ENGINEERING
# ---------------------------------------------------

# First innings total = target
first_inn_totals = (
    deliveries[deliveries["inning"] == 1]
    .groupby("match_id")["total_runs"]
    .sum()
    .reset_index(name="target")
)

# Second innings data
second_inn = deliveries[
    deliveries["inning"] == 2
].copy()

# Merge target scores
second_inn = second_inn.merge(
    first_inn_totals,
    on="match_id"
)

# Merge winner information
second_inn = second_inn.merge(
    matches[["id", "winner"]]
    .rename(columns={"id": "match_id"}),
    on="match_id",
    how="left"
)

# ---------------------------------------------------
# SORT BALL-BY-BALL
# ---------------------------------------------------

second_inn = second_inn.sort_values(
    ["match_id", "over", "ball"]
)

# ---------------------------------------------------
# RUNNING MATCH FEATURES
# ---------------------------------------------------

# Runs scored so far
second_inn["runs_so_far"] = (
    second_inn.groupby("match_id")["total_runs"]
    .cumsum()
)

# Wickets lost
second_inn["wickets_lost"] = (
    second_inn.groupby("match_id")["is_wicket"]
    .cumsum()
)

# Balls bowled
second_inn["balls_bowled"] = (
    second_inn.groupby("match_id")
    .cumcount() + 1
)

# Balls remaining
second_inn["balls_remaining"] = (
    120 - second_inn["balls_bowled"]
)

# Runs required
second_inn["runs_required"] = (
    second_inn["target"]
    - second_inn["runs_so_far"]
    + 1
)

# Required run rate
second_inn["rrr"] = (
    second_inn["runs_required"] * 6 /
    second_inn["balls_remaining"].replace(0, 1)
).round(2)

# ---------------------------------------------------
# CREATE TARGET VARIABLE
# ---------------------------------------------------

second_inn["batting_won"] = (
    second_inn["batting_team"]
    == second_inn["winner"]
).astype(int)

# ---------------------------------------------------
# SNAPSHOT AT HALFWAY POINT
# ---------------------------------------------------

snapshot = second_inn[
    second_inn["balls_bowled"] == 60
].copy()

# Features for prediction
features = [
    "runs_so_far",
    "wickets_lost",
    "runs_required",
    "balls_remaining",
    "rrr",
    "target"
]

X = snapshot[features].dropna()

y = snapshot.loc[
    X.index,
    "batting_won"
]

# ---------------------------------------------------
# TRAIN TEST SPLIT
# ---------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# ---------------------------------------------------
# FEATURE SCALING
# ---------------------------------------------------

scaler = StandardScaler()

X_train_s = scaler.fit_transform(X_train)

X_test_s = scaler.transform(X_test)

# ---------------------------------------------------
# TRAIN MODEL
# ---------------------------------------------------

model = LogisticRegression(
    max_iter=1000
)

model.fit(
    X_train_s,
    y_train
)

# ---------------------------------------------------
# PREDICTIONS
# ---------------------------------------------------

y_pred = model.predict(X_test_s)

# ---------------------------------------------------
# RESULTS
# ---------------------------------------------------

accuracy = accuracy_score(
    y_test,
    y_pred
)

print(f"Accuracy: {accuracy:.3f}")

print("\nClassification Report:\n")

print(
    classification_report(
        y_test,
        y_pred
    )
)

print("\n===== MODEL COMPLETED =====")