import streamlit as st
import random
import time
import pandas as pd

# --- 1. 遊戲初始化設定 ---
st.set_page_config(page_title="機率冒險島", layout="wide")

if 'game_state' not in st.session_state:
    st.session_state.game_state = "LOBBY"  # LOBBY, ROLLING, QUESTION, RESULT
if 'current_step' not in st.session_state:
    st.session_state.current_step = 1
if 'players' not in st.session_state:
    st.session_state.players = {}  # {name: {"score": 0, "last_roll": 0}}
if 'questions' not in st.session_state:
    st.session_state.questions = [
        {"q": "臨床藥學中，下列何者屬於第一線藥物？", "a": "選項 A", "options": ["選項 A", "選項 B", "選項 C", "選項 D"]},
        {"q": "即興劇的核心精神是什麼？", "a": "Yes, and", "options": ["No, but", "Yes, and", "Wait, why", "Never mind"]},
        {"q": "AI 在醫療領域最常見的應用是什麼？", "a": "輔助診斷", "options": ["取代醫師", "輔助診斷", "純聊天", "寫詩"]},
        # ... 可擴充至 10 題
    ] * 4 
if 'winner' not in st.session_state:
    st.session_state.winner = None

# --- 2. 輔助函式 ---
def reset_game():
    st.session_state.current_step = 1
    st.session_state.game_state = "LOBBY"
    st.session_state.players = {}

# --- 3. 側邊欄：玩家加入 (模擬 QR Code 加入) ---
with st.sidebar:
    st.title("🎮 遊戲大廳")
    new_player = st.text_input("輸入暱稱加入遊戲")
    if st.button("加入"):
        if new_player and new_player not in st.session_state.players:
            st.session_state.players[new_player] = {"score": 0, "last_roll": 0}
            st.success(f"{new_player} 已進入房間")
    
    st.write("---")
    st.write("### 目前玩家清單")
    for p in st.session_state.players:
        st.write(f"👤 {p}: {st.session_state.players[p]['score']} 分")
    
    if st.button("重置遊戲", type="primary"):
        reset_game()

# --- 4. 主畫面控制 ---
st.title("🎲 十全十美：機率冒險島")

# 顯示地圖進度
steps = ["🚩"] + ["○"] * 9 + ["🏁"]
steps[st.session_state.current_step - 1] = "🚀"
st.subheader(f"目前進度：第 {st.session_state.current_step} / 10 關")
st.title(" —— ".join(steps))

# --- 5. 遊戲流程邏輯 ---

# A. 大廳階段：等待開始
if st.session_state.game_state == "LOBBY":
    st.info("請所有玩家掃描 QR Code 並點擊側邊欄加入遊戲。")
    if len(st.session_state.players) >= 2:
        if st.button("全員到齊，開始遊戲！"):
            st.session_state.game_state = "ROLLING"
            st.rerun()
    else:
        st.warning("至少需要 2 位玩家才能開始。")

# B. 擲骰子階段
elif st.session_state.game_state == "ROLLING":
    st.header("🎲 命運擲骰中...")
    if st.button("點擊擲骰！"):
        with st.spinner('骰子旋轉中...'):
            time.sleep(1)
            highest_score = -1
            winner_name = ""
            for p in st.session_state.players:
                roll = random.randint(1, 100)
                st.session_state.players[p]['last_roll'] = roll
                if roll > highest_score:
                    highest_score = roll
                    winner_name = p
            st.session_state.winner = winner_name
            st.session_state.game_state = "QUESTION"
            st.rerun()

# C. 答題階段
elif st.session_state.game_state == "QUESTION":
    st.warning(f"👑 點數最高者：【{st.session_state.winner}】，請回答問題！")
    
    q_data = st.session_state.questions[st.session_state.current_step - 1]
    st.subheader(f"Q{st.session_state.current_step}: {q_data['q']}")
    
    # 功能按鈕排版
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        ans = st.radio("選擇答案：", q_data['options'])
    
    with col2:
        if st.button("🆘 求救 (刪除錯誤選項)"):
            st.toast("已為您標註參考方向！")
            
    with col3:
        if st.button("⚡ 搶答按鈕"):
            st.toast("搶答成功！點數歸零，由搶答者接手！")

    if st.button("送出答案"):
        if ans == q_data['a']:
            st.success("回答正確！前進一格！")
            st.session_state.players[st.session_state.winner]['score'] += 10
            st.session_state.current_step += 1
        else:
            st.error(f"答錯了！正確答案是：{q_data['a']}")
        
        if st.session_state.current_step > 10:
            st.session_state.game_state = "RESULT"
        else:
            st.session_state.game_state = "ROLLING"
        time.sleep(2)
        st.rerun()

# D. 結算階段
elif st.session_state.game_state == "RESULT":
    st.balloons()
    st.header("🎊 遊戲結束！")
    final_df = pd.DataFrame([
        {"玩家": p, "總分": st.session_state.players[p]['score']} 
        for p in st.session_state.players
    ]).sort_values(by="總分", ascending=False)
    st.table(final_df)
    if st.button("回首頁"):
        reset_game()

