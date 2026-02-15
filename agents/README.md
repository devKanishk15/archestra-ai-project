# Agent Configurations

This directory contains agent configurations for the Archestra.ai platform. Each agent is specialized for specific tasks and has access to relevant MCP tools.

## Available Agents

### 1. Data Transformer Agent
**File:** `data-transformer-agent.json`

**Purpose:** End-to-end ETL pipeline agent that transforms data from Elasticsearch to PostgreSQL.

**Tools:** 
- All Elasticsearch MCP tools (6 tools)
- All PostgreSQL MCP tools (7 tools)

**Use Cases:**
- Migrating data between systems
- Data transformation and normalization
- Schema mapping and type conversions
- Bulk data transfers

**Key Features:**
- Understands both source and target schemas
- Performs intelligent field mapping
- Handles data type conversions
- Provides progress reporting and verification

---

### 2. Elasticsearch Explorer Agent
**File:** `elasticsearch-agent.json`

**Purpose:** Specialized agent for exploring and analyzing Elasticsearch indices.

**Tools:** 
- Elasticsearch MCP tools only (6 tools)

**Use Cases:**
- Data discovery and exploration
- Complex search queries
- Index analysis
- Data export operations

**Key Features:**
- Expert in Elasticsearch Query DSL
- Schema inspection and analysis
- Efficient bulk export
- Educational explanations of queries

---

### 3. PostgreSQL Database Agent
**File:** `postgres-agent.json`

**Purpose:** Specialized agent for PostgreSQL database operations.

**Tools:** 
- PostgreSQL MCP tools only (7 tools)

**Use Cases:**
- SQL query generation
- Data insertion and updates
- Schema management
- Database analysis

**Key Features:**
- Expert in SQL and PostgreSQL
- Safe query execution (SELECT only for execute_query)
- Bulk insert optimization
- Data validation and integrity

---

## How to Use These Agents in Archestra

### Step 1: Add MCP Servers
First, ensure both MCP servers are registered in Archestra's MCP Registry:
- Elasticsearch MCP Server (`devkanishk/elasticsearch-mcp:latest`)
- PostgreSQL MCP Server (`devkanishk/postgres-mcp:latest`)

See [MCP_QUICK_REF.md](../MCP_QUICK_REF.md) for configuration details.

### Step 2: Create Agents in Archestra UI

For each agent:

1. Go to **Agents** → **"+ Create Agent"**
2. Copy the configuration from the corresponding JSON file
3. Set these fields:
   - **Name:** From `name` field in JSON
   - **Description:** From `description` field in JSON
   - **System Prompt:** From `system_prompt` field in JSON
   - **Model:** From `model_config.model` (e.g., gpt-4)
   - **Temperature:** From `model_config.temperature` (e.g., 0.1)
   - **Max Tokens:** From `model_config.max_tokens`
4. **Enable Tools:**
   - For Data Transformer Agent: Enable `elasticsearch-mcp.*` AND `postgres-mcp.*`
   - For Elasticsearch Agent: Enable `elasticsearch-mcp.*` only
   - For PostgreSQL Agent: Enable `postgres-mcp.*` only
5. Save the agent

### Step 3: Test the Agents

**Data Transformer Agent:**
```
Transform all products from Elasticsearch to PostgreSQL
```

**Elasticsearch Explorer Agent:**
```
What indices do we have? Show me 5 sample products.
```

**PostgreSQL Database Agent:**
```
Show me the schema for the products table and count how many rows we have.
```

---

## Agent Selection Guide

**Choose Data Transformer Agent when:**
- Moving data between Elasticsearch and PostgreSQL
- Need to transform data schemas
- Performing ETL operations

**Choose Elasticsearch Explorer Agent when:**
- Exploring Elasticsearch data
- Need complex search queries
- Analyzing index structures
- Exporting Elasticsearch data

**Choose PostgreSQL Database Agent when:**
- Querying PostgreSQL tables
- Inserting or updating data
- Managing database schema
- Performing SQL analytics

---

## Customization

You can customize these agents by:

1. **Modifying System Prompts:** Edit the `system_prompt` field to change agent behavior
2. **Adjusting Temperature:** Lower (0.0-0.3) for deterministic, higher (0.7-1.0) for creative
3. **Changing Models:** Switch between GPT-4, Claude, or other LLMs
4. **Tool Selection:** Enable/disable specific tools based on security requirements

---

## Best Practices

1. **Start Simple:** Test agents with basic queries before complex operations
2. **Monitor Tool Usage:** Check which tools agents are using in chat logs
3. **Refine Prompts:** Adjust system prompts based on agent performance
4. **Security:** Be careful with write operations (insert, bulk_insert, create_table)
5. **Cost Management:** Use appropriate model tiers based on task complexity

---

## Agent Comparison

| Feature | Data Transformer | Elasticsearch Explorer | PostgreSQL Database |
|---------|------------------|----------------------|---------------------|
| **Tools** | Both ES & PG | Elasticsearch only | PostgreSQL only |
| **Complexity** | High | Medium | Medium |
| **Use Case** | ETL Pipeline | Data Exploration | Database Ops |
| **Temperature** | 0.1 | 0.1 | 0.1 |
| **Best For** | Migrations | Searches | Queries |

---

## Troubleshooting

### Agent Not Using Tools
- Verify MCP servers are registered and "Available"
- Check that tools are enabled with `*` wildcard
- Ensure agent has proper permissions

### Unexpected Behavior
- Review system prompt for clarity
- Check temperature setting (too high = inconsistent)
- Verify tool outputs are correct

### Performance Issues
- Reduce max_tokens for faster responses
- Use more specific prompts
- Consider using a faster model (e.g., gpt-3.5-turbo)

---

**For more information, see:**
- [README.md](../README.md) - Project overview
- [QUICKSTART.md](../QUICKSTART.md) - Quick setup guide
- [MCP_QUICK_REF.md](../MCP_QUICK_REF.md) - MCP server configuration
