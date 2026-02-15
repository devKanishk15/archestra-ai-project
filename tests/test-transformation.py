#!/usr/bin/env python3
"""
Test script to verify data transformation
Validates Elasticsearch and PostgreSQL connectivity and data integrity
"""

import json
import sys
from elasticsearch import Elasticsearch
import psycopg2
from psycopg2.extras import RealDictCursor

# Configuration
ES_URL = "http://localhost:9200"
PG_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "transformation_db",
    "user": "admin",
    "password": "admin123"
}

def test_elasticsearch():
    """Test Elasticsearch connectivity and data."""
    print("=" * 60)
    print("Testing Elasticsearch Connection")
    print("=" * 60)
    
    try:
        es = Elasticsearch([ES_URL])
        
        # Check cluster health
        health = es.cluster.health()
        print(f"✓ Cluster health: {health['status']}")
        
        # Check if products index exists
        if es.indices.exists(index="products"):
            print("✓ Products index exists")
            
            # Get count
            count = es.count(index="products")
            print(f"✓ Document count: {count['count']}")
            
            # Get a sample document
            result = es.search(index="products", size=1)
            if result['hits']['hits']:
                sample = result['hits']['hits'][0]['_source']
                print(f"✓ Sample document retrieved:")
                print(f"  - ID: {sample.get('id')}")
                print(f"  - Name: {sample.get('name')}")
                print(f"  - Price: ${sample.get('price')}")
            
            return count['count']
        else:
            print("✗ Products index does not exist!")
            return 0
            
    except Exception as e:
        print(f"✗ Elasticsearch error: {e}")
        return 0


def test_postgresql():
    """Test PostgreSQL connectivity and schema."""
    print("\n" + "=" * 60)
    print("Testing PostgreSQL Connection")
    print("=" * 60)
    
    try:
        conn = psycopg2.connect(**PG_CONFIG)
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        print("✓ Connected to PostgreSQL")
        
        # Check if products table exists
        cursor.execute("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'products'
            )
        """)
        
        exists = cursor.fetchone()[0]
        if exists:
            print("✓ Products table exists")
            
            # Get schema
            cursor.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns
                WHERE table_name = 'products'
                ORDER BY ordinal_position
            """)
            
            schema = cursor.fetchall()
            print(f"✓ Table schema ({len(schema)} columns):")
            for col in schema[:5]:  # Show first 5 columns
                print(f"  - {col['column_name']}: {col['data_type']}")
            
            # Get count
            cursor.execute("SELECT COUNT(*) as count FROM products")
            count = cursor.fetchone()['count']
            print(f"✓ Row count: {count}")
            
            # Get sample row (excluding the initial sample)
            cursor.execute("SELECT * FROM products WHERE id != 'SAMPLE-000' LIMIT 1")
            sample = cursor.fetchone()
            if sample:
                print(f"✓ Sample row retrieved:")
                print(f"  - ID: {sample['id']}")
                print(f"  - Name: {sample['name']}")
                print(f"  - Price: ${sample['price']}")
            
            cursor.close()
            conn.close()
            return count
        else:
            print("✗ Products table does not exist!")
            cursor.close()
            conn.close()
            return 0
            
    except Exception as e:
        print(f"✗ PostgreSQL error: {e}")
        return 0


def verify_data_integrity(es_count, pg_count):
    """Verify data integrity between source and target."""
    print("\n" + "=" * 60)
    print("Data Integrity Check")
    print("=" * 60)
    
    print(f"Elasticsearch documents: {es_count}")
    print(f"PostgreSQL rows (excl. sample): {pg_count - 1}")  # Exclude SAMPLE-000
    
    if es_count == 0:
        print("⚠ No data in Elasticsearch - transformation not yet performed")
        return False
    elif pg_count <= 1:  # Only sample record
        print("⚠ No transformed data in PostgreSQL - transformation not yet performed")
        return False
    elif es_count == pg_count - 1:  # Account for sample record
        print("✓ Data counts match! Transformation appears complete.")
        return True
    else:
        diff = es_count - (pg_count - 1)
        print(f"⚠ Data count mismatch! Difference: {diff} documents")
        return False


def main():
    """Main test execution."""
    print("\n" + "=" * 60)
    print("DATA TRANSFORMATION TEST SUITE")
    print("=" * 60 + "\n")
    
    es_count = test_elasticsearch()
    pg_count = test_postgresql()
    
    if es_count > 0 or pg_count > 0:
        verify_data_integrity(es_count, pg_count)
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    if es_count > 0 and pg_count > 1:
        print("✓ Both systems are operational and contain data")
        print("\nNext steps:")
        print("1. Access Archestra UI at http://localhost:3000")
        print("2. Select the 'Data Transformer Agent'")
        print("3. Ask: 'Transform all products from Elasticsearch to PostgreSQL'")
    elif es_count > 0:
        print("✓ Elasticsearch is ready")
        print("⚠ PostgreSQL needs data - run the transformation agent")
    else:
        print("⚠ System not fully initialized")
        print("  - Ensure Docker containers are running")
        print("  - Wait for data initialization to complete")
    
    print("")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(0)
