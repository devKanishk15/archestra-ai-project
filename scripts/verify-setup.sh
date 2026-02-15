#!/bin/bash

# Bash verification script for Linux/macOS
# Verifies Docker containers, services, and data initialization

# Color codes
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
WHITE='\033[1;37m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}==========================================${NC}"
echo -e "${CYAN}ARCHESTRA PROJECT SETUP VERIFICATION${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""

# Check Docker
echo -e "${YELLOW}[1/7] Checking Docker...${NC}"
if command -v docker &> /dev/null; then
    echo -e "  ${GREEN}✓ Docker is installed${NC}"
    
    if docker info &> /dev/null 2>&1; then
        echo -e "  ${GREEN}✓ Docker daemon is running${NC}"
    else
        echo -e "  ${RED}✗ Docker daemon is not running!${NC}"
        exit 1
    fi
else
    echo -e "  ${RED}✗ Docker is not installed!${NC}"
    exit 1
fi

echo ""
echo -e "${YELLOW}[2/7] Checking Docker containers...${NC}"
containers=$(docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "archestra-platform|elasticsearch|postgres-db|kibana|pgadmin" || true)

if [ -z "$containers" ]; then
    echo -e "  ${RED}✗ No project containers are running!${NC}"
    echo -e "  ${YELLOW}→ Run: docker-compose up -d${NC}"
    exit 1
else
    echo "$containers" | sed 's/^/  /'
    
    # Count running containers
    running=$(docker ps --filter "status=running" | grep -E "archestra-platform|elasticsearch|postgres-db" | wc -l)
    if [ "$running" -ge 3 ]; then
        echo -e "  ${GREEN}✓ Core containers are running${NC}"
    else
        echo -e "  ${YELLOW}⚠ Not all core containers are running${NC}"
    fi
fi

echo ""
echo -e "${YELLOW}[3/7] Checking Elasticsearch...${NC}"
if curl -s http://localhost:9200/_cluster/health > /dev/null 2>&1; then
    health=$(curl -s http://localhost:9200/_cluster/health 2>/dev/null | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    echo -e "  ${GREEN}✓ Elasticsearch is accessible (status: $health)${NC}"
    
    # Check index
    if curl -s http://localhost:9200/products > /dev/null 2>&1; then
        count=$(curl -s http://localhost:9200/products/_count 2>/dev/null | grep -o '"count":[0-9]*' | cut -d':' -f2)
        echo -e "  ${GREEN}✓ Products index exists ($count documents)${NC}"
    else
        echo -e "  ${RED}✗ Products index not found${NC}"
    fi
else
    echo -e "  ${RED}✗ Elasticsearch is not accessible${NC}"
fi

echo ""
echo -e "${YELLOW}[4/7] Checking PostgreSQL...${NC}"
# Use docker exec instead of requiring psql on host
if docker exec postgres-db psql -U admin -d transformation_db -c "SELECT 1" > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ PostgreSQL is accessible${NC}"
    
    # Check table and get count
    count=$(docker exec postgres-db psql -U admin -d transformation_db -t -c "SELECT COUNT(*) FROM products" 2>/dev/null | tr -d ' ')
    if [ -n "$count" ] && [ "$count" -ge 0 ] 2>/dev/null; then
        echo -e "  ${GREEN}✓ Products table exists ($count rows)${NC}"
    else
        echo -e "  ${YELLOW}⚠ Could not query products table${NC}"
    fi
else
    echo -e "  ${RED}✗ PostgreSQL container not responding${NC}"
fi

echo ""
echo -e "${YELLOW}[5/7] Checking Archestra Platform...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200\|301\|302"; then
    echo -e "  ${GREEN}✓ Archestra UI is accessible at http://localhost:3000${NC}"
else
    echo -e "  ${RED}✗ Archestra UI is not accessible${NC}"
fi

if curl -s http://localhost:9000/health > /dev/null 2>&1; then
    echo -e "  ${GREEN}✓ Archestra API is accessible at http://localhost:9000${NC}"
else
    echo -e "  ${YELLOW}⚠ Archestra API health check not responding${NC}"
fi

echo ""
echo -e "${YELLOW}[6/7] Checking Admin UIs...${NC}"
if curl -s -o /dev/null -w "%{http_code}" http://localhost:5601 | grep -q "200\|301\|302"; then
    echo -e "  ${GREEN}✓ Kibana is accessible at http://localhost:5601${NC}"
else
    echo -e "  ${YELLOW}⚠ Kibana is not accessible${NC}"
fi

if curl -s -o /dev/null -w "%{http_code}" http://localhost:5050 | grep -q "200\|301\|302"; then
    echo -e "  ${GREEN}✓ pgAdmin is accessible at http://localhost:5050${NC}"
else
    echo -e "  ${YELLOW}⚠ pgAdmin is not accessible${NC}"
fi

echo ""
echo -e "${YELLOW}[7/7] Summary...${NC}"
echo -e "${CYAN}==========================================${NC}"
echo -e "${WHITE}Access Points:${NC}"
echo -e "  ${CYAN}- Archestra UI:  http://localhost:3000${NC}"
echo -e "  ${CYAN}- Archestra API: http://localhost:9000${NC}"
echo -e "  ${CYAN}- Elasticsearch: http://localhost:9200${NC}"
echo -e "  ${CYAN}- Kibana:        http://localhost:5601${NC}"
echo -e "  ${CYAN}- PostgreSQL:    localhost:5432${NC}"
echo -e "  ${CYAN}- pgAdmin:       http://localhost:5050${NC}"
echo ""
echo -e "${WHITE}Credentials:${NC}"
echo -e "  ${GRAY}- PostgreSQL: admin / admin123${NC}"
echo -e "  ${GRAY}- pgAdmin:    admin@admin.com / admin123${NC}"
echo -e "${CYAN}==========================================${NC}"
echo ""
echo -e "${GREEN}✓ Verification complete!${NC}"
echo ""
echo -e "${WHITE}Next steps:${NC}"
echo -e "${GRAY}1. Access Archestra at http://localhost:3000${NC}"
echo -e "${GRAY}2. Configure LLM API key in Settings${NC}"
echo -e "${GRAY}3. Register MCP servers in MCP Registry${NC}"
echo -e "${GRAY}4. Create the Data Transformer Agent${NC}"
echo -e "${GRAY}5. Run transformation!${NC}"

