import streamlit as st
import pandas as pd
import itertools
import random
from streamlit_gsheets import GSheetsConnection

# 1. 基本網頁設定
st.set_page_config(page_title="藥學生專業認同調查", page_icon="💊", layout="centered")

# 2. Session 初始化
if "initialized" not in st.session_state:
    factors = {
        "用藥風險": ["風險1：劑量稍高", "風險2：交互作用", "風險3：藥物過敏"],
        "醫師態度": ["高壓：醫師強勢要求", "低壓：醫師表示自負責任"],
        "患者反應": ["負向：患者咆哮", "正向：患者焦慮"],
        "同儕氛圍": ["孤立：建議別惹麻煩", "支持：支持你的判斷"]
    }
    all_vignettes = list(itertools.product(*factors.values()))
    st.session_state.vignettes = random.sample(all_vignettes, 3)
    st.session_state.step = -1
    st.session_state.answers = []
    st.session_state.initialized = True

st.title("💊 藥學生專業認同調查")

# 3. 建立連線 (它會自動去 Secrets 找資料)
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("連線初始化失敗，請檢查 Secrets 設定。")

# 4. 流程控制邏輯
if st.session_state.step == -1:
    with st.form("consent_form"):
        st.subheader("研究說明與同意書")
        st.write("本問卷採匿名制，您可以隨時中止填寫。")
        consent = st.checkbox("我已閱讀並同意參與本研究")
        if st.form_submit_button("開始填寫"):
            if consent:
                st.session_state.step = 0
                st.rerun()
            else:
                st.error("⚠️ 請先勾選同意書")

elif st.session_state.step == 0:
    with st.form("info_form"):
        st.subheader("第一部分：基本資料")
        year = st.selectbox("您的年級", ["請選擇", "藥學系一年級", "藥學系二年級", "藥學系三年級", "藥學系四年級", "藥學系五年級", "藥學系六年級", "PGY1", "PGY2"])
        if st.form_submit_button("下一步"):
            if year == "請選擇":
                st.error("⚠️ 請選擇年級")
            else:
                st.session_state.year = year
                st.session_state.step = 1
                st.rerun()

elif 1 <= st.session_state.step <= 3:
    idx = st.session_state.step - 1
    v = st.session_state.vignettes[idx]
    st.subheader(f"情境題目 ({st.session_state.step} / 3)")
    with st.form(f"v_form_{st.session_state.step}"):
        st.info(f"用藥風險：{v[0]}\n醫師態度：{v[1]}\n患者反應：{v[2]}\n同儕氛圍：{v[3]}")
        score = st.slider("堅持專業判斷的可能性？", 1, 7, 4)
        if st.form_submit_button("下一題"):
            st.session_state.answers.append({
                "年級": st.session_state.year, "用藥風險": v[0], "醫師態度": v[1], "患者反應": v[2], "同儕氛圍": v[3], "分數": score
            })
            st.session_state.step += 1
            st.rerun()

else:
    st.success("✅ 問卷完成，感謝您的參與！")
    df_new = pd.DataFrame(st.session_state.answers)
    
    if "submitted" not in st.session_state:
        with st.spinner("資料同步中..."):
            try:
                existing_data = conn.read()
              with st.spinner("資料同步中..."):
            try:
                # 嘗試讀取資料，如果失敗（如空檔）則建立一個空的 DataFrame
                try:
                    existing_data = conn.read()
                except:
                    # 如果讀不到資料（空表），則建立只有標題的 DataFrame
                    existing_data = pd.DataFrame(columns=["年級", "用藥風險", "醫師態度", "患者反應", "同儕氛圍", "分數"])
                
                # 合併新舊資料
                updated_df = pd.concat([existing_data, df_new], ignore_index=True)
                
                # 寫回雲端
                conn.update(data=updated_df)
                st.session_state.submitted = True
                st.balloons()
                st.info("📊 數據已成功存入雲端！")
            except Exception as e:
                st.error(f"雲端存檔失敗：{e}")
                
    st.dataframe(df_new)
    st.download_button("📥 下載備份", df_new.to_csv(index=False).encode("utf-8-sig"), "result.csv")
    if st.button("🔄 重新填寫"):
        st.session_state.clear()
        st.rerun()
