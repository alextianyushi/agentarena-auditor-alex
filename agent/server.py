"""
Server implementation for the AI agent.
"""
import json
import logging
import httpx
from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks, Header
from pydantic import BaseModel

from agent.services.auditor import Audit, SolidityAuditor
from agent.config import Settings

logger = logging.getLogger(__name__)
app = FastAPI(title="Solidity Audit Agent")

class Notification(BaseModel):
    """Payload received from Agent4rena webhook."""
    task_id: str
    get_contracts_url: str
    post_findings_url: str

class TaskContent(BaseModel):
    """Model for task smart contract content."""
    task_id: str
    files_content: str

def verify_webhook_secret(x_webhook_secret: str = Header(None), config: Settings = Depends(lambda: app.state.config)):
    """Verify the webhook secret if configured."""
    if config.webhook_secret and x_webhook_secret != config.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return True

async def fetch_solidity_files(contracts_url: str, config: Settings) -> str:
    """
    Fetch Solidity files from the API.
    
    Args:
        contracts_url: URL to fetch contracts from
        task_id: Task ID
        file_paths: List of file paths to fetch
        
    Returns:
        List of SolidityFile objects
    """
    try:
        async with httpx.AsyncClient() as client:
            # Fetch all contracts at once from the contracts_url
            response = await client.get(
                contracts_url,
                headers={"X-API-Key": config.agent4rena_api_key}
            )
            response.raise_for_status()
            
            # Parse the response
            return response.json()
        
    except Exception as e:
        logger.error(f"Error fetching contracts: {str(e)}")
    
    return None

async def send_audit_results(callback_url: str, task_id: str, audit: Audit):
    """
    Send audit results back to the API.
    
    Args:
        callback_url: URL to send results to
        task_id: Task ID
        audit: Audit results
    """
    try:
        async with httpx.AsyncClient(timeout=600.0) as client:
            # Convert Pydantic models to dict first
            findings_dict = [finding.model_dump() for finding in audit.findings]
            payload = {"task_id": task_id, "findings": findings_dict}
            
            # Log detailed payload information for debugging
            logger.info(f"Sending audit results to {callback_url} for task {task_id}")
            logger.debug(f"Request payload: {json.dumps(payload, indent=2)}")
            
            # Add more debugging info and increase timeout
            response = await client.post(
                callback_url, 
                json=payload,
                headers={
                    "Content-Type": "application/json",
                    "X-API-Key": app.state.config.agent4rena_api_key
                }
            )
            # Log response details
            logger.info(f"Response status: {response.status_code}")
            logger.debug(f"Response headers: {response.headers}")
            logger.debug(f"Response content: {response.text}")
            
            response.raise_for_status()
            logger.info(f"Successfully sent audit results for task {task_id}")
            
    except httpx.RequestError as e:
        # Network-related errors
        logger.error(f"Network error when sending audit results: {str(e)}", exc_info=True)
    except httpx.HTTPStatusError as e:
        # Server returned error status
        logger.error(f"HTTP error {e.response.status_code} when sending audit results: {e.response.text}", exc_info=True)
    except Exception as e:
        # Any other unexpected errors
        logger.error(f"Unexpected error sending audit results: {str(e)}", exc_info=True)

async def process_notification(notification: Notification, config: Settings):
    """
    Process a notification by fetching files, auditing them, and sending results.
    
    Args:
        payload: Notification payload
        config: Application configuration
    """
    try:
        
        # Fetch Solidity files
        solidity_content = await fetch_solidity_files(
            notification.get_contracts_url,
            config
        )
        
        if not solidity_content:
            logger.warning(f"No Solidity files fetched for task {notification.task_id}")
            return
        
        # Audit files
        auditor = SolidityAuditor(config.openai_api_key, config.openai_model)
        audit = auditor.audit_files(solidity_content)
        
        # Send results back
        await send_audit_results(notification.post_findings_url, notification.task_id, audit)
        
    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")

@app.post("/webhook")# , dependencies=[Depends(verify_webhook_secret)])
async def webhook(notification: Notification, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for receiving notifications.
    
    Args:
        payload: Notification payload
        background_tasks: FastAPI background tasks
        
    Returns:
        Acknowledgement response
    """
    logger.info(f"Received notification for task {notification.task_id}")
    
    # Process the notification in the background
    background_tasks.add_task(
        process_notification, 
        notification=notification, 
        config=app.state.config
    )
    
    return {"status": "processing", "task_id": notification.task_id}

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

def start_server(host: str, port: int, config: Settings):
    """
    Start the FastAPI server.
    
    Args:
        host: Host to bind to
        port: Port to bind to
        config: Application configuration
    """
    import uvicorn
    
    # Configure logging to both console and file
    log_file = config.log_file
    logging.basicConfig(
        level=getattr(logging, config.log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
    
    # Store config in app state
    app.state.config = config
    
    # Start the server
    logger.info(f"Starting server on {host}:{port}")
    uvicorn.run(app, host=host, port=port) 