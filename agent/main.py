#!/usr/bin/env python3
"""
Main entry point for the AI agent that audits Solidity contracts for security vulnerabilities.
"""
import argparse
import sys
from agent.server import start_server
from agent.local import process_local
from agent.config import load_config

def main():
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description="AI Agent for Solidity security auditing")
    parser.add_argument("mode", choices=["server", "local"], help="Run mode: server or local")
    
    # Local mode arguments
    parser.add_argument("--repo", help="GitHub repository URL (required for local mode)")
    parser.add_argument("--output", help="Output file path (for local mode)", default="security_audit_results.txt")
    parser.add_argument("--only-selected-files", action="store_true", help="Display and select specific .sol files to audit")
    
    # Server mode arguments
    parser.add_argument("--host", help="Host for the server (server mode)", default="0.0.0.0")
    parser.add_argument("--port", help="Port for the server (server mode)", type=int, default=8000)
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config()
    
    if args.mode == "server":
        start_server(host=args.host, port=args.port, config=config)
    elif args.mode == "local":
        if not args.repo:
            print("Error: --repo argument is required for local mode")
            parser.print_help()
            sys.exit(1)
        process_local(repo_url=args.repo, output_path=args.output, config=config, only_selected=args.only_selected_files)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()