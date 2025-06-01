import streamlit as st
import pandas as pd
import io
import os
import re

st.header("📥 특강 등록부 생성")

# 📌 명사형 추출 함수
def 명사형으로_변환(col_name):
    col = re.sub(r'\(.*?\)', '', col_name)  # 괄호 제거
    col = re.sub(r'(을|를|에|의|은|는)?\s*(입력|작성|응답|쓰시오|하세요|해주세요)?', '', col)
    return col.strip()

uploaded_file = st.file_uploader("설문 결과 CSV 파일을 업로드하세요.", type="csv")

if uploaded_file is not None:
    base_title = os.path.splitext(uploaded_file.name)[0]
    title_text = f"{base_title} 등록부"

    df = pd.read_csv(uploaded_file)
    columns = df.columns.tolist()

    st.markdown("#### 🔍 설문 항목에서 사용할 두 열을 선택해주세요")
    col1, col2 = st.columns(2)
    with col1:
        selected_col1 = st.selectbox("📌 첫 번째 열 선택", columns, index=next((i for i, c in enumerate(columns) if '학번' in c), 0))
    with col2:
        selected_col2 = st.selectbox("📌 두 번째 열 선택", columns, index=next((i for i, c in enumerate(columns) if '이름' in c), 0))

    # ▶️ 명사형 컬럼 이름
    col1_clean = 명사형으로_변환(selected_col1)
    col2_clean = 명사형으로_변환(selected_col2)

    registration_df = df[[selected_col1, selected_col2]].copy()
    registration_df.columns = [col1_clean, col2_clean]

    def 학번정렬키(x):
        try:
            return int(str(x).replace('-', ''))
        except:
            return str(x)

    registration_df = registration_df.sort_values(by=col1_clean, key=lambda col: col.map(학번정렬키)).reset_index(drop=True)
    registration_df.insert(0, '구분', range(1, len(registration_df)+1))
    registration_df['서명'] = ''
    registration_df['비고'] = ''

    final_columns = ['구분', col1_clean, col2_clean, '서명', '비고']
    registration_df = registration_df[final_columns]

    st.subheader("등록부 미리보기 (상위 10명)")
    st.dataframe(
        registration_df.head(10),
        use_container_width=True,
        hide_index=True,
        height=350,
        column_order=final_columns
    )

    # ✅ 엑셀 저장
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
        registration_df.to_excel(writer, index=False, sheet_name='등록부', startrow=2)
        workbook = writer.book
        worksheet = writer.sheets['등록부']

        title_format = workbook.add_format({
            'bold': True, 'font_size': 22,
            'align': 'center', 'valign': 'vcenter'
        })
        worksheet.merge_range('A1:E1', f'(         ) 특강 등록부', title_format)

        worksheet.set_row(1, 10)

        header_format = workbook.add_format({
            'bold': True, 'font_size': 14,
            'border': 1, 'align': 'center',
            'valign': 'vcenter', 'bg_color': '#D9E1F2'
        })
        cell_format = workbook.add_format({
            'border': 1, 'font_size': 14,
            'align': 'center', 'valign': 'vcenter'
        })

        worksheet.set_column('A:A', 8)
        worksheet.set_column('B:B', 16)
        worksheet.set_column('C:C', 16)
        worksheet.set_column('D:E', 18)

        for col_num, value in enumerate(registration_df.columns.values):
            worksheet.write(2, col_num, value, header_format)

        for row_num in range(len(registration_df)):
            worksheet.set_row(row_num+3, 35)
            for col_num, value in enumerate(registration_df.iloc[row_num]):
                worksheet.write(row_num+3, col_num, value, cell_format)

        worksheet.repeat_rows(0, 2)

    excel_buffer.seek(0)

    st.download_button(
        label="엑셀(xlsx)로 등록부 다운로드",
        data=excel_buffer,
        file_name=f"{base_title}_등록부.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    st.success(f"엑셀 시트에 반영된 열 제목은 '{col1_clean}', '{col2_clean}' 형식으로 간결하게 처리됩니다!")
else:
    st.info("CSV 파일을 업로드하면 미리보기와 편집 가능한 엑셀 파일을 다운로드할 수 있습니다.")
