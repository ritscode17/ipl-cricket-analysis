"""
IPL SQL Analysis
================
Three SQL queries against ipl.db (SQLite) demonstrating:
  - Window functions (SUM OVER PARTITION BY) for season-level win share
  - HAVING clauses and subqueries for filtered leaderboards
  - Multi-condition CASE WHEN for toss-outcome joins

Run from project root:
    python scripts/run_sql_queries.py
"""

import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("data/ipl.db")

print("\n===== IPL SQL ANALYSIS =====\n")

# ---------------------------------------------------
# QUERY 1: Team Win Percentage
# ---------------------------------------------------

query1 = """
SELECT 
    SUBSTR(m.date, 1, 4) AS year,

    m.winner AS team,

    COUNT(*) AS wins,

    ROUND(
        COUNT(*) * 100.0 /

        SUM(COUNT(*)) OVER (
            PARTITION BY SUBSTR(m.date, 1, 4)
        ),

        1
    ) AS win_pct

FROM matches m

WHERE m.result = 'normal'

GROUP BY year, m.winner

ORDER BY year, wins DESC;
"""

team_win = pd.read_sql_query(query1, conn)

print("\nTEAM WIN PERCENTAGE\n")
print(team_win.head(10))

# ---------------------------------------------------
# QUERY 2: Top Batsmen
# ---------------------------------------------------

query2 = """
SELECT 
    batsman,
    COUNT(DISTINCT match_id) AS matches,
    SUM(batsman_runs) AS total_runs,

    ROUND(
        SUM(batsman_runs) * 100.0 /

        COUNT(
            CASE
                WHEN wide_runs = 0
                AND noball_runs = 0
                THEN 1
            END
        ),

        2
    ) AS strike_rate

FROM deliveries

WHERE is_super_over = 0

GROUP BY batsman

HAVING COUNT(DISTINCT match_id) >= 20

ORDER BY total_runs DESC

LIMIT 10;
"""

top_batsmen = pd.read_sql_query(query2, conn)

print("\nTOP BATSMEN\n")
print(top_batsmen)

# ---------------------------------------------------
# QUERY 3: Toss Impact
# ---------------------------------------------------

query3 = """
SELECT 

    toss_decision,

    COUNT(*) AS matches,

    SUM(
        CASE
            WHEN toss_winner = winner
            THEN 1
            ELSE 0
        END
    ) AS toss_winner_won_match,

    ROUND(

        SUM(
            CASE
                WHEN toss_winner = winner
                THEN 1
                ELSE 0
            END
        ) * 100.0 /

        COUNT(*),

        1

    ) AS win_pct

FROM matches

WHERE result = 'normal'

GROUP BY toss_decision;
"""

toss_impact = pd.read_sql_query(query3, conn)

print("\nTOSS IMPACT ANALYSIS\n")
print(toss_impact)

# Close database
conn.close()

print("\n===== SQL ANALYSIS COMPLETED =====")