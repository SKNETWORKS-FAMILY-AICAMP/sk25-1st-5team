import pandas as pd
import folium
from folium.plugins import MarkerCluster
from tqdm import tqdm
import os

try:
    df = pd.read_csv('repair_shop_final.csv', encoding='utf-8-sig')
except FileNotFoundError:
    print("'repair_shop_final.csv' 파일이 없음")
    exit()

df_map = df.dropna(subset=['latitude', 'longitude', 'shop_type']).copy()
df_map['shop_type'] = df_map['shop_type'].astype(int)

df_map = df_map[
    (df_map['latitude'] >= 33) & (df_map['latitude'] <= 39) &
    (df_map['longitude'] >= 124) & (df_map['longitude'] <= 132)
]
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

for idx, row in tqdm(df_map.iterrows(), total=len(df_map), desc="진행률"):
    shop_type_grade = row['shop_type']
    
    marker_color = color_map.get(shop_type_grade, 'gray') 
    type_name = type_names.get(shop_type_grade, '기타')

    popup_html = f"""
    <div style="width:200px">
        <b>업체명:</b> {row['shop_name']}<br>
        <b>유형:</b> {type_name}<br>
        <b>주소:</b> {row['소재지도로명주소'] if pd.notna(row['소재지도로명주소']) else '정보없음'}<br>
        <b>전화:</b> {row['tel'] if pd.notna(row['tel']) else '정보없음'}
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.Icon(color=marker_color, icon='info-sign'), 
        popup=folium.Popup(popup_html, max_width=300) 
    ).add_to(marker_cluster)

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

output_html_file = 'maintenance_marker_map.html'
korea_map.save(output_html_file)