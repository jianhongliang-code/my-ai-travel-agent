import json
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import AsyncGenerator

# Import our graph
from agent_graph import graph_app, AgentState

app = FastAPI(title="Omni Travel Guide API")

# Enable CORS for frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Omni Travel Guide API is running"}

@app.get("/stream-trip/{user_id}")
async def stream_trip_planning(user_id: str, request: Request):
    """
    Stream the trip planning process using Server-Sent Events (SSE).
    """
    async def event_generator() -> AsyncGenerator[str, None]:
        # Config with thread_id for persistence
        config = {"configurable": {"thread_id": user_id}}
        
        # Initial state
        # Only initialize if it's a new thread or we want to restart
        # But for this demo, we assume every GET request is a "new run" or "resume" if state exists?
        # LangGraph with SqliteSaver will load existing state if thread_id matches.
        # We should only provide inputs if we are starting fresh or updating.
        
        # Check if state exists
        current_state = graph_app.get_state(config)
        
        if not current_state.values:
            # New conversation
            inputs = {
                "user_id": user_id,
                "user_request": "我想去巴黎看日落，注重审美，不差钱",
                "iteration_count": 0,
                "errors": [],
                "messages": []
            }
        else:
            # Resuming or re-running (but usually we don't want to re-run from scratch if state exists)
            # If we want to force a new run, we'd need to update configuration or inputs.
            # For this demo, let's assume if we call stream-trip, we might want to send a new request
            # OR just view the current progress.
            # Let's simple pass None to inputs if we just want to "view" or "resume".
            # BUT, if the user wants to start a NEW plan with the same thread_id, we pass inputs.
            # Let's assume for now we always start/restart the flow for the demo purpose.
             inputs = {
                "user_id": user_id,
                "user_request": "我想去巴黎看日落，注重审美，不差钱",
                "iteration_count": 0,
                "errors": [],
                "messages": []
            }

        # Use graph_app.astream to listen to node updates
        # stream_mode="updates" yields the output of each node after it finishes
        # Pass config to enable checkpointing
        async for event in graph_app.astream(inputs, config=config, stream_mode="updates"):
            # Check for client disconnection
            if await request.is_disconnected():
                print(f"Client {user_id} disconnected.")
                break

            # The event is a dictionary where key is node name and value is the output
            # e.g., {'planner': {'itinerary': [...], ...}}
            node_name = list(event.keys())[0]
            node_data = event[node_name]

            # Construct payload for UI
            payload = {
                "node": node_name,
                "status": "completed", # Node finished
                "data": node_data,
                "timestamp": str(asyncio.get_event_loop().time())
            }

            # Send as SSE event
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
            
        # Check if we are interrupted (waiting for human approval)
        state = graph_app.get_state(config)
        if state.next:
            payload = {
                "node": "human_interrupt",
                "status": "waiting",
                "data": {"message": "Waiting for commercial approval..."},
                "timestamp": str(asyncio.get_event_loop().time())
            }
            yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"
        else:
            # Send a final 'done' event if finished
            yield f"data: {json.dumps({'node': 'EOF', 'status': 'done'}, ensure_ascii=False)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.post("/approve-trip/{user_id}")
async def approve_trip(user_id: str):
    """
    Resume the graph execution after human approval.
    """
    config = {"configurable": {"thread_id": user_id}}
    
    # Just passing None as input to resume
    # In LangGraph, passing None to astream when interrupted resumes execution
    # But here we can't easily stream the response back in a POST request if we want to keep the SSE connection separate.
    # Typically, the frontend would receive the "human_interrupt" event, show a button, 
    # and when clicked, call this POST endpoint.
    # This endpoint should trigger the graph to continue. 
    # However, since the SSE connection might be closed or waiting, we need a way to push updates.
    # For this demo, we'll just return a success message, and the Frontend can RE-CONNECT to the stream 
    # or we can assume the graph state is updated and the next stream call will pick it up.
    
    # Actually, a better pattern for SSE + Interrupt is:
    # 1. SSE stream pauses at interrupt.
    # 2. UI calls POST /approve.
    # 3. POST /approve runs the next step(s) and updates state.
    # 4. BUT, to stream the *result* of the approval back to the UI, 
    #    the UI usually needs to keep listening or reconnect.
    
    # Let's execute the remainder of the graph here and return the final result, 
    # OR just return "Approved" and let the user re-trigger the stream?
    
    # Simplified approach for this demo:
    # The POST request will run the rest of the graph and return the final state.
    # Real-time updates for this part won't go through the *original* SSE connection unless we use a pub/sub system.
    # But we can return the final result in the response.
    
    async for event in graph_app.astream(None, config=config, stream_mode="updates"):
         pass # Just run it to completion
         
    final_state = graph_app.get_state(config)
    return {"status": "approved", "final_state": final_state.values}


if __name__ == "__main__":
    uvicorn.run("backend_api:app", host="0.0.0.0", port=8000, reload=True)
