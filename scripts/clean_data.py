"""
IPL Data Cleaning
=================
Cleans and feature-engineers both raw datasets.

matches transformations:
  - Parse dates; extract year and month
  - Standardise team names across seasons
    (e.g. 'Delhi Daredevils' → 'Delhi Capitals')
  - Remove ties and no-result matches
  - Add toss_won_match flag (did toss winner also win the match?)
  - Add bat_first_team and bat_first_won columns

deliveries transformations:
  - Remove super-over deliveries (distort scoring stats)
  - Classify each delivery into phase: Powerplay / Middle / Death
  - Flag legal deliveries (no wide, no no-ball) for economy calculations
  - Add boundary, six, four, and wicket indicator columns

Outputs:
    data/processed/matches_clean.csv
    data/processed/deliveries_clean.csv

Run from project root:
    python scripts/clean_data.py
"""

import pandas as pd
import numpy as np
def clean_matches(df):
    # 1. Fix date column
    df["date"] = pd.to_datetime(df["date"], format="mixed")
    df["year"]  = df["date"].dt.year
    df["month"] = df["date"].dt.month
    # 2. Standardise team names across seasons (teams renamed over years)
    name_map = {
        "Delhi Daredevils":       "Delhi Capitals",
        "Deccan Chargers":        "Sunrisers Hyderabad",
        "Rising Pune Supergiants":"Rising Pune Supergiant",
        "Kings XI Punjab":        "Punjab Kings",
    }
    for col in ["team1", "team2", "toss_winner", "winner"]:
        df[col] = df[col].replace(name_map)
    # 3. Handle ties and no-result matches
    df["result_clean"] = df["result"].fillna("normal")
    df_valid = df[df["result_clean"] == "normal"].copy()
    # 4. Toss advantage flag
    df_valid["toss_won_match"] = (df_valid["toss_winner"] == df_valid["winner"]).astype(int)
    # 5. Batting/chasing indicator
    df_valid["bat_first_team"] = np.where(
        df_valid["toss_decision"] == "bat",
        df_valid["toss_winner"],
        np.where(df_valid["toss_winner"] == df_valid["team1"], df_valid["team2"], df_valid["team1"])
    )
    df_valid["bat_first_won"] = (df_valid["bat_first_team"] == df_valid["winner"]).astype(int)
    return df_valid
def clean_deliveries(df):
    # 1. Remove super overs (they distort scoring stats)
    df = df[df["is_super_over"] == 0].copy()
    # 2. Phase classification
    def classify_phase(over):
        if over <= 6:  return "Powerplay"
        elif over <= 15: return "Middle"
        else: return "Death"
    df["phase"] = df["over"].apply(classify_phase)
    # 3. Legal deliveries flag (for economy calculation)
    df["is_legal"] = ((df["wide_runs"] == 0) & (df["noball_runs"] == 0)).astype(int)
    # 4. Boundary flag
    df["is_boundary"] = df["batsman_runs"].isin([4, 6]).astype(int)
    df["is_six"]      = (df["batsman_runs"] == 6).astype(int)
    df["is_four"]     = (df["batsman_runs"] == 4).astype(int)
    # 5. Wicket flag (legal dismissals only — not run-out off wide)
    df["is_wicket"] = df["player_dismissed"].notna().astype(int)
    return df
matches    = clean_matches(pd.read_csv("data/raw/matches.csv"))
deliveries = clean_deliveries(pd.read_csv("data/raw/deliveries.csv"))
matches.to_csv("data/processed/matches_clean.csv", index=False)
deliveries.to_csv("data/processed/deliveries_clean.csv", index=False)