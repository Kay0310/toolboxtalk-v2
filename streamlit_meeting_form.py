import streamlit as st
import datetime
import os
from fpdf import FPDF

# 관리자 여부 확인
is_admin = st.session_state.get("logged_in", False)
user_name = st.session_state.get("username", "guest")

# 세션 상태 초기화
if "attendees" not in st.session_state:
    st.session_state.attendees = []
if "confirmations" not in st.session_state:
    st.session_state.confirmations = []
if "discussion" not in st.session_state:
    st.session_state.discussion = []
if "tasks" not in st.session_state:
    st.session_state.tasks = []

st.title("📋 Toolbox Talk 회의록 서식")

# 회의 정보
st.header("1️⃣ 회의 정보")
today = datetime.date.today()
now = datetime.datetime.now().strftime("%H:%M")

col1, col2 = st.columns(2)
with col1:
    date = st.date_input("날짜", today)
    place = st.text_input("장소", "현장 A")
with col2:
    time = st.text_input("시간", now)
    task = st.text_input("작업 내용", "고소작업")

# 참석자 관리
st.header("2️⃣ 참석자")
if is_admin:
    leader = st.text_input("리더 이름", user_name)
else:
    leader = "admin"

if is_admin:
    new_member = st.text_input("팀원 이름 추가")
    if st.button("출석 등록") and new_member:
        if new_member not in st.session_state.attendees:
            st.session_state.attendees.append(new_member)

st.write("🧑‍🤝‍🧑 현재 참석자 명단:")
for name in st.session_state.attendees:
    st.markdown(f"- {name}")

# 논의 내용 입력
st.header("3️⃣ 논의 내용 (위험요소 & 안전대책)")
if is_admin:
    risk = st.text_input("위험요소 입력")
    measure = st.text_input("안전대책 입력")
    if st.button("논의 내용 추가") and risk and measure:
        st.session_state.discussion.append((risk, measure))

if st.session_state.discussion:
    st.write("📌 등록된 논의 내용")
    for idx, (r, m) in enumerate(st.session_state.discussion):
        st.markdown(f"**{idx+1}. 위험요소:** {r}  
➡️ **안전대책:** {m}")

# 추가 논의 사항
st.header("4️⃣ 추가 논의 사항")
additional = st.text_area("추가 사항", "" if not is_admin else "추가로 논의된 내용 정리")

# 결정사항 및 조치
st.header("5️⃣ 결정사항 및 조치")
if is_admin:
    col1, col2, col3 = st.columns(3)
    with col1:
        person = st.text_input("담당자")
    with col2:
        role = st.text_input("업무/역할")
    with col3:
        due = st.date_input("완료 예정일", today)

    if st.button("R&R 추가") and person and role:
        st.session_state.tasks.append((person, role, due))

if st.session_state.tasks:
    st.write("📋 등록된 역할 및 조치")
    for p, r, d in st.session_state.tasks:
        st.markdown(f"- **{p}**: {r} (완료일: {d})")

# 회의 내용 확인 및 서명
st.header("6️⃣ 회의록 확인 및 서명")
if user_name not in st.session_state.confirmations:
    if st.button("✅ 회의 내용 확인"):
        st.session_state.confirmations.append(user_name)
        st.success(f"{user_name}님의 확인이 저장되었습니다.")
else:
    st.success(f"{user_name}님은 이미 확인하셨습니다.")

# PDF 저장
if is_admin:
    if st.button("📄 회의록 PDF 저장"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"📋 Toolbox Talk 회의록\n\n일시: {date} {time}\n장소: {place}\n작업내용: {task}\n\n리더: {leader}")
        pdf.multi_cell(0, 10, f"\n참석자: {', '.join(st.session_state.attendees)}")
        pdf.multi_cell(0, 10, "\n🧠 논의 내용")
        for idx, (r, m) in enumerate(st.session_state.discussion):
            pdf.multi_cell(0, 10, f"{idx+1}. 위험요소: {r} / 안전대책: {m}")
        pdf.multi_cell(0, 10, f"\n➕ 추가 논의 사항:\n{additional}")
        pdf.multi_cell(0, 10, "\n✅ 결정사항 및 조치")
        for p, r, d in st.session_state.tasks:
            pdf.multi_cell(0, 10, f"- {p}: {r} (완료 예정일: {d})")
        pdf.multi_cell(0, 10, "\n✍ 확인자 목록")
        for n in st.session_state.confirmations:
            pdf.multi_cell(0, 10, f"- {n} (확인 완료)")

        filename = f"회의록_{datetime.datetime.now().strftime('%Y%m%d_%H%M')}.pdf"
        pdf.output(filename)
        with open(filename, "rb") as f:
            st.download_button("📥 PDF 다운로드", f, file_name=filename)
        os.remove(filename)