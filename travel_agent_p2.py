import os
import json
from dotenv import load_dotenv
import googlemaps
from datetime import datetime, timedelta
from langgraph.graph import StateGraph, END
from typing import TypedDict, List

# 1. 初始化
load_dotenv(".env.local")
gmaps = googlemaps.Client(key=os.getenv("GOOGLE_MAPS_API_KEY"))

# 定义状态机的数据结构
class AgentState(TypedDict):
    itinerary: List[str]
    is_valid: bool
    feedback: str
    iteration: int

# --- 节点 A: 规划者 (Planner) ---
def planner_node(state: AgentState):
    print(f"\n[Planner] 正在生成第 {state['iteration'] + 1} 版方案...")
    
    # 如果审计员给了反馈，AI 会根据反馈调整
    if "堵车" in state['feedback']:
        # 调整后的方案：交换顺序
        new_plan = ["10:00 埃菲尔铁塔", "14:00 卢浮宫"]
    else:
        # 初始方案：先去卢浮宫
        new_plan = ["10:00 卢浮宫", "14:00 埃菲尔铁塔"]
        
    return {"itinerary": new_plan, "iteration": state['iteration'] + 1}

# --- 节点 B: 审计员 (Auditor) ---
def auditor_node(state: AgentState):
    print("[Auditor] 正在调取 Google Maps 验证路况...")
    
    # 这里模拟真实 API 调用逻辑
    # 假设我们只在第一轮模拟一个"堵车"结果
    if state['iteration'] == 1:
        # 实际开发时这里写：gmaps.distance_matrix(...)
        return {
            "is_valid": False, 
            "feedback": "警告：卢浮宫周边下午 14:00 有严重堵车，预计延误 40 分钟。"
        }
    else:
        print("✅ 审计通过：当前行程逻辑顺畅。")
        return {"is_valid": True, "feedback": "通过"}

# --- 路由逻辑 ---
def should_continue(state: AgentState):
    if state["is_valid"]:
        return "end"
    return "replan"

# --- 2. 组装工作流 ---
workflow = StateGraph(AgentState)

workflow.add_node("planner", planner_node)
workflow.add_node("auditor", auditor_node)

workflow.set_entry_point("planner")
workflow.add_edge("planner", "auditor")

workflow.add_conditional_edges(
    "auditor",
    should_continue,
    {
        "replan": "planner",
        "end": END
    }
)

app = workflow.compile()

# --- 3. 运行启动 ---
if __name__ == "__main__":
    print("🚀 AI 旅游 Agent P2 版启动 (带 Google Maps 审计功能)")
    initial_state = {"itinerary": [], "is_valid": False, "feedback": "", "iteration": 0}
    
    for output in app.stream(initial_state):
        for key, value in output.items():
            if "itinerary" in value:
                print(f"当前行程: {value['itinerary']}")
