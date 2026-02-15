#!/bin/bash

# Quick script to load sample data into Elasticsearch
# Run this after containers are up

echo "🔄 Loading sample data into Elasticsearch..."

# Create bulk insert file
cat > /tmp/bulk_data.ndjson << 'EOF'
{"index":{"_index":"products","_id":"PROD-001"}}
{"id":"PROD-001","name":"Wireless Bluetooth Headphones","category":"Electronics","subcategory":"Audio","price":79.99,"description":"Premium wireless headphones with active noise cancellation and 30-hour battery life","stock_quantity":150,"created_at":"2024-01-15T10:30:00Z","ratings":4.5,"reviews_count":328,"brand":"AudioTech","tags":["wireless","bluetooth","noise-cancelling"]}
{"index":{"_index":"products","_id":"PROD-002"}}
{"id":"PROD-002","name":"Smart Fitness Watch","category":"Electronics","subcategory":"Wearables","price":199.99,"description":"Advanced fitness tracker with heart rate monitor, GPS, and sleep tracking","stock_quantity":85,"created_at":"2024-01-20T14:15:00Z","ratings":4.7,"reviews_count":542,"brand":"FitGear","tags":["fitness","smartwatch","health"]}
{"index":{"_index":"products","_id":"PROD-003"}}
{"id":"PROD-003","name":"Ergonomic Office Chair","category":"Furniture","subcategory":"Office","price":349.99,"description":"Premium ergonomic chair with lumbar support and adjustable armrests","stock_quantity":45,"created_at":"2024-02-01T09:00:00Z","ratings":4.8,"reviews_count":215,"brand":"ComfortSeating","tags":["ergonomic","office","furniture"]}
{"index":{"_index":"products","_id":"PROD-004"}}
{"id":"PROD-004","name":"4K Ultra HD Monitor","category":"Electronics","subcategory":"Displays","price":449.99,"description":"27-inch 4K monitor with HDR support and 144Hz refresh rate","stock_quantity":62,"created_at":"2024-02-05T11:45:00Z","ratings":4.6,"reviews_count":189,"brand":"ViewMax","tags":["4k","monitor","gaming"]}
{"index":{"_index":"products","_id":"PROD-005"}}
{"id":"PROD-005","name":"Mechanical Keyboard RGB","category":"Electronics","subcategory":"Accessories","price":129.99,"description":"RGB backlit mechanical keyboard with Cherry MX switches","stock_quantity":120,"created_at":"2024-02-10T16:20:00Z","ratings":4.4,"reviews_count":276,"brand":"KeyPro","tags":["mechanical","rgb","gaming"]}
{"index":{"_index":"products","_id":"PROD-006"}}
{"id":"PROD-006","name":"Standing Desk Converter","category":"Furniture","subcategory":"Office","price":249.99,"description":"Adjustable standing desk converter with dual monitor support","stock_quantity":38,"created_at":"2024-02-12T08:30:00Z","ratings":4.3,"reviews_count":142,"brand":"DeskRise","tags":["standing-desk","adjustable","ergonomic"]}
{"index":{"_index":"products","_id":"PROD-007"}}
{"id":"PROD-007","name":"Noise Cancelling Earbuds","category":"Electronics","subcategory":"Audio","price":149.99,"description":"True wireless earbuds with active noise cancellation and 24-hour battery","stock_quantity":200,"created_at":"2024-02-15T13:10:00Z","ratings":4.6,"reviews_count":412,"brand":"SoundWave","tags":["wireless","earbuds","anc"]}
{"index":{"_index":"products","_id":"PROD-008"}}
{"id":"PROD-008","name":"USB-C Docking Station","category":"Electronics","subcategory":"Accessories","price":179.99,"description":"12-in-1 USB-C hub with dual HDMI, ethernet, and 100W power delivery","stock_quantity":95,"created_at":"2024-02-18T10:00:00Z","ratings":4.5,"reviews_count":167,"brand":"ConnectHub","tags":["usb-c","dock","hub"]}
{"index":{"_index":"products","_id":"PROD-009"}}
{"id":"PROD-009","name":"Leather Laptop Bag","category":"Accessories","subcategory":"Bags","price":89.99,"description":"Premium leather laptop bag with padded compartment for 15-inch laptops","stock_quantity":55,"created_at":"2024-02-20T15:30:00Z","ratings":4.7,"reviews_count":98,"brand":"CarryStyle","tags":["leather","laptop-bag","professional"]}
{"index":{"_index":"products","_id":"PROD-010"}}
{"id":"PROD-010","name":"Smart LED Desk Lamp","category":"Lighting","subcategory":"Desk","price":59.99,"description":"Wi-Fi enabled desk lamp with adjustable color temperature and brightness","stock_quantity":130,"created_at":"2024-02-22T12:15:00Z","ratings":4.4,"reviews_count":234,"brand":"LightSmart","tags":["smart","led","desk-lamp"]}
{"index":{"_index":"products","_id":"PROD-011"}}
{"id":"PROD-011","name":"Wireless Gaming Mouse","category":"Electronics","subcategory":"Accessories","price":79.99,"description":"High-precision wireless gaming mouse with 16000 DPI and RGB lighting","stock_quantity":165,"created_at":"2024-02-25T09:45:00Z","ratings":4.6,"reviews_count":312,"brand":"GamePro","tags":["wireless","gaming","mouse"]}
{"index":{"_index":"products","_id":"PROD-012"}}
{"id":"PROD-012","name":"Portable SSD 1TB","category":"Electronics","subcategory":"Storage","price":119.99,"description":"External SSD with 1050MB/s read speed and USB-C connectivity","stock_quantity":88,"created_at":"2024-03-01T11:20:00Z","ratings":4.8,"reviews_count":445,"brand":"SpeedDrive","tags":["ssd","storage","portable"]}
{"index":{"_index":"products","_id":"PROD-013"}}
{"id":"PROD-013","name":"Webcam 1080p HD","category":"Electronics","subcategory":"Video","price":69.99,"description":"Full HD webcam with auto-focus and built-in dual microphones","stock_quantity":110,"created_at":"2024-03-05T14:00:00Z","ratings":4.3,"reviews_count":187,"brand":"ViewCam","tags":["webcam","1080p","video"]}
{"index":{"_index":"products","_id":"PROD-014"}}
{"id":"PROD-014","name":"Cable Management Kit","category":"Accessories","subcategory":"Organization","price":24.99,"description":"Complete cable management solution with clips, sleeves, and ties","stock_quantity":250,"created_at":"2024-03-08T10:30:00Z","ratings":4.5,"reviews_count":521,"brand":"Organizer","tags":["cables","organization","desk"]}
{"index":{"_index":"products","_id":"PROD-015"}}
{"id":"PROD-015","name":"Monitor Arm Mount","category":"Furniture","subcategory":"Accessories","price":89.99,"description":"Gas spring monitor arm for 13-32 inch displays with cable management","stock_quantity":72,"created_at":"2024-03-10T13:50:00Z","ratings":4.7,"reviews_count":156,"brand":"MountTech","tags":["monitor-arm","mount","ergonomic"]}
EOF

# Load data using curl
curl -X POST "http://localhost:9200/_bulk" -H 'Content-Type: application/x-ndjson' --data-binary @/tmp/bulk_data.ndjson

echo ""
echo "🔄 Refreshing index..."
curl -X POST "http://localhost:9200/products/_refresh"

echo ""
echo "📊 Checking document count..."
curl -X GET "http://localhost:9200/products/_count?pretty"

echo ""
echo "✅ Done! Sample data loaded into Elasticsearch"
