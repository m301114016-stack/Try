import streamlit as st
import pandas as pd
import itertools
import random
from streamlit_gsheets import GSheetsConnection
# 1. 基本網頁設定
st.set_page_config(page_title="台灣藥學生專業認同探討", page_icon="💊", layout="centered")

# 2. Session 初始化
if "initialized" not in st.session_state:
    factors = {
        "用藥風險": ["風險1：劑量偏高", "風險2：藥物交互作用", "風險3：藥物過敏"],
        "醫師態度": ["高壓：醫師強勢要求", "低壓：醫師表示藥師自負責任"],
        "患者反應": ["反應1：患者咆哮", "反應2：患者焦慮", "反應3：患者焦慮" ],
        "同儕氛圍": ["孤立：建議別惹麻煩", "支持：支持你的判斷"]
    }
    all_vignettes = list(itertools.product(*factors.values()))
    st.session_state.vignettes = random.sample(all_vignettes, 3)
    st.session_state.step = -1
    st.session_state.answers = []
    st.session_state.short_answers = {} # 初始化填充題答案儲存
    st.session_state.initialized = True

st.title("💊 台灣藥學生專業認同探討")

# 3. 建立連線
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception as e:
    st.error("連線初始化失敗，請檢查 Secrets 設定。")

# 4. 流程控制邏輯
# --- Step -1：同意書 ---
if st.session_state.step == -1:
    with st.form("consent_form"):
        st.subheader("研究說明與同意書")
        st.write("""各位同學們好:   
        此問卷目的在於了解台灣藥學生專業認同之行為，並探討相關因素之影響。     
                    我們誠摯邀請你填寫問卷，整份問卷約需花費你10分鐘的時間。  
                    本研究已通過台北醫學大學暨附屬醫院聯合人體研究倫理委員會核准，您的資料將視為機密且身分將被保密。     
                    若您在研究過程中有任何對本研究之疑慮，可隨時要求修正、刪除資料，亦可以選擇退出研究。     
                    再次感謝您的協助。     
                    問卷填寫完後，若民有意願領取數位禮券，請留下您常用的email，經研究人員確定為有效問卷後，將依前200名填寫順序寄送。""")
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
        
        # 0. 性別 (修正參數格式)
        gender = st.selectbox("您的性別", ["請選擇", "男", "女", "其他/不願透露"])
        
        # 1. 學校選擇
        q_school_select = st.selectbox("您的學校", ["請選擇", "台灣大學", "陽明交通大學", "台北醫學大學", "中國醫藥大學", "成功大學", "嘉南藥理大學", "高雄醫學大學", "大仁科技大學", "慈濟大學"])
        
        
        # 2. 年級與經驗
        year = st.selectbox("您的年級", ["請選擇", "藥學系一年級", "藥學系二年級", "藥學系三年級", "藥學系四年級", "藥學系五年級", "藥學系六年級"])
        
        # 3. Email (建議換個變數名稱以免混淆)
        q_email = st.text_input("1. 如願意收到電子禮券，請輸入 email", placeholder="例如：example@gmail.com")
        
        if st.form_submit_button("下一步"):
            # 統一邏輯檢查
            if gender == "請選擇":
                st.error("⚠️ 請選擇性別")
            elif q_school_select == "請選擇":
                st.error("⚠️ 請選擇您的學校")
            elif year == "請選擇":
                st.error("⚠️ 請選擇年級")
            else:
                # 將資料存入 session_state
                st.session_state.gender = gender
                st.session_state.year = year
                st.session_state.q_school = q_school_select
                st.session_state.q_email = q_email
            
                
                # 跳轉至 Step 0.5 (填充題頁面)
                st.session_state.step = 0.5
                st.rerun()
