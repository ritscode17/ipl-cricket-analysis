"""
IPL EDA Analysis
================
Builds a 4-panel summary dashboard saved to assets/ipl_dashboard.png:

  Panel 1 (top-left)  — Average runs per match phase (Powerplay / Middle / Death)
  Panel 2 (top-right) — Top 10 career run scorers (horizontal bar)
  Panel 3 (bottom-left) — Toss win % by decision (bat vs field) vs 50% baseline
  Panel 4 (bottom-right) — Dismissal type distribution (pie, top 6 types)

Run from project root:
    python scripts/eda_analysis.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.ticker as mticker
matches    = pd.read_csv("data/processed/matches_clean.csv")
deliveries = pd.read_csv("data/processed/deliveries_clean.csv")
# 
# ANALYSIS 1: Team Win Percentage
# 
total_played = pd.concat([
    matches[["year","team1"]].rename(columns={"team1":"team"}),
    matches[["year","team2"]].rename(columns={"team2":"team"})
]).groupby("team").size().reset_index(name="played")
wins = matches.groupby("winner").size().reset_index(name="wins")
team_stats = total_played.merge(wins, left_on="team", right_on="winner", how="left")
team_stats["win_pct"] = (team_stats["wins"] / team_stats["played"] * 100).round(1)
team_stats = team_stats[team_stats["played"] >= 30].sort_values("win_pct", ascending=False)
# 
# ANALYSIS 2: Batsman Career Stats
# 
bat_stats = deliveries.groupby("batsman").agg(
    runs        = ("batsman_runs", "sum"),
    sixes       = ("is_six",       "sum"),
    fours       = ("is_four",      "sum"),
    boundaries  = ("is_boundary",  "sum"),
    dismissals  = ("is_wicket",    "sum"),
    balls_faced = ("is_legal",     "sum"),
    matches     = ("match_id",     "nunique"),
).reset_index()
bat_stats["strike_rate"] = (bat_stats["runs"] / bat_stats["balls_faced"] * 100).round(2)
bat_stats["average"]     = (bat_stats["runs"] / bat_stats["dismissals"].replace(0, np.nan)).round(2)
bat_stats = bat_stats[bat_stats["matches"] >= 20].sort_values("runs", ascending=False)
top_batsmen = bat_stats.head(15)
# 
# ANALYSIS 3: Bowler Stats
# 
bowl_stats = deliveries.groupby("bowler").agg(
    wickets      = ("is_wicket",  "sum"),
    runs_given   = ("total_runs", "sum"),
    legal_balls  = ("is_legal",   "sum"),
    matches      = ("match_id",   "nunique"),
).reset_index()
bowl_stats["economy"] = (bowl_stats["runs_given"] / bowl_stats["legal_balls"] * 6).round(2)
bowl_stats["avg"]     = (bowl_stats["runs_given"] / bowl_stats["wickets"].replace(0,np.nan)).round(2)
bowl_stats["sr"]      = (bowl_stats["legal_balls"] / bowl_stats["wickets"].replace(0,np.nan)).round(2)
bowl_stats = bowl_stats[(bowl_stats["matches"] >= 15) & (bowl_stats["wickets"] >= 20)]
bowl_stats = bowl_stats.sort_values("wickets", ascending=False)
# 
# VISUALISATION: Run scoring by phase
# 
phase_runs = deliveries.groupby(["match_id","inning","phase"]).agg(
    runs=("total_runs","sum")
).reset_index()
phase_avg = phase_runs.groupby("phase")["runs"].mean().reset_index()
phase_order = ["Powerplay", "Middle", "Death"]
phase_avg["phase"] = pd.Categorical(phase_avg["phase"], categories=phase_order, ordered=True)
phase_avg = phase_avg.sort_values("phase")
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle("IPL Performance Analysis Dashboard", fontsize=16, fontweight="bold")
# Plot 1: Phase runs
axes[0,0].bar(phase_avg["phase"], phase_avg["runs"], color=["#333333","#777777","#AAAAAA"])
axes[0,0].set_title("Average Runs by Match Phase")
axes[0,0].set_ylabel("Average Runs")
# Plot 2: Top batsmen
top10_bat = top_batsmen.head(10)
axes[0,1].barh(top10_bat["batsman"], top10_bat["runs"], color="#333333")
axes[0,1].set_title("Top 10 Run Scorers (Career)")
axes[0,1].set_xlabel("Total Runs")
axes[0,1].invert_yaxis()
# Plot 3: Toss decision impact
toss_impact = matches.groupby("toss_decision")["toss_won_match"].mean().reset_index()
axes[1,0].bar(toss_impact["toss_decision"], toss_impact["toss_won_match"]*100, color=["#333333","#777777"])
axes[1,0].set_title("Toss Win % by Decision (bat/field)")
axes[1,0].set_ylabel("Match Win %")
axes[1,0].axhline(50, color="red", linestyle="--", linewidth=1, label="50% baseline")
axes[1,0].legend()
# Plot 4: Dismissal types
dismiss_counts = deliveries[deliveries["dismissal_kind"].notna()]["dismissal_kind"].value_counts()
axes[1,1].pie(dismiss_counts[:6], labels=dismiss_counts.index[:6],
              autopct="%1.1f%%", colors=plt.cm.Greys(np.linspace(0.3, 0.9, 6)))
axes[1,1].set_title("Dismissal Types Distribution")
plt.tight_layout()
plt.savefig("assets/ipl_dashboard.png", dpi=150, bbox_inches="tight")
print("Saved: assets/ipl_dashboard.png")