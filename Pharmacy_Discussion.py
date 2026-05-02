
import streamlit as st
import random
import time

# 1. Global Shared State: Syncs data across all devices
@st.cache_resource
def get_global_state():
    return {
        "players": {},      # { "Name": Score }
        "buzzer_winner": None,  # Tracks who pressed the steal button first
        "buzzer_locked": False, # Prevents others from stealing after the first click
        "last_action": ""   # To display latest event
    }

global_data = get_global_state()

# Page Configuration
st.set_page_config(page_title="Dice & Steal Battle", page_icon="⚡", layout="centered")

# --- Auto-sync mechanism ---
if "last_sync" not in st.session_state:
    st.session_state.last_sync = time.time()

st.title("⚡ Dice & Steal Battle")
st.write("Roll your dice or be the fastest to STEAL!")

# --- MAIN INTERACTION AREA ---
st.divider()

# Check if the user has joined
if "my_identity" not in st.session_state:
    st.subheader("👋 Welcome! Join the Game")
    name_input = st.text_input("Enter your nickname:", placeholder="e.g., Taylor")
    
    if st.button("JOIN GAME", type="primary", use_container_width=True):
        if name_input:
            clean_name = name_input.strip()
            st.session_state.my_identity = clean_name
            if clean_name not in global_data["players"]:
                global_data["players"][clean_name] = 0
            st.rerun()
else:
    my_name = st.session_state.my_identity
    st.subheader(f"Hello, **{my_name}**!")

    # --- THE STEAL / BUZZER BUTTON ---
    # Show the Steal button if no one has won the buzzer yet
    if not global_data["buzzer_locked"]:
        if st.button("⚡ STEAL / BUZZ!", type="primary", use_container_width=True):
            global_data["buzzer_locked"] = True
            global_data["buzzer_winner"] = my_name
            global_data["last_action"] = f"🚀 {my_name} pressed the buzzer first!"
            st.balloons()
            st.rerun()
    else:
        if global_data["buzzer_winner"] == my_name:
            st.success("🎯 YOU STOLE IT! You were the fastest!")
        else:
            st.warning(f"Too slow! **{global_data['buzzer_winner']}** caught the buzzer.")

    st.divider()

    # --- THE DICE ROLL BUTTON ---
    current_score = global_data["players"].get(my_name, 0)
    if current_score == 0:
        if st.button("🎲 ROLL MY DICE", use_container_width=True):
            my_roll = random.randint(1, 100)
            global_data["players"][my_name] = my_roll
            st.rerun()
    else:
        st.info(f"Your Dice Result: **{current_score}** pts")

# --- LIVE STATUS & LEADERBOARD ---
st.subheader("📊 Live Status")

# Display the Buzzer Winner prominently
if global_data["buzzer_winner"]:
    st.error(f"🚨 BUZZER TAKEN BY: {global_data['buzzer_winner']}")

if not global_data["players"]:
    st.info("Waiting for participants...")
else:
    # Leaderboard Logic
    rolled = {k: v for k, v in global_data["players"].items() if v > 0}
    
    col1, col2 = st.columns(2)
    col1.metric("Total Players", len(global_data["players"]))
    col2.metric("Dice Rolled", len(rolled))

    if rolled:
        sorted_scores = sorted(rolled.items(), key=lambda x: x[1], reverse=True)
        st.markdown(f"### 🏆 Current Leader: **{sorted_scores[0][0]}**")
        
        for idx, (name, score) in enumerate(sorted_scores):
            is_me = " (You)" if name == st.session_state.get("my_identity") else ""
            st.write(f"**#{idx+1} {name}{is_me}**: {score} pts")
            st.progress(score / 100)

# --- ADMIN SECTION ---
with st.expander("🛠️ Admin Tools"):
    if st.button("Reset Buzzer Only"):
        global_data["buzzer_locked"] = False
        global_data["buzzer_winner"] = None
        st.rerun()
        
    if st.button("Reset Entire Game"):
        global_data["players"] = {}
        global_data["buzzer_locked"] = False
        global_data["buzzer_winner"] = None
        st.rerun()

# Rapid refresh to detect the first person to "Steal"
time.sleep(1)
st.rerun()
