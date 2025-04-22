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

def clone_repository(repo_url: str) -> str:
    """
    Clone a GitHub repository to a temporary directory.
    
    Args:
        repo_url: URL of the GitHub repository
        
    Returns:
        Path to the cloned repository
    """
    logger.info(f"Cloning repository: {repo_url}")
    temp_dir = tempfile.mkdtemp()
    git.Repo.clone_from(repo_url, temp_dir)
    return temp_dir

def select_files_interactively(all_files: List[str]) -> List[str]:
    """
    Display all .sol files and let the user select which ones to audit.
    
    Args:
        all_files: List of all Solidity file paths found
        
    Returns:
        List of selected file paths
    """
    if not all_files:
        logger.warning("No Solidity files found in repository")
        return []
        
    print("\nFound the following Solidity files:")
    for idx, file_path in enumerate(all_files, 1):
        print(f"{idx}. {file_path}")
        
    while True:
        try:
            selection = input("\nEnter the numbers of files to audit (comma-separated, e.g. '1,3,4'): ")
            if not selection.strip():
                logger.warning("No files selected, exiting...")
                return []
                
            # Parse and validate selections
            selected_indices = [int(idx.strip()) for idx in selection.split(",")]
            selected_files = []
            
            for idx in selected_indices:
                if 1 <= idx <= len(all_files):
                    selected_files.append(all_files[idx - 1])
                else:
                    print(f"Invalid selection {idx}, skipping...")
            
            if selected_files:
                print("\nSelected files:")
                for file in selected_files:
                    print(f"- {file}")
                return selected_files
            else:
                print("No valid files selected, please try again")
                
        except ValueError:
            print("Invalid input. Please enter comma-separated numbers")

def find_solidity_contracts(repo_path: str, only_selected: bool = False) -> List[SolidityFile]:
    """
    Find all Solidity contracts in a repository.
    
    Args:
        repo_path: Path to the repository
        only_selected: Whether to enable interactive file selection
        
    Returns:
        List of SolidityFile objects
    """
    logger.info(f"Searching for Solidity contracts in {repo_path}")
    
    # Find all .sol files
    all_files = [
        os.path.relpath(f, repo_path)
        for f in glob.glob(f"{repo_path}/**/*.sol", recursive=True)
    ]
    
    if only_selected:
        selected_files = select_files_interactively(all_files)
    else:
        selected_files = all_files
    
    solidity_files = []
    for file_path in selected_files:
        try:
            abs_path = os.path.join(repo_path, file_path)
            with open(abs_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            solidity_files.append(
                SolidityFile(
                    path=file_path,
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

def process_local(repo_url: str, output_path: str, config: Settings, only_selected: bool = False):
    """
    Process a repository in local mode.
    
    Args:
        repo_url: URL of the GitHub repository
        output_path: Path to save the audit results
        config: Application configuration
        only_selected: Whether to enable interactive file selection
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
        repo_path = clone_repository(repo_url)
        
        # Find Solidity contracts
        solidity_contracts = find_solidity_contracts(repo_path, only_selected)
        
        if not solidity_contracts:
            logger.warning(f"No Solidity contracts found in repository {repo_url}")
            return
        
        logger.info(f"Found {len(solidity_contracts)} Solidity contracts to audit")
        
        # Audit contracts
        auditor = SolidityAuditor(config.openai_api_key, config.openai_model)
        audit = auditor.audit_files(solidity_contracts)
        
        # Save results
        save_audit_results(output_path, audit)
        
        logger.info("Security audit completed successfully")
        
    except Exception as e:
        logger.error(f"Error in local processing: {str(e)}")
        raise