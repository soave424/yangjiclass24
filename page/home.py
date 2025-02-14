import streamlit as st
import pandas as pd
import os
from datetime import datetime
import pytz

# CSV 파일 경로 설정
CSV_FILE = "maintenance_requests.csv"

def load_data():
    if not os.path.exists(CSV_FILE):  # 파일이 없으면 생성
        df = pd.DataFrame(columns=["date", "applicant", "contact", "floor", "classroom", "content", "status", "memo", "delete_code"])
        df.to_csv(CSV_FILE, index=False)
    else:
        df = pd.read_csv(CSV_FILE, dtype={'date': str, 'delete_code': str})
    return df

def save_data(df):
    df.to_csv(CSV_FILE, index=False)

# 데이터 불러오기
data = load_data()
st.set_page_config(layout="wide")  # 화면 레이아웃을 넓게 설정

st.title("\U0001F3EB 유지보수 서비스 신청 게시판")

# 레이아웃 설정
col1, col2 = st.columns([2, 3])

# 왼쪽: 신청 폼
with col1:
    st.header("\U0001F4DD 신청하기")
    
    with st.form("request_form"):
        applicant = st.text_input("신청자 이름", "")
        contact = st.text_input("연락처(꼭 필요한 경우만 입력)", value="031-574-0831")
        floor = st.selectbox("교실 위치(층)", [1, 2, 3, 4, 5])
        classroom = st.text_input("교실명", "")
        content = st.text_area("유지보수 신청 내용", "")
        delete_code = st.text_input("삭제코드 (4자리 숫자)", "").zfill(4)
        submit_request = st.form_submit_button("신청")
        
        if submit_request:
            if applicant and contact and classroom and content and delete_code.isdigit() and len(delete_code) == 4:
                korea_tz = pytz.timezone('Asia/Seoul')
                date = datetime.now(korea_tz).strftime("%Y-%m-%d %a %H:%M:%S").replace('Mon', '월').replace('Tue', '화').replace('Wed', '수').replace('Thu', '목').replace('Fri', '금').replace('Sat', '토').replace('Sun', '일')
                new_entry = pd.DataFrame([[date, applicant, contact, floor, classroom, content, "신청 완료", "", delete_code]], 
                                         columns=["date", "applicant", "contact", "floor", "classroom", "content", "status", "memo", "delete_code"])
                data = pd.concat([data, new_entry], ignore_index=True)
                save_data(data)
                st.success("✅ 신청이 완료되었습니다!")
                st.rerun()
            else:
                st.warning("⚠ 비어있는 내용이 있거나 삭제코드가 4자리 숫자가 아닙니다.")

# 오른쪽: 신청 게시판
with col2:
    st.header("\U0001F4CB 신청 목록")
    pending_data = data[data["status"] == "신청 완료"]
    completed_data = data[data["status"] == "해결 완료"]
    
    st.subheader(f"\U0001F7E1 해결 중 ({len(pending_data)}건)")
    if pending_data.empty:
        st.info("🚧 현재 신청 목록이 없습니다.")
    else:
        for idx, row in pending_data.iterrows():
            with st.expander(f"[{row['floor']}층_{row['classroom']}] {row['content'][:20]}...   ({row['date']})"):
                st.write(f"**신청자:** {row['applicant']}")
                st.write(f"**연락처:** {row['contact']}")
                st.write(f"**교실 위치:** {row['floor']}층 {row['classroom']}")
                st.write(f"**신청 내용:** {row['content']}")
                st.write(f"**해결 상태:** {row['status']}")
                st.write(f"**메모:** {row['memo']}")

                # 상태 변경 폼
                with st.form(key=f"status_form_{idx}"):
                    status = st.selectbox("상태 변경", ["해결 완료", "신청 완료"], index=0)
                    memo = st.text_area("메모 입력", placeholder="특이사항이 있는 경우 작성해주세요.")
                    submit_status = st.form_submit_button("확인")
                    
                    if submit_status:
                        data.loc[data.index[idx], "status"] = status
                        data.loc[data.index[idx], "memo"] = memo
                        save_data(data)
                        st.success("✅ 상태가 업데이트되었습니다!")
                        st.rerun()

                # 삭제 기능
                delete_input = st.text_input("삭제를 원하시면 코드를 입력해주세요.", "", key=f"delete_{idx}")
                delete_button = st.button("삭제", key=f"delete_btn_{idx}")
                
                if delete_button:
                    if delete_input == str(row["delete_code"]):
                        data = data.drop(index=data.index[idx]).reset_index(drop=True)
                        save_data(data)
                        st.success("🗑 신청이 삭제되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 삭제 코드가 일치하지 않습니다.")
    
    st.subheader(f"✅ 완료 목록 ({len(completed_data)}건)")
    if completed_data.empty:
        st.info("🔹 해결된 요청이 없습니다.")
    else:
        for idx, row in completed_data.iterrows():
            with st.expander(f"[{row['floor']}층_{row['classroom']}] {row['content'][:20]}...   ({row['date']})"):
                st.write(f"**신청자:** {row['applicant']}")
                st.write(f"**연락처:** {row['contact']}")
                st.write(f"**교실 위치:** {row['floor']}층 {row['classroom']}")
                st.write(f"**신청 내용:** {row['content']}")
                st.write(f"**해결 상태:** {row['status']}")
                st.write(f"**메모:** {row['memo']}")
