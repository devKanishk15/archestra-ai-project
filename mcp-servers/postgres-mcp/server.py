#!/usr/bin/env python3
"""
PostgreSQL MCP Server
Provides tools for interacting with PostgreSQL through the Model Context Protocol
"""

import json
import os
import sys
from typing import Any, Sequence
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor, execute_batch
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

# Database connection parameters
DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "postgres"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "transformation_db"),
    "user": os.getenv("POSTGRES_USER", "admin"),
    "password": os.getenv("POSTGRES_PASSWORD", "admin123")
}

# Initialize MCP server
app = Server("postgres-mcp")


def get_connection():
    """Get a database connection."""
    return psycopg2.connect(**DB_CONFIG)


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available PostgreSQL tools."""
    return [
        Tool(
            name="execute_query",
            description="Execute a SELECT query and return results. For safety, only SELECT queries are allowed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute"
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="insert_data",
            description="Insert a single row of data into a table.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "data": {
                        "type": "object",
                        "description": "Key-value pairs representing column names and values"
                    }
                },
                "required": ["table", "data"]
            }
        ),
        Tool(
            name="bulk_insert",
            description="Insert multiple rows of data into a table efficiently using batch insert.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "data": {
                        "type": "array",
                        "description": "Array of objects, each representing a row to insert",
                        "items": {
                            "type": "object"
                        }
                    },
                    "on_conflict": {
                        "type": "string",
                        "description": "Conflict resolution strategy: 'ignore', 'update', or 'error' (default: 'error')",
                        "enum": ["ignore", "update", "error"],
                        "default": "error"
                    }
                },
                "required": ["table", "data"]
            }
        ),
        Tool(
            name="get_schema",
            description="Get schema information for a table including columns, types, and constraints.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Name of the table"
                    }
                },
                "required": ["table"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="create_table",
            description="Create a new table with specified columns. Use with caution.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Name of the table to create"
                    },
                    "columns": {
                        "type": "object",
                        "description": "Column definitions (column_name: 'data_type constraint')"
                    }
                },
                "required": ["table", "columns"]
            }
        ),
        Tool(
            name="count_rows",
            description="Count rows in a table, optionally with a WHERE clause.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table": {
                        "type": "string",
                        "description": "Name of the table"
                    },
                    "where": {
                        "type": "string",
                        "description": "Optional WHERE clause (without 'WHERE' keyword)"
                    }
                },
                "required": ["table"]
            }
        ),
        Tool(
            name="execute_write_query",
            description="Execute INSERT, UPDATE, or DELETE queries. For safety, DDL commands (DROP, TRUNCATE, ALTER) are not allowed.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL query to execute (INSERT, UPDATE, or DELETE)"
                    },
                    "params": {
                        "type": "array",
                        "description": "Optional parameters for prepared statement",
                        "items": {
                            "type": ["string", "number", "boolean", "null"]
                        }
                    }
                },
                "required": ["query"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution."""
    
    try:
        conn = get_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        if name == "execute_query":
            query = arguments["query"].strip()
            
            # Safety check: only allow SELECT queries
            if not query.upper().startswith("SELECT"):
                return [TextContent(
                    type="text",
                    text="Error: Only SELECT queries are allowed for safety. Use specific tools for INSERT, UPDATE, DELETE."
                )]
            
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Convert to list of dicts
            results_list = [dict(row) for row in results]
            
            cursor.close()
            conn.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "count": len(results_list),
                    "rows": results_list
                }, indent=2, default=str)
            )]
        
        elif name == "insert_data":
            table = arguments["table"]
            data = arguments["data"]
            
            columns = list(data.keys())
            values = list(data.values())
            
            placeholders = ", ".join(["%s"] * len(columns))
            columns_str = ", ".join(columns)
            
            query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders}) RETURNING *"
            cursor.execute(query, values)
            result = cursor.fetchone()
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "inserted_row": dict(result)
                }, indent=2, default=str)
            )]
        
        elif name == "bulk_insert":
            table = arguments["table"]
            data = arguments["data"]
            on_conflict = arguments.get("on_conflict", "error")
            
            if not data:
                return [TextContent(
                    type="text",
                    text=json.dumps({"status": "success", "inserted": 0})
                )]
            
            # Get columns from first row
            columns = list(data[0].keys())
            columns_str = ", ".join(columns)
            placeholders = ", ".join(["%s"] * len(columns))
            
            # Build base query
            query = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
            
            # Add conflict resolution
            if on_conflict == "ignore":
                # Assume first column is primary key
                query += f" ON CONFLICT DO NOTHING"
            elif on_conflict == "update":
                # Update all columns except the first (assumed to be PK)
                update_cols = ", ".join([f"{col} = EXCLUDED.{col}" for col in columns[1:]])
                query += f" ON CONFLICT ({columns[0]}) DO UPDATE SET {update_cols}"
            
            # Prepare data tuples
            values_list = [[row.get(col) for col in columns] for row in data]
            
            # Execute batch insert
            execute_batch(cursor, query, values_list, page_size=100)
            
            conn.commit()
            inserted_count = cursor.rowcount
            
            cursor.close()
            conn.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "inserted": inserted_count,
                    "total_rows": len(data)
                }, indent=2)
            )]
        
        elif name == "get_schema":
            table = arguments["table"]
            
            query = """
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """
            
            cursor.execute(query, (table,))
            schema = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "table": table,
                    "columns": [dict(row) for row in schema]
                }, indent=2, default=str)
            )]
        
        elif name == "list_tables":
            query = """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                ORDER BY table_name
            """
            
            cursor.execute(query)
            tables = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "tables": [row["table_name"] for row in tables]
                }, indent=2)
            )]
        
        elif name == "create_table":
            table = arguments["table"]
            columns = arguments["columns"]
            
            column_defs = ", ".join([f"{col} {dtype}" for col, dtype in columns.items()])
            query = f"CREATE TABLE IF NOT EXISTS {table} ({column_defs})"
            
            cursor.execute(query)
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "message": f"Table {table} created successfully"
                })
            )]
        
        elif name == "count_rows":
            table = arguments["table"]
            where = arguments.get("where", "")
            
            query = f"SELECT COUNT(*) as count FROM {table}"
            if where:
                query += f" WHERE {where}"
            
            cursor.execute(query)
            result = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "table": table,
                    "count": result["count"]
                }, indent=2)
            )]
        
        elif name == "execute_write_query":
            query = arguments["query"].strip()
            params = arguments.get("params", [])
            
            # Safety check: only allow INSERT, UPDATE, DELETE
            query_upper = query.upper()
            allowed_keywords = ["INSERT", "UPDATE", "DELETE"]
            disallowed_keywords = ["DROP", "TRUNCATE", "ALTER", "CREATE"]
            
            # Check if query starts with allowed keyword
            starts_with_allowed = any(query_upper.startswith(kw) for kw in allowed_keywords)
            contains_disallowed = any(kw in query_upper for kw in disallowed_keywords)
            
            if not starts_with_allowed or contains_disallowed:
                return [TextContent(
                    type="text",
                    text="Error: Only INSERT, UPDATE, and DELETE queries are allowed. DDL commands (DROP, TRUNCATE, ALTER, CREATE) are not permitted."
                )]
            
            # Execute the query
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            affected_rows = cursor.rowcount
            conn.commit()
            
            cursor.close()
            conn.close()
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "status": "success",
                    "affected_rows": affected_rows,
                    "query_type": query_upper.split()[0]
                }, indent=2)
            )]
        
        else:
            cursor.close()
            conn.close()
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
        if 'conn' in locals():
            conn.rollback()
            conn.close()
        
        return [TextContent(
            type="text",
            text=f"Error executing {name}: {str(e)}"
        )]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options()
        )


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