# --- Step 0.5：填充題頁面 ---
elif st.session_state.step == 0.5:
    # 1. 返回按鈕放在 Form 外面
    if st.button("⬅️ 返回修改基本資料"):
        st.session_state.step = 0
        st.rerun()

    # 2. 開啟表單
    with st.form("sa_form"):
        st.subheader("第二部分：前言")
        st.write("""
        假設你已經成為執照在手的藥師，接下來我們會遇到一些情境，
        請依照您在該情境下「堅持專業判斷」的可能性進行評分。
        """)
        
        # 3. 提交按鈕必須在 with st.form 的縮排內
        submit_btn = st.form_submit_button("進入情境題")
        
        if submit_btn:
            st.session_state.step = 1  # 跳轉到第一題情境題
            st.rerun() # 確保與 if 對齊
            
# --- Step 1~3：情境題 ---
elif 1 <= st.session_state.step <= 3:
    idx = st.session_state.step - 1
    v = st.session_state.vignettes[idx]
    
    # 導航欄：顯示進度與返回
    col1, col2 = st.columns([1, 5])
    with col1:
        if st.button("⬅️ 返回"):
            if st.session_state.step == 1:
                st.session_state.step = 0.5
            else:
                st.session_state.step -= 1
                st.session_state.answers.pop() # 移除上一次存入的答案
            st.rerun()
    
    st.subheader(f"情境題目 ({st.session_state.step} / 3)")
    with st.form(f"v_form_{st.session_state.step}"):
        st.info(f"用藥風險：{v[0]}\n醫師態度：{v[1]}\n患者反應：{v[2]}\n同儕氛圍：{v[3]}")
        score = st.slider("堅持專業判斷的可能性？", 1, 7, 4)
        if st.form_submit_button("下一題"):
            st.session_state.answers.append({
                "年級": st.session_state.year, 
                "用藥風險": v[0], 
                "醫師態度": v[1], 
                "患者反應": v[2], 
                "同儕氛圍": v[3], 
                "分數": score
            })
            st.session_state.step += 1
            st.rerun()

# --- Step 4：完成與上傳 ---
# --- Step 4：完成與上傳 ---
# --- Step 4：完成與上傳 ---
else:
    st.success("✅ 問卷完成，感謝您的參與！")
    
    if "submitted" not in st.session_state:
        with st.spinner("資料同步中..."):
            try:
                # 1. 準備合併後的完整資料
                final_data = []
                for ans in st.session_state.answers:
                    # 直接從 session_state 抓取第一頁存好的變數
                    new_row = {
                        "性別": st.session_state.get("gender", ""),
                        "年級": st.session_state.get("year", ""),
                        "學校名稱": st.session_state.get("q_school", ""), # 修正：直接抓 q_school
                        "電子郵件": st.session_state.get("q_email", ""), # 確保包含 Email
                        **ans # 展開情境題的資料
                    }
                    final_data.append(new_row)
                
                df_new = pd.DataFrame(final_data)

                # 2. 讀取與合併雲端資料
                try:
                    existing_data = conn.read()
                except:
                    # 定義初始欄位名稱（確保順序與 Google 試算表一致）
                    existing_data = pd.DataFrame(columns=["性別", "年級", "學校名稱", "電子郵件", "用藥風險", "醫師態度", "患者反應", "同儕氛圍", "分數"])
                
                # 3. 執行更新
                updated_df = pd.concat([existing_data, df_new], ignore_index=True)
                conn.update(data=updated_df)
                
                st.session_state.submitted = True
                st.balloons()
                st.info("📊 數據已成功存入雲端！")
            except Exception as e:
                st.error(f"雲端存檔失敗：{e}")
    # 顯示填答紀錄供使用者確認
    df_display = pd.DataFrame(st.session_state.answers)
    st.dataframe(df_display, use_container_width=True)
    st.download_button("📥 下載備份 (CSV)", df_display.to_csv(index=False).encode("utf-8-sig"), "result.csv")
    
    if st.button("🔄 重新填寫"):
        st.session_state.clear()
        st.rerun()
