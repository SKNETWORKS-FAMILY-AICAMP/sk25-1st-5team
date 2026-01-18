import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from util import get_table_df
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from components.layout import render_sidebar, render_main_box

# --------------------------------------------------
# 1. 데이터 로드 함수
# --------------------------------------------------
@st.cache_data
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
# 4. 분기별 꺾은선 그래프 함수
# --------------------------------------------------
def plot_quarter_line(df_quarter: pd.DataFrame, region: str):
    df = df_quarter.copy()
    df["YearQuarter"] = df["Year"].astype(str) + "-" + df["Quarter"]

    # 전국 / 시도 분기
    if region == "전국":
        df_plot = (
            df
            .groupby("YearQuarter")[["psg_car", "van", "truck", "sp_car"]]
            .sum()
            .reset_index()
        )
        title = "전국 분기별 차량 등록 현황"
    else:
        df_plot = df[df["sido"] == region]
        title = f"{region} 분기별 차량 등록 현황"

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

    # wide → long
    df_melt = df_plot.melt(
        id_vars="YearQuarter",
        value_vars=["psg_car", "van", "truck", "sp_car"],
        var_name="CarType",
        value_name="Count"
    )

    fig = px.line(
        df_melt,
        x="YearQuarter",
        y="Count",
        color="CarType",
        markers=True,
        title=title
    )

    # ===== ipynb와 동일한 y축 스타일 =====
    fig.update_layout(
        height=500,
        plot_bgcolor="white",
        paper_bgcolor="white",
        font=dict(color="black")
    )

    fig.update_xaxes(
        tickangle=45,
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
# 5. 분기별 Stacked Bar Plot 함수
# --------------------------------------------------
def plot_quarter_stacked_bar(df_quarter: pd.DataFrame, region: str):
    df = df_quarter.copy()
    df["YearQuarter"] = df["Year"].astype(str) + "-" + df["Quarter"]

    # 전국 / 시도 분기
    if region == "전국":
        df_plot = (
            df
            .groupby("YearQuarter")[["psg_car", "van", "truck", "sp_car"]]
            .sum()
            .reset_index()
        )
        title = "전국 분기별 차량 종류별 구성"
    else:
        df_plot = df[df["sido"] == region]
        title = f"{region} 분기별 차량 종류별 구성"

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

    # 총 대수와 비율 계산
    df_plot['total'] = df_plot['psg_car'] + df_plot['van'] + df_plot['truck'] + df_plot['sp_car']
    df_plot['psg_car_ratio'] = (df_plot['psg_car'] / df_plot['total'] * 100).round(2)
    df_plot['truck_ratio'] = (df_plot['truck'] / df_plot['total'] * 100).round(2)
    df_plot['van_ratio'] = (df_plot['van'] / df_plot['total'] * 100).round(2)
    df_plot['sp_car_ratio'] = (df_plot['sp_car'] / df_plot['total'] * 100).round(2)

    # Stacked Bar Chart 생성 - 파스텔 톤
    fig = go.Figure()

    # 가장 많은 순서부터 추가 (아래부터 위로)
    fig.add_trace(go.Bar(
        x=df_plot['YearQuarter'],
        y=df_plot['psg_car'],
        name='승용차 (psg_car)',
        marker_color='#A7C7E7',  # 파스텔 블루
        hovertemplate='<b>승용차</b><br>대수: %{y:,}<br>비율: ' + df_plot['psg_car_ratio'].astype(str) + '%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_plot['YearQuarter'],
        y=df_plot['truck'],
        name='화물차 (truck)',
        marker_color='#B4E7CE',  # 파스텔 민트
        hovertemplate='<b>화물차</b><br>대수: %{y:,}<br>비율: ' + df_plot['truck_ratio'].astype(str) + '%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_plot['YearQuarter'],
        y=df_plot['van'],
        name='승합차 (van)',
        marker_color='#FFB3D9',  # 파스텔 핑크
        hovertemplate='<b>승합차</b><br>대수: %{y:,}<br>비율: ' + df_plot['van_ratio'].astype(str) + '%<extra></extra>'
    ))

    fig.add_trace(go.Bar(
        x=df_plot['YearQuarter'],
        y=df_plot['sp_car'],
        name='특수차 (sp_car)',
        marker_color='#FFD4A3',  # 파스텔 오렌지
        hovertemplate='<b>특수차</b><br>대수: %{y:,}<br>비율: ' + df_plot['sp_car_ratio'].astype(str) + '%<extra></extra>'
    ))

    # Stacked bar로 설정 및 스타일 적용
    total_max = df_plot['total'].max()
    
    fig.update_layout(
        barmode='stack',
        title=title,
        xaxis_title='분기',
        yaxis_title='차량수',
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(color="black")
    )

    # x축, y축 선만 검정색으로 표시 (그리드 제거)
    fig.update_xaxes(
        tickangle=45,
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


# --------------------------------------------------
# 6. 레이아웃 렌더링 및 UI
# --------------------------------------------------
render_sidebar()
box = render_main_box(title="등록 현황")

with box:
    df = load_data()
    df_q = preprocess_to_quarter_df(df)
    
    # 지역과 그래프 타입 선택을 나란히 배치
    col1, col2 = st.columns(2)
    with col1:
        region = render_region_selectbox(df_q)
    with col2:
        chart_type = st.selectbox("그래프 타입", ["Line Plot", "Stacked Bar Plot"])
    
    # 선택된 그래프 타입에 따라 표시
    if chart_type == "Line Plot":
        fig = plot_quarter_line(df_q, region)
    else:
        fig = plot_quarter_stacked_bar(df_q, region)
    
    st.plotly_chart(fig, use_container_width=True)

