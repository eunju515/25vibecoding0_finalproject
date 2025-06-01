import streamlit as st
import pandas as pd
import io
import re

st.header("생활기록부 기초파일 생성기")

uploaded_file = st.file_uploader("설문 결과 CSV 파일을 업로드하세요.", type="csv")

def extract_main_word(question):
    q = re.sub(r'\s*\(.*\)\s*', '', question)
    q = re.sub(r'[\s.,?…!]*$', '', q)
    q = re.sub(r'(을|를|에|의|은|는|도|가|이|으로|로|에서|에게|께|한테|부터|까지|와|과|및|이나|나|든지|라도|마저|조차|처럼|보다|밖에|만)\s*', '', q)
    q = re.sub(r'(쓰시오|적으시오|입력하시오|작성|적기|써주세요|다시 입력하시오|있다면|있을까요|있나요|있습니까|해주세요|해 주세요|해주십시오|해주시기 바랍니다|해주시길 바랍니다|해보세요|해보면|해보는|해보자)', '', q)
    q = re.sub(r'[\s]+', ' ', q)
    return q.strip() or question

def 학번정렬키(x):
    try:
        return int(str(x).replace('-', '').replace(' ', ''))
    except:
        return str(x)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    columns = list(df.columns)

    # 학번, 이름 컬럼 자동 탐지
    id_col = next((col for col in columns if '학번' in col), None)
    name_col = next((col for col in columns if '이름' in col), None)

    if not id_col or not name_col:
        st.error("CSV 파일에 학번 또는 이름 컬럼이 존재하지 않습니다.")
        st.stop()

    # 선택 가능한 컬럼(학번, 이름 제외)
    selectable_cols = [col for col in columns if col not in [id_col, name_col]]

    # 멀티셀렉트: 선택/해제 모두 실시간 반영
    selected_cols = st.multiselect(
        "생기부 기초파일에 포함할 설문 항목을 선택/제거하세요. (학번, 이름은 항상 포함됩니다)",
        selectable_cols,
        default=[],
        key="selected_cols"
    )

    # 최종 컬럼 및 명사형 항목명 변환
    final_cols = [id_col, name_col] + selected_cols
    new_col_names = [extract_main_word(col) for col in final_cols]

    # 학번 기준 오름차순 정렬 + 빈칸 공백 처리
    if all(col in df.columns for col in final_cols):
        sorted_df = df[final_cols].copy()
        sorted_df = sorted_df.sort_values(
            by=id_col, 
            key=lambda col: col.map(학번정렬키),
            ascending=True
        ).reset_index(drop=True)
        sorted_df = sorted_df.fillna('')  # 빈칸 공백 처리

        # 미리보기
        preview_df = sorted_df.head(10)
        preview_df.columns = new_col_names
        st.markdown(f"**현재 선택된 항목:** {' → '.join(new_col_names)}")
        st.subheader("생기부 기초파일 미리보기 (상위 10명, 학번 오름차순)")
        st.dataframe(preview_df, use_container_width=True, hide_index=True)
    else:
        st.error("선택한 항목 중 일부가 CSV 파일에 존재하지 않습니다.")

    # 엑셀 다운로드
    if final_cols and all(col in df.columns for col in final_cols):
        output = io.BytesIO()
        base_df = df[final_cols].copy()
        base_df = base_df.sort_values(
            by=id_col, 
            key=lambda col: col.map(학번정렬키),
            ascending=True
        ).reset_index(drop=True)
        base_df = base_df.fillna('')  # 빈칸 공백 처리
        base_df.columns = new_col_names
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            base_df.to_excel(writer, index=False, sheet_name="생기부기초")
            workbook = writer.book
            worksheet = writer.sheets["생기부기초"]
            header_format = workbook.add_format({
                'bold': True, 'font_size': 12, 'align': 'center',
                'valign': 'vcenter', 'border': 1, 'bg_color': '#D9E1F2'
            })
            cell_format = workbook.add_format({
                'font_size': 12, 'align': 'center', 'valign': 'vcenter', 'border': 1
            })
            worksheet.set_row(0, 28)
            for col_num, value in enumerate(new_col_names):
                worksheet.write(0, col_num, value, header_format)
                worksheet.set_column(col_num, col_num, 18)
            for row_num in range(1, len(base_df)+1):
                worksheet.set_row(row_num, 22)
                for col_num in range(len(new_col_names)):
                    # 빈칸(None/NaN)도 공백으로 저장
                    val = base_df.iloc[row_num-1, col_num]
                    worksheet.write(row_num, col_num, val if pd.notnull(val) else '', cell_format)
        output.seek(0)
        st.download_button(
            label="생기부 기초 엑셀파일 다운로드",
            data=output,
            file_name="생기부기초.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    else:
        st.warning("다운로드 가능한 데이터가 없습니다.")
else:
    st.info("CSV 파일을 업로드하면 항목을 선택/제거해 생기부 기초파일을 만들 수 있습니다.")
