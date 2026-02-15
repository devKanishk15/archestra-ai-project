# PostgreSQL MCP Server Testing Guide

This guide provides commands to test if your PostgreSQL MCP server is working correctly.

## Prerequisites

Make sure the PostgreSQL MCP container is running:
```bash
docker ps | grep postgres-mcp
```

If not running:
```bash
docker-compose up -d postgres-mcp
```

## Method 1: Automated Test Script (Recommended)

Run the comprehensive test script:

```bash
python scripts/test-postgres-mcp.py
```

**What it tests:**
- ✅ Lists all available tools (7 tools)
- ✅ Lists tables in the database
- ✅ Gets schema for products table
- ✅ Counts rows in products table
- ✅ Executes a SELECT query

## Method 2: Manual Docker Commands

### Test 1: List Available Tools

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}' | \
docker exec -i postgres-mcp python /app/server.py
```

**Expected output:** List of 7 tools (list_tables, get_schema, execute_query, etc.)

### Test 2: List Tables

```bash
echo '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"list_tables","arguments":{}}}' | \
docker exec -i postgres-mcp python /app/server.py
```

**Expected output:** JSON response showing "products" table

### Test 3: Get Table Schema

```bash
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"get_schema","arguments":{"table_name":"products"}}}' | \
docker exec -i postgres-mcp python /app/server.py
```

**Expected output:** Schema with all columns (id, name, category, price, etc.)

### Test 4: Count Rows

```bash
echo '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"count_rows","arguments":{"table_name":"products"}}}' | \
docker exec -i postgres-mcp python /app/server.py
```

**Expected output:** Row count (should be 1 or more)

### Test 5: Execute Query

```bash
echo '{"jsonrpc":"2.0","id":5,"method":"tools/call","params":{"name":"execute_query","arguments":{"query":"SELECT id, name, price FROM products LIMIT 3"}}}' | \
docker exec -i postgres-mcp python /app/server.py
```

**Expected output:** JSON with 3 product rows

### Test 6: Insert Data

```bash
echo '{"jsonrpc":"2.0","id":6,"method":"tools/call","params":{"name":"insert_data","arguments":{"table_name":"products","data":{"id":"TEST-001","name":"Test Product","category":"Test","price":99.99}}}}' | \
docker exec -i postgres-mcp python /app/server.py
```

**Expected output:** Success message with inserted row ID

## Method 3: Test from Archestra UI

Once the MCP server is registered in Archestra:

1. Create a test agent with PostgreSQL MCP tools enabled
2. Send these test prompts:

```
"List all tables in the database"
```

```
"Show me the schema for the products table"
```

```
"Count how many rows are in the products table"
```

```
"Query the first 5 products from the database"
```

## Method 4: Direct Python Test

Create a quick Python test:

```python
import json
import subprocess

# Test list_tables
request = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
        "name": "list_tables",
        "arguments": {}
    }
}

result = subprocess.run(
    ["docker", "exec", "-i", "postgres-mcp", "python", "/app/server.py"],
    input=json.dumps(request) + "\n",
    capture_output=True,
    text=True
)

print(json.dumps(json.loads(result.stdout), indent=2))
```

## Troubleshooting

### Server not responding
```bash
# Check logs
docker logs postgres-mcp

# Restart container
docker-compose restart postgres-mcp
```

### Connection refused
Check environment variables:
```bash
docker exec postgres-mcp env | grep POSTGRES
```

Should show:
```
POSTGRES_HOST=host.docker.internal    # or your IP
POSTGRES_PORT=5432
POSTGRES_DB=transformation_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
```

### Wrong credentials
Verify PostgreSQL is accessible:
```bash
docker exec postgres-db psql -U admin -d transformation_db -c "SELECT 1;"
```

### Tools not found
Rebuild the image:
```bash
docker-compose build postgres-mcp
docker-compose up -d postgres-mcp
```

## Expected Results Summary

| Test | Expected Result |
|------|----------------|
| **List Tools** | 7 tools returned |
| **List Tables** | "products" table found |
| **Get Schema** | 14 columns shown |
| **Count Rows** | 1+ rows |
| **Execute Query** | 3 products returned |
| **Insert Data** | Success message |

## Success Indicators

✅ All JSON-RPC responses have `"result"` field (not `"error"`)  
✅ Tools return data in expected format  
✅ Can connect to PostgreSQL database  
✅ Can query and insert data  
✅ MCP protocol communication works  

---

**Quick Test Command:**
```bash
python scripts/test-postgres-mcp.py
```

If all tests pass, your PostgreSQL MCP server is working correctly! 🎉
