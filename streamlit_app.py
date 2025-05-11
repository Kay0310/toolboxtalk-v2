import streamlit as st
import openai
import os
import uuid
from dotenv import load_dotenv
from fpdf import FPDF

# 환경 변수 로드
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY", "")

# 세션 상태 초기화
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "attendees" not in st.session_state:
    st.session_state.attendees = []
if "transcript" not in st.session_state:
    st.session_state.transcript = ""
if "summary" not in st.session_state:
    st.session_state.summary = ""

# 로그인 화면
def login():
    st.title("🔐 관리자 로그인")
    username = st.text_input("아이디")
    password = st.text_input("비밀번호", type="password")
    if st.button("로그인"):
        if username == "admin" and password == "1234":
            st.session_state.logged_in = True
            st.success("로그인 성공!")
        else:
            st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

# 출석 체크
def attendance():
    st.subheader("🧾 출석 체크")
    name = st.text_input("참석자 이름 입력")
    if st.button("출석 추가"):
        if name and name not in st.session_state.attendees:
            st.session_state.attendees.append(name)
    st.write("현재 참석자 명단:")
    for i, person in enumerate(st.session_state.attendees):
        st.write(f"{i+1}. {person}")

# 음성 업로드 + Whisper 변환
def upload_and_transcribe():
    st.subheader("🔊 음성 파일 업로드")
    audio_file = st.file_uploader("음성 파일 선택", type=["mp3", "wav", "m4a"])
    if st.button("Whisper 변환 실행") and audio_file:
        with open(f"temp_{audio_file.name}", "wb") as f:
            f.write(audio_file.read())
        try:
            with open(f"temp_{audio_file.name}", "rb") as f:
                transcript = openai.Audio.transcribe("whisper-1", f, language="ko")
                st.session_state.transcript = transcript.get("text", "")
        except Exception as e:
            st.error(f"오류 발생: {e}")

    if st.session_state.transcript:
        st.subheader("📝 변환된 회의록")
        st.session_state.summary = st.text_area("회의 내용 수정", st.session_state.transcript, height=300)

# PDF 저장
def download_pdf():
    if st.session_state.summary and st.button("📄 회의록 PDF 저장"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 10, f"회의록\n\n참석자: {', '.join(st.session_state.attendees)}\n\n내용:\n{st.session_state.summary}")
        file_path = f"회의록_{uuid.uuid4().hex[:6]}.pdf"
        pdf.output(file_path)
        with open(file_path, "rb") as f:
            st.download_button("📥 PDF 다운로드", f, file_name=file_path)
        os.remove(file_path)

# 앱 실행 흐름
if not st.session_state.logged_in:
    login()
else:
    st.title("📋 Toolbox Talk 회의록 시스템")
    attendance()
    upload_and_transcribe()
    download_pdf()