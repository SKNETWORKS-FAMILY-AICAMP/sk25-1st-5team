from ctypes import util
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import util
import plotly.express as px

def load_data():
    """DB에서 인구와 차량등록현황 데이터 로드"""
    pop_df = util.get_table_df('Population')
    reg_df = util.get_table_df('Car_reg')
    return pop_df, reg_df

def preprocess_data(pop_df, reg_df):
    """데이터 전처리"""
    # 차량 총합 계산
    reg_df['total_car'] = reg_df['psg_car'] + reg_df['van'] + reg_df['truck'] + reg_df['sp_car']
    
    # Year-Month 컬럼 생성 및 데이터 집계
    pop_df['year_month'] = pop_df['YEAR'].astype(str) + '-' + pop_df['month'].astype(str).str.zfill(2)
    pop_grouped = pop_df.groupby('year_month')['population'].sum().reset_index()
    
    reg_df['year_month'] = reg_df['Year'].astype(str) + '-' + reg_df['Month'].astype(str).str.zfill(2)
    reg_grouped = reg_df.groupby('year_month')['total_car'].sum().reset_index()
    
    return pop_grouped, reg_grouped


def draw_population_car_plot(pop_grouped, reg_grouped):
    # 색상
    pastel_blue = '#6BA3D1'
    pastel_red = '#FF6B6B'
    
    # Multiple y axes line plot
    fig = px.line()
    fig.add_scatter(x=pop_grouped['year_month'], y=pop_grouped['population'], 
                    mode='lines+markers', name='Population', yaxis='y1',
                    line=dict(color=pastel_blue), marker=dict(color=pastel_blue))
    fig.add_scatter(x=reg_grouped['year_month'], y=reg_grouped['total_car'], 
                    mode='lines+markers', name='Total Cars', yaxis='y2',
                    line=dict(color=pastel_red), marker=dict(color=pastel_red))
    
    fig.update_layout(
        title='Population and Total Cars Over Year-Month',
        plot_bgcolor='white',
        paper_bgcolor='white',
        xaxis=dict(
            title='Year-Month',
            showline=True,
            linecolor='black',
            linewidth=2,
            ticks='outside',
            tickcolor='black',
            tickfont=dict(color='black')
        ),
        yaxis=dict(
            title=dict(text='Population', font=dict(color=pastel_blue)),
            showline=True,
            linecolor=pastel_blue,
            linewidth=2,
            ticks='outside',
            tickcolor=pastel_blue,
            tickfont=dict(color=pastel_blue),
            side='left'
        ),
        yaxis2=dict(
            title=dict(text='Total Cars', font=dict(color=pastel_red)),
            showline=True,
            linecolor=pastel_red,
            linewidth=2,
            ticks='outside',
            tickcolor=pastel_red,
            tickfont=dict(color=pastel_red),
            overlaying='y',
            side='right'
        ),
        legend=dict(x=0.1, y=0.9)
    )
    
    return fig


def test_monthly_anomalies(pop_df):
    """월별 인구수 데이터 이상값 테스트"""
    import pandas as pd
    
    pop_df['year_month'] = pop_df['YEAR'].astype(str) + '-' + pop_df['month'].astype(str).str.zfill(2)
    
    # 각 년-월별 데이터 개수 확인
    print("데이터 개수:", pop_df.groupby('year_month').size())
    
    # 2021년 2월-3월 비교
    print("\n" + "=" * 50)
    print("2021년 2월 vs 3월 비교")
    print("=" * 50)
    feb_2021 = pop_df[pop_df['year_month'] == '2021-02'].groupby(['sido', 'age_group'])['population'].sum().reset_index()
    mar_2021 = pop_df[pop_df['year_month'] == '2021-03'].groupby(['sido', 'age_group'])['population'].sum().reset_index()
    
    test_df = feb_2021.merge(mar_2021, on=['sido', 'age_group'], suffixes=('_feb', '_mar'))
    test_df['diff'] = test_df['population_mar'] - test_df['population_feb']
    test_df['diff_abs'] = test_df['diff'].abs()
    test_df = test_df.sort_values('diff_abs', ascending=False)
    
    pd.set_option('display.max_columns', None)
    print("[상위 10개 차이]:", test_df.head(10))
    
    # 2022년 8월-9월 비교
    aug_2022 = pop_df[pop_df['year_month'] == '2022-08'].groupby(['sido', 'age_group'])['population'].sum().reset_index()
    sep_2022 = pop_df[pop_df['year_month'] == '2022-09'].groupby(['sido', 'age_group'])['population'].sum().reset_index()
    
    test_df2 = aug_2022.merge(sep_2022, on=['sido', 'age_group'], suffixes=('_aug', '_sep'))
    test_df2['diff'] = test_df2['population_sep'] - test_df2['population_aug']
    test_df2['diff_abs'] = test_df2['diff'].abs()
    test_df2 = test_df2.sort_values('diff_abs', ascending=False)
    
    print("[상위 10개 차이]:", test_df2.head(10))
    print("\n")


def main():
    """메인 함수. 그래프 생성 및 데이터 이상값 테스트"""
    # 데이터 로드
    pop_df, reg_df = load_data()
    pop_grouped, reg_grouped = preprocess_data(pop_df, reg_df)
    
    # 그래프 생성
    fig = draw_population_car_plot(pop_grouped, reg_grouped)
    fig.show()
    
    # 월별 이상값 테스트
    test_monthly_anomalies(pop_df)

if __name__ == "__main__":
    main()