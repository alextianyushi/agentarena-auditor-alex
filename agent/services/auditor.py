"""
Core service for auditing Solidity contracts using OpenAI.
"""
import logging
from typing import List, Dict, Any
from openai import OpenAI
from agent.models.solidity_file import SolidityFile
from agent.services.prompts.search_prompt import SEARCH_VULNERABILITIES_PROMPT
from agent.services.prompts.evaluate_prompt import EVALUATE_VULNERABILITIES_PROMPT

logger = logging.getLogger(__name__)

class SolidityAuditor:
    """Service for auditing Solidity contracts using OpenAI."""
    
    def __init__(self, api_key: str, model: str):
        """
        Initialize the auditor with OpenAI credentials.
        
        Args:
            api_key: OpenAI API key
            model: OpenAI model to use
        """
        self.model = model
        self.client = OpenAI(api_key=api_key)

    def search_vulnerabilities(self, prompt: str) -> str:
        try:
            logger.debug(f"Searching vulnerabilities with prompt: {prompt}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error searching vulnerabilities: {e}")
            return ""

    def evaluate_vulnerabilities(self, prompt: str) -> str:
        try:
            logger.debug(f"Evaluating vulnerabilities with prompt: {prompt}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error evaluating vulnerabilities: {e}")
            return ""

    def audit_files(self, solidity_files: List[SolidityFile]) -> str:
        """
        Audit a list of Solidity contracts and return the audit results.
        
        Args:
            solidity_files: List of SolidityFile objects to audit
            
        Returns:
            Audit results as a string
        """
        known_issues = ""
        i = 0
        while i < 10:
            try:
                logger.info(f"Audit iteration {i}")
                # Construct the search prompt with known issues
                contracts = "\n".join([f"Contract: {file.path}\n```solidity\n{file.content}\n```" for file in solidity_files])
                search_prompt = SEARCH_VULNERABILITIES_PROMPT.format(contracts=contracts, known_issues=known_issues)
                
                # Step 1: Searcher
                findings = self.search_vulnerabilities(search_prompt)
                
                # Step 2: Evaluator
                evaluate_prompt = EVALUATE_VULNERABILITIES_PROMPT.format(vulnerabilities=findings, contracts=contracts)
                issues = self.evaluate_vulnerabilities(evaluate_prompt)
                
                # Update known issues
                known_issues += issues
                logger.info(f"Iteration completed. Found issues: {issues}")

                i += 1
            except Exception as e:
                logger.error(f"Error during audit iteration {i}: {e}")

        return known_issues