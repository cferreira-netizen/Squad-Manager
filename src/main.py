import os
import json
import pandas as pd
import streamlit as st
from datetime import date

# path helpers

APP_PATH = os.path.dirname(os.path.abspath(__file__))

def get_data_path(filename: str) -> str:
    """returns the absolute path to a file inside the data/ """

    return os.path.join(APP_PATH, "data", filename)

# DATA Persistence

SQUAD_FILE = get_data_path("squad.json")
MATCHES_FILE = get_data_path("matches.json")

def load_json(filename: str, default):
    """Load JSON from disk returning default if file dosen't exist."""
    
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default

def save_json(filename: str, data):
    """Save JSON to disk."""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
        json.dump(data, f, indent=2, default=str)

# Session State

def init_state():
    """Initialize session state variables."""
    if "squad" not in st.session_state:
        st.session_state.squad = load_json(SQUAD_FILE, [])
    if "matches" not in st.session_state:
        st.session_state.matches = load_json(MATCHES_FILE, [])

# Helper utilities 

POSITIONS = ["GK", "CB","LB", "RB", "CDM","CM", "CAM", "LW", "RW", "ST"]

FITNESS_LEVELS = ["🟢 Fit", "🟡 Slight knock", "🔴 Injured", "⚪ Unknown"]

def get_squad_df():
    """Convert squad list to a DataFrame."""
    if st.session_state.squad:
        return pd.DataFrame(st.session_state.squad)
    return pd.DataFrame(columns=["name", "position", "fitness", "availability", "notes", "form"])

def calculate_form(player_name: str):
    """Calculate player form based on recent matches."""
    score = 5.0 # Base score
    revelant = [m for m in st.session_state.matches if player_name in m.get("squad",[])][-5:]
    if not revelant:
        return score
    total = 0.0
    for match in revelant:
        pts = 0
        for match in revelant:
            pts = 0
            if match.get("result") == "W":
                pts += 3
            elif match.get("result") == "D":
                pts += 1
            goals = match.get("scorers",{}).get(player_name, 0)
            assists = match.get("assisters",{}).get(player_name, 0)
            pts += goals * 1.5 + assists * 0.75
            total += pts
        
    # Normalize to 0-10
    max_possible = len(revelant) * (3 + 3 * 1.5 + 3 * 0.75)
    score = min(10.0, round((total / max(max_possible, 1 )) * 10, 1))
    return score

# Page: Squad Management

def page_squad():
    st.header ("👥 Squad")

    # Add Player
    with st.expander("➕ Add new player", expanded=False):
        with st.form("add_player_form", clear_on_submit=True):
            col1, col2 = st.columns(2)
            name = col1.text_input("player name")
            postion = col2.selectbox("poistion", POSITIONS)
            fitness = col1.selectbox("Fitness", FITNESS_LEVELS)
            availability = col2.checkbox("Available for selection", value=True)
            notes = st.text_area("Notes (optional)", height=60)
            submitted = st.form_submit_button("Add Player")
            if submitted:
                if not name.strip():
                    st.warning("Please enter a player name.")
                elif any(p["name"].lower() == name.strip().lower() for p in st.session_state.squad):
                    st.warning("Player with this name already exists.")
                else:
                    st.session_state.squad.append({
                        "name": name.strip(),
                        "position": postion,
                        "fitness": fitness,
                        "availability": availability,
                        "notes": notes.strip(),
                        "form": 5.0
                    })
                    save_json(SQUAD_FILE, st.session_state.squad)
                    st.success(f"ADDED {name.strip()}!")
                    st.rerun()
        df = get_squad_df()
        if df.empty:
            st.info("No players yet - add some above")
            return
        

        # Display

        st.subheader(f"Roster ({len(df)} players)")
        for i, player in enumerate(st.session_state.squad):
            with st.expander(f"{player['name']}  .   {player['position']}   .   {player['fitness']}"):
                col1, col2, col3 = st.columns([2, 2, 1])
                new_pos = col1.selectbox("position", POSITIONS, index=POSITIONS.index(player["position"]), key=f"pos_{i}")
                new_fit = col2.selectbox("Fitness", FITNESS_LEVELS, index=FITNESS_LEVELS.index(player["fitness"]), key=f"fit_{i}")
                new_avail = col3.checkbox("Available", value=player["availability"], key=f"av_{i}")
                new_notes = st.text_area("Notes", value=player["notes"], height=60, key=f"notes_{i}")
                form_score = calculate_form(player["name"])
                st.caption(f"Form score: **{form_score}/10**")
                st.progress(form_score / 10)

                c1, c2 = st.columns(2)
                if c1.button("💾 Save", key=f"save_{i}"):
                    st.session_state.squad[i].update({
                        "position": new_pos,
                        "fitness": new_fit,
                        "availability": new_avail,
                        "notes": new_notes,
                        "form": form_score,
                    })
                    save_json(SQUAD_FILE, st.session_state.squad)
                    st.success("Saved!")
                    st.rerun()
                if c2.button("🗑️ Remove", key=f"del_{i}"):
                    st.session_state.squad.pop(i)
                    save_json(SQUAD_FILE, st.session_state.squad)
                    st.rerun()

