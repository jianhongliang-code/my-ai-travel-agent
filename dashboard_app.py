import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import random
import time
import asyncio
# Import local agent graph for simulation
try:
    from agent_graph import graph_app
except ImportError:
    graph_app = None

# Page Configuration
st.set_page_config(
    page_title="AI Travel Agent - B端计调工作台 (P3 Beta)",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Session State Init ---
if 'deadlock_triggered' not in st.session_state:
    st.session_state['deadlock_triggered'] = False

# --- 1. Data Loading & Enrichment ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('travel_data_p3_refined.csv')
    except FileNotFoundError:
        # Fallback if P3 data missing
        df = pd.DataFrame({
            'aesthetic_score': np.random.normal(7, 1, 100),
            'profit_margin': np.random.normal(0.2, 0.05, 100),
            'agent_version': ['v1-balanced']*100,
            'plan_id': [str(i) for i in range(100)],
            'net_profit': np.random.randint(100, 1000, 100),
            'user_segment': ['standard']*100
        })
    
    # Mocking new KPIs for the dashboard
    np.random.seed(42)
    df['pareto_health'] = df.apply(lambda x: min(100, int((x['aesthetic_score'] * 10 + x['profit_margin'] * 100) / 1.5)), axis=1)
    df['inventory_match'] = np.random.randint(40, 95, len(df))
    df['audit_recurrence'] = np.random.randint(0, 5, len(df))
    df['mood_consistency'] = df['aesthetic_score'].apply(lambda x: min(10, x + np.random.normal(0, 0.5)))
    df['golden_hour_coverage'] = np.random.uniform(0.1, 0.8, len(df))
    df['fatigue_index'] = np.random.choice(['Low', 'Medium', 'High'], len(df))
    df['congestion_risk'] = np.random.uniform(0, 0.4, len(df))
    df['buffer_flexibility'] = np.random.randint(10, 30, len(df)) # minutes
    
    return df

df = load_data()

# --- 2. Top Status Bar (Simulated) ---
col_t1, col_t2, col_t3, col_t4 = st.columns([1, 1, 4, 2])
with col_t1:
    st.markdown("🚦 **交通预警**: <span style='color:green'>正常</span>", unsafe_allow_html=True)
with col_t2:
    st.markdown("🌦️ **天气状况**: <span style='color:orange'>局部阵雨</span>", unsafe_allow_html=True)
with col_t3:
    st.markdown("**当前任务**: 正在处理 P3 阶段高净值客户方案 (ID: 8821-X)")
with col_t4:
    # 需求 2：流式生成占位符
    if st.button("🔄 刷新数据流"):
        if graph_app:
            with st.status("AI Agent 正在协作中 (Real-time LangGraph)...", expanded=True) as status:
                async def run_agent_stream():
                    inputs = {
                        "user_request": "Refine itinerary for high-net-worth client",
                        "iteration_count": 0,
                        "errors": [],
                        "messages": []
                    }
                    # Run the graph
                    async for event in graph_app.astream(inputs, stream_mode="updates"):
                        node_name = list(event.keys())[0]
                        data = event[node_name]
                        
                        if node_name == "planner":
                            st.write("🗺️ **Planner**: 已生成初始行程草案...")
                            st.caption(f"包含 {len(data['itinerary'])} 个节点")
                        elif node_name == "auditor":
                            if data.get("errors"):
                                st.write(f"🔍 **Auditor**: ⚠️ 发现 {len(data['errors'])} 个逻辑冲突!")
                            else:
                                st.write("🔍 **Auditor**: ✅ 行程逻辑校验通过")
                        elif node_name == "commercial_arbiter":
                            st.write(f"⚖️ **Arbiter**: 最终定价完成 (Profit: {data['profit_margin']}%)")
                        
                        # Simulate a tiny bit of delay for visual pacing if needed, 
                        # though the nodes themselves have sleep.
                
                # Run the async function
                try:
                    asyncio.run(run_agent_stream())
                except RuntimeError:
                    # Fallback for environments with running loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(run_agent_stream())
                    loop.close()
                
                status.update(label="数据流已更新！", state="complete", expanded=False)
            st.toast("数据流已刷新 (Powered by LangGraph)", icon="✅")
        else:
            # Fallback if graph_app not loaded
            with st.status("AI Agent 正在协作中...", expanded=True) as status:
                st.write("🔍 Auditor Agent: 正在扫描实时路况...")
                time.sleep(1)
                st.write("🚦 Risk Manager: 检测到 Day 3 拥堵风险...")
                time.sleep(0.8)
                st.write("✨ Aesthetic Scorer: 正在重新计算黄金时刻...")
                time.sleep(0.5)
                status.update(label="数据流已更新！", state="complete", expanded=False)
            st.toast("数据流已刷新", icon="✅")

st.divider()

# --- 3. Sidebar: Quick Selection (Pareto View) ---
with st.sidebar:
    st.title("🎛️ 计调控制台")
    
    st.subheader("快速择优 (Pareto View)")
    # Scatter Plot for Sidebar
    fig_sidebar = px.scatter(
        df, 
        x="aesthetic_score", 
        y="profit_margin", 
        color="agent_version",
        hover_data=["plan_id", "net_profit"],
        title="方案分布 (左侧导航)",
        labels={"aesthetic_score": "审美分", "profit_margin": "利润率"},
        height=400
    )
    fig_sidebar.update_layout(margin=dict(l=0, r=0, t=30, b=0), showlegend=False)
    # Highlight Frontier (Mock)
    st.plotly_chart(fig_sidebar, use_container_width=True)
    
    st.info("💡 提示: 点击左侧散点可快速定位高潜方案。")

# --- 4. Main Layout (Center + Right Panel) ---
col_main, col_right = st.columns([3, 1])

# --- Right Control Panel ---
with col_right:
    # 需求 1：Inspiration Agent 模拟
    with st.expander("🎨 灵感输入 (Inspiration)", expanded=True):
        uploaded_file = st.file_uploader("拖入图片定义风格", type=['jpg', 'png', 'jpeg'])
        if uploaded_file is not None:
            st.success("图片识别成功！")
            st.markdown("""
            **视觉标签识别**:
            - `#圣托里尼风` (Confidence: 98%)
            - `#蓝白影调` (Confidence: 92%)
            - `#高饱和度` (Confidence: 85%)
            """)
            st.info("🧠 User Vector 已更新: aesthetic_weight +0.15")

    st.subheader("⚙️ 策略调控")
    st.caption("根据客户反馈实时调整 AI 倾向")
    
    with st.container(border=True):
        st.markdown("**权重滑块**")
        aesthetic_weight = st.slider("Aesthetic (审美)", 0, 100, 70)
        profit_weight = st.slider("Profit (利润)", 0, 100, 30)
        st.progress(aesthetic_weight / (aesthetic_weight + profit_weight + 0.1))
        
    with st.container(border=True):
        st.markdown("**路由干预**")
        st.checkbox("强制锁定 v2 (高净值)", value=True)
        st.checkbox("开启 v3 阶梯惩罚", value=True)
    
    # 需求 3：异常处理 UI
    st.markdown("---")
    st.subheader("⚠️ 异常测试")
    if st.button("🔴 触发博弈死循环"):
        st.session_state['deadlock_triggered'] = True
    
    st.markdown("---")
    st.metric("当前模型版本", "v3.1-Beta")
    with st.expander("🛠️ 开发者模式 / 架构"):
        st.caption("生产环境建议架构：")
        st.markdown("""
        **Frontend**: React/Vue + EventSource  
        **Backend**: FastAPI + LangGraph  
        **Protocol**: Server-Sent Events (SSE)
        """)
        st.markdown("**本地演示文件**:")
        st.markdown("- `backend_api.py`: FastAPI SSE 服务")
        st.markdown("- `frontend_demo.html`: 前端流式演示")
        st.markdown("- `agent_graph.py`: LangGraph 逻辑定义")
        st.warning("提示: 运行 `python backend_api.py` 后打开 html 文件即可体验完整 SSE 架构。")

# --- Center Canvas ---
with col_main:
    # 异常处理：Human-in-the-loop 对话框
    if st.session_state['deadlock_triggered']:
        with st.container(border=True):
            st.error("🛑 **System Alert: 检测到逻辑死循环**")
            st.markdown("""
            **Auditor** 与 **Planner** 在 `[Day 3: 圣家堂]` 节点发生 3 次以上冲突，无法自动收敛。
            
            - **冲突原因**: 景点闭馆时间 (18:00) vs 最佳拍摄光线 (18:30)
            - **影响**: 可能导致行程逻辑错误或审美评分大幅下降
            
            请人工介入决策：
            """)
            col_d1, col_d2 = st.columns(2)
            if col_d1.button("👤 人工介入调整 (推荐)"):
                st.session_state['deadlock_triggered'] = False
                st.success("已切换至人工编辑模式，请在下方行程卡片中手动修改时间。")
                time.sleep(1)
                st.rerun()
            if col_d2.button("🤖 强制忽略审美"):
                st.session_state['deadlock_triggered'] = False
                st.warning("已强制按逻辑优先排期，审美评分可能降低。")
                time.sleep(1)
                st.rerun()

    # Filter/Select a Plan (Mock selection)
    selected_plan_id = st.selectbox("选择当前处理的方案 ID:", df['plan_id'].head(10))
    plan_data = df[df['plan_id'] == selected_plan_id].iloc[0]

    # --- KPI Dashboard Layout ---

    st.header(f"📋 方案详情 (ID: {selected_plan_id})")

    # Metric Row 1: High Level
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Agent 版本", plan_data['agent_version'])
    m2.metric("预计净利润", f"${plan_data['net_profit']}", delta=f"{random.randint(-5, 10)}% vs Market")
    m3.metric("审美评分", f"{plan_data['aesthetic_score']:.1f}/10")
    m4.metric("转化概率预测", f"{random.randint(20, 80)}%")

    # Tabs for specific KPI Groups
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 方案效能", 
        "💰 商业利润", 
        "🎨 客户体验", 
        "⚠️ 动态风险"
    ])

