import streamlit as st
import pandas as pd
import io
import os

# 페이지 설정
st.set_page_config(
    page_title="Quick Sign Sheet - 특강 등록부 생성기",
    page_icon="🧾",
    layout="centered"
)

# 제목
st.title("🧾 Quick Sign Sheet")
st.subheader("빠르게 특강 등록부를 만들어주는 시스템입니다 🚀")

st.markdown("""
### 👈 왼쪽 메뉴를 클릭하여 시작해 주세요!
특강 신청 설문조사 결과 파일을 업로드하면,  
자동으로 정리된 특강 등록부를 만들어드립니다. 😊

✅ **파일 형식**: CSV  
✅ **기능**: 신청자 리스트 정리, 특강별 신청 현황 확인 등
""")

st.header("📥 특강 등록부 생성")

uploaded_file = st.file_uploader("설문 결과 CSV 파일을 업로드하세요.", type="csv")

if uploaded_file is not None:
    # 파일명에서 확장자 제거하여 제목 생성
    base_title = os.path.splitext(uploaded_file.name)[0]
    title_text = f"{base_title} 등록부"

    df = pd.read_csv(uploaded_file)

    # 🔍 사용자에게 학번/이름 항목 선택받기
    columns = df.columns.tolist()

    st.markdown("#### 🔍 설문 항목에서 '학번'과 '이름' 항목을 선택해주세요")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_student_id_col = st.selectbox("🆔 학번 항목 선택", columns, index=next((i for i, c in enumerate(columns) if '학번' in c), 0))
    with col2:
        selected_name_col = st.selectbox("👤 이름 항목 선택", columns, index=next((i for i, c in enumerate(columns) if '이름' in c), 0))

    # 학번, 이름 추출 및 정리
    registration_df = df[[selected_student_id_col, selected_name_col]].copy()
    registration_df.columns = ['학번', '이름']  # 열 이름 통일

    def 학번정렬키(x):
        try:
            return int(str(x).replace('-', ''))
        except:
            return str(x)

    registration_df = registration_df.sort_values(by='학번', key=lambda col: col.map(학번정렬키)).reset_index(drop=True)
    registration_df.insert(0, '구분', range(1, len(registration_df)+1))
    registration_df['서명'] = ''
    registration_df['비고'] = ''
    registration_df = registration_df[['구분', '학번', '이름', '서명', '비고']]

    # 🔍 등록부 미리보기
    st.subheader("등록부 미리보기 (상위 10명)")
    st.dataframe(
        registration_df.head(10),
        use_container_width=True,
        hide_index=True,
        height=350,
        column_order=['구분', '학번', '이름', '서명', '비고']
    )

    # 📥 엑셀 다운로드 처리
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        registration_df.to_excel(writer, index=False, sheet_name='등록부', startrow=2)
        workbook = writer.book
        worksheet = writer.sheets['등록부']

        # 제목
        title_format = workbook.add_format({
            'bold': True,
            'font_size': 22,
            'align': 'center',
            'valign': 'vcenter'
        })
        worksheet.merge_range('A1:E1', '(         ) 특강 등록부', title_format)

        # 빈 행
        worksheet.set_row(1, 10)

        # 헤더 및 셀 서식
        header_format = workbook.add_format({
            'bold': True,
            'font_size': 14,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#D9E1F2'
        })
        cell_format = workbook.add_format({
            'border': 1,
            'font_size': 14,
            'align': 'center',
            'valign': 'vcenter'
        })

        # 컬럼 너비
        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 16)
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:E', 18)

        # 헤더 서식 적용
        for col_num, value in enumerate(registration_df.columns.values):
            worksheet.write(2, col_num, value, header_format)

        # 데이터 서식
        for row_num in range(len(registration_df)):
            worksheet.set_row(row_num+3, 35)
            for col_num, value in enumerate(registration_df.iloc[row_num]):
                worksheet.write(row_num+3, col_num, value, cell_format)

        worksheet.repeat_rows(0, 2)

    excel_buffer.seek(0)

    # 다운로드 버튼
    st.download_button(
        label="엑셀(xlsx)로 등록부 다운로드",
        data=excel_buffer,
        file_name=f"{base_title}_등록부.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success(f"엑셀 인쇄 시 모든 페이지 상단에 '{title_text}'와 항목명이 반복되고, 데이터 행은 35로 고정됩니다.")

else:
    st.info("CSV 파일을 업로드하면 미리보기와 편집 가능한 엑셀 파일을 다운로드할 수 있습니다.")
