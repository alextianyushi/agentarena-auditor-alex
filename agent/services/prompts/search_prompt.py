SEARCH_VULNERABILITIES_PROMPT = """
You are a solidity security expert. 
Audit the provided Solidity contracts for security vulnerabilities.

Contracts:
{contracts}

The following vulnerabilities are known to exist in the codebase. Please do not report them as vulnerabilities. If no new vulnerabilities are found, return an empty string ("")
Known vulnerabilities: 
{known_issues}

For each finding, provide:
- Title of the vulnerability
- Description of the vulnerability
- Location in the code
- Potential impact
- Recommended fix

Example output:

```
1. Signature Replay Vulnerability (THREAT LEVEL: CRITICAL)  
• Description: The signature verification logic reuses a “transaction hash” computed using only the recipient address and amount. Without a nonce or unique identifier, the same valid signature may be replayed multiple times.  
• Location: In SignatureReplay.sol, function getTxHash() and transfer() in contract SignatureReplayVulnerable.  
• Potential impact: An attacker (or even the owner) could replay a previously signed message to send funds multiple times from the contract.  
• Recommended fix: Include a unique nonce (or the sender address, block number, etc.) in the hash (for example, by using abi.encode or abi.encodePacked with a nonce that is updated after each use) so that each signature can only be consumed once.

2. Reentrancy in Cross-Function Withdraw (THREAT LEVEL: CRITICAL)  
• Description: In CrossFunctionReentrancyVulnerable the withdraw() function sends Ether before updating the state (the sender’s share balance). This allows an attacker contract’s fallback to reenter and trigger further withdrawals.  
• Location: In CrossFunctionReentrancy.sol, function withdraw() in contract CrossFunctionReentrancyVulnerable.  
• Potential impact: An attacker can drain the contract by repeatedly withdrawing funds before the share balance is set to zero.  
• Recommended fix: Always follow the “checks–effects–interactions” pattern; update the state (set shares[msg.sender] = 0) before performing the external call. Alternatively, use a ReentrancyGuard.

3. Logic Issues with Forced ETH (Force Send) (THREAT LEVEL: HIGH)  
• Description: ForceSendVulnerable’s game logic depends on the contract’s ETH balance to designate a “winner.” However, an attacker (via selfdestruct in ForceSendAttacker) can force Ether into the contract, thereby manipulating the balance and game state.  
• Location: In ForceSend.sol, function deposit() in contract ForceSendVulnerable.  
• Potential impact: The attacker might trigger the winning condition without following the intended “1 Ether per deposit” mechanism or spoil the game for honest participants.  
• Recommended fix: Do not rely solely on the raw balance to track game progress. Use an internal counter (or mapping) to track the number of deposits instead of inferring it from the contract’s balance.
```

Summary:
- 1. Search for vulnerabilities in the codebase
- 2. Remove the known vulnerabilities from the list of findings
- 3. Return the unique findings
      
Output:

"""