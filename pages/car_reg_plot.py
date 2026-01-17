from util import get_table_df
import plotly.express as px
import pandas as pd


#테이블 가공(분기 추가 및 분기별 차량 데이터 합산)
def load_data():
    """DB에서 인구와 차량등록현황 데이터 로드"""
    df = util.get_table_df('Car_reg')
    return df

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
    df['Quarter'] = df['Month'].apply(month_to_quarter)

    

    #분기별 데이터 월별 합산 과정
    df_quarter = (
        df
        .groupby(['Year', 'Quarter', 'sido'], as_index=False)
        [['psg_car', 'van', 'truck', 'sp_car']]
        .sum()
    )

    return df_quarter





def plot_quarter_line(df_quarter: pd.DataFrame):
    """
    분기별 차량 등록 현황 꺾은선 그래프 반환
    (process.preprocess_to_quarter_df 결과를 input으로 받음)
    """

    df = df_quarter.copy()

    # 1. 연도 + 분기 컬럼 생성
    df['YearQuarter'] = df['Year'].astype(str) + ' ' + df['Quarter']

    # 2. 전국 기준 합산 (시도 무시)
    df_nation = (
        df
        .groupby('YearQuarter')[['psg_car', 'van', 'truck', 'sp_car']]
        .sum()
        .reset_index()
    )

    # 3. x축 순서 지정
    quarters_order = []
    for year in sorted(df['Year'].unique()):
        for q in ['1분기', '2분기', '3분기', '4분기']:
            quarters_order.append(f"{year} {q}")

    df_nation['YearQuarter'] = pd.Categorical(
        df_nation['YearQuarter'],
        categories=quarters_order,
        ordered=True
    )

    # 4. wide → long
    df_melt = df_nation.melt(
        id_vars='YearQuarter',
        value_vars=['psg_car', 'van', 'truck', 'sp_car'],
        var_name='CarType',
        value_name='Count'
    )

    # 5. 꺾은선 그래프
    fig = px.line(
        df_melt,
        x='YearQuarter',
        y='Count',
        color='CarType',
        markers=True,
        title='Quarterly Vehicle Registration (Nationwide)'
    )

    # ===== 스타일 =====
    fig.update_layout(
        width=1000,
        height=500,
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(size=12, color='black')
    )

    fig.update_xaxes(
        tickangle=45,
        showline=True,
        linecolor='black',
        ticks='outside',
        tickcolor='black'
    )

    fig.update_yaxes(
        showline=True,
        linecolor='black',
        ticks='outside',
        tickcolor='black'
    )

    fig.update_traces(marker=dict(size=4))

    return fig


