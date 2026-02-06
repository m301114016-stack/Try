import streamlit as st
import pandas as pd
import itertools
import random
from streamlit_gsheets import GSheetsConnection
import uuid

# 1. 基本網頁設定
st.set_page_config(page_title="大眾抗生素使用意願調查", page_icon="💊", layout="centered")

# 2. Session 初始化 (抗生素抗藥性因子設定)
if "initialized" not in st.session_state:
    factors = {
        "症狀感受": ["輕微流鼻涕、喉嚨癢", "持續高燒 38.5 度且全身無力"],
        "時間壓力": ["接下來幾天可以請假在家休息", "後天有非常重要的工作面試或出國行程"],
        "過往經驗": ["以前感冒吃抗生素病很快就好了", "以前吃抗生素產生過嚴重腹瀉或過敏"],
        "醫師建議": ["醫師明確告知是病毒感染，抗生素無效", "醫師態度模糊，表示開藥當作預防性治療"],
        "取得便利性": ["家裡藥櫃剛好有上次剩的抗生素", "家裡沒剩藥，需重新掛號排隊才能拿藥"]
    }
    # 產生所有組合 (2x2x2x2x2 = 32 種)
    all_vignettes = list(itertools.product(*factors.values()))
    
    st.session_state.response_id = str(uuid.uuid4())[:8].upper() 
    # 隨機抽取 5 題，確保負擔不會太大
    st.session_state.vignettes = random.sample(all_vignettes, 5) 
    
    st.session_state.step = -1
    st.session_state.answers = []
    st.session_state.initialized = True

st.title("💊 大眾抗生素使用意願調查")

# 3. 建立連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("連線初始化失敗，請檢查 Secrets 設定。")

def slider_label():
    c1, c2 = st.columns([1, 1])
    c1.caption("⬅️ 非常不可能 / 低")
    c2.markdown("<p style='text-align: right; color: gray; font-size: small;'>非常可能 / 高 ➡️</p>", unsafe_allow_html=True)

# 4. 流程控制邏輯
# --- Step -1：同意書 ---
if st.session_state.step == -1:
    with st.form("consent_form"):
        st.subheader("研究說明與同意書")
        st.write("""
        這是一項關於「大眾對抗生素使用決策」的學術調查。  
        我們希望了解在不同生活情境下，民眾對於使用抗生素的真實想法。   
        我們誠摯邀請你填寫問卷，整份問卷約需花費你10分鐘的時間。    
        本研究已通過台北醫學大學暨附屬醫院聯合人體研究倫理委員會核准，您的資料將視為機密且身分將被保密。    
        若您在研究過程中有任何對本研究之疑慮，可隨時要求修正、刪除資料，亦可以選擇退出研究。    
        再次感謝您的協助。   
        問卷填寫完後，若您有意願領取數位禮券，請留下您常用的email，經研究人員確定為有效問卷後，將依前200名填寫順序寄送。
        """)
        st.write("本問卷採匿名制，您可以隨時中止填寫。")
        st.write("""台北醫學大學藥學系碩士班   
        學生:張嘉真  
        指導教授: 張雅惠 副教授""")
        st.write("""如需額外相關資訊或有任何問題，歡迎與我們聯繫。  
        聯絡人:張嘉真  
        連絡電話:(02)2376-1661#6177  
        Email:m301114016@tmu.edu.tw""")
        consent = st.checkbox("我已閱讀並同意參與本研究")
        if st.form_submit_button("開始填寫"):
            if consent:
                st.session_state.step = 0
                st.rerun()
            else:
                st.error("⚠️ 請先勾選同意書")

