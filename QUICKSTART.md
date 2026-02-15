# 🚀 Quick Start Guide

Get your Archestra.ai Data Transformation project running in 5 minutes!

## Architecture Overview

This project uses a **multi-agent architecture** for data transformation:

```
┌─────────────────────────────────────┐
│   Data Transformer Agent            │
│   (Root Orchestrator)                │
│   - Coordinates ETL workflow         │
│   - Delegates to sub-agents          │
│   - Handles data transformation      │
└──────────┬──────────────────────────┘
           │
           ├──────────────┬─────────────────┐
           │              │                 │
           ▼              ▼                 ▼
┌──────────────────┐ ┌──────────────────┐
│ Elasticsearch    │ │ PostgreSQL       │
│ Explorer Agent   │ │ Database Agent   │
│ (Sub-agent)      │ │ (Sub-agent)      │
├──────────────────┤ ├──────────────────┤
│ • Search data    │ │ • Query tables   │
│ • Export records │ │ • Insert data    │
│ • Inspect schema │ │ • Manage schema  │
└────────┬─────────┘ └──────────┬───────┘
         │                      │
         ▼                      ▼
┌────────────────┐    ┌─────────────────┐
│ Elasticsearch  │    │ PostgreSQL      │
│ MCP Server     │    │ MCP Server      │
└────────────────┘    └─────────────────┘
```

## Prerequisites Check

✅ Docker Desktop running  
✅ LLM API key ready (OpenAI, Anthropic, Gemini, or Cerebras)  
✅ 8GB RAM available  
✅ 10GB disk space  

## Step-by-Step Setup

### 1. Start the Platform (2 minutes)

```powershell
# Navigate to project
cd c:\Users\imart\Desktop\archestra-proj

# Start all services
docker-compose up -d

# Watch initialization (optional)
docker-compose logs -f

# Wait for "Elasticsearch initialization completed!" message
# Then Ctrl+C to stop watching logs
```

**Verify:**
```powershell
docker-compose ps
# All services should show "Up" status
```

### 2. Verify Services (1 minute)

**Run verification script:**
```powershell
.\scripts\verify-setup.ps1
```

**Check manually:**
- Archestra UI: http://localhost:3000 ✅
- Elasticsearch: http://localhost:9200 ✅
- Kibana: http://localhost:5601 ✅
- pgAdmin: http://localhost:5050 ✅

### 3. Configure Archestra (2 minutes)

**3.1 Add LLM API Key:**
1. Open http://localhost:3000
2. Go to **Settings** → **LLM API Keys**
3. Click **Add New**
4. Select your provider (e.g., OpenAI)
5. Enter API key
6. Click **Test Connection** → **Save**

**3.2 Register MCP Servers:**

**For Elasticsearch MCP:**
1. Go to **MCP Registry** → **Add New**
2. Name: `elasticsearch-mcp`
3. Type: **Build from Directory**
4. Path: `./mcp-servers/elasticsearch-mcp`
5. Click **Build & Deploy**
6. Wait ~30 seconds for Kubernetes pod to start
7. Verify status: **Running** ✅

**For PostgreSQL MCP:**
1. Go to **MCP Registry** → **Add New**
2. Name: `postgres-mcp`
3. Type: **Build from Directory**
4. Path: `./mcp-servers/postgres-mcp`
5. Click **Build & Deploy**
6. Wait ~30 seconds
7. Verify status: **Running** ✅

**3.3 Create Agents (3 agents required):**

**Important:** This project uses a multi-agent architecture:
- **Data Transformer Agent** (Root/Orchestrator) - Coordinates the ETL process
- **Elasticsearch Explorer Agent** (Sub-agent) - Handles Elasticsearch operations  
- **PostgreSQL Database Agent** (Sub-agent) - Handles PostgreSQL operations

**Create Agent 1: Elasticsearch Explorer Agent**
1. Go to **Agents** → **Create New**
2. Name: `Elasticsearch Explorer Agent`
3. Description: `Specialized agent for Elasticsearch data exploration and search`
4. System Prompt: Copy from `agents/elasticsearch-agent.json` file
5. Select Model: **GPT-4** (or your configured model)
6. **Enable Tools**: ✅ Select all tools from `elasticsearch-mcp.*`
7. Temperature: `0.1`
8. Max Tokens: `3000`
9. Click **Save**

**Create Agent 2: PostgreSQL Database Agent**
1. Go to **Agents** → **Create New**
2. Name: `PostgreSQL Database Agent`
3. Description: `Specialized agent for PostgreSQL database operations`
4. System Prompt: Copy from `agents/postgres-agent.json` file
5. Select Model: **GPT-4**
6. **Enable Tools**: ✅ Select all tools from `postgres-mcp.*`
7. Temperature: `0.1`
8. Max Tokens: `3000`
9. Click **Save**

