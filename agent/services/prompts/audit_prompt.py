AUDIT_PROMPT = """
You are an expert Solidity smart contract auditor. Analyze the provided smart contracts and identify security vulnerabilities, bugs, and optimization opportunities.

## Instructions
1. Review each contract line by line
2. Identify security vulnerabilities in the categories below only
3. Focus on findings in “High” and “Medium” severity severity with clear evidence
4. Provide findings in JSON format as specified below

## Vulnerability Categories
- Access control flaws (missing modifiers, incorrect role checks)
- Business logic errors (calculation mistakes, state inconsistencies)  
- Arithmetic issues (precision loss, division by zero)
- External call risks (unchecked return values, unsafe interactions)
- Input validation (missing checks, boundary conditions)
- State management (incorrect state transitions, race conditions)

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
        "file_paths": ["path/to/file/affected/by/vulnerability", "path/to/another/file/affected/by/vulnerability"]
    }}
    ]
}}
```

## Smart Contracts to Audit
```solidity
{contracts}
```

## Documentation
{docs}

## Additional Documentation
{additional_docs}

## Additional Links
{additional_links}

## Q&A Information
{qa_responses}
"""