# Page: Pick Lineup
def page_lineup():
    st.header("📋 Pick Lineup")

    available = [p for p in st.session_state.squad if p.get("availability")]
    if len(available) <11:
        st.warning(f"You only have {len(available)} available players — need at least 11.")
        return
    
    st.markdown("Select your starting 11 from available players:")

    # Lineup recommender

    with st.expander("🤖 Who should start? (recommender)", expanded=False):
        st.caption("Players ranked by form score, position, and fitness.")
        scored = []
        for p in available:
            form = calculate_form(p["name"])
            fit_bonus = {"🟢 Fit": 2.0, "🟡 Slight knock": 0.5, "🔴 Injured": -5.0, "⚪ Unknown": 0.0}
            total = form + fit_bonus.get(p["fitness"], 0)
            scored.append({**p, "score": round(total,2)})
            scored.sort(key=lambda x: x["score"], reverse=True)
            rec_df=pd.DataFrame(scored)[["name", "position", "fitness", "score"]]
            rec_df.columns = ["Player", "Position", "Fitness", "Recommendation Score"]
            st.dataframe(rec_df, use_container_width=True, hide_index=True)

    # Manual Selection
    names = [p["name"] for p in available]
    selected = st.multiselect("Starting XI", names, max_selections=11, default=names[:min(11,len(names))])
    subs = st.multiselect("Substitutes", [n for n in names if n not in selected])

    if st.button("✅ Confirm lineup") and len(selected) == 11:
        st.session_state["current_lineup"] = selected
        st.session_state["current_subs"] = subs
        st.success("Lineup saved for this session!")
    
    if "current_lineup" in st.session_state:
        st.subheader("Current Lineup")
        lineup_df = pd.DataFrame([ p for p in st.session_state.squad if p["name"] in st.session_state["current_lineup"]])[["name", "position", "fitness"]]
        lineup_df.columns = ["Player", "Position", "Fitness"]
        st.dataframe(lineup_df, use_container_width=True, hide_index=True)

# Page: Log Match

