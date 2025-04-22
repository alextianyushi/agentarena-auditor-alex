"""
Local execution mode for the AI agent.
"""
import os
import logging
import tempfile
from typing import List
import git
import glob
from agent.services.auditor import SolidityAuditor
from agent.models.solidity_file import SolidityFile
from agent.config import Settings

logger = logging.getLogger(__name__)

def clone_repository(repo_url: str, commit_hash: str | None = None) -> str:
    """
    Clone a GitHub repository to a temporary directory.
    
    Args:
        repo_url: URL of the GitHub repository
        commit_hash: Optional specific commit hash to checkout
        
    Returns:
        Path to the cloned repository
    """
    logger.info(f"Cloning repository: {repo_url}")
    temp_dir = tempfile.mkdtemp()
    repo = git.Repo.clone_from(repo_url, temp_dir)
    
    if commit_hash:
        logger.info(f"Checking out commit: {commit_hash}")
        repo.git.checkout(commit_hash)
        
    return temp_dir

def find_solidity_contracts(repo_path: str) -> List[SolidityFile]:
    """
    Find all Solidity contracts in a repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        List of SolidityFile objects
    """
    logger.info(f"Searching for Solidity contracts in {repo_path}")
    solidity_files = []
    
    for file_path in glob.glob(f"{repo_path}/**/*.sol", recursive=True):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Get relative path within the repository
            rel_path = os.path.relpath(file_path, repo_path)
            
            solidity_files.append(
                SolidityFile(
                    path=rel_path,
                    content=content
                )
            )
        except Exception as e:
            logger.error(f"Error reading contract {file_path}: {str(e)}")
    
    return solidity_files

def save_audit_results(output_path: str, audit: str):
    """
    Save audit results to a file.
    
    Args:
        output_path: Path to save the results to
        audit: Audit results
    """
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(audit)
        logger.info(f"Security audit results saved to {output_path}")
    except Exception as e:
        logger.error(f"Error saving audit results: {str(e)}")
        raise

def process_local(repo_url: str, output_path: str, config: Settings, commit_hash: str | None = None):
    """
    Process a repository in local mode.
    
    Args:
        repo_url: URL of the GitHub repository
        output_path: Path to save the audit results
        config: Application configuration
        commit_hash: Optional specific commit hash to checkout
    """
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
    
    try:
        # Clone the repository
        repo_path = clone_repository(repo_url, commit_hash)
        
        # Find Solidity contracts
        solidity_contracts = find_solidity_contracts(repo_path)
        
        if not solidity_contracts:
            logger.warning(f"No Solidity contracts found in repository {repo_url}")
            return
        
        logger.info(f"Found {len(solidity_contracts)} Solidity contracts")
        
        # Audit contracts
        auditor = SolidityAuditor(config.openai_api_key, config.openai_model)
        audit = auditor.audit_files(solidity_contracts)
        
        # Save results
        save_audit_results(output_path, audit)
        
        logger.info("Security audit completed successfully")
        
    except Exception as e:
        logger.error(f"Error in local processing: {str(e)}")
        raise