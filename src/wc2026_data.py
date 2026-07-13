# ============================================================
# FIFA World Cup 2026 - Groups, Format & Rankings (CORRECTED)
# Last updated: June 11, 2026 (official FIFA ranking)
# ============================================================

GROUPS = {
    "A": ["Mexico", "South Africa", "South Korea", "Czech Republic"],
    "B": ["Canada", "Bosnia and Herzegovina", "Qatar", "Switzerland"],
    "C": ["Brazil", "Morocco", "Haiti", "Scotland"],
    "D": ["United States", "Paraguay", "Australia", "Turkey"],
    "E": ["Germany", "Curacao", "Ivory Coast", "Ecuador"],
    "F": ["Netherlands", "Japan", "Sweden", "Tunisia"],
    "G": ["Belgium", "Egypt", "Iran", "New Zealand"],
    "H": ["Spain", "Cape Verde", "Saudi Arabia", "Uruguay"],
    "I": ["France", "Senegal", "Iraq", "Norway"],
    "J": ["Argentina", "Algeria", "Austria", "Jordan"],
    "K": ["Portugal", "DR Congo", "Uzbekistan", "Colombia"],
    "L": ["England", "Croatia", "Ghana", "Panama"],
}

# Official FIFA Rankings - June 11, 2026 (most recent before WC)
FIFA_RANKINGS = {
    "Argentina": 1, "Spain": 2, "France": 3, "England": 4,
    "Portugal": 5, "Brazil": 6, "Netherlands": 7, "Morocco": 8,
    "Belgium": 9, "Germany": 10, "Croatia": 11, "Colombia": 12,
    "Senegal": 13, "Mexico": 14, "Uruguay": 15, "United States": 17,
    "Japan": 18, "Switzerland": 19, "Ecuador": 20, "Turkey": 21,
    "South Korea": 22, "Norway": 23, "Austria": 24, "Sweden": 26,
    "Algeria": 27, "Tunisia": 28, "Scotland": 29, "Czech Republic": 30,
    "Canada": 30, "Saudi Arabia": 32, "Ivory Coast": 33,
    "Paraguay": 34, "Nigeria": 35, "South Africa": 36,
    "Egypt": 37, "Qatar": 38, "Iran": 39,
    "Bosnia and Herzegovina": 40, "Ghana": 41, "Panama": 42,
    "Jordan": 43, "Cape Verde": 44, "Uzbekistan": 45,
    "New Zealand": 46, "DR Congo": 47, "Curacao": 48,
    "Haiti": 49, "Iraq": 50, "Australia": 25,
}

FORMAT = {
    "total_teams": 48,
    "total_groups": 12,
    "teams_per_group": 4,
    "group_matches_per_team": 3,
    "auto_qualifiers_per_group": 2,
    "third_place_qualifiers": 8,
    "total_knockout_teams": 32,
    "knockout_rounds": [
        "Round of 32", "Round of 16",
        "Quarter Finals", "Semi Finals", "Final"
    ],
    "points": {"win": 3, "draw": 1, "loss": 0},
    "tiebreakers": [
        "goal_difference", "goals_scored",
        "head_to_head", "fair_play", "drawing_of_lots"
    ]
}

# Top 4 protected — can only meet in Semis or Final
PROTECTED_TEAMS = ["Argentina", "Spain", "France", "England"]

if __name__ == "__main__":
    print("=== FIFA World Cup 2026 ===")
    print(f"Total teams: {FORMAT['total_teams']}")
    print()
    for group, teams in GROUPS.items():
        print(f"Group {group}: {', '.join(teams)}")
    print()
    print("Top 10 FIFA Rankings (June 11, 2026):")
    top10 = sorted(FIFA_RANKINGS.items(), key=lambda x: x[1])[:10]
    for team, rank in top10:
        print(f"  #{rank} {team}")