def page_log_match():
    st.header("⚽ Log Match Result")
    if not st.session_state.squad:
        st.info("Add players first.")
        return
    
    with st.form("match_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        opponet = col1.text_input("Opponet")
        match_date = col2.date_input("Date", value=date.today())
        col3, col4 = st.columns(2)
        goals_for = col3.number_input("Goals for", min_value=0, max_value=20, step=1)
        goals_against = col4.number_input("Goals against", min_value=0, max_value=20, step=1)

        all_names = [p["name"] for p in st.session_state.squad]
        squad_played = st.multiselect("Player who played", all_names, default=st.session_state.get("current_lineup", []))
        scorers = st.multiselect("Goal scorer(s)", squad_played)
        assisters = st.multiselect("Assist(s)", squad_played)

        notes = st.text_area("Match notes", height=60)
        submitted = st.form_submit_button("log result")

    if submitted:
        if not opponent.strip():
            st.warning("Enter the opponets name.")
        else:
            if goals_for > goals_against:
                result = "W"
            elif goals_for == goals_against:
                result = "D"
            else:
                result = "L" 
            
            match = {
                "date": str(match_date),
                "opponent": opponent.strip(),
                "goals_for": int(goals_for),
                "goals_aganist": int(goals_aganist),
                "result": result,
                "squad": squad_played,
                "scorers": {p: scorers.count(p) for p in set(scorers)},
                "assisters": {p: assisters.count(p) for p in set(assisters)},
                "notes": notes.strip(),
            }
            st.session_state.matches.append(match)
            save_json(MATCHES_FILE, st.session_state.matches)

            badge = {"W": "🟢 Win", "D": "🟡 Draw", "L": "🔴 Loss"}[result]
            st.success(f"Logged: {badge} vs {opponent.strip()} ({goals_for}-{goals_against})")
            st.rerun()

# Season Stats

def page_stats():
    st.header("📊 Season Stats")

    matches = st.session_state.matches
    if not matches:
        st.info("No matches logged yet.")
        return

    df = pd.DataFrame(matches)


    # Season Summary

    wins = (df["result"] == "W").sum()
    draws = (df["result"] == "D").sum()
    Losses = (df["result"] == "L").sum()
    gf = df["goals_for"].sum()
    ga = df["goals_against"].sum()
    pts = wins * 3 + draws


    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Played", len(df))
    c2.metric("points", pts)
    c3.metric("W/D/L", f"{wins}/{draws}/{losses}")
    c4.metric("Goals for", gf)
    c5.metric("Goals against", ga)

    # Match Log
    st.subheader("Match Log")
    display = df[["date", "opponent", "goals_for", "goals_against", "result", "notes"]].copy()
    display.columns = ["Date", "Opponent", "GF", "GA", "Result", "Notes"]
    display["Result"] = display["Result"].map({"W": "🟢 W", "D": "🟡 D", "L": "🔴 L"})
    st.dataframe(display.sort_values("Date", ascending=False), use_container_width=True, hide_index=True)

    # Player stats
    st.subheader("Player stats")
    player_stats = {}
    for _, row in df.iterrows():
        for player in row.get("squad", []):
            if player not in player_stats:
                player_stats[player] = {"apps": 0, "goals": 0, "assists": 0, "wins": 0}
            player_stats[player]["apps"] += 1
        player_stats[player]["goals"]   += row.get("scorers", {}).get(player, 0)
        player_stats[player]["assists"]  += row.get("assisters", {}).get(player, 0)
        if row["result"] == "W":
            player_stats[player]["wins"] += 1
    
    if player_stats:
        stats_df = pd.DataFrame(player_status).T.reset_index()
        stats_df.columns = ["player", "Apps", "Goals", "Assists", "Wins"]
        stats_df = stats_df.sort_values("Goals", ascending=False)
        st.dataframe(stats_df, use_container_width=True, hide_index=True)
    
    # Delete Match
    with st.expander("🗑️ Delete a match"):
        labels = [f"{m['date']} vs {m['opponent']}" for m in matches]
        to_del = st.selectbox("Select match to delete", labels)
        if st.button("Delete match"):
            idx = labels.index(to_del)
            st.session_state.matches.pop(idx)
            save_json(MATCHES_FILE, st.session_state.matches)
            st.rerun()

def main():
    st.set_page_config(page_title="Squad Manager", page_icon="⚽", layout="wide")
    init_state()

    st.title("⚽ Squad Manager")
    st.caption("Track your squad, pick lineups, log results, and see season stats.")


    tab1, tab2, tab3, tab4 = st.tabs(["Squad", "Pick Lineup", "Log Match", "Season Stats"])
    with tab1: page_squad()
    with tab2: page_lineup()
    with tab3: page_log_match()
    with tab4: page_stats()

if __name__ == "__main__":
    main()



    


            
            
                            
                
        