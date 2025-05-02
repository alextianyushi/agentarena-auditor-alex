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
WEBHOOK_SECRET=your_webhook_secret
```

## Usage

### Server Mode

#### ⚠️ Warning ⚠️ - This mode does not work yet. It will be available once Agent4rena is released.

Join the [telegram group](https://t.me/agent4rena) to stay updated with the latest news.

To run the agent in server mode, you need to run the following command:

```bash
audit-agent server
```

By default, the agent will run on port 8000. To use a custom port, you can use the following command:

```bash
audit-agent server --port 8008
```

### Local Mode

Run the agent in local mode to audit a GitHub repository directly.

You can use the following example repository to test out the agent. The results will be saved in JSON format in the specified output file, by default that is `audit.json`.

```bash
audit-agent local --repo https://github.com/andreitoma8/learn-solidity-hacks.git --output audit.json
```

This mode is useful for testing the agent or auditing repositories outside of the Agent4rena platform.

## License

MIT 