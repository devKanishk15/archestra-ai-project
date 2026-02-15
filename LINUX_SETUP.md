# Linux Quick Setup Guide

## Running on Linux

All the scripts are designed to run on Linux. Make sure you're in a **bash terminal** (not PowerShell).

### 1. Start the Platform

```bash
cd ~/Desktop/archestra-proj  # or your project path
docker-compose up -d
```

### 2. Load Sample Data into Elasticsearch

The automated init script may fail if `jq` is not installed. Use this manual script instead:

```bash
chmod +x scripts/load-elasticsearch-data.sh
./scripts/load-elasticsearch-data.sh
```

### 3. Verify Setup

```bash
chmod +x scripts/verify-setup.sh
./scripts/verify-setup.sh
```

### 4. Check Data

**Elasticsearch:**
```bash
curl http://localhost:9200/products/_count?pretty
# Should show 15 documents
```

**PostgreSQL:**
```bash
docker exec -it postgres-db psql -U admin -d transformation_db -c "SELECT COUNT(*) FROM products;"
# Should show 1+ rows
```

### 5. Test Connectivity

**PostgreSQL from host (requires psql client):**
```bash
# Install if needed:
sudo apt-get install postgresql-client  # Ubuntu/Debian
# OR
sudo yum install postgresql              # CentOS/RHEL

# Then test:
PGPASSWORD=admin123 psql -h localhost -U admin -d transformation_db -c "SELECT COUNT(*) FROM products;"
```

### Alternative: Use Docker Exec

If you don't want to install `psql` on your host:

```bash
# PostgreSQL
docker exec -it postgres-db psql -U admin -d transformation_db -c "SELECT * FROM products LIMIT 5;"

# Elasticsearch
docker exec -it elasticsearch curl -X GET "http://localhost:9200/products/_search?pretty"
```

## All-in-One Setup Script

```bash
# Make all scripts executable
chmod +x scripts/*.sh

# Load sample data
./scripts/load-elasticsearch-data.sh

# Verify everything
./scripts/verify-setup.sh
```

## Troubleshooting

### PostgreSQL Connection Failed
This is normal if you don't have the `psql` client installed on your host machine. The database is still working fine inside Docker. Either:
- Install postgresql-client: `sudo apt-get install postgresql-client`
- Or use Docker: `docker exec -it postgres-db psql -U admin -d transformation_db`

### Elasticsearch Has 0 Documents
Run the load script:
```bash
./scripts/load-elasticsearch-data.sh
```

### Permission Denied
Make scripts executable:
```bash
chmod +x scripts/*.sh
```

## Next Steps

Once data is loaded and verified:
1. Open http://localhost:3000 (Archestra UI)
2. Add your LLM API key
3. Register the MCP servers
4. Create the Data Transformer Agent
5. Run your first transformation!
