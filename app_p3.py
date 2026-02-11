import streamlit as st
from travel_agent_p2 import app  # 引入我们刚才写的 Agent 逻辑
import time

# --- 网页配置 ---
st.set_page_config(page_title="AI 智能旅行专家", page_icon="✈️")
st.title("🌍 AI 智能旅行专家 (P3版)")
st.caption("基于 Google Maps 实时审计与 LangGraph 多 Agent 协作")

# 初始化聊天记录
if "messages" not in st.session_state:
    st.session_state.messages = []

# 显示历史消息
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 用户输入 ---
if prompt := st.chat_input("想去哪里玩？比如：我想去巴黎，先看卢浮宫..."):
    # 显示用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # --- 调用 Agent 逻辑 ---
    with st.chat_message("assistant"):
        status_placeholder = st.empty()
        with st.status("🚀 Agent 正在思考并验证路况...", expanded=True) as status:
            
            # 运行 LangGraph
            initial_state = {"itinerary": [], "is_valid": False, "feedback": "", "iteration": 0}
            final_itinerary = []
            
            # 模拟 Agent 内部对话
            for output in app.stream(initial_state):
                for key, value in output.items():
                    if key == "planner":
                        st.write(f"✍️ **Planner:** 生成了方案 v{value['iteration']}")
                    elif key == "auditor":
                        if value["is_valid"]:
                            st.write("✅ **Auditor:** 实时路况验证通过！")
                        else:
                            st.write(f"⚠️ **Auditor:** 发现冲突！{value['feedback']}")
                    
                    if "itinerary" in value:
                        final_itinerary = value["itinerary"]
            
            status.update(label="规划完成！", state="complete", expanded=False)

        # 最终呈现结果
        res_text = "### ✨ 为您生成的优化行程：\n" + "\n".join([f"- {item}" for item in final_itinerary])
        st.markdown(res_text)
        
        # 模拟地图展示（你可以后续接入真实 Google Map 组件）
        st.info("💡 提示：该行程已自动避开了高峰拥堵时段。")
        
    st.session_state.messages.append({"role": "assistant", "content": res_text})