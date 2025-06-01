import streamlit as st

# 페이지 설정
st.set_page_config(
    page_title="Quick Sign Sheet - 특강 등록부 생성기",
    page_icon="🧾",
    layout="centered"
)

# 제목
st.title("🧾 Quick Sign Sheet")
st.subheader("빠르게 특강 등록부를 만들어주는 시스템입니다 🚀")

# 안내 메시지
st.markdown("""
### 👈 왼쪽 메뉴를 클릭하여 시작해 주세요!
특강 신청 설문조사 결과 파일을 업로드하면,  
자동으로 정리된 특강 등록부를 만들어드립니다. 😊

✅ **파일 형식**: CSV  
✅ **기능**: 신청자 리스트 정리, 특강별 신청 현황 확인 등
""")

# 부가적인 응원 메시지
st.info("간단한 CSV 파일 하나면 충분해요! 지금 바로 등록부를 만들어보세요 💪")
