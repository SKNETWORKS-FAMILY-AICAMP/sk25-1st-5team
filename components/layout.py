import streamlit as st

def render_sidebar():
    st.markdown(
        """
        <style>
        section[data-testid="stSidebar"] .stButton { 
            display: flex; 
            justify-content: center; 
            width: 100%;
            margin-top: 2px;
        }
        section[data-testid="stSidebar"] .stButton > button {
            background-color: #5D8C7A ;
            color: white;
            font-weight: 700;
            border-radius: 8px;
            width: 200px;
            height: 50px;
            text-align: center;
        }

        section[data-testid="stSidebar"] .stImage {
            display: flex;
            justify-content: center;
        }

        section[data-testid="stSidebar"] .stImage > div {
            height: 150px !important;
            overflow: hidden !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        section[data-testid="stSidebar"] img { display:block; margin: 0 auto; }
        section[data-testid="stSidebar"] .stCaption { text-align:center !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.image("./img/autok_logo.png")
        st.caption("(v 1.0.0. copyright by SKN25 TEAM5)")

        if st.button("등록 현황"):
            st.switch_page("pages/main.py")
        if st.button("인구 차량 추이"):
            st.switch_page("pages/population.py")
        if st.button("정비소 비율"):
            st.switch_page("pages/repair_ratio_map.py")
        if st.button("정비소 지도"):
            st.switch_page("pages/maintenance.py")
        if st.button("정비 FAQ"):
            st.switch_page("pages/faq.py")


def render_main_box(title: str):
    st.markdown(
        """
        <style>
        .main-title {
            background: #f1d7d2;
            border-radius: 8px;
            padding: 10px 18px;
            font-weight: 800;
            color: #222;
            display: inline-block;
            margin-bottom: 10px;
        }

        
        div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stContainer"]) {
            min-height: 720px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"<div class='main-title'>{title}</div>", unsafe_allow_html=True)

    box = st.container(border=True)
    return box
