import pandas as pd
import streamlit as st
import ast

from components.layout import render_sidebar, render_main_box

st.set_page_config(page_title="FAQ", layout="wide")

render_sidebar()
box = render_main_box(title="FAQ")

# Box 안에 FAQ 렌더
with box:
    # 회사 이름(탭 버튼) -> 해당 회사 FAQ CSV 파일 경로를 매핑
    COMPANY_FILES = {
        "HYUNDAI": "data/hyundai_faq.csv",
        "KIA": "data/kia_faq.csv",
        "GENESIS": "data/genesis_faq.csv",
        "KGM": "data/kgm_faq.csv",
        "CHEVROLET": "data/chevrolet_faq.csv",
        "BMW": "data/bmw_faq.csv",
    }

    companies = list(COMPANY_FILES.keys())

    # 기본값 현대로 설정
    if "company" not in st.session_state:
        st.session_state.company = "HYUNDAI"

    # 기업별 버튼 만들기
    tab_cols = st.columns(len(companies), gap="small")
    for i, c in enumerate(companies):
        with tab_cols[i]:
            if st.button(c, key=f"tab_{c}", use_container_width=True):
                st.session_state.company = c


    # 선택된 기업 저장 및 faq 데이터 불러오기
    selected = st.session_state.company

    df = pd.read_csv(COMPANY_FILES[selected])
    pairs_col = df.columns[1]

    qa_list = []
    for _, row in df.iterrows():
        pairs = row[pairs_col]
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
    for q, a in qa_list:
        with st.expander(q):
            st.write(a)
