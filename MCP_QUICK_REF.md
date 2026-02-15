# Quick Reference: Add MCP Servers to Archestra

##  Add to Archestra MCP Registry

Go to: **http://localhost:3000 → Settings → MCP Registry → "+ Add MCP Server"**

Select Tab: **"Self-hosted (orchestrated by Archestra in K8s)"**

---

### Elasticsearch MCP Server

```
Name: Elasticsearch MCP Server
Command: python
Docker Image: devkanishk/elasticsearch-mcp:latest
Arguments (one per line):
    /app/server.py

Environment Variables:
    ELASTICSEARCH_URL = http://host.docker.internal:9200

Transport Type: ● stdio (default)
```

---

### PostgreSQL MCP Server

```
Name: PostgreSQL MCP Server
Command: python
Docker Image: devkanishk/postgres-mcp:latest
Arguments (one per line):
    /app/server.py

Environment Variables:
    POSTGRES_HOST = host.docker.internal
    POSTGRES_PORT = 5432
    POSTGRES_DB = transformation_db
    POSTGRES_USER = admin
    POSTGRES_PASSWORD = admin123

Transport Type: ● stdio (default)
```

**Important:** Use `host.docker.internal` instead of `postgres-db` because Archestra runs MCP servers in its Kubernetes cluster, which can't directly access Docker Compose container names. This hostname allows the K8s pod to reach services on your host machine.

**Alternative (if host.docker.internal doesn't work):**
- On Linux: Use your machine's IP address (e.g., `192.168.1.100`)
- Find your IP: `ip addr show` or `hostname -I`

---

## ✅ Verify

After adding both servers, check:
- MCP Registry → Registry tab
- Both servers should show as "Available"

## 🤖 Create Agent

1. Go to **Agents** → "+ Create Agent"
2. Name: `Data Transformer Agent`
3. **Enable all tools** from both servers:
   - `elasticsearch-mcp.*`
   - `postgres-mcp.*`
4. Paste system prompt from `agents/data-transformer-agent.json`
5. Save!

## 🎉 Test

1. Open **Chat**
2. Select "Data Transformer Agent"
3. Send: `Transform all products from Elasticsearch to PostgreSQL`
4. Watch the magic! ✨

---

**Full Details:** See [ARCHESTRA_MCP_CONFIG.md](./ARCHESTRA_MCP_CONFIG.md)
