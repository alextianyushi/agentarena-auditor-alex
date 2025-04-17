"""
Core service for auditing Solidity contracts using OpenAI.
"""
import json
import logging
from typing import List
from pydantic import BaseModel, Field
from openai import OpenAI

logger = logging.getLogger(__name__)

class VulnerabilityFinding(BaseModel):
    """Model representing a single vulnerability finding."""
    title: str = Field(..., description="Title of the vulnerability")
    description: str = Field(..., description="Detailed description of the vulnerability")
    severity: str = Field(..., description="Severity level: Critical, High, Medium, Low, or Informational")
    file_path: str = Field(..., description="Path to the file containing the vulnerability")

class AuditResponse(BaseModel):
    """Model representing the complete audit response."""
    findings: List[VulnerabilityFinding] = Field(default_factory=list, description="List of vulnerability findings")

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
        
    # Define the audit prompt as a class constant
    AUDIT_PROMPT = """
    You are an expert Solidity smart contract auditor. Analyze the provided smart contracts and identify security vulnerabilities, bugs, and optimization opportunities.

    ## Instructions
    1. Analyze each contract thoroughly
    2. Identify all possible security vulnerabilities
    3. Provide your findings in JSON format as specified below
    
    ## Vulnerability Categories To Consider
    - Reentrancy vulnerabilities
    - Access control issues
    - Integer overflow/underflow
    - Denial of service vectors
    - Logic errors and edge cases
    - Gas optimization issues
    - Centralization risks
    - Front-running opportunities
    - Timestamp manipulation
    - Unchecked external calls
    - Improper error handling
    - Incorrect inheritance
    - Missing validation
    - Flash loan attack vectors
    - Business logic flaws
    - Insufficient testing coverage

    ## Severity Levels
    - High: Significant vulnerabilities that could lead to loss of funds
    - Medium: Vulnerabilities that pose risks but have limited impact
    - Low: Minor issues that should be addressed but don't pose immediate risks
    - Info: Suggestions for best practices, optimizations, or code quality improvements

    ## Response Format
    Return your findings in the following JSON format:
    ```json
    {{
      "findings": [
        {{
          "title": "Clear, concise title of the vulnerability",
          "description": "Detailed explanation including how the vulnerability could be exploited and recommendation to fix",
          "severity": "High|Medium|Low|Info",
          "file_path": "path/to/the/file/containing/the/vulnerability"
        }}
      ]
    }}
    ```

    ## Smart Contracts to Audit
    ```solidity
    {contracts}
    ```
    """

    def audit_files(self, contracts: str) -> AuditResponse:
        """
        Audit a list of Solidity contracts and return structured findings.
        
        Args:
            solidity_files: List of SolidityFile objects to audit
            
        Returns:
            Dictionary containing the audit findings in a structured format
        """
        try:
            # Prepare the audit prompt
            audit_prompt = self.AUDIT_PROMPT.format(contracts=contracts)
            
            # Send single request to OpenAI
            logger.info("Sending audit request to OpenAI")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Solidity smart contract auditor."},
                    {"role": "user", "content": audit_prompt}
                ],
                response_format={"type": "json_object"}
            )
            
            # Extract and parse the JSON response
            result_text = response.choices[0].message.content
            logger.debug(f"Received audit response from OpenAI")
            
            try:
                # Parse the JSON response
                audit_result = json.loads(result_text)
                
                logger.info(f"Audit result: {audit_result}")

                # Validate using Pydantic model
                validated_result = AuditResponse(**audit_result)
                
                logger.info(f"Audit completed successfully with {len(validated_result.findings)} findings")
                return validated_result
            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to parse JSON response: {json_err}")
                logger.debug(f"Raw response: {result_text}")
                return AuditResponse(findings=[])
            except Exception as validation_err:
                logger.error(f"Validation error with audit response: {validation_err}")
                return AuditResponse(findings=[])
                
        except Exception as e:
            logger.error(f"Error during audit: {str(e)}", exc_info=True)
            return AuditResponse(findings=[])