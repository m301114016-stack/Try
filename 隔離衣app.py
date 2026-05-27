import streamlit as st
import random

# 1. 網頁基本設定
st.set_page_config(page_title="隔離衣穿脫順序挑戰", page_icon="🥼", layout="centered")

st.title("🥼 隔離衣穿脫順序挑戰賽")
st.write("請利用下拉選單，拼出正確的步驟順序！")

# 2. 定義正確答案
CORRECT_DONNING = ["內層口罩", "髮帽", "外層口罩", "內層手套", "隔離衣", "外層手套", "鞋套"]
CORRECT_DOFFING = ["外層手套", "隔離衣(由外而內反摺捲起)", "內層手套", "洗手(第一次)", "外層口罩", "髮帽", "內層口罩", "洗手(第二次)"]

# 3. 初始化題目（打亂順序）
if "donning_options" not in st.session_state:
    st.session_state.donning_options = sorted(CORRECT_DONNING)
if "doffing_options" not in st.session_state:
    # 脫衣時前台顯示「洗手」即可，避免劇透
    st.session_state.doffing_options = sorted(list(set([s.split("(")[0] if "洗手" in s else s for s in CORRECT_DOFFING])))

# 建立 穿/脫 分頁
tab1, tab2 = st.tabs(["🟢 挑戰一：穿上隔離衣 (Donning)", "🔴 挑戰二：脫卸隔離衣 (Doffing)"])

# -------------------------------------------------------------------------
# 🟢 TAB 1: 穿上隔離衣
# -------------------------------------------------------------------------
with tab1:
    st.subheader("請選出【穿上】隔離衣的正確順序：")
    
    user_donning = []
    col1, col2 = st.columns(2)
    
    with col1:
        for i in range(1, 5):
            choice = st.selectbox(f"第 {i} 步", ["--請選擇--"] + st.session_state.donning_options, key=f"don_{i}")
            user_donning.append(choice)
    with col2:
        for i in range(5, 8):
            choice = st.selectbox(f"第 {i} 步", ["--請選擇--"] + st.session_state.donning_options, key=f"don_{i}")
            user_donning.append(choice)
            
    st.write("---")
    if st.button("🧩 檢查穿上順序", type="primary"):
        if "--請選擇--" in user_donning:
            st.warning("⚠️ 請填寫完所有步驟再送出喔！")
        elif user_donning == CORRECT_DONNING:
            st.success("🎉 太棒了！穿上順序完全正確！無菌感控做得非常到位！")
        else:
            st.error("❌ 順序有誤！這樣可能會造成局部污染，再試一次吧！")
            st.info("💡 **正確穿上順序提示：**\n\n" + " ➡️ ".join(CORRECT_DONNING))

# -------------------------------------------------------------------------
# 🔴 TAB 2: 脫卸隔離衣
# -------------------------------------------------------------------------
with tab2:
    st.subheader("請選出【脫卸】隔離衣的正確順序：")
    st.caption("⚠️ 注意：請特別留意「洗手」出現的時機點！")
    
    user_doffing_raw = []
    col1, col2 = st.columns(2)
    
    with col1:
        for i in range(1, 5):
            choice = st.selectbox(f"第 {i} 步", ["--請選擇--"] + st.session_state.doffing_options, key=f"doff_{i}")
            user_doffing_raw.append(choice)
    with col2:
        for i in range(5, 9):
            choice = st.selectbox(f"第 {i} 步", ["--請選擇--"] + st.session_state.doffing_options, key=f"doff_{i}")
            user_doffing_raw.append(choice)
            
    st.write("---")
    if st.button("🧩 檢查脫卸順序", type="primary"):
        if "--請選擇--" in user_doffing_raw:
            st.warning("⚠️ 請填寫完所有 8 個步驟再送出喔！")
        else:
            # 後台將使用者的「洗手」轉換為第一次與第二次，用來精準對答案
            handwash_count = 0
            user_doffing_processed = []
            for item in user_doffing_raw:
                if item == "洗手":
                    handwash_count += 1
                    user_doffing_processed.append("洗手(第一次)" if handwash_count == 1 else "洗手(第二次)")
                else:
                    user_doffing_processed.append(item)
            
            # 檢查答案
            if user_doffing_processed == CORRECT_DOFFING:
                st.success("🎉 完美！脫卸順序完全正確！成功保護自己與環境安全！")
            else:
                st.error("❌ 糟糕，順序不對！在碰觸面部（口罩、髮帽）前，必須先確保手部乾淨喔！")
                # 呈現給使用者看時洗掉後台標記
                clean_correct = [s.split("(")[0] if "洗手" in s else s for s in CORRECT_DOFFING]
                st.info("💡 **正確脫卸順序提示：**\n\n" + " ➡️ ".join(clean_correct))
