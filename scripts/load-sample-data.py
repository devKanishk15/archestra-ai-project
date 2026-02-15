#!/usr/bin/env python3
"""
Load sample data into Elasticsearch
Simple script to bulk insert products from JSON file
"""

import json
import sys
from elasticsearch import Elasticsearch

# Connect to Elasticsearch
es = Elasticsearch(['http://localhost:9200'])

# Check connection
if not es.ping():
    print("❌ Cannot connect to Elasticsearch!")
    sys.exit(1)

print("✅ Connected to Elasticsearch")

# Load sample data
with open('data/sample-data.json', 'r') as f:
    products = json.load(f)

print(f"📦 Loaded {len(products)} products from file")

# Bulk insert
bulk_data = []
for product in products:
    bulk_data.append({
        "index": {
            "_index": "products",
            "_id": product["id"]
        }
    })
    bulk_data.append(product)

# Convert to newline-delimited JSON
from elasticsearch.helpers import bulk

actions = [
    {
        "_index": "products",
        "_id": product["id"],
        "_source": product
    }
    for product in products
]

try:
    success, failed = bulk(es, actions, raise_on_error=False)
    print(f"✅ Successfully indexed {success} documents")
    if failed:
        print(f"⚠️  Failed to index {len(failed)} documents")
except Exception as e:
    print(f"❌ Error during bulk insert: {e}")
    sys.exit(1)

# Refresh index
es.indices.refresh(index="products")
print("🔄 Index refreshed")

# Verify count
count = es.count(index="products")
print(f"✅ Total documents in index: {count['count']}")

print("\n🎉 Data loading complete!")
