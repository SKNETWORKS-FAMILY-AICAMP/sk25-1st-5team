import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util import get_table_df
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from components.layout import render_sidebar, render_main_box

# color settings
pastel_blue = '#6BA3D1'
pastel_red = '#FF6B6B'
pastel_yellow = '#FFE66D'
pastel_green = '#A8E6A1'

COLOR_MAP = {
    'psg_car': pastel_blue,
    'van': pastel_yellow,
    'truck': pastel_red,
    'sp_car': pastel_green
}

LABEL_MAP = {
    'psg_car': '승용차',
    'van': '승합차',
    'truck': '화물차',
    'sp_car': '특수차'
}

# --------------------------------------------------
# 1. 데이터 로드 함수
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    """DB에서 차량 등록 데이터 로드"""
    return get_table_df("Car_reg")

# --------------------------------------------------
# 2. Streamlit selectbox 생성 함수
# --------------------------------------------------
def render_region_selectbox(df: pd.DataFrame) -> str:
    """
    시도 선택 selectbox 렌더링
    - 하드코딩 없이 df 기준으로 생성
    """
    sido_list = sorted(df["sido"].dropna().unique().tolist())
    options = ["전국"] + sido_list

    return st.selectbox("지역 선택", options)


# --------------------------------------------------
# 3. 분기 단위 데이터 가공 함수
# --------------------------------------------------
def preprocess_to_quarter_df(df: pd.DataFrame) -> pd.DataFrame:
    def month_to_quarter(month):
        if month in [1, 2, 3]:
            return '1분기'
        elif month in [4, 5, 6]:
            return '2분기'
        elif month in [7, 8, 9]:
            return '3분기'
        else:
            return '4분기'

    df = df.copy()
    df["Quarter"] = df["Month"].apply(month_to_quarter)

    df_quarter = (
        df
        .groupby(["Year", "Quarter", "sido"], as_index=False)
        [["psg_car", "van", "truck", "sp_car"]]
        .sum()
    )

    return df_quarter


# --------------------------------------------------
# 4. 공통 데이터 전처리 함수
# --------------------------------------------------
def prepare_quarter_data(df_quarter: pd.DataFrame, region: str) -> tuple[pd.DataFrame, str]:
    """
    분기별 데이터를 그래프용으로 전처리
    Returns: (전처리된 데이터프레임, 그래프 제목)
    """
    df = df_quarter.copy()
    df["YearQuarter"] = df["Year"].astype(str) + "-" + df["Quarter"]

    # 전국 / 시도 필터링 및 집계
    if region == "전국":
        df_plot = (
            df
            .groupby("YearQuarter")[["psg_car", "van", "truck", "sp_car"]]
            .sum()
            .reset_index()
        )
    else:
        df_plot = df[df["sido"] == region]

    # x축 순서 보정
    quarters_order = [
        f"{year}-{q}"
        for year in sorted(df["Year"].unique())
        for q in ["1분기", "2분기", "3분기", "4분기"]
    ]

    df_plot["YearQuarter"] = pd.Categorical(
        df_plot["YearQuarter"],
        categories=quarters_order,
        ordered=True
    )
    df_plot = df_plot.sort_values("YearQuarter")

    return df_plot


