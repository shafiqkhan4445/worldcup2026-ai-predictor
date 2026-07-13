# ============================================================
# dashboard.py - Interactive WC 2026 Streamlit Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import subprocess
import sys
import os

# Page config
st.set_page_config(
    page_title="FIFA World Cup 2026 AI Predictor",
    page_icon="🏆",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main { background-color: #0f172a; }
    .stApp { background-color: #0f172a; }
    h1, h2, h3 { color: white; }
    .metric-card {
        background: #1e293b;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        border: 1px solid #334155;
    }
    .medal { font-size: 40px; }
</style>
""", unsafe_allow_html=True)

# Confederation mapping
def get_confederation(team):
    UEFA = ["Spain", "France", "England", "Portugal", "Germany",
            "Netherlands", "Belgium", "Croatia", "Switzerland",
            "Austria", "Norway", "Scotland", "Turkey", "Serbia",
            "Sweden", "Czech Republic", "Bosnia and Herzegovina"]
    CONMEBOL = ["Argentina", "Brazil", "Colombia", "Ecuador",
                "Uruguay", "Paraguay"]
    CONCACAF = ["United States", "Mexico", "Canada", "Panama",
                "Curacao", "Haiti"]
    AFC = ["Japan", "South Korea", "Australia", "Iran",
           "Saudi Arabia", "Qatar", "Iraq", "Uzbekistan", "Jordan"]
    CAF = ["Morocco", "Senegal", "Ivory Coast", "Algeria", "Tunisia",
           "Egypt", "South Africa", "Ghana", "Cameroon", "DR Congo",
           "Cape Verde", "Nigeria"]
    if team in UEFA: return "UEFA"
    if team in CONMEBOL: return "CONMEBOL"
    if team in CONCACAF: return "CONCACAF"
    if team in AFC: return "AFC"
    if team in CAF: return "CAF"
    return "OTHER"

CONF_COLORS = {
    "UEFA": "#3b82f6",
    "CONMEBOL": "#10b981",
    "CONCACAF": "#f59e0b",
    "AFC": "#ef4444",
    "CAF": "#8b5cf6",
    "OTHER": "#6b7280",
}

# ---- HEADER ----
st.markdown("""
<h1 style='text-align:center; color:white; font-size:42px;'>
    🏆 FIFA World Cup 2026
</h1>
<p style='text-align:center; color:#94a3b8; font-size:18px;'>
    AI Tournament Predictor — Monte Carlo Simulation
</p>
<p style='text-align:center; color:#475569; font-size:13px;'>
    Built by Shafiq | Python • Elo Ratings • FIFA Rankings • 51,653 matches
</p>
""", unsafe_allow_html=True)

st.markdown("---")

# ---- LOAD DATA ----
@st.cache_data
def load_data():
    df = pd.read_csv("results/wc2026_predictions.csv")
    df["Confederation"] = df["Team"].apply(get_confederation)
    df["Color"] = df["Confederation"].map(CONF_COLORS)
    df = df.sort_values("Win_Probability_%", ascending=False).reset_index(drop=True)
    df["Rank"] = df.index + 1
    return df

df = load_data()

# ---- RUN NEW SIMULATION BUTTON ----
col1, col2, col3 = st.columns([2, 1, 2])
with col2:
    if st.button("🔄 Run New Simulation", use_container_width=True):
        with st.spinner("Running 10,000 simulations..."):
            subprocess.run(
                [sys.executable, "src/simulate.py"],
                cwd=os.getcwd()
            )
            st.cache_data.clear()
            st.success("✅ Done! Refreshing...")
            st.rerun()

st.markdown("---")

# ---- TOP 3 MEDALS ----
st.markdown("### 🏅 Top Predictions")
m1, m2, m3 = st.columns(3)

top3 = df.head(3)
medals = ["🥇", "🥈", "🥉"]
bg_colors = ["#854d0e", "#475569", "#7c2d12"]

for i, (col, medal) in enumerate(zip([m1, m2, m3], medals)):
    row = top3.iloc[i]
    with col:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='medal'>{medal}</div>
            <h3 style='color:white; margin:8px 0'>{row['Team']}</h3>
            <h2 style='color:#10b981; margin:4px 0'>{row['Win_Probability_%']}%</h2>
            <p style='color:#94a3b8; margin:0'>{row['Confederation']}</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ---- SIDEBAR FILTERS ----
st.sidebar.markdown("## 🔍 Filters")
confederations = ["All"] + sorted(df["Confederation"].unique().tolist())
selected_conf = st.sidebar.selectbox("Filter by Confederation", confederations)

min_prob = st.sidebar.slider(
    "Minimum Win Probability (%)",
    min_value=0.0,
    max_value=float(df["Win_Probability_%"].max()),
    value=0.0,
    step=0.1
)

# Apply filters
filtered_df = df.copy()
if selected_conf != "All":
    filtered_df = filtered_df[filtered_df["Confederation"] == selected_conf]
filtered_df = filtered_df[filtered_df["Win_Probability_%"] >= min_prob]

# ---- MAIN CHART ----
st.markdown("### 📊 Win Probabilities — All Teams")

fig = px.bar(
    filtered_df.sort_values("Win_Probability_%"),
    x="Win_Probability_%",
    y="Team",
    orientation="h",
    color="Confederation",
    color_discrete_map=CONF_COLORS,
    hover_data={"Win_Probability_%": ":.1f", "Confederation": True},
    labels={"Win_Probability_%": "Win Probability (%)"},
    height=600
)

fig.update_layout(
    paper_bgcolor="#0f172a",
    plot_bgcolor="#1e293b",
    font_color="white",
    xaxis=dict(gridcolor="#334155"),
    yaxis=dict(gridcolor="#334155"),
    legend=dict(
        bgcolor="#1e293b",
        bordercolor="#334155"
    ),
    margin=dict(l=10, r=10, t=10, b=10)
)

fig.update_traces(
    hovertemplate="<b>%{y}</b><br>Win Probability: %{x:.1f}%<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

# ---- STATS ROW ----
st.markdown("---")
st.markdown("### 📈 Quick Stats")

s1, s2, s3, s4 = st.columns(4)
with s1:
    st.metric("🏆 Favourite", df.iloc[0]["Team"],
              f"{df.iloc[0]['Win_Probability_%']}%")
with s2:
    uefa_prob = df[df["Confederation"]=="UEFA"]["Win_Probability_%"].sum()
    st.metric("🌍 UEFA Combined", f"{uefa_prob:.1f}%")
with s3:
    conmebol_prob = df[df["Confederation"]=="CONMEBOL"]["Win_Probability_%"].sum()
    st.metric("🌎 CONMEBOL Combined", f"{conmebol_prob:.1f}%")
with s4:
    st.metric("🎲 Total Teams", len(df))

# ---- FULL TABLE ----
st.markdown("---")
st.markdown("### 📋 Full Rankings Table")

display_df = filtered_df[["Rank", "Team", "Win_Probability_%",
                           "Confederation"]].copy()
display_df.columns = ["Rank", "Team", "Win Probability (%)", "Confederation"]

st.dataframe(
    display_df,
    use_container_width=True,
    hide_index=True,
    height=400
)

# ---- FOOTER ----
st.markdown("---")
st.markdown("""
<p style='text-align:center; color:#475569; font-size:12px;'>
    Built by Shafiq | Data: Kaggle (51,653 matches) | 
    Model: Elo Ratings + FIFA Rankings + Recent Form | 
    Monte Carlo Simulation — 10,000 runs
</p>
""", unsafe_allow_html=True)