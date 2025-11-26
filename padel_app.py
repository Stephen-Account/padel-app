import streamlit as st
import pandas as pd

# -------- BASIC CONFIG --------
st.set_page_config(page_title="Padel Round Robin", layout="wide")

st.title("Padel Round Robin Night")
st.write("8 teams · 4 courts · 7 rounds · total points wins")

# Small CSS tweaks for spacing + separators
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 0.5rem;
        padding-bottom: 0.5rem;
        padding-left: 0.75rem;
        padding-right: 0.75rem;
    }
    h1 {
        margin-bottom: 0.4rem;
    }
    h2, h3 {
        margin-top: 0.6rem;
        margin-bottom: 0.3rem;
    }
    .court-row {
        padding-top: 0.4rem;
        padding-bottom: 0.4rem;
    }
    .court-separator {
        border-top: 4px solid #ffffff;
        margin: 0.9rem 0 0.9rem 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------- FIXED SCHEDULE --------
# (round, court, teamA, teamB)
matches = [
    (1, 1, 1, 8), (1, 2, 2, 7), (1, 3, 3, 6), (1, 4, 4, 5),
    (2, 1, 2, 5), (2, 2, 3, 4), (2, 3, 1, 7), (2, 4, 8, 6),
    (3, 1, 7, 5), (3, 2, 1, 6), (3, 3, 8, 4), (3, 4, 2, 3),
    (4, 1, 6, 4), (4, 2, 1, 5), (4, 3, 8, 2), (4, 4, 7, 3),
    (5, 1, 6, 2), (5, 2, 7, 8), (5, 3, 5, 3), (5, 4, 1, 4),
    (6, 1, 1, 3), (6, 2, 4, 2), (6, 3, 6, 7), (6, 4, 5, 8),
    (7, 1, 3, 8), (7, 2, 5, 6), (7, 3, 1, 2), (7, 4, 4, 7),
]

# -------- INITIALISE SESSION STATE FOR SCORES --------
for idx, _ in enumerate(matches):
    a_key = f"m{idx}_a"
    b_key = f"m{idx}_b"
    if a_key not in st.session_state:
        st.session_state[a_key] = 0
    if b_key not in st.session_state:
        st.session_state[b_key] = 0

# -------- SIDEBAR: TEAMS + RESET --------
st.sidebar.header("Teams")

team_names = {}
for i in range(1, 9):
    team_names[i] = st.sidebar.text_input(
        f"Team {i} name",
        value=st.session_state.get(f"team_{i}_name", f"Team {i}"),
        key=f"team_{i}_name",
    )

if st.sidebar.button("Reset scores (new night)"):
    for idx, _ in enumerate(matches):
        st.session_state[f"m{idx}_a"] = 0
        st.session_state[f"m{idx}_b"] = 0
    st.experimental_rerun()

# -------- TABS: SUMMARY + ROUNDS --------
tab_labels = ["Summary"] + [f"Round {r}" for r in range(1, 8)]
tabs = st.tabs(tab_labels)

# -------- HELPER: CALCULATE TOTALS --------
def calculate_totals():
    totals = {i: 0 for i in range(1, 9)}
    wins = {i: 0 for i in range(1, 9)}
    draws = {i: 0 for i in range(1, 9)}
    losses = {i: 0 for i in range(1, 9)}

    for idx, (_, _, ta, tb) in enumerate(matches):
        a = st.session_state.get(f"m{idx}_a", 0)
        b = st.session_state.get(f"m{idx}_b", 0)

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
        rows.append(
            {
                "Team #": i,
                "Team": team_names[i],
                "Total points": totals[i],
                "Wins": wins[i],
                "Draws": draws[i],
                "Losses": losses[i],
            }
        )

    df = (
        pd.DataFrame(rows)
        .sort_values(by=["Total points", "Wins"], ascending=False)
        .reset_index(drop=True)
    )
    return df

# -------- RENDER ONE COURT (ONE ROW, TWO COLUMNS) --------
def render_court(idx: int, court: int, ta: int, tb: int):
    a_key = f"m{idx}_a"
    b_key = f"m{idx}_b"

    st.markdown("<div class='court-row'>", unsafe_allow_html=True)

    col_info, col_scores = st.columns([2, 1])

    with col_info:
        st.markdown(f"**Court {court}**")
        st.markdown(f"{team_names[ta]}  \nvs  \n{team_names[tb]}")

    with col_scores:
        st.caption(f"{team_names[ta]} pts")
        st.number_input(
            "",
            min_value=0,
            step=1,
            key=a_key,
        )
        st.caption(f"{team_names[tb]} pts")
        st.number_input(
            " ",
            min_value=0,
            step=1,
            key=b_key,
        )

    st.markdown("</div>", unsafe_allow_html=True)

# -------- TAB 0: SUMMARY --------
with tabs[0]:
    st.header("Summary")
    st.write("Totals across all rounds.")
    df_totals = calculate_totals()
    st.dataframe(df_totals, use_container_width=True)

# -------- TABS 1–7: ROUNDS (ONE COURT PER ROW) --------
for round_idx in range(1, 8):
    with tabs[round_idx]:
        st.header(f"Round {round_idx}")

        # All matches for this round, ordered by court
        round_matches = [
            (idx, r, court, ta, tb)
            for idx, (r, court, ta, tb) in enumerate(matches)
            if r == round_idx
        ]
        round_matches = sorted(round_matches, key=lambda x: x[2])

        for i, (idx, _, court, ta, tb) in enumerate(round_matches):
            render_court(idx, court, ta, tb)
            # separator between courts (not after last one)
            if i < len(round_matches) - 1:
                st.markdown("<div class='court-separator'></div>", unsafe_allow_html=True)
