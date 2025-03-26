# Solidity Audit Agent Template

An AI-powered agent template for auditing Solidity smart contracts using OpenAI models.

## Features

- Audit Solidity contracts for security vulnerabilities
- Security findings classified by threat level (Critical, High, Medium, Low, Informational)
- Two operation modes:
  - **Server mode**: Runs a webhook server to receive notifications from Agent4rena when a new challenge begins
  - **Local mode**: Processes a GitHub repository directly

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/solidity-audit-agent.git
cd solidity-audit-agent

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install the package
pip install -e .

# Create .env file from example
cp .env.example .env
# Edit .env with your configuration
```

## Configuration

Create a `.env` file with the following variables:

```
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=o3-mini
LOG_LEVEL=INFO

# For server mode only
API_BASE_URL=https://api.example.com/v1
WEBHOOK_SECRET=your_webhook_secret
```

## Usage

### Server Mode

Run the agent in server mode to listen for notifications from Agent4rena:

```bash
solidity-audit server --host 0.0.0.0 --port 8000
```

The server exposes the following endpoints:
- `POST /webhook`: Receives notifications from Agent4rena when a new challenge begins
- `GET /health`: Health check endpoint

When Agent4rena sends a notification about a new challenge, the agent will:
1. Fetch the Solidity contracts from the Agent4rena API
2. Perform a security audit on the contracts
3. Send the audit results back to Agent4rena

### Local Mode

Run the agent in local mode to audit a GitHub repository directly:

```bash
audit-agent local --repo https://github.com/andreitoma8/learn-solidity-hacks.git --output audit.txt
```

This mode is useful for testing the agent or auditing repositories outside of the Agent4rena platform.

## License

MIT 