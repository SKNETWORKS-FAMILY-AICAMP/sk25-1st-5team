import pandas as pd
import streamlit as st
import ast

from components.layout import render_sidebar, render_main_box
from util import get_table_df

st.set_page_config(page_title="FAQ", layout="wide")

render_sidebar()
box = render_main_box(title="FAQ")

# 회사 이름(탭 버튼) -> 해당 회사 FAQ CSV 파일 경로를 매핑
COMPANY_MAP = {
    "HYUNDAI": "현대",
    "KIA": "KIA",
    "GENESIS": "Genesis",
    "KGM": "KGM",
    "CHEVROLET": "Chevrolet",
    "BMW": "BMW"
}

companies = list(COMPANY_MAP.keys())

# 기본값 현대로 설정
if "company" not in st.session_state:
    st.session_state.company = "HYUNDAI"


# Box 안에 FAQ 렌더
with box:
    # 기업별 버튼 만들기
    tab_cols = st.columns(len(companies), gap="small")

    # 클릭 시 즉시 상태 변경을 위한 콜백
    def set_company(name):
        st.session_state.company = name

    for i, c in enumerate(companies):
        label = f"▶ {c}" if c == st.session_state.company else c

        with tab_cols[i]:
            st.button(
                label,
                key=f"tab_{c}",
                use_container_width=True,
                on_click=set_company,
                args=(c,)
            )

    # 웹에서 표시될 기업명
    selected_display = st.session_state.company

    # DB 기업명
    selected_db_name = COMPANY_MAP[selected_display]

    # 선택된 기업 저장 및 faq 데이터 불러오기
    df = get_table_df("FAQ")
    df = df[df["company_name"] == selected_db_name]

    qa_list = []
    for _, row in df.iterrows():
        pairs = row["faq_pairs"]
        if isinstance(pairs, str):
            pairs = ast.literal_eval(pairs)
        for q, a in pairs.items():
            qa_list.append((str(q).strip(), str(a).strip()))

    
    # 검색 입력창 (키워드로 질문 필터링)
    keyword = st.text_input("검색", placeholder="예: 정비 예약, 에어백...")
    if keyword:
        kw = keyword.lower()
        qa_list = [(q, a) for (q, a) in qa_list if kw in q.lower()]

    # 질문 목록 출력:
    # 질문은 접었다 펼 수 있는 expander로 표시
    # 질문을 클릭하면 답변이 보이게 함
    if not qa_list:
        st.info("검색 결과가 없습니다.")
    else:
        for q, a in qa_list:
            with st.expander(q):
                st.text(a)
