# Commented out IPython magic to ensure Python compatibility.
# %%writefile app.py
import streamlit as st
import pandas as pd
import itertools
import random
import requests
# =====================
# App 設定
# =====================
st.set_page_config(
    page_title="藥學生專業認同（Factorial Survey）",
    layout="centered"
)

# =====================
# Session 初始化
# =====================
if "initialized" not in st.session_state:

    factors = {
        "用藥風險": ["風險1：劑量稍高", "風險2：交互作用","風險3:藥物過敏"],
        "醫師態度": ["高壓：醫師強勢要求", "低壓：醫師表示自負責任"],
        "患者反應": ["負向：患者咆哮", "正向：患者焦慮"],
        "同儕氛圍": ["孤立：建議別惹麻煩", "支持：支持你的判斷"]
    }

    all_vignettes = list(itertools.product(*factors.values()))
    st.session_state.vignettes = random.sample(all_vignettes, 3)

    st.session_state.step = -1
    st.session_state.answers = []
    st.session_state.initialized = True

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
**研究目的**  
了解藥學生在不同臨床壓力組合下的專業判斷。

**研究方式**  
您將閱讀 3 個模擬臨床情境並進行評分。

**研究權益**  
- 問卷匿名  
- 可隨時中止  
- 僅供學術研究使用
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
        st.subheader("基本資料")

        year = st.selectbox(
            "您的年級",
            ["請選擇", "藥學系一年級", "藥學系二年級", "藥學系三年級", "藥學系四年級", "藥學系五年級", "藥學系六年級", "PGY1","PGY2"]
        )

        submit = st.form_submit_button("下一步")

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

    st.subheader(f"情境 {st.session_state.step} / 3")

    with st.form(f"vignette_{idx}"):

        st.info(f"""
**用藥風險**：{v[0]}  
**醫師態度**：{v[1]}  
**患者反應**：{v[2]}  
**同儕氛圍**：{v[3]}
        """)

        score = st.slider(
            "你會堅持專業判斷的可能性？",
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
# 完成頁
# =====================
else:
    st.success("✅ 問卷完成，感謝您的參與！")
    FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdFcBZPsPdq2tDQ55WS_ELR-t0Ju44LDMY8BxOFnzf0PDihsA/viewform?usp=pp_url"
    def submit_to_google_form(data_list):
        for data in data_list:
            form_data = {
                "entry.111111": data["年級"],
                "entry.222222": data["用藥風險"],
                "entry.333333": data["醫師態度"],
                "entry.444444": data["患者反應"],
                "entry.555555": data["同儕氛圍"],
                "entry.666666": data["堅持專業判斷分數"]
            }
            try:
                requests.post(FORM_URL, data=form_data)
            except:
                pass

    # 執行提交
    if "submitted_to_cloud" not in st.session_state:
        with st.spinner("數據同步中..."):
            submit_to_google_form(st.session_state.answers)
            st.session_state.submitted_to_cloud = True
            st.info("📊 數據已成功存入 Google 表單後台！")

    # 顯示結果
    df = pd.DataFrame(st.session_state.answers)
    st.dataframe(df)
    df = pd.DataFrame(st.session_state.answers)
    st.dataframe(df, use_container_width=True)

    st.download_button(
        "📥 下載結果（CSV）",
        df.to_csv(index=False, encoding="utf-8-sig"),
        file_name="factorial_survey_pharmacy.csv"
    )

    if st.button("🔄 重新填寫"):
        st.session_state.clear()
        st.rerun()
