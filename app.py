import streamlit as st
import pandas as pd
import itertools
import random
from streamlit_gsheets import GSheetsConnection

# =====================
# App 設定
# =====================
st.set_page_config(
    page_title="藥學生專業認同調查",
    page_icon="💊",
    layout="centered"
)

# =====================
# Session 初始化
# =====================
if "initialized" not in st.session_state:
    # 定義階乘實驗因子
    factors = {
        "用藥風險": ["風險1：劑量稍高", "風險2：交互作用", "風險3：藥物過敏"],
        "醫師態度": ["高壓：醫師強勢要求", "低壓：醫師表示自負責任"],
        "患者反應": ["負向：患者咆哮", "正向：患者焦慮"],
        "同儕氛圍": ["孤立：建議別惹麻煩", "支持：支持你的判斷"]
    }

    # 產生所有組合並隨機抽取 3 題
    all_vignettes = list(itertools.product(*factors.values()))
    st.session_state.vignettes = random.sample(all_vignettes, 3)

    # 流程控制與資料儲存
    st.session_state.step = -1
    st.session_state.answers = []
    st.session_state.initialized = True

# =====================
# 建立資料庫連線
# =====================
# 這會自動讀取 Cloud Secrets 中的 [connections.gsheets]
conn = st.connection("gsheets", type=GSheetsConnection)

# =====================
# 標題
# =====================
st.title("💊 藥學生專業認同調查（Factorial Survey）")

# =====================
# Step -1：研究同意書
# =====================
if st.session_state.step == -1:
    with st.form("consent_form"):
        st.subheader("研究說明與同意書")
        st.markdown("""
        **研究目的**：了解藥學生在不同臨床壓力組合下的專業判斷。  
        **研究方式**：您將閱讀 3 個模擬臨床情境並進行評分。  
        **研究權益**：本問卷採完全匿名制，資料僅供學術研究使用，您可以隨時中止填寫。
        """)
        
        consent = st.checkbox("我已閱讀並同意參與本研究")
        submit = st.form_submit_button("開始填寫")

        if submit:
            if consent:
                st.session_state.step = 0
                st.rerun()
            else:
                st.error("⚠️ 請先勾選同意書")

# =====================
# Step 0：基本資料
# =====================
elif st.session_state.step == 0:
    with st.form("info_form"):
        st.subheader("第一部分：基本資料")
        year = st.selectbox(
            "您的年級",
            ["請選擇", "藥學系一年級", "藥學系二年級", "藥學系三年級", "藥學系四年級", "藥學系五年級", "藥學系六年級", "PGY1", "PGY2"]
        )
        submit = st.form_submit_button("進入情境題")

        if submit:
            if year == "請選擇":
                st.error("⚠️ 請選擇年級")
            else:
                st.session_state.year = year
                st.session_state.step = 1
                st.rerun()

# =====================
# Step 1–3：情境題
# =====================
elif 1 <= st.session_state.step <= 3:
    idx = st.session_state.step - 1
    v = st.session_state.vignettes[idx]

    st.subheader(f"情境題目 ({st.session_state.step} / 3)")

    with st.form(f"vignette_form_{st.session_state.step}"):
        st.info(f"""
        **用藥風險**：{v[0]}  
        **醫師態度**：{v[1]}  
        **患者反應**：{v[2]}  
        **同儕氛圍**：{v[3]}
        """)

        score = st.slider(
            "在此情境下，您堅持專業判斷的可能性？(1:極低, 7:極高)",
            min_value=1,
            max_value=7,
            value=4
        )

        submit = st.form_submit_button("下一題")

        if submit:
            st.session_state.answers.append({
                "年級": st.session_state.year,
                "用藥風險": v[0],
                "醫師態度": v[1],
                "患者反應": v[2],
                "同儕氛圍": v[3],
                "堅持專業判斷分數": score
            })
            st.session_state.step += 1
            st.rerun()

# =====================
# Step 4：完成頁與雲端上傳
# =====================
else:
    st.success("✅ 問卷完成，感謝您的參與！")
    
    df_new = pd.DataFrame(st.session_state.answers)

    # 雲端自動儲存邏輯
    if "submitted_to_gsheet" not in st.session_state:
        with st.spinner("正在同步數據至雲端資料庫..."):
            try:
                # 1. 讀取現有資料
                existing_data = conn.read()
                # 2. 合併新舊資料
                updated_df = pd.concat([existing_data, df_new], ignore_index=True)
                # 3. 更新回 Google Sheets
                conn.update(data=updated_df)
                
                st.session_state.submitted_to_gsheet = True
                st.balloons()
                st.info("📊 數據已成功存入後端試算表！")
            except Exception as e:
                st.error("⚠️ 雲端同步失敗，請務必點擊下方按鈕下載 CSV 存檔並回傳給研究員。")

    st.subheader("填答紀錄預覽")
    st.dataframe(df_new, use_container_width=True)

    # 備份下載按鈕
    csv_data = df_new.to_csv(index=False).encode("utf-8-sig")
    st.download_button(
        label="📥 下載個人填答結果 (CSV)",
        data=csv_data,
        file_name="pharmacy_survey_result.csv",
        mime="text/csv"
    )

    if st.button("🔄 重新填寫問卷"):
        st.session_state.clear()
        st.rerun()
