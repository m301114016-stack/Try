import streamlit as st
import random

# 設定網頁標題與風格
st.set_page_config(page_title="PPE 穿脫順序挑戰賽", page_icon="🥼", layout="centered")

st.title("🥼 PPE 穿脫順序挑戰賽")
st.write("作為醫療與研究人員，正確的感控防護是必備基本功！請拖曳或選擇正確的步驟順序。")

# 正確答案資料庫
CORRECT_DONNING = ["內層口罩", "髮帽", "外層口罩", "內層手套", "隔離衣", "外層手套", "鞋套"]
CORRECT_DOFFING = ["外層手套", "隔離衣(由外而內反摺捲起)", "內層手套", "洗手(第一次)", "外層口罩", "髮帽", "內層口罩", "洗手(第二次)"]

# 初始化 Session State
if "donning_shuffled" not in st.session_state:
    st.session_state.donning_shuffled = random.sample(CORRECT_DONNING, len(CORRECT_DONNING))
if "doffing_shuffled" not in st.session_state:
    # 為了避免兩個「洗手」造成混淆，後台給予標記，前台顯示時再隱藏標記
    st.session_state.doffing_shuffled = random.sample(CORRECT_DOFFING, len(CORRECT_DOFFING))

tab1, tab2 = st.tabs(["挑戰 1：穿上隔離衣 (Donning)", "挑戰 2：脫卸隔離衣 (Doffing)"])

# -------------------------------------------------------------------------
# TAB 1: 穿上隔離衣
# -------------------------------------------------------------------------
with tab1:
    st.subheader("請排列【穿上】隔離衣的正確順序：")
    st.caption("請由上至下選取第 1 步到第 7 步")
    
    user_donning = []
    # 使用 multiselect 讓使用者依序選擇
    selected_donning = st.multiselect(
        "點擊依序選擇步驟：",
        options=st.session_state.donning_shuffled,
        key="donning_select",
        help="請按照順序點選"
    )
    
    # 顯示目前使用者排好的順序
    if selected_donning:
        st.markdown("#### **你目前排好的順序：**")
        for i, step in enumerate(selected_donning):
            st.markdown(f"**第 {i+1} 步：** {step}")
            
    if st.button("提交穿上順序檢查", type="primary"):
        if len(selected_donning) != len(CORRECT_DONNING):
            st.warning(f"填寫不完整喔！你只選擇了 {len(selected_donning)} 個步驟，總共有 {len(CORRECT_DONNING)} 個。")
        elif selected_donning == CORRECT_DONNING:
            st.success("🎉 太棒了！穿上隔離衣的順序完全正確！無菌感控一級棒！")
        else:
            st.error("❌ 喔不！順序有點瑕疵，可能會有污染風險，再試一次吧！")
            st.markdown("💡 **正確順序提示：**")
            st.info(" ➡️ ".join(CORRECT_DONNING))

# -------------------------------------------------------------------------
# TAB 2: 脫卸隔離衣
# -------------------------------------------------------------------------
with tab2:
    st.subheader("請排列【脫卸】隔離衣的正確順序：")
    st.caption("請特別注意『洗手』的時間點！")
    
    # 前台顯示時，把後台區分第一次/第二次洗手的標記洗掉，維持遊戲難度
    display_options = [s.split("(")[0] if "洗手" in s else s for s in st.session_state.doffing_shuffled]
    
    # 建立一個對照字典，方便檢查答案
    display_to_real = {}
    for real_step in st.session_state.doffing_shuffled:
        disp = real_step.split("(")[0] if "洗手" in real_step else real_step
        # 如果是洗手，因為有兩個，我們用 list 存
        if disp in display_to_real:
            display_to_real[disp].append(real_step)
        else:
            display_to_real[disp] = [real_step]

    selected_doffing_display = st.multiselect(
        "點擊依序選擇步驟：",
        options=list(set(display_options)), # 去重顯示
        key="doffing_select",
        help="請按照順序點選，『洗手』可以重複點選兩次"
    )
    
    # 因為洗手要選兩次，multiselect 預設元件去重可能不方便重複選，這裡改用下拉選單組合以確保精準度
    st.write("---")
    st.markdown("#### 🛠️ 請下拉選單填入 1~8 步：")
    
    col1, col2 = st.columns(2)
    user_doffing_display = []
    
    # 建立 8 個下拉選單
    available_choices = ["請選擇..."] + sorted(list(set(display_options)))
    
    with col1:
        for i in range(1, 5):
            choice = st.selectbox(f"第 {i} 步", options=available_choices, key=f"step_{i}")
            user_doffing_display.append(choice)
    with col2:
        for i in range(5, 9):
            choice = st.selectbox(f"第 {i} 步", options=available_choices, key=f"step_{i}")
            user_doffing_display.append(choice)

    if st.button("提交脫卸順序檢查", type="primary"):
        if "請選擇..." in user_doffing_display:
            st.warning("請把 8 個步驟全部填寫完畢再送出喔！")
        else:
            # 驗證邏輯：轉換使用者選的「洗手」成有標記的版本來比對答案
            handwash_count = 0
            user_real_sequence = []
            for item in user_doffing_display:
                if item == "洗手":
                    handwash_count += 1
                    user_real_sequence.append(f"洗手(第一次)" if handwash_count == 1 else f"洗手(第二次)")
                else:
                    user_real_sequence.append(item)
            
            # 核對答案
            if user_real_sequence == CORRECT_DOFFING:
                st.success("🎉 完美！脫卸順序完全正確！這能確保你和環境的安全！")
            else:
                st.error("❌ 糟了！脫卸順序有誤，這可能會讓你在脫除過程中接觸到病原體！")
                st.markdown("💡 **正確順序提示：**")
                # 呈現給使用者看時去掉後台標記
                clean_correct = [s.split("(")[0] if "洗手" in s else s for s in CORRECT_DOFFING]
                st.info(" ➡️ ".join(clean_correct))
                st.caption("註：隔離衣脫卸時需由外而內反摺捲起，且在接觸面部（口罩、髮帽）前必須先洗手！")

# 重新洗牌按鈕
if st.sidebar.button("🔄 重新洗牌題目"):
    st.session_state.pop("donning_shuffled", None)
    st.session_state.pop("doffing_shuffled", None)
    st.rerun()
