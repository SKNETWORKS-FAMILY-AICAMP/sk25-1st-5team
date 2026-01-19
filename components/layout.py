import streamlit as st
import os
from pathlib import Path
import base64

# 색상
SIDEBAR_SHADOW = "rgba(0, 0, 0, 0.1)"
BUTTON_BG_COLOR = "#5D8C7A"
BUTTON_TEXT_COLOR = "white"
SELECTBOX_BORDER_COLOR = "#d0d0d0"
MAIN_TITLE_BG_COLOR = "#f1d7d2"
MAIN_TITLE_TEXT_COLOR = "#222"

# 이미지 경로 설정
BASE_DIR = Path(__file__).resolve().parent.parent
IMG_PATH = BASE_DIR / "img" / "help.png"


def render_sidebar():
    st.markdown(
        f"""
        <style>
        section[data-testid="stSidebar"] {{
            box-shadow: 2px 0 8px {SIDEBAR_SHADOW};
        }}
        
        section[data-testid="stSidebar"] .stButton {{ 
            display: flex; 
            justify-content: center; 
            width: 100%;
            margin-top: 2px;
        }}
        section[data-testid="stSidebar"] .stButton > button {{
            background-color: {BUTTON_BG_COLOR};
            color: {BUTTON_TEXT_COLOR};
            font-weight: 700;
            border-radius: 8px;
            width: 200px;
            height: 50px;
            text-align: center;
            transition: all 0.3s ease;
        }}
        
        section[data-testid="stSidebar"] .stButton > button:hover {{
            background-color: #4a6f5f;
        }}

        section[data-testid="stSidebar"] .stImage {{
            display: flex;
            justify-content: center;
        }}

        section[data-testid="stSidebar"] .stImage > div {{
            height: 150px !important;
            overflow: hidden !important;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        section[data-testid="stSidebar"] img {{ display:block; margin: 0 auto; }}
        section[data-testid="stSidebar"] .stCaption {{ text-align:center !important; }}
        
        /* Selectbox style */
        div[data-baseweb="select"] > div {{
            border: 1px solid {SELECTBOX_BORDER_COLOR};
        }}
        
        div[data-baseweb="select"] {{
            max-width: 200px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    with st.sidebar:
        # 프로젝트 루트 경로 찾기
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        logo_path = os.path.join(root_dir, 'img', 'autok_logo.png')
        st.image(logo_path)
        st.caption("(v 1.0.0. copyright by SKN25 TEAM5)")

        if st.button("등록 현황"):
            st.switch_page("pages/main.py")
        if st.button("인구 차량 추이"):
            st.switch_page("pages/population.py")
        if st.button("정비소 인프라 현황"):
            st.switch_page("pages/repair_ratio_map.py")
        if st.button("정비소 지도"):
            st.switch_page("pages/maintenance.py")
        if st.button("정비 FAQ"):
            st.switch_page("pages/faq.py")


def render_main_box(title: str):
    st.markdown(
        f"""
        <style>
        .main-title {{
            background: {MAIN_TITLE_BG_COLOR};
            border-radius: 8px 8px 0 0;
            padding: 10px 18px;
            font-weight: 800;
            color: {MAIN_TITLE_TEXT_COLOR};
            display: inline-block;
            margin-left: 4px;
            margin-bottom: 0;
            min-width: 120px;
            text-align: center;
        }}
        
        div[data-testid="stContainer"] {{
            border-top-left-radius: 0px !important;
        }}

        div[data-testid="stVerticalBlock"] > div:has(> div[data-testid="stContainer"]) {{
            min-height: 720px;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(f"<div class='main-title'>{title}</div>", unsafe_allow_html=True)

    box = st.container(border=True)
    return box


# 도움말
def render_help_icon(
    tooltip: str,
    align: str = "left",  # left | right | center
    width: int = 20,
    margin_top: int = 10
):
    with open(IMG_PATH, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    text_align = {
        "left": "left",
        "right": "right",
        "center": "center"
    }[align]

    st.markdown(
        f"""
        <div style="text-align:{text_align};">
            <img src="data:image/png;base64,{encoded}"
                 title="{tooltip}"
                 style="width:{width}px; cursor:help; margin-top:{margin_top}px;">
        </div>
        """,
        unsafe_allow_html=True
    )

