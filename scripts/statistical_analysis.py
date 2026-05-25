"""
IPL Statistical Analysis
========================
Three inferential tests on IPL match and delivery data:

  1. Chi-Square Test of Independence
     H0: Toss decision (bat/field) and match outcome are independent.
     Reject H0 if p < 0.05.

  2. Bootstrap Confidence Interval (10,000 iterations)
     Estimates the population mean innings score with a 95% CI,
     without assuming a normal distribution.

  3. Mann-Whitney U Test (non-parametric)
     Tests whether 1st-innings and 2nd-innings score distributions
     are drawn from the same population.

Run from project root:
    python scripts/statistical_analysis.py
"""

import pandas as pd
import numpy as np
from scipy import stats

# ---------------------------------------------------
# LOAD CLEANED DATA
# ---------------------------------------------------

matches = pd.read_csv("data/processed/matches_clean.csv")
deliveries = pd.read_csv("data/processed/deliveries_clean.csv")

print("\n===== IPL STATISTICAL ANALYSIS =====\n")

# ---------------------------------------------------
# 1. CHI-SQUARE TEST
# Toss decision vs outcome
# ---------------------------------------------------

print("1. Chi-Square Test")

contingency = pd.crosstab(
    matches["toss_decision"],
    matches["toss_won_match"]
)

chi2, p_value, dof, expected = stats.chi2_contingency(contingency)

print(f"Chi-square statistic: {chi2:.4f}")
print(f"p-value: {p_value:.4f}")

print(
    f"Interpretation: "
    f"{'Significant association' if p_value < 0.05 else 'No significant association'}"
)

# ---------------------------------------------------
# 2. BOOTSTRAP CONFIDENCE INTERVAL
# ---------------------------------------------------

print("\n2. Bootstrap Confidence Interval")

def bootstrap_mean(data, n_iterations=10000, ci=95):

    bootstrap_means = [
        np.mean(
            np.random.choice(
                data,
                size=len(data),
                replace=True
            )
        )
        for _ in range(n_iterations)
    ]

    lower = np.percentile(
        bootstrap_means,
        (100 - ci) / 2
    )

    upper = np.percentile(
        bootstrap_means,
        100 - (100 - ci) / 2
    )

    return np.mean(data), lower, upper

innings_scores = (
    deliveries.groupby(["match_id", "inning"])["total_runs"]
    .sum()
    .values
)

mean, lower, upper = bootstrap_mean(innings_scores)

print(
    f"Average innings score: "
    f"{mean:.1f} [{lower:.1f}, {upper:.1f}] (95% CI)"
)

# ---------------------------------------------------
# 3. MANN-WHITNEY U TEST
# ---------------------------------------------------

print("\n3. Mann-Whitney U Test")

first_innings = (
    deliveries[deliveries["inning"] == 1]
    .groupby("match_id")["total_runs"]
    .sum()
)

second_innings = (
    deliveries[deliveries["inning"] == 2]
    .groupby("match_id")["total_runs"]
    .sum()
)

stat, p = stats.mannwhitneyu(
    first_innings,
    second_innings,
    alternative="two-sided"
)

print(f"Mann-Whitney p-value: {p:.4f}")

print("\n===== ANALYSIS COMPLETED =====")