**Create Agent 3: Data Transformer Agent (Orchestrator)**
1. Go to **Agents** → **Create New**
2. Name: `Data Transformer Agent`
3. Description: `Orchestrator agent that coordinates data transformation`
4. System Prompt: Copy from `agents/data-transformer-agent.json` file
5. Select Model: **GPT-4**
6. **Enable Sub-Agents**:
   - ✅ Select `Elasticsearch Explorer Agent`
   - ✅ Select `PostgreSQL Database Agent`
7. **Enable Tools**: None (delegates to sub-agents)
8. Temperature: `0.1`
9. Max Tokens: `4000`
10. Click **Save**

### 4. Run Your First Transformation! (30 seconds)

1. Go to **Chat**
2. Select **Data Transformer Agent** from dropdown
3. Type:
   ```
   Transform all products from Elasticsearch to PostgreSQL
   ```
4. Press **Send**
5. Watch the magic happen! 🎉

**What you'll see:**
- Agent discovers indices and schemas
- Exports 15 products from Elasticsearch
- Transforms data types and field names
- Bulk inserts into PostgreSQL
- Verifies and reports results

### 5. Verify Results (1 minute)

**Option A: Run test script**
```powershell
pip install elasticsearch psycopg2-binary
python tests/test-transformation.py
```

**Option B: Check UI**

**Kibana (Source Data):**
1. Open http://localhost:5601
2. Click **☰ Menu** → **Dev Tools**
3. Run query:
   ```json
   GET /products/_search
   ```
4. See 15 products ✅

**pgAdmin (Transformed Data):**
1. Open http://localhost:5050
2. Login: `admin@admin.com` / `admin123`
3. **Add New Server**:
   - Name: `Local PostgreSQL`
   - Host: `postgres`
   - Port: `5432`
   - Username: `admin`
   - Password: `admin123`
   - Database: `transformation_db`
4. Navigate: **Servers** → **Local PostgreSQL** → **Databases** → **transformation_db** → **Schemas** → **public** → **Tables** → **products**
5. Right-click → **View/Edit Data** → **All Rows**
6. See 15+ products ✅

## Success Indicators

✅ **Archestra UI** - Accessible at http://localhost:3000  
✅ **2 MCP Servers** - Both showing "Running" status  
✅ **3 Agents** - Data Transformer (orchestrator), Elasticsearch Explorer, PostgreSQL Database  
✅ **15 documents** - In Elasticsearch products index  
✅ **15+ rows** - In PostgreSQL products table  
✅ **Agent execution** - Successfully transformed data via delegation  

## Troubleshooting

### Issue: Docker containers won't start
```powershell
# Restart Docker Desktop
# Then retry:
docker-compose down
docker-compose up -d
```

### Issue: MCP servers not building
```powershell
# Check Docker socket mount
docker-compose down
# Edit docker-compose.yml if needed on Windows:
# Change: /var/run/docker.sock:/var/run/docker.sock
# To: //var/run/docker.sock://var/run/docker.sock
docker-compose up -d
```

### Issue: Elasticsearch not initializing
```powershell
# Check logs
docker logs elasticsearch

# Manually initialize
docker exec -it elasticsearch sh /usr/local/bin/init-elasticsearch.sh
```

### Issue: Agent not using tools
- Ensure all tools are enabled (checkboxes) in agent config
- Use GPT-4 or equivalent (GPT-3.5 may struggle)
- Try re-phrasing: "Use Elasticsearch and PostgreSQL tools to transform product data"

## What's Next?

✨ **Experiment with agents:**

**With Data Transformer Agent (orchestrator):**
- "Transform all products from Elasticsearch to PostgreSQL"
- "Transform only products with price > $100"
- "Migrate electronics category to PostgreSQL"

**Directly with Elasticsearch Explorer Agent:**
- "Show me the schema of the products index"
- "Search for products with ratings above 4.5"
- "Export all products in the Electronics category"

**Directly with PostgreSQL Database Agent:**
- "Show me the schema of the products table"
- "Count products by category"
- "Insert a new product with these details..."

🏗️ **Multi-Agent Architecture Benefits:**
- **Separation of concerns** - Each agent specializes in one system
- **Reusability** - Use Elasticsearch/PostgreSQL agents independently
- **Maintainability** - Update one agent without affecting others
- **Scalability** - Easily add new data sources as sub-agents

🔧 **Customize:**
- Edit orchestrator logic in `agents/data-transformer-agent.json`
- Modify sub-agent prompts for specialized behavior
- Add new transformation rules

🚀 **Advanced:**
- Create MCP Gateway for external access
- Connect to Claude Code
- Schedule transformations
- Add new data sources

## Support

- 📚 [Full README](README.md)
- 🏗️ [Architecture Docs](ARCHITECTURE.md)
- 💬 [Archestra Community Slack](https://join.slack.com/t/archestra-community/shared_invite/zt-2v2gsjn4p-OqIYN7xR8PqnFLvpQBqBXw)
- 🌐 [Archestra Documentation](https://archestra.ai/docs)

---

**Estimated Total Time**: 5-7 minutes  
**Difficulty**: Beginner  
**Result**: Fully functional AI-powered ETL pipeline! 🎉
