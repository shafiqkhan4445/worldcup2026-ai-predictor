# ============================================================
# features.py - Load data & build team strength features
# NOW INCLUDES ELO RATINGS
# ============================================================

import pandas as pd
import numpy as np
from wc2026_data import GROUPS, FIFA_RANKINGS

def load_matches():
    df = pd.read_csv("data/all_matches.csv")
    print(f"✅ Loaded {len(df)} matches")
    print(f"   Date range: {df['date'].min()} to {df['date'].max()}")
    return df

def load_elo():
    df = pd.read_csv("data/elo_ratings_wc2026.csv")
    print(f"✅ Loaded Elo ratings: {len(df)} rows")
    return df

def get_latest_elo(elo_df, team):
    """Get the most recent Elo rating for a team"""
    # Try to match team name
    team_data = elo_df[elo_df["country"].str.lower() == team.lower()]
    
    if len(team_data) == 0:
        # Try partial match
        team_data = elo_df[elo_df["country"].str.lower().str.contains(
            team.lower().split()[0], na=False
        )]
    
    if len(team_data) == 0:
        return None
    
    # Get most recent snapshot
    latest = team_data.sort_values("snapshot_date").iloc[-1]
    return latest["rating"]

def get_recent_form(matches_df, team, n_matches=10):
    """Get a team's recent form - last N matches"""
    team_matches = matches_df[
        (matches_df["home_team"] == team) |
        (matches_df["away_team"] == team)
    ].copy()

    team_matches["date"] = pd.to_datetime(team_matches["date"])
    team_matches = team_matches.sort_values("date").tail(n_matches)

    wins, draws, losses = 0, 0, 0
    goals_scored, goals_conceded = 0, 0

    for _, row in team_matches.iterrows():
        if row["home_team"] == team:
            gf, ga = row["home_score"], row["away_score"]
        else:
            gf, ga = row["away_score"], row["home_score"]

        goals_scored += gf
        goals_conceded += ga

        if gf > ga: wins += 1
        elif gf == ga: draws += 1
        else: losses += 1

    total = len(team_matches)
    return {
        "win_rate": wins / total if total > 0 else 0,
        "draw_rate": draws / total if total > 0 else 0,
        "avg_goals_scored": goals_scored / total if total > 0 else 0,
        "avg_goals_conceded": goals_conceded / total if total > 0 else 0,
        "form_points": (wins * 3 + draws) / (total * 3) if total > 0 else 0,
    }

def build_team_features(matches_df, elo_df):
    """Build feature set for all 48 WC teams including Elo"""
    all_teams = []
    for group, teams in GROUPS.items():
        for team in teams:
            all_teams.append((team, group))

    # Get Elo rating range for normalization
    all_elo_ratings = []
    for team, _ in all_teams:
        elo = get_latest_elo(elo_df, team)
        if elo:
            all_elo_ratings.append(elo)
    
    elo_min = min(all_elo_ratings) if all_elo_ratings else 1500
    elo_max = max(all_elo_ratings) if all_elo_ratings else 2100
    elo_mean = sum(all_elo_ratings) / len(all_elo_ratings)

    features = []
    print("\n📊 Building features for all 48 teams (with Elo)...")

    for team, group in all_teams:
        form = get_recent_form(matches_df, team, n_matches=15)
        fifa_rank = FIFA_RANKINGS.get(team, 50)
        
        # Get Elo rating (normalized 0-1)
        elo_raw = get_latest_elo(elo_df, team)
        if elo_raw:
            elo_normalized = (elo_raw - elo_min) / (elo_max - elo_min)
        else:
            # Fallback: estimate from FIFA rank
            elo_raw = elo_mean - (fifa_rank * 5)
            elo_normalized = max(0, (elo_raw - elo_min) / (elo_max - elo_min))

        features.append({
            "team": team,
            "group": group,
            "fifa_rank": fifa_rank,
            "fifa_rank_score": 1 / fifa_rank,
            "elo_rating": elo_raw,
            "elo_normalized": round(elo_normalized, 4),
            **form
        })

    df = pd.DataFrame(features)
    print(f"✅ Built features for {len(df)} teams")
    return df

if __name__ == "__main__":
    print("=== Loading Data & Building Features ===\n")

    matches = load_matches()
    elo = load_elo()

    print()
    team_features = build_team_features(matches, elo)

    print("\n📋 Top 15 teams by Elo rating:")
    top15 = team_features.sort_values("elo_rating", ascending=False).head(15)
    print(top15[["team", "group", "fifa_rank", "elo_rating", 
                  "win_rate", "form_points"]].to_string(index=False))

    team_features.to_csv("data/team_features.csv", index=False)
    print("\n✅ Saved updated features to data/team_features.csv")