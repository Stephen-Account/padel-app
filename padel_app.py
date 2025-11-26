import streamlit as st
import pandas as pd
from pathlib import Path
import json

# -------- BASIC CONFIG --------
st.set_page_config(page_title="Padel Round Robin", layout="wide")

# Small CSS tweaks for mobile/tablet look
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    /* tighten headings a bit */
    h1 {
        margin-bottom: 0.4rem;
    }
    h2, h3 {
        margin-top: 0.6rem;
        margin-bottom: 0.3rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("Padel Round Robin Night")
st.write("8 teams · 4 courts · 7 rounds · total points wins")

# SAVE FILE IN YOUR ICLOUD FOLDER (used when you run it locally)
DATA_FILE = Path(
    r"C:\Users\sfranken\iCloudDrive\Documents\03_Personal\00_APPS\padel_data.json"
)

# -------- FIXED SCHEDULE --------
matches = [
    (1, 1, 1, 8), (1, 2, 2, 7), (1, 3, 3, 6), (1, 4, 4, 5),
    (2, 1, 2, 5), (2, 2, 3, 4), (2, 3, 1, 7), (2, 4, 8, 6),
    (3, 1, 7, 5), (3, 2, 1, 6), (3, 3, 8, 4), (3, 4, 2, 3),
    (4, 1, 6, 4), (4, 2, 1, 5), (4, 3, 8, 2), (4, 4, 7, 3),
    (5, 1, 6, 2), (5, 2, 7, 8), (5, 3, 5, 3), (5, 4, 1, 4),
    (6, 1, 1, 3), (6, 2, 4, 2), (6, 3, 6, 7), (6, 4, 5, 8),
    (7, 1, 3, 8), (7, 2, 5, 6), (7, 3, 1, 2), (7, 4, 4, 7),
]


# -------- LOAD / SAVE HELPERS (for local runs) --------
def load_saved_data():
    if not DATA_FILE.exists():
        return {}

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_data(teams, scores):
    data = {
        "teams": {str(i): teams[i] for i in range(1, 9)},
        "scores": scores,
    }
    try:
        DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        st.error(f"Could not save data: {e}")


saved = load_saved_data()
saved_teams = saved.get("teams", {})
saved_scores = saved.get("scores", {})

# -------- SIDEBAR TEAM SETUP + RESET --------
st.sidebar.header("Teams")

team_names = {}
for i in range(1, 9):
    default_name = saved_teams.get(str(i), f"Team {i}")
    team_names[i] = st.sidebar.text_input(
        f"Team {i} name",
        value=default_name,
        key=f"team_{i}_name",
    )

if st.sidebar.button("Reset scores (new night)"):
    empty_scores = {}
    for idx in range(len(matches)):
        a_key = f"m{idx}_a"
        b_key = f"m{idx}_b"
        st.session_state[a_key] = 0
        st.session_state[b_key] = 0
        empty_scores[a_key] = 0
        empty_scores[b_key] = 0

    save_data(team_names, empty_scores)
    st.rerun()

# -------- MATCHES UI (MOBILE-FIRST) --------
st.header("Matches & Scores")

current_round = None
scores_current = {}

for idx, (rnd, court, ta, tb) in enumerate(matches):
    # thick divider between rounds
    if current_round is None:
        current_round = rnd
    elif rnd != current_round:
        st.markdown(
            '<hr style="border: 3px solid #555; margin: 1rem 0;">',
            unsafe_allow_html=True,
        )
        current_round = rnd

    score_key_a = f"m{idx}_a"
    score_key_b = f"m{idx}_b"

    saved_a = saved_scores.get(score_key_a, 0)
    saved_b = saved_scores.get(score_key_b, 0)

    box = st.container()
    with box:
        st.markdown(f"**Round {rnd} – Court {court}**")
        st.markdown(f"{team_names[ta]}  \nvs  \n{team_names[tb]}")

        c1, c2 = st.columns(2)

        with c1:
            st.caption(f"{team_names[ta]} pts")
            a_score = st.number_input(
                "",
                min_value=0,
                step=1,
                value=saved_a,
                key=score_key_a,
            )

        with c2:
            st.caption(f"{team_names[tb]} pts")
            b_score = st.number_input(
                " ",
                min_value=0,
                step=1,
                value=saved_b,
                key=score_key_b,
            )

    scores_current[score_key_a] = int(a_score)
    scores_current[score_key_b] = int(b_score)

st.markdown("---")

# -------- TOTALS + W/D/L --------
totals = {i: 0 for i in range(1, 9)}
wins = {i: 0 for i in range(1, 9)}
draws = {i: 0 for i in range(1, 9)}
losses = {i: 0 for i in range(1, 9)}

for idx, (_, _, ta, tb) in enumerate(matches):
    a = scores_current.get(f"m{idx}_a", 0)
    b = scores_current.get(f"m{idx}_b", 0)

    totals[ta] += a
    totals[tb] += b

    if a == 0 and b == 0:
        continue

    if a > b:
        wins[ta] += 1
        losses[tb] += 1
    elif b > a:
        wins[tb] += 1
        losses[ta] += 1
    else:
        draws[ta] += 1
        draws[tb] += 1

rows = []
for i in range(1, 9):
    rows.append({
        "Team #": i,
        "Team": team_names[i],
        "Total points": totals[i],
        "Wins": wins[i],
        "Draws": draws[i],
        "Losses": losses[i],
    })

df_totals = (
    pd.DataFrame(rows)
    .sort_values(by=["Total points", "Wins"], ascending=False)
    .reset_index(drop=True)
)

st.header("Standings")
st.dataframe(df_totals, use_container_width=True)

# -------- AUTO-SAVE (for local runs) --------
save_data(team_names, scores_current)
