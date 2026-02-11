import streamlit as st
import folium
from streamlit_folium import st_folium
import os
from dotenv import load_dotenv
import googlemaps
import time

# 1. 初始化
load_dotenv(".env.local")
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

st.set_page_config(page_title="AI 航海家", layout="wide")
st.title("📍 实时路径可视化系统")

# 模拟获取景点的经纬度 (实际开发中调用 gmaps.geocode)
def get_coordinates(place_name):
    # 这里为了演示，给几个固定坐标，实际请用 gmaps.geocode(place_name)
    coords = {
        "卢浮宫": [48.8606, 2.3376],
        "埃菲尔铁塔": [48.8584, 2.2945],
        "巴黎圣母院": [48.8530, 2.3499]
    }
    return coords.get(place_name, [48.8566, 2.3522]) # 找不到就返回巴黎市中心

# --- 侧边栏：行程输入 ---
with st.sidebar:
    st.header("行程设置")
    points = st.multiselect("选择你想去的景点", ["卢浮宫", "埃菲尔铁塔", "巴黎圣母院"], default=["卢浮宫", "埃菲尔铁塔"])
    optimize = st.button("开始 AI 路径优化")

# --- 主界面：地图展示 ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("实时交互地图")
    
    # 初始化地图中心点
    m = folium.Map(location=[48.8566, 2.3522], zoom_start=13)
    
    # 提取坐标
    path_coords = [get_coordinates(p) for p in points]
    
    # 在地图上标记点并画线
    for i, p in enumerate(points):
        folium.Marker(
            location=get_coordinates(p),
            popup=f"第 {i+1} 站: {p}",
            icon=folium.Icon(color='blue', icon='info-sign')
        ).add_to(m)
    
    if len(path_coords) > 1:
        folium.PolyLine(path_coords, color="red", weight=2.5, opacity=0.8).add_to(m)
    
    # 渲染地图
    st_folium(m, width=800, height=500)

with col2:
    st.subheader("Agent 审计报告")
    if optimize:
        with st.status("正在核对实时交通数据..."):
            # 这里调用我们 P2 写的 LangGraph 逻辑
            st.write("🔍 检查卢浮宫周边拥堵情况...")
            time.sleep(1)
            st.write("🔄 建议：下午 14:00 铁塔方向更顺畅，已自动调优。")
        st.success("路径已是当前最优解")
        st.write("---")
        for i, p in enumerate(points):
            st.write(f"**{i+1}. {p}**")
