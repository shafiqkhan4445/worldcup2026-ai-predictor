# ============================================================
# visualize.py - Beautiful WC 2026 Predictions Chart
# ============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import numpy as np

def get_confederation(team):
    """Return confederation for color coding"""
    UEFA = ["Spain", "France", "England", "Portugal", "Germany",
            "Netherlands", "Belgium", "Croatia", "Switzerland",
            "Austria", "Norway", "Scotland", "Turkey", "Serbia",
            "Denmark", "Sweden", "Czech Republic", "Bosnia and Herzegovina",
            "Ukraine", "Poland", "Slovenia", "Slovakia", "Albania",
            "Georgia", "Romania", "Hungary", "Iceland"]
    CONMEBOL = ["Argentina", "Brazil", "Colombia", "Ecuador",
                "Uruguay", "Paraguay", "Chile", "Venezuela", "Peru"]
    CONCACAF = ["United States", "Mexico", "Canada", "Panama",
                "Costa Rica", "Jamaica", "Honduras", "Curacao", "Haiti"]
    AFC = ["Japan", "South Korea", "Australia", "Iran", "Saudi Arabia",
           "Qatar", "Iraq", "Uzbekistan", "Jordan"]
    CAF = ["Morocco", "Senegal", "Ivory Coast", "Algeria", "Tunisia",
           "Egypt", "South Africa", "Ghana", "Cameroon", "DR Congo",
           "Cape Verde", "Nigeria"]

    if team in UEFA: return "UEFA"
    if team in CONMEBOL: return "CONMEBOL"
    if team in CONCACAF: return "CONCACAF"
    if team in AFC: return "AFC"
    if team in CAF: return "CAF"
    return "OTHER"

# Confederation colors
CONF_COLORS = {
    "UEFA":     "#3b82f6",   # Blue
    "CONMEBOL": "#10b981",   # Green
    "CONCACAF": "#f59e0b",   # Amber
    "AFC":      "#ef4444",   # Red
    "CAF":      "#8b5cf6",   # Purple
    "OTHER":    "#6b7280",   # Gray
}

def create_chart():
    # Load predictions
    df = pd.read_csv("results/wc2026_predictions.csv")
    df = df[df["Win_Probability_%"] >= 0.5].sort_values(
        "Win_Probability_%", ascending=True
    )

    # Add confederation
    df["confederation"] = df["Team"].apply(get_confederation)
    df["color"] = df["confederation"].map(CONF_COLORS)

    fig, ax = plt.subplots(figsize=(14, 12))

    # Dark background
    fig.patch.set_facecolor("#0f172a")
    ax.set_facecolor("#1e293b")

    # Draw bars
    bars = ax.barh(
        df["Team"],
        df["Win_Probability_%"],
        color=df["color"],
        height=0.65,
        edgecolor="none",
        alpha=0.9
    )

    # Add percentage labels on bars
    for bar, (_, row) in zip(bars, df.iterrows()):
        width = bar.get_width()
        ax.text(
            width + 0.15,
            bar.get_y() + bar.get_height() / 2,
            f"{width:.1f}%",
            va="center", ha="left",
            color="white", fontsize=9,
            fontweight="bold"
        )

    # Add medals for top 3
    top3 = df.nlargest(3, "Win_Probability_%")
    medals = {"🥇": 0, "🥈": 0, "🥉": 0}
    medal_list = ["🥇", "🥈", "🥉"]
    top3_teams = top3["Team"].tolist()[::-1]
    for i, team in enumerate(top3_teams[-3:]):
        y_pos = list(df["Team"]).index(team)
        ax.text(
            -0.8, y_pos,
            medal_list[2 - i],
            va="center", ha="center",
            fontsize=13
        )

    # Title and labels
    fig.text(
        0.5, 0.97,
        "🏆 FIFA WORLD CUP 2026",
        ha="center", va="top",
        color="white", fontsize=22,
        fontweight="bold"
    )
    fig.text(
        0.5, 0.93,
        "AI Tournament Simulation — 10,000 Runs",
        ha="center", va="top",
        color="#94a3b8", fontsize=12
    )

    # Axis styling
    ax.set_xlabel("Win Probability (%)", color="#94a3b8",
                  fontsize=11, labelpad=10)
    ax.tick_params(colors="white", labelsize=10)
    ax.xaxis.label.set_color("#94a3b8")
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.xaxis.set_tick_params(color="#334155")
    ax.yaxis.set_tick_params(left=False)

    # Grid lines
    ax.xaxis.grid(True, color="#334155", linestyle="--",
                  linewidth=0.7, alpha=0.7)
    ax.set_axisbelow(True)

    # Confederation legend
    legend_patches = [
        mpatches.Patch(color=color, label=conf)
        for conf, color in CONF_COLORS.items()
        if conf != "OTHER"
    ]
    legend = ax.legend(
        handles=legend_patches,
        loc="lower right",
        title="Confederation",
        title_fontsize=9,
        fontsize=8,
        framealpha=0.2,
        facecolor="#1e293b",
        edgecolor="#334155",
        labelcolor="white"
    )
    legend.get_title().set_color("#94a3b8")

    # Watermark
    fig.text(
        0.5, 0.01,
        "Built with Python • Data: Kaggle • Model: Elo + FIFA Rankings + Form",
        ha="center", color="#475569", fontsize=8
    )

    plt.tight_layout(rect=[0, 0.03, 1, 0.92])
    plt.savefig(
        "results/wc2026_predictions.png",
        dpi=180, bbox_inches="tight",
        facecolor="#0f172a"
    )
    print("✅ Chart saved to results/wc2026_predictions.png")
    plt.show()
    print("🎨 Done!")

if __name__ == "__main__":
    create_chart()