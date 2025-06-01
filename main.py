import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="특강 등록부 생성기",
    page_icon="🧾",
    layout="centered"
)

# 제목
st.title("🧾 특강 신청 설문조사 ➡️ 특강 등록부 생성기")
st.subheader("설문조사 파일을 업로드하면 자동으로 등록부를 만들어드려요 😊")

# 파일 업로드
uploaded_file = st.file_uploader("📤 특강 신청 설문조사 결과 파일을 업로드하세요 (엑셀 또는 CSV)", type=["xlsx", "xls", "csv"])

if uploaded_file is not None:
    try:
        # 파일 읽기
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.success("✅ 설문조사 파일이 성공적으로 업로드되었습니다!")
        st.write("📄 원본 설문조사 데이터:")
        st.dataframe(df)

        # 여기서 등록부 생성 로직을 추가할 수 있어요!

    except Exception as e:
        st.error(f"❌ 파일을 읽는 중 오류가 발생했습니다: {e}")