# --- Step 0：基本資料 ---
elif st.session_state.step == 0:
    with st.form("info_form"):
        st.subheader("第一部分：基本資料")
        gender = st.selectbox("您的性別", ["請選擇", "男", "女", "其他"])
        age = st.selectbox("您的年齡層", ["請選擇", "20歲以下", "21-30歲", "31-40歲", "41-50歲", "51-60歲","61-70歲","71歲-80歲","81歲-90歲","91歲以上" ])
        edu = st.selectbox("您的教育程度", ["請選擇", "高中職以下", "大專院校", "研究所及以上"])
        q_email = st.text_input("若您有意願領取數位禮券，請輸入 email", placeholder="example@gmail.com")

        if st.form_submit_button("下一步"):
            if "請選擇" in [gender, age, edu]:
                st.error("⚠️ 請完整填寫所有必填欄位")
            else:
                st.session_state.gender = gender
                st.session_state.age = age
                st.session_state.edu = edu
                st.session_state.q_email = q_email
                st.session_state.step = 1
                st.rerun()

# --- Step 1~5：情境題 ---
elif 1 <= st.session_state.step <= 5:
    idx = int(st.session_state.step - 1)
    v = st.session_state.vignettes[idx]
    
    st.subheader(f"🤔 決策情境 ({int(st.session_state.step)} / 5)")
    
    # 將因子組合成一段流暢的故事
    vignette_text = f"""
    【想像以下情境】  
    你目前感到 **{v[0]}**。考量到 **{v[1]}**，你非常希望病情能快速好轉。  
    根據你的記憶，**{v[2]}**。  
    就醫時，**{v[3]}**。  
    回到家後，你發現 **{v[4]}**。
    """
    
    with st.form(key=f"v_form_{st.session_state.step}"):
        st.info(vignette_text)
        st.write("---")
        
        st.write("1. 您「主動要求醫師開立」或「自行服用」抗生素的可能性？")
        score_1 = st.slider("Q1", 0, 10, 5, key=f"q1_s{st.session_state.step}", label_visibility="collapsed")
        slider_label()
        
        st.write("2. 如果最後「沒有」服用抗生素，您對病情惡化的「擔心程度」？")
        score_2 = st.slider("Q2", 0, 10, 5, key=f"q2_s{st.session_state.step}", label_visibility="collapsed")
        slider_label()
        
        st.write("3. 您對於該位醫師專業判斷的「信任程度」？")
        score_3 = st.slider("Q3", 0, 10, 5, key=f"q3_s{st.session_state.step}", label_visibility="collapsed")
        slider_label()
        
        if st.form_submit_button("下一題" if st.session_state.step < 5 else "提交問卷"):
            common = {
                "症狀": v[0], "壓力": v[1], "經驗": v[2], "醫囑": v[3], "便利性": v[4]
            }
            # 儲存三個問題的回饋
            st.session_state.answers.append({**common, "維面": "使用意願", "分數": score_1})
            st.session_state.answers.append({**common, "維面": "風險擔憂", "分數": score_2})
            st.session_state.answers.append({**common, "維面": "醫師信任", "分數": score_3})
            st.session_state.step += 1
            st.rerun()

# --- Step 6：上傳與完成 ---
else:
    st.success(f"✅ 問卷完成！您的填答代碼為：{st.session_state.response_id}")
    
    if "submitted" not in st.session_state:
        with st.spinner("傳送數據至雲端..."):
            try:
                # 欄位重新對齊
                target_cols = [
                    "填答代碼", "性別", "年齡","教育程度", "電子郵件", 
                    "症狀", "壓力", "經驗", "醫囑", "便利性", "維面", "分數"
                ]

                final_data = []
                for ans in st.session_state.answers:
                    new_row = {
                        "填答代碼": st.session_state.response_id,
                        "性別": st.session_state.gender,
                        "年級_年齡": st.session_state.age,
                        "學校_教育": st.session_state.edu,
                        "電子郵件": st.session_state.q_email,
                        **ans 
                    }
                    final_data.append(new_row)
                
                df_new = pd.DataFrame(final_data).reindex(columns=target_cols)

                # 讀取並合併 Google Sheets
                existing_data = conn.read()
                updated_df = pd.concat([existing_data, df_new], ignore_index=True)
                conn.update(data=updated_df)
                
                st.session_state.submitted = True
                st.balloons()
            except Exception as e:
                st.error(f"存檔發生錯誤：{e}")

    if st.button("🔄 重新填寫"):
        st.session_state.clear()
        st.rerun()
