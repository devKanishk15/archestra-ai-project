# Quick Reference: Add MCP Servers to Archestra

## 🌐 Platform Access

| Service              | URL                          |
|----------------------|------------------------------|
| Archestra UI         | http://localhost:3000         |
| Archestra API        | http://localhost:9000         |
| Kibana               | http://localhost:5601         |
| pgAdmin              | http://localhost:5050         |
| Elasticsearch        | http://localhost:9200         |
| PostgreSQL           | `localhost:5433`              |

---

## 🔧 LLM Configuration

The Archestra platform uses a **LiteLLM-compatible** endpoint (OpenAI-compatible `/v1` API):

| Variable                       | Value                                  |
|--------------------------------|----------------------------------------|
| `ARCHESTRA_VLLM_BASE_URL`     | Set in `.env` file                     |
| `ARCHESTRA_CHAT_VLLM_API_KEY` | Set in `.env` file                     |

> **Note**: Configure these values in your `.env` file. See `.env.example` for template.

---

## ➕ Add MCP Servers to Archestra Registry

Go to: **http://localhost:3000 → Settings → MCP Registry → "+ Add MCP Server"**

Select Tab: **"Self-hosted (orchestrated by Archestra in K8s)"**

---

### Elasticsearch MCP Server

```
Name:         Elasticsearch MCP Server
Command:      python
Docker Image: devkanishk15/elasticsearch-mcp:latest

Arguments (one per line):
    /app/server.py

Environment Variables:
    ELASTICSEARCH_URL = http://host.docker.internal:9200

Transport Type: ● stdio (default)
```

**Available Tools:**

| Tool                | Description                                        |
|---------------------|----------------------------------------------------|
| `search_documents`  | Search documents using Elasticsearch Query DSL      |
| `get_document`      | Retrieve a specific document by ID                 |
| `list_indices`      | List all available indices                         |
| `get_mapping`       | Get index mapping (schema)                         |
| `bulk_export`       | Export documents in batches using scroll API        |
| `count_documents`   | Count documents matching a query                   |

---

### PostgreSQL MCP Server

```
Name:         PostgreSQL MCP Server
Command:      python
Docker Image: devkanishk15/postgres-mcp:latest

Arguments (one per line):
    /app/server.py

Environment Variables:
    POSTGRES_HOST     = host.docker.internal
    POSTGRES_PORT     = 5433
    POSTGRES_DB       = transformation_db
    POSTGRES_USER     = admin
    POSTGRES_PASSWORD = admin123

Transport Type: ● stdio (default)
```

**Available Tools:**

| Tool                 | Description                                               |
|----------------------|-----------------------------------------------------------|
| `execute_query`      | Execute SELECT queries (read-only)                        |
| `execute_write_query`| Execute INSERT, UPDATE, DELETE queries (no DDL)           |
| `insert_data`        | Insert a single row into a table                          |
| `bulk_insert`        | Batch insert multiple rows with conflict resolution       |
| `get_schema`         | Get table schema (columns, types, constraints)            |
| `list_tables`        | List all tables in the database                           |
| `create_table`       | Create a new table with specified columns                 |
| `count_rows`         | Count rows with optional WHERE clause                     |

---

## 🔗 Networking Notes

> **Important:** Use `host.docker.internal` for MCP server environment variables because Archestra deploys MCP servers inside its internal Kubernetes cluster. The MCP pods need `host.docker.internal` to reach services exposed on the Docker host.

**Port Reference:**

| Service         | Internal Port (container-to-container)  | Host-Exposed Port (your machine) |
|-----------------|-----------------------------------------|----------------------------------|
| PostgreSQL      | `5432`                                  | `5433`                           |
| Elasticsearch   | `9200`                                  | `9200`                           |
| Archestra API   | `9000`                                  | `9000`                           |
| Archestra UI    | `3000`                                  | `3000`                           |
| Kibana          | `5601`                                  | `5601`                           |
| pgAdmin         | `80`                                    | `5050`                           |

---

## ✅ Verify

After adding both MCP servers:
1. Go to **MCP Registry → Registry** tab
2. Both servers should show as **"Available"**
3. Check pods are running: `docker exec archestra-mcp-control-plane kubectl get pods`

---

## 🤖 Create Agents

### 1. Elasticsearch Explorer Agent

1. Go to **Agents** → "+ Create Agent"
2. Name: `Elasticsearch Explorer Agent`
3. Enable tools: `elasticsearch-mcp.*`
   - `search_documents`, `get_document`, `list_indices`, `get_mapping`, `bulk_export`, `count_documents`
4. Paste system prompt from [`agents/elasticsearch-agent.yaml`](./agents/elasticsearch-agent.yaml)

### 2. PostgreSQL Database Agent

1. Go to **Agents** → "+ Create Agent"
2. Name: `PostgreSQL Database Agent`
3. Enable tools: `postgres-mcp.*`
   - `execute_query`, `execute_write_query`, `insert_data`, `bulk_insert`, `get_schema`, `list_tables`, `create_table`, `count_rows`
4. Paste system prompt from [`agents/postgres-agent.yaml`](./agents/postgres-agent.yaml)

### 3. Data Transformer Agent (Orchestrator)

1. Go to **Agents** → "+ Create Agent"
2. Name: `Data Transformer Agent`
3. Enable tools: **both** `elasticsearch-mcp.*` and `postgres-mcp.*`
4. Paste system prompt from [`agents/data-transformer-agent.yaml`](./agents/data-transformer-agent.yaml)

---

## 🎉 Test

1. Open **Chat**
2. Select an agent (e.g., `PostgreSQL Database Agent`)
3. Try: `What tables do we have in the database?`
4. Or select `Data Transformer Agent` and try: `Transform all products from Elasticsearch to PostgreSQL`

> **Tip:** If you see "No running pod found for MCP server deployment", wait 1–2 minutes after redeploying for the internal K8s pods to initialize, then retry.

---

## 🐳 Docker Images

| MCP Server      | Image                                    |
|-----------------|------------------------------------------|
| Elasticsearch   | `devkanishk15/elasticsearch-mcp:latest`  |
| PostgreSQL      | `devkanishk15/postgres-mcp:latest`       |

**Rebuild & push (if making changes):**
```bash
docker build -t devkanishk15/postgres-mcp:latest ./mcp-servers/postgres-mcp
docker push devkanishk15/postgres-mcp:latest

docker build -t devkanishk15/elasticsearch-mcp:latest ./mcp-servers/elasticsearch-mcp
docker push devkanishk15/elasticsearch-mcp:latest
```
