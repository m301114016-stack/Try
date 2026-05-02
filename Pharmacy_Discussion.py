
import streamlit as st
import random
import time

# 設定頁面與標題
st.set_page_config(page_title="天選之人：骰子對決", page_icon="🎲")

# 初始化玩家清單
if 'players' not in st.session_state:
    st.session_state.players = {}

st.title("🎲 天選之人：骰子對決")
st.write("掃描 QR Code 加入，由點數最大者勝出！")

# --- 側邊欄：加入區域 ---
with st.sidebar:
    st.header("📲 參與者進入")
    name = st.text_input("輸入你的暱稱", placeholder="例如：學生 A")
    if st.button("點我加入"):
        if name:
            if name not in st.session_state.players:
                st.session_state.players[name] = 0
                st.success(f"【{name}】已成功登錄！")
            else:
                st.warning("這個名字已經有人用了喔！")
    
    st.divider()
    if st.button("重置所有資料", type="secondary"):
        st.session_state.players = {}
        st.rerun()

# --- 主畫面：對決區域 ---
if not st.session_state.players:
    st.info("目前還沒有人加入，請在側邊欄輸入暱稱。")
else:
    st.subheader(f"目前候選人 ({len(st.session_state.players)} 位)")
    # 顯示目前在場名單
    player_names = ", ".join(st.session_state.players.keys())
    st.text(f"名單：{player_names}")

    if st.button("🔥 全員同時擲骰子！", type="primary", use_container_width=True):
        st.divider()
        
        # 模擬擲骰子動畫感
        with st.status("正在瘋狂搖晃骰子盅...", expanded=True) as status:
            time.sleep(1.5)
            # 產生隨機點數 (1-100)
            results = {name: random.randint(1, 100) for name in st.session_state.players}
            st.session_state.players.update(results)
            status.update(label="開蓋！結果揭曉！", state="complete", expanded=False)

        # 找出最高分
        winner = max(results, key=results.get)
        max_point = results[winner]

        # 慶祝動畫
        st.balloons()
        st.header(f"👑 最終贏家：【{winner}】")
        st.subheader(f"以 {max_point} 點力壓群雄！")

        # 顯示所有人的戰果
        st.write("---")
        st.write("### 戰報統計")
        
        # 將結果排序顯示
        sorted_results = sorted(results.items(), key=lambda x: x[1], reverse=True)
        for name, score in sorted_results:
            st.write(f"🎲 {name}：{score} 點")

