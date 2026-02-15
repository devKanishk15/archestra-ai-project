#!/usr/bin/env python3
"""
Simple test for PostgreSQL MCP Server
Tests by sending JSON-RPC requests via stdin/stdout
"""

import json
import subprocess
import sys

def send_request(request):
    """Send a request to the MCP server and get response"""
    proc = subprocess.Popen(
        ["docker", "exec", "-i", "postgres-mcp", "python", "/app/server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Send request
    stdout, stderr = proc.communicate(json.dumps(request))
    
    if stderr and "warning" not in stderr.lower():
        print(f"STDERR: {stderr}")
    
    # Parse response (multiple JSON objects may be returned)
    responses = []
    for line in stdout.strip().split('\n'):
        if line.strip():
            try:
                responses.append(json.loads(line))
            except json.JSONDecodeError:
                print(f"Could not parse: {line}")
    
    return responses

def main():
    print("🧪 Testing PostgreSQL MCP Server...\n")
    
    # Initialize the server first
    print("=" * 60)
    print("Initializing MCP server...")
    print("=" * 60)
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }
    
    responses = send_request(init_request)
    print(f"✅ Initialize response received: {len(responses)} message(s)")
    if responses:
        print(json.dumps(responses[0], indent=2))
    print()
    
    # Now we can list tools
    print("=" * 60)
    print("Test 1: List available tools")
    print("=" * 60)
    
    tools_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/list",
        "params": {}
    }
    
    responses = send_request(tools_request)
    if responses:
        for response in responses:
            if "result" in response:
                tools = response["result"].get("tools", [])
                print(f"✅ Found {len(tools)} tools:")
                for tool in tools:
                    print(f"   - {tool['name']}: {tool.get('description', '')[:60]}...")
            elif "error" in response:
                print(f"❌ Error: {response['error']}")
    
    print("\n" + "=" * 60)
    print("Note: Full MCP protocol testing requires persistent connection")
    print("For complete testing, use the server within Archestra UI")
    print("=" * 60)

if __name__ == "__main__":
    # Check if postgres-mcp container is running
    result = subprocess.run(
        ["docker", "ps", "--filter", "name=postgres-mcp", "--format", "{{.Names}}"],
        capture_output=True,
        text=True
    )
    
    if "postgres-mcp" not in result.stdout:
        print("❌ postgres-mcp container is not running!")
        print("Start it with: docker-compose up -d postgres-mcp")
        sys.exit(1)
    
    main()
