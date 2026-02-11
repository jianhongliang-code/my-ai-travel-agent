import random
import asyncio
import sqlite3
import googlemaps
from datetime import datetime, time, timedelta
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from pydantic import BaseModel, Field

# --- Pydantic Models for Auditor ---

class Location(BaseModel):
    place_id: str
    lat: float = 0.0
    lng: float = 0.0
    address: str = ""

class Activity(BaseModel):
    title: str
    location: Location
    start_time: time
    end_time: time
    description: str = ""

class DailyPlan(BaseModel):
    date: str # YYYY-MM-DD
    activities: List[Activity]

class Itinerary(BaseModel):
    daily_plans: List[DailyPlan]

# --- State Definition ---

class AgentState(TypedDict):
    user_id: str
    user_request: str
    itinerary_raw: List[str] # Keeping old simple list for compatibility/display
    itinerary: Itinerary     # Structured Pydantic model for Auditor
    errors: List[str]
    profit_margin: float
    aesthetic_score: float
    iteration_count: int
    messages: List[str]
    user_context: str
    system_instruction_add_on: str

# --- Memory Retrieval Logic ---

def mock_get_user_preferences(user_id: str) -> str:
    """Mock database lookup for user preferences"""
    # In production, this would query a Vector Store or SQL DB
    if "user_123" in user_id:
        return "偏好：喜欢摄影（需安排黄金时刻拍摄），反感强制购物，必须包含当地特色美食。"
    elif "vip" in user_id:
        return "偏好：出行必须是豪华专车，酒店只住五星级，行程要极其宽松。"
    else:
        return "偏好：标准行程，注重性价比。"

def mock_get_org_memory() -> str:
    """Mock database lookup for organizational knowledge"""
    return "组织记忆：1. 巴黎丽兹酒店大巴无法进入，需安排小车接驳。 2. 卢浮宫周二闭馆，排期需避开。"

async def memory_retrieval(state: AgentState):
    """
    Memory Retrieval Node: Fetches long-term user preferences and organizational wisdom.
    """
    print("--- Memory Retrieval Node ---")
    user_id = state.get("user_id", "anonymous")
    
    # 1. Fetch User Long-term Memory
    user_prefs = mock_get_user_preferences(user_id)
    
    # 2. Fetch Organizational Memory
    org_wisdom = mock_get_org_memory()
    
    combined_context = f"用户画像: {user_prefs}\n企业知识库: {org_wisdom}"
    
    return {
        "user_context": combined_context,
        "system_instruction_add_on": f"【重要约束】请严格遵守以下记忆信息：\n{combined_context}",
        "messages": [f"Memory: Retrieved context for {user_id}"]
    }


# --- Mock Data Helpers ---
# Since we don't have real Place IDs, we mock them
def create_mock_itinerary():
    # Day 1
    act1 = Activity(
        title="Hotel Ritz Check-in",
        location=Location(place_id="ChIJ-b-5...MockID1"),
        start_time=time(14, 0),
        end_time=time(15, 0)
    )
    # Day 2
    act2 = Activity(
        title="Café de Flore",
        location=Location(place_id="ChIJ-b-5...MockID2"),
        start_time=time(9, 0),
        end_time=time(10, 30)
    )
    act3 = Activity(
        title="Musée d'Orsay",
        location=Location(place_id="ChIJ-b-5...MockID3"),
        start_time=time(13, 0),
        end_time=time(16, 0)
    )
    
    return Itinerary(daily_plans=[
        DailyPlan(date="2024-06-01", activities=[act1]),
        DailyPlan(date="2024-06-02", activities=[act2, act3])
    ])

# --- Google Maps Client ---
# Initialize with a dummy key for now, or use env var
# For production, replace 'YOUR_KEY' with os.getenv("GOOGLE_MAPS_API_KEY")
try:
    gmaps = googlemaps.Client(key='YOUR_GOOGLE_MAPS_API_KEY')
except ValueError:
    print("Warning: Google Maps API Key not provided. Using mock mode.")
    gmaps = None

# --- Auditor Logic ---

async def check_traffic_and_timing(act_a: Activity, act_b: Activity, date_str: str) -> List[str]:
    issue = []
    # Mock logic if no API key
    if not gmaps:
        await asyncio.sleep(0.2) # Simulate network
        # Hardcoded logic for demo purpose:
        # If going from Cafe to Museum, pretend there is traffic
        if "Café" in act_a.title and "Musée" in act_b.title:
             # Let's say planned gap is 2.5 hours (10:30 to 13:00), which is fine.
             # But let's randomly inject a delay
             if random.random() < 0.3:
                 issue.append(f"交通冲突 (Mock): 从 {act_a.title} 到 {act_b.title} 预计拥堵，建议提前出发。")
        return issue

    departure_time = datetime.combine(datetime.strptime(date_str, "%Y-%m-%d"), act_a.end_time)
    
    try:
        # Run synchronous gmaps call in executor
        loop = asyncio.get_running_loop()
        res = await loop.run_in_executor(
            None, 
            lambda: gmaps.distance_matrix(
                origins=f"place_id:{act_a.location.place_id}",
                destinations=f"place_id:{act_b.location.place_id}",
                departure_time=departure_time,
                traffic_model="pessimistic"
            )
        )
        
        if res['rows'][0]['elements'][0]['status'] == 'OK':
            element = res['rows'][0]['elements'][0]
            real_duration = element['duration_in_traffic']['value'] / 60
            
            # Calculate gap
            dt_a_end = datetime.combine(datetime.min, act_a.end_time)
            dt_b_start = datetime.combine(datetime.min, act_b.start_time)
            planned_gap = (dt_b_start - dt_a_end).seconds / 60
            
            if real_duration > planned_gap:
                issue.append(f"交通冲突: 从 {act_a.title} 到 {act_b.title} 实测需 {int(real_duration)}分钟，但仅预留了 {int(planned_gap)}分钟。")
                
    except Exception as e:
        issue.append(f"API调用失败: {str(e)}")
        
    return issue

