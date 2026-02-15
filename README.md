# Archestra.ai Data Transformation Hackathon Project

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Docker](https://img.shields.io/badge/docker-required-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

An intelligent data transformation tool built with **Archestra.ai** that uses AI agents and MCP (Model Context Protocol) servers to extract data from Elasticsearch, transform it, and load it into PostgreSQL.

## 🎯 Project Overview

This hackathon project demonstrates the power of Archestra.ai by creating an autonomous agent that:
- **Extracts** data from Elasticsearch using custom MCP server
- **Transforms** data according to schema requirements
- **Loads** data into PostgreSQL using custom MCP server
- **Validates** data integrity and reports results

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Archestra.ai Platform                │
│  ┌──────────────────────────────────────────────────┐  │
│  │         Data Transformer Agent (LLM)             │  │
│  └──────────────┬───────────────┬───────────────────┘  │
│                 │               │                       │
│        ┌────────▼─────┐  ┌─────▼──────────┐           │
│        │ ES MCP Server│  │ PG MCP Server  │           │
│        └────────┬─────┘  └─────┬──────────┘           │
└─────────────────┼───────────────┼──────────────────────┘
                  │               │
        ┌─────────▼─────┐  ┌─────▼──────────┐
        │ Elasticsearch │  │   PostgreSQL   │
        │  (Products)   │  │  (Products)    │
        └───────────────┘  └────────────────┘
```

## ✨ Features

- **🤖 AI-Powered Transformation**: Intelligent agent that understands schemas and performs smart data mapping
- **🔌 MCP Integration**: Custom MCP servers for Elasticsearch and PostgreSQL
- **📊 Sample Data**: Pre-loaded e-commerce product catalog (15 products)
- **🎨 Admin UIs**: Kibana for Elasticsearch, pgAdmin for PostgreSQL
- **✅ Verification Tools**: Automated testing and validation scripts
- **🐳 Docker Everything**: Complete Docker Compose setup for easy deployment

## 📋 Prerequisites

- **Docker Desktop** (Windows/Mac) or Docker Engine (Linux)
- **LLM API Key** - Choose one:
  - OpenAI (GPT-4, GPT-3.5)
  - Anthropic (Claude)
  - Google Gemini
  - Cerebras (Free tier available)
  - Local Ollama instance
- **Python 3.8+** (for testing scripts)
- **Git** (to clone the repository)

## 🚀 Quick Start

### 1. Start the Platform

```powershell
# Navigate to project directory
cd c:\Users\imart\Desktop\archestra-proj

# Start all services
docker-compose up -d

# Wait for initialization (2-3 minutes)
# Check status
docker-compose ps
```

### 2. Verify Setup

**Windows:**
```powershell
.\scripts\verify-setup.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/verify-setup.sh
./scripts/verify-setup.sh
```

### 3. Configure Archestra

1. **Access Archestra UI**: http://localhost:3000

2. **Add LLM API Key**:
   - Go to **Settings** → **LLM API Keys**
   - Add your preferred provider key
   - Test the connection

3. **Register MCP Servers**:
   - Go to **MCP Registry** → **Add New**
   - **Elasticsearch MCP**:
     - Name: `elasticsearch-mcp`
     - Build from local directory: `./mcp-servers/elasticsearch-mcp`
     - Wait for Kubernetes deployment
   - **PostgreSQL MCP**:
     - Name: `postgres-mcp`
     - Build from local directory: `./mcp-servers/postgres-mcp`
     - Wait for Kubernetes deployment

4. **Create Agent**:
   - Go to **Agents** → **Create New**
   - Name: `Data Transformer Agent`
   - Copy system prompt from `agents/data-transformer-agent.json`
   - **Enable all tools** from both MCP servers:
     - ✅ elasticsearch-mcp: all tools
     - ✅ postgres-mcp: all tools
   - Select your LLM model
   - Save agent

### 4. Run Transformation

1. Go to **Chat** interface
2. Select **Data Transformer Agent**
3. Send message:
   ```
   Transform all products from Elasticsearch to PostgreSQL
   ```
4. Watch the agent work! It will:
   - Discover source data in Elasticsearch
   - Analyze schemas
   - Extract documents
   - Transform data types
   - Bulk insert into PostgreSQL
   - Verify and report results

### 5. Verify Results

**Run test script:**
```powershell
pip install elasticsearch psycopg2-binary
python tests/test-transformation.py
```

**Check UIs:**
- **Kibana**: http://localhost:5601 (view source data)
- **pgAdmin**: http://localhost:5050 (view transformed data)
  - Login: `admin@admin.com` / `admin123`
  - Add server: host=`postgres`, port=`5432`, user=`admin`, password=`admin123`

## 🧪 Testing

### Automated Tests

```powershell
# Install dependencies
pip install -r tests/requirements.txt

# Run tests
python tests/test-transformation.py
```

### Manual Testing

**Test Elasticsearch:**
```bash
curl http://localhost:9200/products/_search?pretty
```

**Test PostgreSQL:**
```powershell
# Connect via pgAdmin at http://localhost:5050
# Or use psql:
docker exec -it postgres-db psql -U admin -d transformation_db -c "SELECT * FROM products LIMIT 5;"
```

## 📁 Project Structure

```
archestra-proj/
├── docker-compose.yml          # Multi-container orchestration
├── data/
│   ├── sample-data.json        # 15 sample products
│   ├── init-postgres.sql       # PostgreSQL schema
│   └── init-elasticsearch.sh   # Elasticsearch initialization
├── mcp-servers/
│   ├── elasticsearch-mcp/
│   │   ├── server.py          # MCP server implementation
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   └── postgres-mcp/
│       ├── server.py          # MCP server implementation
│       ├── Dockerfile
│       └── requirements.txt
├── agents/
│   └── data-transformer-agent.json  # Agent configuration
├── scripts/
│   ├── verify-setup.ps1       # Windows verification
│   └── verify-setup.sh        # Linux/Mac verification
├── tests/
│   └── test-transformation.py # Automated tests
├── README.md
└── ARCHITECTURE.md
```

## 🔧 Configuration

### Environment Variables

**Elasticsearch MCP Server:**
- `ELASTICSEARCH_URL` (default: `http://elasticsearch:9200`)

**PostgreSQL MCP Server:**
- `POSTGRES_HOST` (default: `postgres`)
- `POSTGRES_PORT` (default: `5432`)
- `POSTGRES_DB` (default: `transformation_db`)
- `POSTGRES_USER` (default: `admin`)
- `POSTGRES_PASSWORD` (default: `admin123`)

### Ports

| Service | Port | Description |
|---------|------|-------------|
| Archestra UI | 3000 | Web interface |
| Archestra API | 9000 | REST API |
| Elasticsearch | 9200 | HTTP API |
| Kibana | 5601 | Elasticsearch UI |
| PostgreSQL | 5432 | Database |
| pgAdmin | 5050 | PostgreSQL UI |

## 🎓 How It Works

### Data Flow

1. **Agent receives request**: "Transform products from Elasticsearch to PostgreSQL"

2. **Discovery phase**:
   - Agent calls `list_indices` to find Elasticsearch indices
   - Agent calls `get_mapping` to understand source schema
   - Agent calls `get_schema` to understand target schema

3. **Extraction phase**:
   - Agent calls `bulk_export` to retrieve all documents from Elasticsearch

4. **Transformation phase**:
   - Agent maps fields between schemas
   - Converts data types (ES arrays → PG arrays, dates, etc.)
   - Handles special fields like tags

5. **Loading phase**:
   - Agent calls `bulk_insert` with transformed data
   - Uses conflict resolution for duplicates

6. **Verification phase**:
   - Agent calls `count_rows` to verify insertion
   - Compares with source count
   - Reports success/failure

### MCP Servers

**Elasticsearch MCP Tools:**
- `search_documents` - Query with DSL
- `get_document` - Retrieve by ID
- `list_indices` - Discovery
- `get_mapping` - Schema inspection
- `bulk_export` - Batch export
- `count_documents` - Count matching docs

**PostgreSQL MCP Tools:**
- `execute_query` - Run SELECT queries
- `insert_data` - Single row insert
- `bulk_insert` - Batch insert with conflict resolution
- `get_schema` - Table schema inspection
- `list_tables` - Discovery
- `count_rows` - Count table rows

## 🐛 Troubleshooting

### Containers won't start
```powershell
# Check Docker is running
docker info

# Check logs
docker-compose logs

# Restart containers
docker-compose restart
```

### Elasticsearch not initializing
```powershell
# Check Elasticsearch logs
docker logs elasticsearch

# Manually run init script
docker exec -it elasticsearch sh /usr/local/bin/init-elasticsearch.sh
```

### MCP servers not registering
- Ensure Docker socket is mounted
- Check Archestra has access to build MCP server images
- Verify Kubernetes pods: `kubectl get pods` (from within Archestra container)

### Agent not using tools
- Verify tools are enabled in agent configuration
- Check LLM API key is valid
- Try with a more capable model (GPT-4 recommended)

## 🌟 Advanced Features

### MCP Gateway

Create an MCP Gateway to expose the agent to external tools like Claude Code:

1. Go to **MCP Gateways** → **Create New**
2. Add **Data Transformer Agent** as sub-agent
3. Copy MCP configuration
4. Add to Claude:
   ```bash
   claude mcp add archestra "http://localhost:9000/v1/mcp/YOUR-ID" \
     --transport http \
     --header "Authorization: Bearer YOUR-TOKEN"
   ```

### Custom Transformations

Modify the agent's system prompt in `agents/data-transformer-agent.json` to:
- Add custom field mappings
- Implement data validation rules
- Add business logic transformations

## 📚 Resources

- [Archestra.ai Documentation](https://archestra.ai/docs)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

## 🤝 Contributing

This is a hackathon project, but contributions are welcome!

## 📝 License

MIT License - feel free to use this for your own projects!

## 🙏 Acknowledgments

- **Archestra.ai** team for the amazing platform
- **Anthropic** for the MCP protocol
- The open-source community

---

Built with ❤️ using Archestra.ai for the hackathon
