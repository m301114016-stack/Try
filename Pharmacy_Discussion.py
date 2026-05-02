import streamlit as st
import random
import time

# 1. 核心：建立一個所有連線者共用的「全局資料庫」
@st.cache_resource
def get_global_state():
    return {
        "players": {},      # {name: last_roll}
        "game_status": "WAITING", # WAITING, ROLLING, FINISHED
        "winner": None,
        "max_score": 0
    }

global_data = get_global_state()

st.set_page_config(page_title="Global Dice Battle", page_icon="🎲")

# --- 自動重新整理介面 (每 2 秒)，讓大家看到最新的玩家名單 ---
# 如果沒按按鈕，這段會讓畫面保持更新
if "last_update" not in st.session_state:
    st.session_state.last_update = time.time()

st.title("🎲 Global Dice Battle")
st.write("Real-time Multiplayer Mode")

# --- 側邊欄：加入區域 ---
with st.sidebar:
    st.header("📲 Join Game")
    my_name = st.text_input("Enter your name", key="name_input")
    
    if st.button("Join Now"):
        if my_name:
            global_data["players"][my_name] = 0
            st.success(f"Hello {my_name}, you are in!")
    
    st.divider()
    if st.button("Admin: Reset Game", type="secondary"):
        global_data["players"] = {}
        global_data["game_status"] = "WAITING"
        global_data["winner"] = None
        st.rerun()

# --- 主畫面：顯示所有已連線玩家 ---
st.subheader(f"Participants ({len(global_data['players'])})")
if global_data['players']:
    # 用標籤顯示目前在線上的所有人
    cols = st.columns(5)
    for idx, p_name in enumerate(global_data['players'].keys()):
        cols[idx % 5].info(f"👤 {p_name}")
else:
    st.info("Waiting for players to join...")

st.divider()

# --- 遊戲控制邏輯 ---
if global_data["game_status"] == "WAITING":
    if st.button("🔥 EVERYONE ROLL NOW!", type="primary", use_container_width=True):
        global_data["game_status"] = "ROLLING"
        # 幫所有人擲骰子
        results = {name: random.randint(1, 100) for name in global_data["players"]}
        global_data["players"].update(results)
        
        # 計算贏家
        winner = max(results, key=results.get)
        global_data["winner"] = winner
        global_data["max_score"] = results[winner]
        global_data["game_status"] = "FINISHED"
        st.rerun()

elif global_data["game_status"] == "FINISHED":
    st.balloons()
    st.header(f"👑 Winner: {global_data['winner']}")
    st.subheader(f"Score: {global_data['max_score']} pts")
    
    # 顯示排行榜
    st.write("### Full Scoreboard")
    sorted_scores = sorted(global_data["players"].items(), key=lambda x: x[1], reverse=True)
    for name, score in sorted_scores:
        st.write(f"🎲 {name}: {score} pts")
    
    if st.button("Next Round"):
        global_data["game_status"] = "WAITING"
        # 重置分數
        for name in global_data["players"]:
            global_data["players"][name] = 0
        st.rerun()

# 讓頁面每 3 秒自動重整一次 (簡單的同步機制)
time.sleep(3)
st.rerun()
