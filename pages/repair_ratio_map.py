import pandas as pd
import geopandas as gpd
import folium
from folium.plugins import HeatMap
import streamlit as st
import streamlit.components.v1 as components

import util
from components.layout import render_sidebar, render_main_box

st.set_page_config(page_title="정비소 비율", layout="wide")

render_sidebar()
box = render_main_box(title="정비소 인프라 현황")

# 캐싱 함수 추가 (속도)
# 차량, 정비소 데이터 캐싱
@st.cache_data(show_spinner=False)
def load_db():
    car_df = util.get_table_df("Car_reg")
    shop_df = util.get_table_df("Repair_shop")
    return car_df, shop_df

# 행정구역 
@st.cache_data(show_spinner=False)
def load_geojson():
    gdf = gpd.read_file(
        "https://raw.githubusercontent.com/vuski/admdongkor/master/ver20230701/HangJeongDong_ver20230701.geojson"
    )
    return gdf

# 데이터 처리
@st.cache_data(show_spinner=False)
def preprocess(car_df, shop_df):
    # 차량 데이터 (2025년 12월)
    car_df = car_df[
        (car_df["Year"] == 2025) &
        (car_df["Month"] == 12)
    ]

    # 총 차량 수 
    car_df["car_cnt"] = (
        car_df["psg_car"].fillna(0)
        + car_df["van"].fillna(0)
        + car_df["truck"].fillna(0)
        + car_df["sp_car"].fillna(0)
    )

    # 시도, 구군별로 차량 수 합계
    car_region = (
        car_df
        .groupby(["sido", "gugun"], as_index=False)["car_cnt"]
        .sum()
    )

    # 정비소 (폐업 제외)
    shop_df = shop_df[shop_df["end_date"].isna()]

    # 시도, 구군별로 정비소 수 합계
    repair_region = (
        shop_df
        .groupby(["sido", "gugun"])
        .size()
        .reset_index(name="repair_cnt")
    )

    # 정비소, 차량 merge
    merged = pd.merge(
        car_region,
        repair_region,
        on=["sido", "gugun"],
        how="left"
    )
    merged["repair_cnt"] = merged["repair_cnt"].fillna(0)

    # 정비소 1개 당 차량 수 계산 
    merged["car_per_repair"] = merged.apply(
        lambda r: r["car_cnt"] / r["repair_cnt"]
        if r["repair_cnt"] > 0 else float("inf"),
        axis=1
    )

    # 분위 계산
    valid = merged[merged["repair_cnt"] > 0]
    q75 = valid["car_per_repair"].quantile(0.75) # 상위 25%
    q90 = valid["car_per_repair"].quantile(0.90) # 상위 10%

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
    return merged, q75, q90, shop_df

# 지도 생성
@st.cache_resource(show_spinner=False)
def make_map(_map_gdf, shop_df):
    m = folium.Map(
        location=[36.5, 127.8], # 한국 중앙에서 지도 시작
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

    geo_layer = folium.FeatureGroup(
        name="정비소 부족 단계 (구군별)",
        show=True
    )

    folium.GeoJson(
        _map_gdf,
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

    heat_layer = folium.FeatureGroup(name="정비소 밀도 HeatMap", show=False)

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

    return m

# 화면
with box:
    # 지도, 표 선택
    view_mode = st.radio(
        "보기 방식 선택",
        ["🗺 지도 보기", "📊 표로 보기"],
        horizontal=True
    )

    # 행정구역 json 정규화 (수원시팔달구 -> 수원시)
    def normalize_gugun(name):
        if isinstance(name, str) and name.endswith("구") and "시" in name:
            return name[:name.find("시") + 1]
        return name

    # 데이터 로드 
    car_df, shop_df = load_db()
    merged, q75, q90, shop_df = preprocess(car_df, shop_df)

    # 지도 선택 시
    if view_mode == "🗺 지도 보기":
        gdf = load_geojson()
        gdf["sido"] = gdf["sidonm"]
        gdf["gugun"] = gdf["sggnm"].apply(normalize_gugun)

        map_gdf = gdf.merge(
            merged,
            on=["sido", "gugun"],
            how="left"
        )

        map_gdf["repair_cnt"] = map_gdf["repair_cnt"].fillna(0)

        m = make_map(map_gdf, shop_df)

        components.html(
            m.get_root().render(),
            height=650,
            scrolling=False
        )

    # 표 선택 시
    else:
        st.subheader("📊 시도별 정비소 부족 요약")

        base = merged[merged["repair_cnt"] > 0]

        summary = (
            base
            .groupby("sido")
            .agg(
                total_car=("car_cnt", "sum"),
                repair_shop_cnt=("repair_cnt", "sum"),
                avg_car_per_repair=("car_per_repair", "mean"),
            )
            .reset_index()
        )

        summary["q75_over_cnt"] = (
            base.groupby("sido")["car_per_repair"]
            .apply(lambda x: (x >= q75).sum())
            .values
        )

        summary["q90_over_cnt"] = (
            base.groupby("sido")["car_per_repair"]
            .apply(lambda x: (x >= q90).sum())
            .values
        )

        def classify_sido(row):
            if row["q90_over_cnt"] > 2:
                return "심각"
            elif row["q75_over_cnt"] > 2:
                return "주의"
            else:
                return "정상"

        summary["lack_grade"] = summary.apply(classify_sido, axis=1)
        summary["avg_car_per_repair"] = summary["avg_car_per_repair"].round(1)

        summary_display = summary.rename(columns={
            "sido": "지역",
            "total_car": "총 차량 대수",
            "repair_shop_cnt": "정비소 수",
            "avg_car_per_repair": "평균 차량 대비 정비소",
            "q75_over_cnt": "상위 25% 기준 시군구 수",
            "q90_over_cnt": "상위 10% 기준 시군구 수",
            "lack_grade": "정비소 부족 등급"
        })

        st.dataframe(summary_display, use_container_width=True)
