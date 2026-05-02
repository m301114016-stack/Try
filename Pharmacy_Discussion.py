import streamlit as st
import random
import time

# 1. Global Shared State: This allows all connected users to see the same data
@st.cache_resource
def get_global_state():
    return {
        "players": {},  # Format: { "Name": Score }, Score 0 means not rolled yet
    }

global_data = get_global_state()

# Page Setup
st.set_page_config(page_title="Individual Dice Battle", page_icon="🎲")

# --- Auto-refresh mechanism (every 3 seconds) to sync all screens ---
if "last_sync" not in st.session_state:
    st.session_state.last_sync = time.time()

st.title("🎲 Individual Dice Battle")
st.write("Join the game and roll your own dice. The leaderboard updates in real-time!")

# --- Sidebar: Player Control Panel ---
with st.sidebar:
    st.header("🎮 Player Control")
    
    # Login Logic
    if "my_identity" not in st.session_state:
        name_input = st.text_input("Enter your name to join:", placeholder="e.g., Alex")
        if st.button("Join Game", use_container_width=True):
            if name_input:
                st.session_state.my_identity = name_input
                # Initialize score to 0 in the global database if new
                if name_input not in global_data["players"]:
                    global_data["players"][name_input] = 0 
                st.rerun()
    else:
        # Interface for logged-in players
        my_name = st.session_state.my_identity
        st.success(f"Signed in as: **{my_name}**")
        
        # Roll Button Logic
        # Only show button if player hasn't rolled yet (score is 0)
        current_score = global_data["players"].get(my_name, 0)
        
        if current_score == 0:
            if st.button("🎲 ROLL MY DICE", type="primary", use_container_width=True):
                my_roll = random.randint(1, 100)
                global_data["players"][my_name] = my_roll
                st.balloons()
                st.rerun()
        else:
            st.info(f"Your Result: **{current_score}** pts")
            if st.button("Change Name / Re-join", use_container_width=True):
                del st.session_state.my_identity
                st.rerun()

    st.divider()
    # Admin Controls
    st.subheader("Admin Tools")
    if st.button("Reset Leaderboard", type="secondary", help="Clears all player data"):
        global_data["players"] = {}
        st.rerun()

# --- Main Area: Live Leaderboard ---
st.subheader("📊 Live Leaderboard")

if not global_data["players"]:
    st.info("Waiting for participants to join and roll...")
else:
    # Separate players into those who finished and those still waiting
    rolled = {k: v for k, v in global_data["players"].items() if v > 0}
    waiting = [k for k, v in global_data["players"].items() if v == 0]

    # Quick Stats
    col1, col2 = st.columns(2)
    col1.metric("Total Participants", len(global_data["players"]))
    col2.metric("Dice Rolled", len(rolled))

    st.divider()

    # Display Ranked Leaderboard
    if rolled:
        # Sort by score descending
        sorted_scores = sorted(rolled.items(), key=lambda x: x[1], reverse=True)
        
        # Highlight the current leader
        leader_name, leader_score = sorted_scores[0]
        st.markdown(f"### 🏆 Current Leader: **{leader_name}** ({leader_score} pts)")

        # Visual Scoreboard
        for idx, (name, score) in enumerate(sorted_scores):
            st.write(f"**#{idx+1} {name}**")
            st.progress(score / 100) # Visual progress bar (0.0 to 1.0)
            st.caption(f"Score: {score} pts")
    
    # Display names of players who haven't rolled yet
    if waiting:
        st.write("---")
        st.write("⏳ **Waiting for these players to roll:**")
        st.write(", ".join(waiting))

# Force update every 3 seconds so the big screen stays in sync with mobile inputs
time.sleep(3)
st.rerun()
