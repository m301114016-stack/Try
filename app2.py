import streamlit as st
import pandas as pd
import itertools
import random
from streamlit_gsheets import GSheetsConnection
import uuid

# 1. 基本網頁設定
st.set_page_config(page_title="台灣藥學生專業認同探討", page_icon="💊", layout="centered")

# 2. Session 初始化 (確保邏輯順序：定義組合 -> 生成代碼 -> 抽樣)
if "initialized" not in st.session_state:
    factors = {
        "用藥風險": ["風險1：劑量偏高", "風險2：藥物交互作用", "風險3：藥物過敏"],
        "醫師態度": ["高壓：醫師強勢要求", "低壓：醫師表示藥師自負責任"],
        "病人反應": ["反應1：病人咆哮", "反應2：病人焦慮", "反應3：病人煩躁" ],
        "同儕氛圍": ["孤立：建議別惹麻煩", "支持：支持你的判斷"]
    }
    # 先產生所有可能的情境組合
    all_vignettes = list(itertools.product(*factors.values()))
    
    # 生成唯一填答代碼
    st.session_state.response_id = str(uuid.uuid4())[:8].upper() 
    
    # 從組合中隨機抽取 5 題情境
    st.session_state.vignettes = random.sample(all_vignettes, 5) 
    
    st.session_state.step = -1
    st.session_state.answers = []
    st.session_state.initialized = True

st.title("💊 台灣藥學生專業認同探討")

# 3. 建立連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("連線初始化失敗，請檢查 Secrets 設定。")

# 定義顯示標籤的輔助函數
def slider_label():
    c1, c2 = st.columns([1, 1])
    c1.caption("⬅️ 非常不可能")
    c2.markdown("<p style='text-align: right; color: gray; font-size: small;'>非常可能 ➡️</p>", unsafe_allow_html=True)

# 4. 流程控制邏輯
# --- Step -1：同意書 ---
if st.session_state.step == -1:
    with st.form("consent_form"):
        st.subheader("研究說明與同意書")
        st.write("""各位同學們好: 此問卷目的在於了解台灣藥學生專業認同之行為，並探討相關因素之影響。  
        我們誠摯邀請你填寫問卷，整份問卷約需花費你10分鐘的時間。  
        本研究已通過台北醫學大學暨附屬醫院聯合人體研究倫理委員會核准，您的資料將視為機密且身分將被保密。  
        若您在研究過程中有任何對本研究之疑慮，可隨時要求修正、刪除資料，亦可以選擇退出研究。  
        再次感謝您的協助。  
        問卷填寫完後，若您有意願領取數位禮券，請留下您常用的email，經研究人員確定為有效問卷後，將依前200名填寫順序寄送。""")
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
        gender = st.selectbox("您的性別", ["請選擇", "男", "女", "其他/不願透露"])
        q_school_select = st.selectbox("您的學校", ["請選擇", "台灣大學", "陽明交通大學", "台北醫學大學", "中國醫藥大學", "成功大學", "嘉南藥理大學", "高雄醫學大學", "大仁科技大學", "慈濟大學"])
        year = st.selectbox("您的年級", ["請選擇", "藥學系一年級", "藥學系二年級", "藥學系三年級", "藥學系四年級", "藥學系五年級", "藥學系六年級"])
        q_interests = st.multiselect("4. 您未來感興趣的執業領域是？(可多選)", ["醫院藥局", "社區藥局", "藥廠", "診所", "公部門", "學術研究", "還在考慮中"])
        q_email = st.text_input("1. 如願意收到電子禮券，請輸入 email", placeholder="例如：example@gmail.com")

        if st.form_submit_button("下一步"):
            if gender == "請選擇" or q_school_select == "請選擇" or year == "請選擇" or not q_interests:
                st.error("⚠️ 請完整填寫所有必填欄位")
            else:
                st.session_state.gender = gender
                st.session_state.year = year
                st.session_state.q_school = q_school_select
                st.session_state.q_email = q_email
                st.session_state.q_interests = ", ".join(q_interests)
                st.session_state.step = 0.5
                st.rerun()