with tab1:
    st.markdown("#### 方案“含金量”评估")
    c1, c2, c3 = st.columns(3)
    
    # Gauge for Pareto Health
    fig_health = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = plan_data['pareto_health'],
        title = {'text': "帕累托健康度"},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "darkblue"}}
    ))
    fig_health.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
    c1.plotly_chart(fig_health, use_container_width=True)
    
    with c2:
        st.metric("📦 资源利用率 (Inventory Match)", f"{plan_data['inventory_match']}%", help="自有库存使用比例")
        st.progress(plan_data['inventory_match'] / 100)
        st.caption("自有车队与预签酒店的高利用率能显著降低成本。")
        
    with c3:
        st.metric("🤖 逻辑纠错频次 (Audit Recurrence)", f"{plan_data['audit_recurrence']} 次", delta="-2 vs Avg", delta_color="inverse")
        st.info("Auditor 已拦截 3 次路线冲突，为您节省约 15 分钟人工检查时间。")

with tab2:
    st.markdown("#### 商业价值深度分析")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        st.markdown("**返佣热力分布 (Commission Heatmap)**")
        # Mock Heatmap Data
        days = ['Day 1', 'Day 2', 'Day 3', 'Day 4', 'Day 5']
        categories = ['Hotel', 'Transport', 'Ticket', 'Dining']
        z_data = np.random.rand(4, 5)
        fig_heat = px.imshow(z_data, x=days, y=categories, color_continuous_scale='RdBu_r', aspect="auto")
        fig_heat.update_layout(height=300)
        st.plotly_chart(fig_heat, use_container_width=True)
    
    with c2:
        st.markdown("**价格竞争力**")
        comp_price = plan_data['total_revenue'] * 1.15
        st.metric("本方案报价", f"${plan_data['total_revenue']:.2f}")
        st.metric("携程/Expedia 竞对", f"${comp_price:.2f}")
        st.metric("价格优势", f"-15%", delta_color="normal")
        st.success("当前定价具有显著市场竞争力，建议保持。")

