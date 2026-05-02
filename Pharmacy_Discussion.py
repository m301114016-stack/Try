import streamlit as st
import random
import time

# Page Configuration
st.set_page_config(page_title="The Chosen One: Dice Showdown", page_icon="🎲")

# Initialize session state for players
if 'players' not in st.session_state:
    st.session_state.players = {}

st.title("🎲 The Chosen One: Dice Showdown")
st.write("Scan the QR code to join. The highest roll wins!")

# --- Sidebar: Join Section ---
with st.sidebar:
    st.header("📲 Join Game")
    name = st.text_input("Enter your nickname", placeholder="e.g., Researcher Smith")
    if st.button("Join Now"):
        if name:
            if name not in st.session_state.players:
                st.session_state.players[name] = 0
                st.success(f"Welcome, {name}!")
            else:
                st.warning("This name is already taken!")
    
    st.divider()
    if st.button("Reset All Data", type="secondary"):
        st.session_state.players = {}
        st.rerun()

# --- Main Area: Battle Zone ---
if not st.session_state.players:
    st.info("Waiting for participants... Please join via the sidebar.")
else:
    st.subheader(f"Current Candidates ({len(st.session_state.players)})")
    # Display the list of players
    player_names = ", ".join(st.session_state.players.keys())
    st.text(f"Participants: {player_names}")

    if st.button("🔥 ROLL THE DICE!", type="primary", use_container_width=True):
        st.divider()
        
        # Simulated rolling animation
        with st.status("Shaking the dice cup...", expanded=True) as status:
            time.sleep(1.5)
            # Generate random points (1-100)
            results = {name: random.randint(1, 100) for name in st.session_state.players}
            st.session_state.players.update(results)
            status.update(label="Dice revealed!", state="complete", expanded=False)

        # Determine the winner
        winner = max(results, key=results.get)
        max_point = results[winner]

        # Celebration animation
        st.balloons()
        st.header(f"👑 Winner: 【{winner}】")
        st.subheader(f"Dominating with {max_point} points!")

        # Detailed Scoreboard
        st.write("---")
        st.write("### Battle Report")
        
        # Sort results by score (descending)
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        for name, score in sorted_results:
            st.write(f"🎲 {name}: {score} pts")

