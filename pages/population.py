import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from components.layout import render_sidebar, render_main_box
import util
import plotly.express as px

@st.cache_data
def load_data():
    """DB에서 인구와 차량등록현황 데이터 로드"""
    pop_df = util.get_table_df('Population')
    reg_df = util.get_table_df('Car_reg')
    
    # 시도명 표준화 (로드 시점에 통일)
    sido_mapping = {
        '전라북도': '전북특별자치도'
    }
    reg_df['sido'] = reg_df['sido'].replace(sido_mapping)
    
    return pop_df, reg_df

def preprocess_data(pop_df, reg_df, sido_list=None):
    """데이터 전처리 - 지역 필터링 가능"""
    # 지역 필터링
    if sido_list:
        pop_df = pop_df[pop_df['sido'].isin(sido_list)]
        reg_df = reg_df[reg_df['sido'].isin(sido_list)]
    
    # 차량 총합 계산
    reg_df['total_car'] = reg_df['psg_car'] + reg_df['van'] + reg_df['truck'] + reg_df['sp_car']
    
    # Year-Month 컬럼 생성 및 데이터 집계
    pop_df['year_month'] = pop_df['YEAR'].astype(str) + '-' + pop_df['month'].astype(str).str.zfill(2)
    pop_grouped = pop_df.groupby('year_month')['population'].sum().reset_index()
    
    reg_df['year_month'] = reg_df['Year'].astype(str) + '-' + reg_df['Month'].astype(str).str.zfill(2)
    reg_grouped = reg_df.groupby('year_month')['total_car'].sum().reset_index()
    
    return pop_grouped, reg_grouped

def draw_population_car_plot(pop_grouped, reg_grouped):
    """인구수와 차량대수 비교 그래프 생성"""
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
            tickfont=dict(color='black'),
            showgrid=False
        ),
        yaxis=dict(
            title=dict(text='Population', font=dict(color=pastel_blue)),
            showline=True,
            linecolor=pastel_blue,
            linewidth=2,
            ticks='outside',
            tickcolor=pastel_blue,
            tickfont=dict(color=pastel_blue),
            side='left',
            showgrid=False
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
            side='right',
            showgrid=False
        ),
        legend=dict(x=0.1, y=0.9)
    )
    
    return fig

def app():
    render_sidebar()   
    box = render_main_box(title="인구 차량 추이")
    
    with box:
        pop_df, reg_df = load_data()
        
        # 그래프 상단에 지역 선택 드롭다운 추가
        sido_options = sorted(pop_df['sido'].unique().tolist())
        selected_sido = st.multiselect(
            "지역 선택",
            options=sido_options,
            default=None
        )
        
        # 필터링된 데이터로 전처리
        sido_list = selected_sido if selected_sido else None
        
        pop_grouped, reg_grouped = preprocess_data(
            pop_df.copy(), 
            reg_df.copy(), 
            sido_list=sido_list
        )

        # 그래프 그리기
        fig = draw_population_car_plot(pop_grouped, reg_grouped)
        st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    app()