with tab3:
    st.markdown("#### 体验与美感量化")
    c1, c2, c3 = st.columns(3)
    
    with c1:
        st.metric("🎬 情绪连贯性 (Mood)", f"{plan_data['mood_consistency']:.1f}/10")
        st.progress(min(plan_data['mood_consistency'] / 10, 1.0))
        st.caption("景点转场顺滑，无突兀风格跳变。")
        
    with c2:
        st.metric("📸 黄金时刻覆盖 (Golden Hour)", f"{plan_data['golden_hour_coverage']:.0%}")
        st.progress(plan_data['golden_hour_coverage'])
        st.caption("关键景点已安排在日出/日落前后 1 小时。")
        
    with c3:
        fatigue = plan_data['fatigue_index']
        color = "green" if fatigue == "Low" else "orange" if fatigue == "Medium" else "red"
        st.markdown(f"**🏃 疲劳度指数**: <span style='color:{color};font-size:1.2em'>{fatigue}</span>", unsafe_allow_html=True)
        st.caption("基于步行距离与海拔升降计算。")

with tab4:
    st.markdown("#### P2 阶段实时风控")
    c1, c2 = st.columns(2)
    
    with c1:
        risk = plan_data['congestion_risk']
        st.metric("🚗 拥堵风险系数", f"{risk:.1%}", delta=f"{'+' if risk > 0.2 else '-'}0.5%")
        if risk > 0.3:
            st.warning("检测到 Day 3 下午返程高峰风险，建议推迟 30 分钟出发。")
        else:
            st.success("路况预测良好。")
            
    with c2:
        buffer = plan_data['buffer_flexibility']
        st.metric("🛡️ 补位灵活度 (Buffer)", f"{buffer} min")
        st.caption("预留的机动时间，足以应对一般性突发延误。")

# --- 5. Itinerary Card Flow (Main Canvas - Bottom) ---
st.markdown("### 🗓️ 行程卡片流 (Interactive Itinerary)")

with st.expander("展开查看详细行程节点", expanded=True):
    # Mock Itinerary items
    col1, col2, col3, col4, col5 = st.columns(5)
    cols = [col1, col2, col3, col4, col5]
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(f"**Day {i+1}**")
            st.info(f"📍 景点 A{i}")
            st.warning(f"🏨 酒店 H{i} (利润高)")
            st.success(f"🍽️ 餐厅 R{i}")
            if i == 2:
                st.error("⚠️ 拥堵预警")

st.markdown("---")
st.caption("Omni Travel Guide AI - Internal Tool v3.0.1 | Powered by Gemini & Streamlit")
