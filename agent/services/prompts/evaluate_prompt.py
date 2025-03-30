EVALUATE_VULNERABILITIES_PROMPT = """
You are a solidity security expert. 
Assess the severity of the following vulnerabilities and classify them by threat level (Critical, High, Medium, Low, Informational). 
If no vulnerabilities are provided below, return an empty string ("")

Vulnerabilities:
{vulnerabilities}

Contracts:
{contracts}

Use the guidelines below to classify the vulnerabilities:
- CRITICAL: Vulnerabilities that can lead to direct loss of funds or complete contract takeover
- HIGH: Serious vulnerabilities that could potentially lead to loss of funds
- MEDIUM: Vulnerabilities that could lead to contract malfunction
- LOW: Minor issues with limited security impact
- INFORMATIONAL: Best practices and code quality suggestions

Keep the descriptions of each vulnerability as is, add the threat level to the title.

Example vulnerability:

````
1. Signature Replay Vulnerability 
• Description: The signature verification logic reuses a “transaction hash” computed using only the recipient address and amount. Without a nonce or unique identifier, the same valid signature may be replayed multiple times.  
• Location: In SignatureReplay.sol, function getTxHash() and transfer() in contract SignatureReplayVulnerable.  
• Potential impact: An attacker (or even the owner) could replay a previously signed message to send funds multiple times from the contract.  
• Recommended fix: Include a unique nonce (or the sender address, block number, etc.) in the hash (for example, by using abi.encode or abi.encodePacked with a nonce that is updated after each use) so that each signature can only be consumed once.
```

Example output:

```
1. Signature Replay Vulnerability (THREAT LEVEL: CRITICAL)
• Description: The signature verification logic reuses a “transaction hash” computed using only the recipient address and amount. Without a nonce or unique identifier, the same valid signature may be replayed multiple times.  
• Location: In SignatureReplay.sol, function getTxHash() and transfer() in contract SignatureReplayVulnerable.  
• Potential impact: An attacker (or even the owner) could replay a previously signed message to send funds multiple times from the contract.  
• Recommended fix: Include a unique nonce (or the sender address, block number, etc.) in the hash (for example, by using abi.encode or abi.encodePacked with a nonce that is updated after each use) so that each signature can only be consumed once.
```

Output:
"""