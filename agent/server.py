"""
Server implementation for the AI agent.
"""
import logging
from typing import Dict, Any, List, Union, Optional
import httpx
from fastapi import FastAPI, Request, Depends, HTTPException, BackgroundTasks, Header
from fastapi.responses import JSONResponse
from pydantic import BaseModel, validator

from agent.services.auditor import SolidityAuditor
from agent.models.solidity_file import SolidityFile
from agent.config import Settings

logger = logging.getLogger(__name__)
app = FastAPI(title="Solidity Audit Agent")

class NotificationPayload(BaseModel):
    """Payload received from Agent4rena webhook."""
    task_id: str
    files: List[str]
    post_findings_url: str
    get_contracts_url: str

class AuditResult(BaseModel):
    """Model for audit results."""
    task_id: str
    audit: str

def verify_webhook_secret(x_webhook_secret: str = Header(None), config: Settings = Depends(lambda: app.state.config)):
    """Verify the webhook secret if configured."""
    if config.webhook_secret and x_webhook_secret != config.webhook_secret:
        raise HTTPException(status_code=401, detail="Invalid webhook secret")
    return True

async def fetch_solidity_files(contracts_url: str, task_id: str, file_paths: List[str]) -> List[SolidityFile]:
    """
    Fetch Solidity files from the API.
    
    Args:
        contracts_url: URL to fetch contracts from
        task_id: Task ID
        file_paths: List of file paths to fetch
        
    Returns:
        List of SolidityFile objects
    """
    solidity_files = []
    try:
        async with httpx.AsyncClient() as client:
            # Fetch all contracts at once from the contracts_url
            response = await client.get(contracts_url)
            response.raise_for_status()
            
            # Parse the response
            contracts_data = response.json()
            
            # Process each contract
            for contract in contracts_data:
                if contract["path"] in file_paths:
                    solidity_files.append(
                        SolidityFile(
                            path=contract["path"],
                            content=contract["content"],
                            repo_url=contract.get("repo_url")
                        )
                    )
    except Exception as e:
        logger.error(f"Error fetching contracts: {str(e)}")
    
    return solidity_files

async def send_audit_results(callback_url: str, task_id: str, audit: str):
    """
    Send audit results back to the API.
    
    Args:
        callback_url: URL to send results to
        task_id: Task ID
        audit: Audit results
    """
    try:
        async with httpx.AsyncClient() as client:
            # Match the API's expected format
            payload = {"findings": audit}
            response = await client.post(callback_url, json=payload)
            response.raise_for_status()
            logger.info(f"Successfully sent audit results for task {task_id}")
    except Exception as e:
        logger.error(f"Error sending audit results: {str(e)}")

async def process_notification(payload: NotificationPayload, config: Settings):
    """
    Process a notification by fetching files, auditing them, and sending results.
    
    Args:
        payload: Notification payload
        config: Application configuration
    """
    try:
        
        # Fetch Solidity files
        solidity_files = await fetch_solidity_files(
            payload.get_contracts_url,
            payload.task_id,
            payload.files
        )
        
        if not solidity_files:
            logger.warning(f"No Solidity files fetched for task {payload.task_id}")
            return
        
        # Audit files
        auditor = SolidityAuditor(config.openai_api_key, config.openai_model)
        audit = auditor.audit_files(solidity_files)
        
        # Send results back
        await send_audit_results(payload.post_findings_url, payload.task_id, audit)
        
    except Exception as e:
        logger.error(f"Error processing notification: {str(e)}")

@app.post("/webhook", dependencies=[Depends(verify_webhook_secret)])
async def webhook(payload: NotificationPayload, background_tasks: BackgroundTasks):
    """
    Webhook endpoint for receiving notifications.
    
    Args:
        payload: Notification payload
        background_tasks: FastAPI background tasks
        
    Returns:
        Acknowledgement response
    """
    logger.info(f"Received notification for task {payload.task_id} with {len(payload.files)} files")
    
    # Process the notification in the background
    background_tasks.add_task(
        process_notification, 
        payload=payload, 
        config=app.state.config
    )
    
    return {"status": "processing", "task_id": payload.task_id}

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