import streamlit as st
from streamlit_sortables import sort_items

# 設定網頁
st.set_page_config(page_title="PPE 穿脫順序拼圖挑戰", page_icon="🧩", layout="centered")

st.title("🧩 PPE 穿脫順序拼圖遊戲")
st.write("用滑鼠**上下拖曳**右側的卡片，拼出正確的感控防護順序吧！")

# 正確答案定義
CORRECT_DONNING = ["內層口罩", "髮帽", "外層口罩", "內層手套", "隔離衣", "外層手套", "鞋套"]
# 為了避免拖曳時兩個「洗手」卡片完全等價導致程式錯亂，我們在字尾加上不可見的空格
CORRECT_DOFFING = ["外層手套", "隔離衣(由外而內反摺捲起)", "內層手套", "洗手 ", "外層口罩", "髮帽", "內層口罩", "洗手"]

# 初始化題目（只在第一次載入或重置時打亂順序）
if "donning_puzzle" not in st.session_state:
    import random
    st.session_state.donning_puzzle = random.sample(CORRECT_DONNING, len(CORRECT_DONNING))
if "doffing_puzzle" not in st.session_state:
    import random
    st.session_state.doffing_puzzle = random.sample(CORRECT_DOFFING, len(CORRECT_DOFFING))

# 切換 穿/脫 分頁
tab1, tab2 = st.tabs(["🟢 挑戰一：穿上隔離衣", "🔴 挑戰二：脫卸隔離衣"])

# -------------------------------------------------------------------------
# TAB 1: 穿上隔離衣拼圖
# -------------------------------------------------------------------------
with tab1:
    st.subheader("請由上至下拖曳拼圖，完成【穿上】順序：")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("順序參考：")
        for i in range(1, 8):
            st.markdown(f"**第 {i} 步** 👇")
            
    with col2:
        # 呼叫拖曳元件
        current_donning_order = sort_items(
            st.session_state.donning_puzzle, 
            direction="vertical", 
            key="donning_sortable"
        )
        
    st.write("---")
    if st.button("🧩 檢查穿上拼圖結果", type="primary", key="check_don"):
        if current_donning_order == CORRECT_DONNING:
            st.success("🎉 完美拼出！穿上順序完全正確，防護結界無懈可擊！")
        else:
            st.error("❌ 拼圖順序有點不對勁喔！這樣可能會有感控漏洞，再調整看看！")
            st.markdown("**💡 正確拼圖順序：**")
            st.info(" ➡️ ".join(CORRECT_DONNING))

# -------------------------------------------------------------------------
# TAB 2: 脫卸隔離衣拼圖
# -------------------------------------------------------------------------
with tab2:
    st.subheader("請由上至下拖曳拼圖，完成【脫卸】順序：")
    st.caption("提示：注意兩次『洗手』發生的關鍵時間點！")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write("順序參考：")
        for i in range(1, 9):
            st.markdown(f"**第 {i} 步** 👇")
            
    with col2:
        # 呼叫拖曳元件
        current_doffing_order = sort_items(
            st.session_state.doffing_puzzle, 
            direction="vertical", 
            key="doffing_sortable"
        )
        
    st.write("---")
    if st.button("🧩 檢查脫卸拼圖結果", type="primary", key="check_doff"):
        if current_doffing_order == CORRECT_DOFFING:
            st.success("🎉 太厲害了！脫卸順序完全正確！成功保護自己與外部環境！")
        else:
            st.error("❌ 糟了，這個拼法會讓你在脫除時暴露於污染風險中！")
            st.markdown("**💡 正確拼圖順序：**")
            # 呈現給使用者看時，把後台為了不重複而加的空格去掉
            clean_correct = [s.strip() for s in CORRECT_DOFFING]
            st.info(" ➡️ ".join(clean_correct))
            st.caption("🔍 核心防護觀念：脫掉內層手套後要立刻洗手，才能去碰觸面部的口罩與髮帽喔！")

# 側邊欄控制
with st.sidebar:
    st.markdown("### 🎮 遊戲控制面板")
    if st.button("🔄 重新打亂拼圖"):
        st.session_state.pop("donning_puzzle", None)
        st.session_state.pop("doffing_puzzle", None)
        st.rerun()
