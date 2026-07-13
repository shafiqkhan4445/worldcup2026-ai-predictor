# ============================================================
# simulate.py - Train model & simulate WC 2026 tournament
# ============================================================

import pandas as pd
import numpy as np
from collections import defaultdict
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from wc2026_data import GROUPS, FIFA_RANKINGS

# Load team features
def load_features():
    df = pd.read_csv("data/team_features.csv")
    features = {}
    for _, row in df.iterrows():
        features[row["team"]] = row.to_dict()
    return features

def team_strength(team, features):
    """Calculate overall team strength score (0-1) WITH ELO"""
    if team not in features:
        return 0.3
    f = features[team]
    score = (
        f["elo_normalized"]  * 0.40 +   # Elo = most predictive
        f["fifa_rank_score"] * 0.25 +   # FIFA ranking
        f["win_rate"]        * 0.20 +   # Recent win rate
        f["form_points"]     * 0.10 +   # Form
        f["avg_goals_scored"] / 5 * 0.05 # Goals scored
    )
    return min(score, 1.0)

def predict_match(team_a, team_b, features):
    """
    Predict match outcome between two teams.
    Returns: (goals_a, goals_b)
    """
    str_a = team_strength(team_a, features)
    str_b = team_strength(team_b, features)
    total = str_a + str_b

    # Win probability based on relative strength
    prob_a = str_a / total
    prob_b = str_b / total
    prob_draw = 0.25  # football always has draws!
    prob_a = prob_a * (1 - prob_draw)
    prob_b = prob_b * (1 - prob_draw)

    # Expected goals (Poisson distribution = realistic football scores)
    avg_goals = 2.5
    lambda_a = avg_goals * str_a / total * 1.8
    lambda_b = avg_goals * str_b / total * 1.8

    goals_a = np.random.poisson(lambda_a)
    goals_b = np.random.poisson(lambda_b)
    return goals_a, goals_b

def simulate_group_stage(features):
    """Simulate all 12 groups, return qualified teams"""
    qualified = []     # top 2 from each group
    all_thirds = []    # all third place teams for comparison

    for group_name, teams in GROUPS.items():
        standings = {t: {"pts": 0, "gd": 0, "gf": 0} for t in teams}

        # Play every team against every other (round robin)
        for i in range(len(teams)):
            for j in range(i + 1, len(teams)):
                ta, tb = teams[i], teams[j]
                ga, gb = predict_match(ta, tb, features)

                standings[ta]["gf"] += ga
                standings[tb]["gf"] += gb
                standings[ta]["gd"] += ga - gb
                standings[tb]["gd"] += gb - ga

                if ga > gb:
                    standings[ta]["pts"] += 3
                elif gb > ga:
                    standings[tb]["pts"] += 3
                else:
                    standings[ta]["pts"] += 1
                    standings[tb]["pts"] += 1

        # Sort by points, then goal difference, then goals scored
        sorted_teams = sorted(
            standings.items(),
            key=lambda x: (x[1]["pts"], x[1]["gd"], x[1]["gf"]),
            reverse=True
        )

        qualified.append(sorted_teams[0][0])  # 1st place
        qualified.append(sorted_teams[1][0])  # 2nd place

        # Track third place team with their stats
        third = sorted_teams[2]
        all_thirds.append({
            "team": third[0],
            "pts": third[1]["pts"],
            "gd": third[1]["gd"],
            "gf": third[1]["gf"]
        })

    # Best 8 third-place teams also qualify
    all_thirds.sort(key=lambda x: (x["pts"], x["gd"], x["gf"]), reverse=True)
    for t in all_thirds[:8]:
        qualified.append(t["team"])

    return qualified  # 32 teams total

def simulate_knockout(teams, features):
    """Simulate knockout rounds until we have a winner"""
    remaining = teams.copy()
    np.random.shuffle(remaining)

    rounds = ["Round of 32", "Round of 16", "Quarter Finals", "Semi Finals", "Final"]

    for round_name in rounds:
        if len(remaining) == 1:
            break
        next_round = []
        for i in range(0, len(remaining), 2):
            if i + 1 >= len(remaining):
                next_round.append(remaining[i])
                continue
            ta, tb = remaining[i], remaining[i + 1]
            ga, gb = predict_match(ta, tb, features)

            # In knockouts, no draws — extra time/penalties
            if ga == gb:
                # Coin flip weighted by strength for penalties
                str_a = team_strength(ta, features)
                str_b = team_strength(tb, features)
                winner = ta if np.random.random() < str_a / (str_a + str_b) else tb
            else:
                winner = ta if ga > gb else tb
            next_round.append(winner)
        remaining = next_round

    return remaining[0]

def run_simulation(n_simulations=10000):
    """Run full tournament simulation N times"""
    print(f"🔄 Running {n_simulations:,} tournament simulations...\n")
    features = load_features()
    win_counts = defaultdict(int)

    for i in range(n_simulations):
        if (i + 1) % 1000 == 0:
            print(f"   Completed {i + 1:,} simulations...")
        qualified = simulate_group_stage(features)
        winner = simulate_knockout(qualified, features)
        win_counts[winner] += 1

    # Convert to probabilities
    results = {}
    for team, count in win_counts.items():
        results[team] = round((count / n_simulations) * 100, 2)

    return dict(sorted(results.items(), key=lambda x: x[1], reverse=True))

if __name__ == "__main__":
    print("🏆 FIFA World Cup 2026 - AI Tournament Simulator")
    print("=" * 50)

    results = run_simulation(n_simulations=10000)

    print("\n🏆 WORLD CUP 2026 WIN PROBABILITIES")
    print("=" * 50)
    medals = ["🥇", "🥈", "🥉"]
    for i, (team, prob) in enumerate(results.items()):
        if prob < 0.5:
            break
        medal = medals[i] if i < 3 else "  "
        bar = "█" * int(prob / 2)
        print(f"{medal} {team:<25} {prob:>5.1f}%  {bar}")

    print("\n📊 Full results saved!")
    pd.DataFrame(
        list(results.items()), columns=["Team", "Win_Probability_%"]
    ).to_csv("results/wc2026_predictions.csv", index=False)