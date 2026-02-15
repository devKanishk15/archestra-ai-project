# PostgreSQL MCP Connection Fix

## Problem
When the MCP server (running in Archestra's Kubernetes) tries to connect to PostgreSQL using `host.docker.internal:5432`, it reaches a **different PostgreSQL instance** on your host machine that doesn't have the "admin" user.

## Solutions

### Solution 1: Find Your Host Machine IP (Recommended)

1. **Get your actual IP address:**

```powershell
# Windows
ipconfig | Select-String "IPv4"

# Look for your main network adapter IP (e.g., 192.168.1.100)
```

2. **Update MCP Server Configuration in Archestra:**

Go to **MCP Registry** → **PostgreSQL MCP Server** → **Edit**

Change environment variable:
```
POSTGRES_HOST = 192.168.1.XXX  # Your actual IP from step 1
```

**Example:**
```
POSTGRES_HOST = 192.168.1.100
POSTGRES_PORT = 5432
POSTGRES_DB = transformation_db
POSTGRES_USER = admin
POSTGRES_PASSWORD = admin123
```

### Solution 2: Use Different Port for Docker PostgreSQL

If port 5432 is already used by another PostgreSQL, change the docker-compose port mapping:

1. **Edit docker-compose.yml:**

```yaml
postgres:
  ports:
    - "5433:5432"  # Change host port to 5433
```

2. **Restart container:**
```bash
docker-compose down
docker-compose up -d postgres
```

3. **Update MCP Server in Archestra:**
```
POSTGRES_HOST = host.docker.internal
POSTGRES_PORT = 5433  # Changed port
```

### Solution 3: Connect MCP to Host's PostgreSQL

If you want to use the PostgreSQL on your host machine:

1. **Create the admin user in your host PostgreSQL:**

```sql
-- Connect to your host PostgreSQL (as superuser)
psql -U postgres

-- Create admin user
CREATE USER admin WITH PASSWORD 'admin123';
CREATE DATABASE transformation_db OWNER admin;

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE transformation_db TO admin;
```

2. **Create products table:**

Run the init script: `data/init-postgres.sql`

### Solution 4: Verify Which PostgreSQL is Responding

Check what's running at `host.docker.internal:5432`:

```bash
# From within the MCP container
docker exec postgres-mcp psql -h host.docker.internal -U postgres -l
```

This will show which PostgreSQL instance is responding.

## How to Apply the Fix

### Quick Fix (Recommended):

1. **Get your IP:**
```powershell
ipconfig
# Find your Ethernet/WiFi IPv4 address (e.g., 192.168.1.100)
```

2. **Update in Archestra:**
- Go to **MCP Registry**
- Click **Edit** on PostgreSQL MCP Server
- Change `POSTGRES_HOST` to your IP address (e.g., `192.168.1.100`)
- Click **Save** and **Restart** the MCP server

3. **Test:**
Send to PostgreSQL Database Agent:
```
"List all tables in the database"
```

## Verification

After applying the fix, you should see:

```json
{
  "tables": ["products"]
}
```

Instead of:
```
Error: role "admin" does not exist
```

---

**TL;DR:** Replace `host.docker.internal` with your actual computer's IP address in the PostgreSQL MCP server configuration within Archestra.
