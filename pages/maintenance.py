import sys
import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import util
from components.layout import render_sidebar, render_main_box, render_help_icon


# --------------------------------------------------
# 1. 데이터 로드 함수
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def load_repair_shop_data():
    return util.get_table_df('Repair_shop')

# --------------------------------------------------
# 2. 데이터 전처리 함수
# --------------------------------------------------
def preprocess_repair_data(df: pd.DataFrame) -> pd.DataFrame:
    """정비소 데이터 전처리 및 필터링"""
    df_map = df.dropna(subset=['latitude', 'longitude', 'shop_type']).copy()
    df_map['shop_type'] = df_map['shop_type'].astype(int)
    
    # 한국 영역 필터링
    df_map = df_map[
        (df_map['latitude'] >= 33) & (df_map['latitude'] <= 39) &
        (df_map['longitude'] >= 124) & (df_map['longitude'] <= 132)
    ]
    
    return df_map


# --------------------------------------------------
# 3. 지도 생성 함수
# --------------------------------------------------
def create_maintenance_map(df_map: pd.DataFrame) -> folium.Map:
    """정비소 위치 지도 생성"""
    korea_map = folium.Map(location=[36.5, 127.5], zoom_start=7)
    marker_cluster = MarkerCluster().add_to(korea_map)
    
    color_map = {
        1: 'green',
        2: 'blue',
        3: 'orange',
        4: 'red'
    }
    
    type_names = {
        1: '자동차종합정비업(1급)',
        2: '소형자동차정비업(2급)',
        3: '자동차전문정비업(3급)',
        4: '원동기전문정비업(4급)'
    }
    
    # 마커 추가
    for idx, row in df_map.iterrows():
        shop_type_grade = row['shop_type']
        marker_color = color_map.get(shop_type_grade, 'gray')
        type_name = type_names.get(shop_type_grade, '기타')
        
        popup_html = f"""
        <div style="width:200px">
            <b>업체명:</b> {row['shop_name']}<br>
            <b>유형:</b> {type_name}<br>
            <b>주소:</b> {row['road_addr'] if pd.notna(row['road_addr']) else '정보없음'}<br>
            <b>전화:</b> {row['tel'] if pd.notna(row['tel']) else '정보없음'}
        </div>
        """
        
        folium.Marker(
            location=[row['latitude'], row['longitude']],
            icon=folium.Icon(color=marker_color, icon='info-sign'),
            popup=folium.Popup(popup_html, max_width=300)
        ).add_to(marker_cluster)
    
    # 범례 추가
    legend_html = '''
         <div style="position: fixed; 
                     top: 20px; right: 20px; width: 220px; height: 130px; 
                     background-color: white; border:2px solid grey; z-index:9999; font-size:13px;
                     padding: 10px; line-height: 1.6;">
         <b style="font-size:14px;">자동차정비업 종류 (시행령)</b><br>
         <i class="fa fa-map-marker" style="color:green"></i> 1급: 자동차종합정비업<br>
         <i class="fa fa-map-marker" style="color:blue"></i> 2급: 소형자동차정비업<br>
         <i class="fa fa-map-marker" style="color:orange"></i> 3급: 자동차전문정비업<br>
         <i class="fa fa-map-marker" style="color:red"></i> 4급: 원동기전문정비업<br>
         </div>
         '''
    korea_map.get_root().html.add_child(folium.Element(legend_html))
    
    return korea_map


# --------------------------------------------------
# 4. 레이아웃 렌더링 및 UI
# --------------------------------------------------
render_sidebar()
box = render_main_box(title="정비소 위치")

with box:
    render_help_icon("정비소 위치를 지도에 시각화합니다.\n마커를 클릭하면 정비소 정보를 확인할 수 있습니다.", align="right")
    df = load_repair_shop_data()
    
    if df is not None:
        df_map = preprocess_repair_data(df)
        
        with st.spinner("정비소 지도를 불러오는 중..."):
            korea_map = create_maintenance_map(df_map)
        
        # Streamlit에서 지도 표시
        folium_static(korea_map, width=1200, height=600)