async def check_opening_hours(activity: Activity, date_str: str) -> List[str]:
    issue = []
    if not gmaps:
        await asyncio.sleep(0.1)
        # Mock logic: Museum closed on Mondays
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        if "Musée" in activity.title and dt.weekday() == 0: # Monday
             issue.append(f"营业时间冲突 (Mock): {activity.title} 周一闭馆。")
        return issue

    # Real API logic would go here
    # ...
    return issue

# --- Node Functions ---

async def planner(state: AgentState):
    """
    AI Planner: Generates the initial itinerary.
    """
    print("--- Planner Node ---")
    await asyncio.sleep(1.0)
    
    # Check for memory context
    memory_context = state.get("system_instruction_add_on", "")
    print(f"Planner Context: {memory_context}")
    
    # In a real app, LLM would generate this structure
    structured_plan = create_mock_itinerary()
    
    initial_itinerary_display = [
        "Day 1: Arrive in Paris, check into Hotel Ritz.",
        "Day 2: Morning coffee at Café de Flore, afternoon visit to Musée d'Orsay.",
        "Day 3: Day trip to Giverny to see Monet's gardens.",
        "Day 4: Sunset cruise on the Seine, dinner at Le Jules Verne."
    ]
    
    # If memory exists, we might want to "modify" the plan to show it's working
    msg = "Planner: Drafted initial structured itinerary."
    if "卢浮宫" in memory_context:
         msg += " (Note: Checked organizational memory for Louvre opening hours)"
    
    return {
        "itinerary": structured_plan,
        "itinerary_raw": initial_itinerary_display,
        "messages": [msg]
    }

async def auditor(state: AgentState):
    """
    Auditor: Checks for logistical conflicts using concurrent API calls.
    """
    print("--- Auditor Node (Concurrent) ---")
    
    plan = state.get("itinerary")
    if not plan:
        return {"errors": ["No itinerary found to audit."]}

    errors = []
    tasks = []
    
    # 1. Traffic Checks
    for day in plan.daily_plans:
        for i in range(len(day.activities) - 1):
            tasks.append(
                check_traffic_and_timing(
                    day.activities[i],
                    day.activities[i+1],
                    day.date
                )
            )
            
    # 2. Opening Hours Checks
    for day in plan.daily_plans:
        for activity in day.activities:
            tasks.append(check_opening_hours(activity, day.date))

    # 3. Execute all tasks concurrently
    if tasks:
        results = await asyncio.gather(*tasks)
        for res in results:
            if res:
                errors.extend(res)
    
    # Add random error for demo visual effect if none found (optional)
    if not errors and random.random() < 0.2:
         errors.append("Traffic Alert (Simulated): Giverny route has heavy construction delays.")

    # Generate feedback
    feedback_msg = "Auditor: Logic check passed."
    if errors:
        feedback_msg = f"Auditor: Found {len(errors)} issues."

    return {
        "errors": errors,
        "messages": [feedback_msg]
    }

async def commercial_arbiter(state: AgentState):
    """
    Commercial Arbiter: Balances profit and aesthetics.
    """
    print("--- Commercial Arbiter Node ---")
    await asyncio.sleep(0.5) # Simulate calculation
    
    # Simulate profit/aesthetic calculation
    base_profit = 15.0
    base_aesthetic = 9.0
    
    if state.get("errors"):
        base_profit -= 2.0 # Penalty for errors
        base_aesthetic -= 1.0
        
    return {
        "profit_margin": base_profit,
        "aesthetic_score": base_aesthetic,
        "messages": [f"Arbiter: Calculated Profit Margin: {base_profit}%, Aesthetic Score: {base_aesthetic}"]
    }

# --- Graph Construction ---

workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("memory_retrieval", memory_retrieval)
workflow.add_node("planner", planner)
workflow.add_node("auditor", auditor)
workflow.add_node("commercial_arbiter", commercial_arbiter)

# Set entry point
workflow.set_entry_point("memory_retrieval")

# Add edges
workflow.add_edge("memory_retrieval", "planner")
workflow.add_edge("planner", "auditor")
workflow.add_edge("auditor", "commercial_arbiter")
workflow.add_edge("commercial_arbiter", END)

# Setup SQLite Persistence
# check_same_thread=False is needed for FastAPI async environment
conn = sqlite3.connect("checkpoints.db", check_same_thread=False)
memory = SqliteSaver(conn)

# Compile the graph with Checkpointer and Interrupt
# We interrupt BEFORE commercial_arbiter to allow Human-in-the-loop approval
graph_app = workflow.compile(
    checkpointer=memory,
    interrupt_before=["commercial_arbiter"] 
)