# --- Step 0.5：前言 ---
elif st.session_state.step == 0.5:
    if st.button("⬅️ 返回修改基本資料"):
        st.session_state.step = 0
        st.rerun()
    with st.form("sa_form"):
        st.subheader("第二部分：前言")
        st.info("接下來會有 5 個情境，每頁包含 3 個子問題。請依照您的真實感受評分。")
        if st.form_submit_button("進入情境題"):
            st.session_state.step = 1
            st.rerun()

# --- Step 1~5：情境題 ---
elif 1 <= st.session_state.step <= 5:
    idx = int(st.session_state.step - 1)
    v = st.session_state.vignettes[idx]
    
    st.subheader(f"情境題目 ({int(st.session_state.step)} / 5)")
    with st.form(key=f"v_form_{st.session_state.step}"):
        st.info(f"【當前情境】\n用藥風險：{v[0]}\n醫師態度：{v[1]}\n病人反應：{v[2]}\n同儕氛圍：{v[3]}")
        
        st.write("1. 您堅持專業判斷的可能性？")
        score_1 = st.slider("Q1", 1, 10, 5, key=f"q1_s{st.session_state.step}", label_visibility="collapsed")
        slider_label()
        
        st.write("2. 您對此處方安全性感到擔憂的程度？")
        score_2 = st.slider("Q2", 1, 10, 5, key=f"q2_s{st.session_state.step}", label_visibility="collapsed")
        slider_label()
        
        st.write("3. 您承受此職場壓力的負擔感？")
        score_3 = st.slider("Q3", 1, 10, 5, key=f"q3_s{st.session_state.step}", label_visibility="collapsed")
        slider_label()
        
        if st.form_submit_button("下一題" if st.session_state.step < 5 else "提交問卷"):
            common = {
                "性別": st.session_state.gender, 
                "年級": st.session_state.year, 
                "學校": st.session_state.q_school, 
                "領域": st.session_state.q_interests, 
                "風險": v[0], "態度": v[1], "反應": v[2], "氛圍": v[3]
            }
            st.session_state.answers.append({**common, "題目": "堅持判斷", "分數": score_1})
            st.session_state.answers.append({**common, "題目": "安全擔憂", "分數": score_2})
            st.session_state.answers.append({**common, "題目": "職場壓力", "分數": score_3})
            st.session_state.step += 1
            st.rerun()

# --- Step 6：完成與上傳 ---
# --- Step 6：完成與上傳 ---
else:
    st.success(f"✅ 問卷完成，感謝參與！您的填答代碼為：{st.session_state.response_id}")
    
    if "submitted" not in st.session_state:
        with st.spinner("資料同步中..."):
            try:
                # ✅ 這裡的縮排必須對齊 try 內部
                target_cols = [
                    "填答代碼", "性別", "年級", "學校", "領域", 
                    "電子郵件", "風險", "態度", "反應", "氛圍", "題目", "分數"
                ]

                # 準備資料
                final_data = []
                for ans in st.session_state.answers:
                    new_row = {
                        "填答代碼": st.session_state.response_id,
                        "性別": st.session_state.get("gender", ""),
                        "年級": st.session_state.get("year", ""),
                        "學校": st.session_state.get("q_school", ""),
                        "領域": st.session_state.get("q_interests", ""),
                        "電子郵件": st.session_state.get("q_email", ""),
                        **ans 
                    }
                    final_data.append(new_row)
                
                # 轉成 DataFrame 並強制排序欄位
                df_new = pd.DataFrame(final_data)
                df_new = df_new.reindex(columns=target_cols)

                # 讀取並合併
                try:
                    existing_data = conn.read()
                    updated_df = pd.concat([existing_data, df_new], ignore_index=True)
                except Exception:
                    updated_df = df_new
                
                # 上傳更新內容
                conn.update(data=updated_df)
                st.session_state.submitted = True
                st.balloons()
                
            except Exception as e:
                # ✅ 這裡的縮排必須對齊 except 內部
                st.error(f"雲端存檔失敗，請確認試算表欄位。錯誤：{e}")

    st.write("### 您的填答摘要預覽")
    st.dataframe(pd.DataFrame(st.session_state.answers), use_container_width=True)
    
    if st.button("🔄 重新填寫"):
        st.session_state.clear()
        st.rerun()
