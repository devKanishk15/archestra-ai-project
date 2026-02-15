# Archestra MCP Server Configuration Guide

This guide shows you how to add your self-hosted MCP servers to Archestra.ai's MCP Registry.

## Step 1: Build and Start MCP Servers

First, build and start the MCP server containers:

```bash
cd ~/Desktop/archestra-proj
docker-compose up -d --build elasticsearch-mcp postgres-mcp
```

Verify they're running:
```bash
docker ps | grep mcp
```

You should see:
- `elasticsearch-mcp`
- `postgres-mcp`

## Step 2: Add to Archestra MCP Registry

Open Archestra UI at http://localhost:3000, go to **Settings → MCP Registry**, and click **"Add MCP Server to the Private Registry"**.

### Configuration for Elasticsearch MCP Server

**Tab: Self-hosted (orchestrated by Archestra in K8s)**

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** * | `Elasticsearch MCP Server` |
| **Command** * | `python` |
| **Docker Image (optional)** | `elasticsearch-mcp:latest` |
| **Arguments (one per line)** | `/app/server.py` |
| **Environment Variables** | Click "+ Add Variable"<br>Key: `ELASTICSEARCH_URL`<br>Value: `http://elasticsearch:9200` |
| **Secret Files** | (Leave empty) |
| **Transport Type** | ● stdio (default) |

**Notes:**
- The Docker image will be built from your local `mcp-servers/elasticsearch-mcp` directory
- Archestra will run this in its embedded Kubernetes cluster
- The `ELASTICSEARCH_URL` points to the Elasticsearch container on the Docker network

### Configuration for PostgreSQL MCP Server

**Tab: Self-hosted (orchestrated by Archestra in K8s)**

Fill in the form:

| Field | Value |
|-------|-------|
| **Name** * | `PostgreSQL MCP Server` |
| **Command** * | `python` |
| **Docker Image (optional)** | `postgres-mcp:latest` |
| **Arguments (one per line)** | `/app/server.py` |
| **Environment Variables** | Click "+ Add Variable" for each:<br><br>Key: `POSTGRES_HOST`<br>Value: `postgres-db`<br><br>Key: `POSTGRES_PORT`<br>Value: `5432`<br><br>Key: `POSTGRES_DB`<br>Value: `transformation_db`<br><br>Key: `POSTGRES_USER`<br>Value: `admin`<br><br>Key: `POSTGRES_PASSWORD`<br>Value: `admin123` |
| **Secret Files** | (Leave empty) |
| **Transport Type** | ● stdio (default) |

## Step 3: Build Docker Images for Archestra

Archestra needs to access the Docker images. Build them with proper tags:

```bash
# Build Elasticsearch MCP
cd ~/Desktop/archestra-proj/mcp-servers/elasticsearch-mcp
docker build -t elasticsearch-mcp:latest .

# Build PostgreSQL MCP
cd ~/Desktop/archestra-proj/mcp-servers/postgres-mcp
docker build -t postgres-mcp:latest .

# Verify images exist
docker images | grep mcp
```

## Step 4: Alternative - Use Container References

If Archestra cannot find the images, you can reference the running containers directly:

### Option A: Use Image Name

In the **Docker Image** field, use:
- `elasticsearch-mcp:latest`
- `postgres-mcp:latest`

### Option B: Use Full Command (No Docker Image)

Leave **Docker Image** empty and use:

**For Elasticsearch MCP:**
- Command: `docker`
- Arguments (one per line):
  ```
  exec
  -i
  elasticsearch-mcp
  python
  /app/server.py
  ```

**For PostgreSQL MCP:**
- Command: `docker`
- Arguments (one per line):
  ```
  exec
  -i
  postgres-mcp
  python
  /app/server.py
  ```

## Step 5: Verify MCP Servers in Registry

After adding both servers:

1. Go to **MCP Registry → Registry** tab
2. You should see both servers listed:
   - ✅ Elasticsearch MCP Server
   - ✅ PostgreSQL MCP Server
3. Click on each to verify status shows "Available"

## Step 6: Enable Tools in Agent

When creating the **Data Transformer Agent**:

1. Go to **Agents** → Create New Agent
2. Name it `Data Transformer Agent`
3. In the **Tools** section, enable ALL tools from:
   - `elasticsearch-mcp.*` (all 6 tools)
   - `postgres-mcp.*` (all 7 tools)
4. Copy the system prompt from `agents/data-transformer-agent.json`
5. Save the agent

## Quick Reference

### Environment Variables Summary

**Elasticsearch MCP:**
```
ELASTICSEARCH_URL=http://elasticsearch:9200
```

**PostgreSQL MCP:**
```
POSTGRES_HOST=postgres-db
POSTGRES_PORT=5432
POSTGRES_DB=transformation_db
POSTGRES_USER=admin
POSTGRES_PASSWORD=admin123
```

### Docker Network

All services run on the `archestra-network` Docker network, so they can communicate using container names:
- `elasticsearch` (Elasticsearch service)
- `postgres-db` (PostgreSQL service)
- `archestra-platform` (Archestra service)

## Troubleshooting

### Server Not Found
If Archestra can't find the Docker images:
```bash
# Make sure images are built
docker build -t elasticsearch-mcp:latest ./mcp-servers/elasticsearch-mcp
docker build -t postgres-mcp:latest ./mcp-servers/postgres-mcp
```

### Connection Failed
If MCP server can't connect to databases:
- Verify all containers are on same network: `docker network inspect archestra-network`
- Check environment variables are correct
- Ensure database containers are running: `docker ps`

### Tools Not Showing
- Make sure to enable `*` (all tools) for each MCP server
- Refresh the agent creation page
- Check MCP server status in Registry

## Next Steps

Once both MCP servers are added and the agent is created:
1. Open the **Chat** interface
2. Select **Data Transformer Agent**
3. Send: `"Transform all products from Elasticsearch to PostgreSQL"`
4. Watch the agent use MCP tools to complete the transformation!

---

**Need Help?** Check the main [README.md](../README.md) or [QUICKSTART.md](../QUICKSTART.md) for more details.
