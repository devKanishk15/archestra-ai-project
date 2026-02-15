# PowerShell verification script for Windows
# Verifies Docker containers, services, and data initialization

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "ARCHESTRA PROJECT SETUP VERIFICATION" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Check Docker
Write-Host "[1/7] Checking Docker..." -ForegroundColor Yellow
if (Get-Command docker -ErrorAction SilentlyContinue) {
    Write-Host "  ✓ Docker is installed" -ForegroundColor Green
    
    $dockerInfo = docker info 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Docker daemon is running" -ForegroundColor Green
    } else {
        Write-Host "  ✗ Docker daemon is not running!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  ✗ Docker is not installed!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "[2/7] Checking Docker containers..." -ForegroundColor Yellow
$containers = docker ps --format "table {{.Names}}\t{{.Status}}" | Select-String -Pattern "archestra-platform|elasticsearch|postgres-db|kibana|pgadmin"

if ($null -eq $containers -or $containers.Count -eq 0) {
    Write-Host "  ✗ No project containers are running!" -ForegroundColor Red
    Write-Host "  → Run: docker-compose up -d" -ForegroundColor Yellow
    exit 1
} else {
    $containers | ForEach-Object { Write-Host "  $_" }
    
    $running = (docker ps --filter "status=running" | Select-String -Pattern "archestra-platform|elasticsearch|postgres-db").Count
    if ($running -ge 3) {
        Write-Host "  ✓ Core containers are running" -ForegroundColor Green
    } else {
        Write-Host "  ⚠ Not all core containers are running" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "[3/7] Checking Elasticsearch..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "http://localhost:9200/_cluster/health" -Method Get -ErrorAction Stop
    Write-Host "  ✓ Elasticsearch is accessible (status: $($health.status))" -ForegroundColor Green
    
    try {
        $count = Invoke-RestMethod -Uri "http://localhost:9200/products/_count" -Method Get
        Write-Host "  ✓ Products index exists ($($count.count) documents)" -ForegroundColor Green
    } catch {
        Write-Host "  ✗ Products index not found" -ForegroundColor Red
    }
} catch {
    Write-Host "  ✗ Elasticsearch is not accessible" -ForegroundColor Red
}

Write-Host ""
Write-Host "[4/7] Checking PostgreSQL..." -ForegroundColor Yellow
Write-Host "  ⚠ Skipping direct PostgreSQL check (requires psql client)" -ForegroundColor Yellow
Write-Host "  → Use pgAdmin at http://localhost:5050 to verify" -ForegroundColor Cyan

Write-Host ""
Write-Host "[5/7] Checking Archestra Platform..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3000" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Archestra UI is accessible at http://localhost:3000" -ForegroundColor Green
} catch {
    Write-Host "  ✗ Archestra UI is not accessible" -ForegroundColor Red
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:9000/health" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Archestra API is accessible at http://localhost:9000" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Archestra API health check not responding" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[6/7] Checking Admin UIs..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:5601" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ Kibana is accessible at http://localhost:5601" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ Kibana is not accessible" -ForegroundColor Yellow
}

try {
    $response = Invoke-WebRequest -Uri "http://localhost:5050" -Method Get -TimeoutSec 5 -ErrorAction Stop
    Write-Host "  ✓ pgAdmin is accessible at http://localhost:5050" -ForegroundColor Green
} catch {
    Write-Host "  ⚠ pgAdmin is not accessible" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "[7/7] Summary..." -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "Access Points:" -ForegroundColor White
Write-Host "  - Archestra UI:  http://localhost:3000" -ForegroundColor Cyan
Write-Host "  - Archestra API: http://localhost:9000" -ForegroundColor Cyan
Write-Host "  - Elasticsearch: http://localhost:9200" -ForegroundColor Cyan
Write-Host "  - Kibana:        http://localhost:5601" -ForegroundColor Cyan
Write-Host "  - PostgreSQL:    localhost:5432" -ForegroundColor Cyan
Write-Host "  - pgAdmin:       http://localhost:5050" -ForegroundColor Cyan
Write-Host ""
Write-Host "Credentials:" -ForegroundColor White
Write-Host "  - PostgreSQL: admin / admin123" -ForegroundColor Gray
Write-Host "  - pgAdmin:    admin@admin.com / admin123" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✓ Verification complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor White
Write-Host "1. Access Archestra at http://localhost:3000" -ForegroundColor Gray
Write-Host "2. Configure LLM API key in Settings" -ForegroundColor Gray
Write-Host "3. Register MCP servers in MCP Registry" -ForegroundColor Gray
Write-Host "4. Create the Data Transformer Agent" -ForegroundColor Gray
Write-Host "5. Run transformation!" -ForegroundColor Gray
