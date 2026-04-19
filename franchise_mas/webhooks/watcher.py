from fastapi import APIRouter, Request, BackgroundTasks
import json

router = APIRouter()

def process_watcher_event(event_data: dict):
    """
    Process incoming Watcher events asynchronously.
    This is where the agents will be triggered (e.g., Drafting a social post, generating an alert).
    """
    print(f"Processing watcher event for company: {event_data.get('company_name', 'Unknown')}")
    # TODO: Pass event to relevant agent based on event type
    # e.g., if event_type == 'headcount_drop', send to Supply Chain Agent
    pass

@router.post("/crustdata/watcher")
async def handle_watcher_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint to receive events from Crustdata Watcher API.
    """
    try:
        payload = await request.json()
        print(f"Received Watcher Event: {json.dumps(payload, indent=2)}")
        
        # Dispatch event processing to a background task
        background_tasks.add_task(process_watcher_event, payload)
        
        return {"status": "success", "message": "Event received"}
    except Exception as e:
        print(f"Error handling watcher webhook: {e}")
        return {"status": "error", "message": str(e)}

