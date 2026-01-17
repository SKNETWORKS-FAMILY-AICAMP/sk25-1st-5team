import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import streamlit as st
import streamlit.components.v1 as components
import util  

# 행정구역 json 정규화 
def normalize_gugun(name):
    if isinstance(name, str) and name.endswith("구") and "시" in name:
        return name[:name.find("시") + 1]
    return name

# db load
car_df = util.get_table_df("Car_reg")
shop_df = util.get_table_df("Repair_shop")

# 지역별 차량 수 
car_df = car_df[
    (car_df["Year"] == 2025) &
    (car_df["Month"] == 12)
]

car_df["car_cnt"] = (
    car_df["psg_car"].fillna(0)
    + car_df["van"].fillna(0)
    + car_df["truck"].fillna(0)
    + car_df["sp_car"].fillna(0)
)

car_region = (
    car_df
    .groupby(["sido", "gugun"], as_index=False)["car_cnt"]
    .sum()
)

# 정비소 (폐업 제외)
shop_df = shop_df[shop_df["end_date"].isna()]

repair_region = (
    shop_df
    .groupby(["sido", "gugun"])
    .size()
    .reset_index(name="repair_cnt")
)


merged = pd.merge(
    car_region,
    repair_region,
    on=["sido", "gugun"],
    how="left"
)

merged["repair_cnt"] = merged["repair_cnt"].fillna(0)

merged["car_per_repair"] = merged.apply(
    lambda r: r["car_cnt"] / r["repair_cnt"] if r["repair_cnt"] > 0 else float("inf"),
    axis=1
)

# 분위수
valid = merged[merged["repair_cnt"] > 0]
q75 = valid["car_per_repair"].quantile(0.75)
q90 = valid["car_per_repair"].quantile(0.90)

def classify(row):
    if row["repair_cnt"] == 0:
        return "정비소 없음"
    elif row["car_per_repair"] >= q90:
        return "심각"
    elif row["car_per_repair"] >= q75:
        return "부족"
    else:
        return "보통"

merged["lack_level"] = merged.apply(classify, axis=1)

#geojson load
gdf = gpd.read_file(
    "https://raw.githubusercontent.com/vuski/admdongkor/master/ver20230701/HangJeongDong_ver20230701.geojson"
)

gdf["sido"] = gdf["sidonm"]
gdf["gugun"] = gdf["sggnm"].apply(normalize_gugun)

map_gdf = gdf.merge(
    merged,
    on=["sido", "gugun"],
    how="left"
)

map_gdf["repair_cnt"] = map_gdf["repair_cnt"].fillna(0)

# 지도 생성
m = folium.Map(
    location=[36.5, 127.8],
    zoom_start=7,
    tiles="OpenStreetMap"
)

def color_fn(feature):
    return {
        "정비소 없음": "#000000",
        "심각": "#800026",
        "부족": "#FD8D3C",
        "보통": "#FED976",
    }.get(feature["properties"]["lack_level"], "#DDDDDD")

#geojson layer
geo_layer = folium.FeatureGroup(
    name="정비소 부족 단계 (구군별)",
    show=True
)

folium.GeoJson(
    map_gdf,
    style_function=lambda f: {
        "fillColor": color_fn(f),
        "color": None,
        "weight": 0.2,
        "fillOpacity": 0.45
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["sido", "gugun", "car_cnt", "repair_cnt", "lack_level"],
        aliases=["시도", "구군", "차량 수", "정비소 수", "부족 단계"]
    )
).add_to(geo_layer)

geo_layer.add_to(m)

# heatmap layer
heat_layer = folium.FeatureGroup(
    name="정비소 밀도 HeatMap",
    show=False
)

HeatMap(
    shop_df[["latitude", "longitude"]]
    .dropna()
    .values
    .tolist(),
    radius=8,
    blur=12,
    min_opacity=0.4
).add_to(heat_layer)

heat_layer.add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

# 범례
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("⬛ **정비소 없음**")
with col2:
    st.markdown("🟥 **심각** (상위 10%)")
with col3:
    st.markdown("🟧 **부족** (상위 25%)")
with col4:
    st.markdown("🟨 **보통**")



# streamlit 출력
html = m.get_root().render()

components.html(
    html,
    height=650,
    scrolling=False
)
