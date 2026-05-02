import streamlit as st
import random
import time

# 1. Global Shared State: Syncs data across all devices
@st.cache_resource
def get_global_state():
    return {
        "players": {},  # { "Name": Score }
    }

global_data = get_global_state()

# Page Configuration
st.set_page_config(page_title="Dice Battle: Main Edition", page_icon="🎲", layout="centered")

# --- Auto-sync mechanism ---
if "last_sync" not in st.session_state:
    st.session_state.last_sync = time.time()

st.title("🎲 Individual Dice Battle")
st.write("Join and roll directly below!")

# --- MAIN INTERACTION AREA ---
st.divider()

# Logic: Check if the user has joined
if "my_identity" not in st.session_state:
    # STEP 1: JOINING
    st.subheader("👋 Welcome! Join the Game")
    name_input = st.text_input("Enter your nickname to start:", placeholder="e.g., Taylor")
    
    if st.button("JOIN GAME", type="primary", use_container_width=True):
        if name_input:
            # Clean name and add to global data
            clean_name = name_input.strip()
            st.session_state.my_identity = clean_name
            if clean_name not in global_data["players"]:
                global_data["players"][clean_name] = 0
            st.rerun()
        else:
            st.error("Please enter a name first!")

else:
    # STEP 2: ROLLING or VIEWING RESULT
    my_name = st.session_state.my_identity
    current_score = global_data["players"].get(my_name, 0)
    
    st.subheader(f"Hello, **{my_name}**!")
    
    if current_score == 0:
        # User hasn't rolled yet
        st.info("Ready to test your luck?")
        if st.button("🎲 ROLL MY DICE", type="primary", use_container_width=True):
            my_roll = random.randint(1, 100)
            global_data["players"][my_name] = my_roll
            st.balloons()
            st.rerun()
    else:
        # User has finished rolling
        st.success(f"You rolled a **{current_score}**!")
        if st.button("Leave / Change Name", use_container_width=False):
            del st.session_state.my_identity
            st.rerun()

st.divider()

# --- LIVE LEADERBOARD AREA ---
st.subheader("📊 Live Leaderboard")

if not global_data["players"]:
    st.info("Waiting for participants to join...")
else:
    # Data Processing
    rolled = {k: v for k, v in global_data["players"].items() if v > 0}
    waiting = [k for k, v in global_data["players"].items() if v == 0]

    # Stats Summary
    c1, c2 = st.columns(2)
    c1.metric("Total Players", len(global_data["players"]))
    c2.metric("Finished Rolls", len(rolled))

    # Leaderboard Display
    if rolled:
        sorted_scores = sorted(rolled.items(), key=lambda x: x[1], reverse=True)
        
        # Crown the leader
        leader, high_score = sorted_scores[0]
        st.markdown(f"### 🏆 Leader: **{leader}** ({high_score} pts)")
        
        for idx, (name, score) in enumerate(sorted_scores):
            # Highlight the current user in the list
            label = f"**#{idx+1} {name}**" + (" (You)" if name == st.session_state.get("my_identity") else "")
            st.write(label)
            st.progress(score / 100)
            st.caption(f"Score: {score} pts")

    # Waiting List
    if waiting:
        st.write("---")
        st.write("⏳ **Waiting for:** " + ", ".join(waiting))

# --- ADMIN SECTION (Hidden at bottom) ---
with st.expander("🛠️ Admin Tools"):
    if st.button("Reset Entire Game"):
        global_data["players"] = {}
        st.rerun()

# Auto-refresh every 3 seconds
time.sleep(3)
st.rerun()
