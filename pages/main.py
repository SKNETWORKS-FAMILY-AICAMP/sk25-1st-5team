from util import get_table_df
import plotly.express as px
import pandas as pd
from components.layout import render_sidebar, render_main_box
import streamlit as st

render_sidebar()
box = render_main_box(title="등록 현황")

with box:

    # --------------------------------------------------
    # 1. 데이터 로드 함수
    # --------------------------------------------------
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


    df = load_data()
    df_q = preprocess_to_quarter_df(df)
    region = render_region_selectbox(df_q)
    fig = plot_quarter_line(df_q, region)
    st.plotly_chart(fig)