# --------------------------------------------------
# 5. 분기별 꺾은선 그래프 함수
# --------------------------------------------------
def plot_quarter_line(df_quarter: pd.DataFrame, region: str):
    df_plot = prepare_quarter_data(df_quarter, region)
    title = "전국 분기별 차량 등록 현황" if region == "전국" else f"{region} 분기별 차량 등록 현황"

    # wide → long
    df_melt = df_plot.melt(
        id_vars="YearQuarter",
        value_vars=["psg_car", "van", "truck", "sp_car"],
        var_name="CarType",
        value_name="Count"
    )

    df_melt['CarTypeLabel'] = df_melt['CarType'].map(LABEL_MAP)

    # 범례 순서
    category_orders = ['psg_car', 'truck', 'van', 'sp_car']
    df_melt['CarType'] = pd.Categorical(
        df_melt['CarType'],
        categories=category_orders,
        ordered=True
    )

    fig = px.line(
        df_melt,
        x="YearQuarter",
        y="Count",
        color="CarType",
        markers=True,
        title=title,
        color_discrete_map=COLOR_MAP,
        labels={
            'CarType': '차량 종류',
            'YearQuarter': '분기',
            'Count': '대수'
        }
    )
    
    # 범례 이름, 호버 템플릿 수정
    for trace in fig.data:
        car_type_key = trace.name
        car_type_label = LABEL_MAP.get(car_type_key, car_type_key)
        trace.name = car_type_label
        trace.hovertemplate = '<b>' + car_type_label + '</b><br>분기: %{x}<br>대수: %{y:,}<extra></extra>'

    # ===== ipynb와 동일한 y축 스타일 =====
    fig.update_layout(
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="black"),
        legend_title_text="차량 종류"  # 범례 타이틀 추가
    )

    fig.update_xaxes(
        tickangle=90,
        showline=True,
        linecolor="black",
        ticks="outside",
        tickcolor="black"
    )

    fig.update_yaxes(
        showline=True,
        linecolor="black",
        ticks="outside",
        tickcolor="black"
    )

    fig.update_traces(marker=dict(size=4))

    return fig

# --------------------------------------------------
# 6. 분기별 스택형 막대 그래프 함수
# --------------------------------------------------
def plot_quarter_stacked_bar(df_quarter: pd.DataFrame, region: str):
    """분기별 데이터로 stacked bar plot 생성"""
    df_plot = prepare_quarter_data(df_quarter, region)
    title = "전국 분기별 차량 종류별 구성" if region == "전국" else f"{region} 분기별 차량 종류별 구성"

    # 총 대수 및 비율 계산
    df_plot['total'] = df_plot['psg_car'] + df_plot['van'] + df_plot['truck'] + df_plot['sp_car']
    df_plot['psg_car_ratio'] = (df_plot['psg_car'] / df_plot['total'] * 100).round(2)
    df_plot['truck_ratio'] = (df_plot['truck'] / df_plot['total'] * 100).round(2)
    df_plot['van_ratio'] = (df_plot['van'] / df_plot['total'] * 100).round(2)
    df_plot['sp_car_ratio'] = (df_plot['sp_car'] / df_plot['total'] * 100).round(2)

    fig = go.Figure()

    car_types = ['psg_car', 'truck', 'van', 'sp_car']
    
    for car_type in car_types:
        fig.add_trace(go.Bar(
            x=df_plot['YearQuarter'],
            y=df_plot[car_type],
            name=LABEL_MAP[car_type],
            marker_color=COLOR_MAP[car_type],
            hovertemplate=(
                f'<b>{LABEL_MAP[car_type]}</b><br>'
                '분기: %{x}<br>'
                '대수: %{y:,}<br>'
                '비율: ' + df_plot[f'{car_type}_ratio'].astype(str) + '%<br>'
                '총 차량대수: ' + df_plot['total'].apply(lambda x: f'{x:,}').astype(str) + 
                '<extra></extra>'
            )
        ))

    # Stacked bar 설정 및 스타일 적용
    fig.update_layout(
        barmode='stack',
        title=title,
        xaxis_title='분기',
        yaxis_title='차량수',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="black"),
        legend_title_text="차량 종류",
        legend=dict(traceorder='normal')
    )

    fig.update_xaxes(
        tickangle=90,
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor='black',
        ticks="outside",
        tickcolor="black"
    )
    fig.update_yaxes(
        showgrid=False,
        showline=True,
        linewidth=2,
        linecolor='black',
        ticks="outside",
        tickcolor="black"
    )

    return fig

# main app rendering
render_sidebar()
box = render_main_box(title="등록 현황")

with box:
    df = load_data()
    df_q = preprocess_to_quarter_df(df)
    
    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        region = render_region_selectbox(df_q)
    with col2:
        chart_type = st.selectbox("그래프 타입", ["Line Plot", "Stacked Bar Plot"])
    
    if chart_type == "Line Plot":
        fig = plot_quarter_line(df_q, region)
    else:
        fig = plot_quarter_stacked_bar(df_q, region)
    
    st.plotly_chart(fig)