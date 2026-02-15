#!/bin/sh

# Elasticsearch Initialization Script
# Waits for Elasticsearch to be ready, creates index with mapping, and loads sample data

echo "Waiting for Elasticsearch to be ready..."
until curl -s http://elasticsearch:9200/_cluster/health | grep -q '"status":"green"\|"status":"yellow"'; do
  echo "Elasticsearch not ready yet, waiting..."
  sleep 5
done

echo "Elasticsearch is ready!"

# Create index with mapping
echo "Creating products index with mapping..."
curl -X PUT "http://elasticsearch:9200/products" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0,
    "analysis": {
      "analyzer": {
        "product_analyzer": {
          "type": "standard",
          "stopwords": "_english_"
        }
      }
    }
  },
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"
      },
      "name": {
        "type": "text",
        "analyzer": "product_analyzer",
        "fields": {
          "keyword": {
            "type": "keyword"
          }
        }
      },
      "category": {
        "type": "keyword"
      },
      "subcategory": {
        "type": "keyword"
      },
      "price": {
        "type": "float"
      },
      "description": {
        "type": "text",
        "analyzer": "product_analyzer"
      },
      "stock_quantity": {
        "type": "integer"
      },
      "created_at": {
        "type": "date"
      },
      "ratings": {
        "type": "float"
      },
      "reviews_count": {
        "type": "integer"
      },
      "brand": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      }
    }
  }
}
'

echo ""
echo "Index created successfully!"

# Load sample data using bulk API
echo "Loading sample data..."

# Read the JSON file and create bulk request
cat /data/sample-data.json | jq -c '.[]' | while read -r doc; do
  id=$(echo "$doc" | jq -r '.id')
  echo "{\"index\":{\"_index\":\"products\",\"_id\":\"$id\"}}"
  echo "$doc"
done | curl -X POST "http://elasticsearch:9200/_bulk" -H 'Content-Type: application/json' --data-binary @-

echo ""
echo "Sample data loaded successfully!"

# Refresh index to make data searchable
echo "Refreshing index..."
curl -X POST "http://elasticsearch:9200/products/_refresh"

echo ""
echo "Getting document count..."
curl -X GET "http://elasticsearch:9200/products/_count?pretty"

echo ""
echo "Elasticsearch initialization completed!"
