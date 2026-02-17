#!/usr/bin/env python3
"""
Elasticsearch MCP Server
Provides tools for interacting with Elasticsearch through the Model Context Protocol
"""

import json
import os
import sys
from typing import Any, Sequence
from datetime import datetime

from elasticsearch import Elasticsearch
from mcp.server import Server
from mcp.types import Tool, TextContent, ImageContent, EmbeddedResource
from mcp.server.stdio import stdio_server

# Initialize Elasticsearch client
ES_URL = os.getenv("ELASTICSEARCH_URL", "http://elasticsearch:9200")
# ES 8.x Python client handles compatibility mode automatically by default
es_client = Elasticsearch([ES_URL])

# Initialize MCP server
app = Server("elasticsearch-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List available Elasticsearch tools."""
    return [
        Tool(
            name="search_documents",
            description="Search documents in Elasticsearch using query DSL. Returns matching documents.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Name of the index to search"
                    },
                    "query": {
                        "type": "object",
                        "description": "Elasticsearch query DSL (default: match_all)"
                    },
                    "size": {
                        "type": "integer",
                        "description": "Number of results to return (default: 10)",
                        "default": 10
                    },
                    "from_": {
                        "type": "integer",
                        "description": "Starting offset for pagination (default: 0)",
                        "default": 0
                    }
                },
                "required": ["index"]
            }
        ),
        Tool(
            name="get_document",
            description="Retrieve a specific document by ID from an index.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Name of the index"
                    },
                    "doc_id": {
                        "type": "string",
                        "description": "Document ID"
                    }
                },
                "required": ["index", "doc_id"]
            }
        ),
        Tool(
            name="list_indices",
            description="List all available indices in Elasticsearch.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_mapping",
            description="Get the mapping (schema) for an index.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Name of the index"
                    }
                },
                "required": ["index"]
            }
        ),
        Tool(
            name="bulk_export",
            description="Export documents from an index in batches using scroll API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Name of the index to export from"
                    },
                    "query": {
                        "type": "object",
                        "description": "Elasticsearch query DSL to filter documents (default: match_all)"
                    },
                    "batch_size": {
                        "type": "integer",
                        "description": "Number of documents per batch (default: 100)",
                        "default": 100
                    }
                },
                "required": ["index"]
            }
        ),
        Tool(
            name="count_documents",
            description="Count documents matching a query in an index.",
            inputSchema={
                "type": "object",
                "properties": {
                    "index": {
                        "type": "string",
                        "description": "Name of the index"
                    },
                    "query": {
                        "type": "object",
                        "description": "Elasticsearch query DSL (default: match_all)"
                    }
                },
                "required": ["index"]
            }
        )
    ]


@app.call_tool()
async def call_tool(name: str, arguments: Any) -> Sequence[TextContent | ImageContent | EmbeddedResource]:
    """Handle tool execution."""
    
    try:
        if name == "search_documents":
            index = arguments["index"]
            query = arguments.get("query", {"match_all": {}})
            size = arguments.get("size", 10)
            from_ = arguments.get("from_", 0)
            
            result = es_client.search(
                index=index,
                query=query,
                size=size,
                from_=from_
            )
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "total": result["hits"]["total"]["value"],
                    "documents": [hit["_source"] for hit in result["hits"]["hits"]],
                    "took_ms": result["took"]
                }, indent=2)
            )]
        
        elif name == "get_document":
            index = arguments["index"]
            doc_id = arguments["doc_id"]
            
            result = es_client.get(index=index, id=doc_id)
            
            return [TextContent(
                type="text",
                text=json.dumps(result["_source"], indent=2)
            )]
        
        elif name == "list_indices":
            indices = es_client.indices.get_alias(index="*")
            index_list = [
                {
                    "name": idx,
                    "aliases": list(info.get("aliases", {}).keys())
                }
                for idx, info in indices.items()
                if not idx.startswith(".")  # Filter out system indices
            ]
            
            return [TextContent(
                type="text",
                text=json.dumps(index_list, indent=2)
            )]
        
        elif name == "get_mapping":
            index = arguments["index"]
            mapping = es_client.indices.get_mapping(index=index)
            
            return [TextContent(
                type="text",
                text=json.dumps(mapping, indent=2)
            )]
        
        elif name == "bulk_export":
            index = arguments["index"]
            query = arguments.get("query", {"match_all": {}})
            batch_size = arguments.get("batch_size", 100)
            
            # Use scroll API for efficient bulk export
            result = es_client.search(
                index=index,
                query=query,
                scroll='2m',
                size=batch_size
            )
            
            scroll_id = result['_scroll_id']
            documents = [hit["_source"] for hit in result["hits"]["hits"]]
            total = result["hits"]["total"]["value"]
            
            # Get all remaining documents
            while len(result["hits"]["hits"]) > 0:
                result = es_client.scroll(scroll_id=scroll_id, scroll='2m')
                documents.extend([hit["_source"] for hit in result["hits"]["hits"]])
            
            # Clear scroll
            es_client.clear_scroll(scroll_id=scroll_id)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "total": total,
                    "exported": len(documents),
                    "documents": documents
                }, indent=2)
            )]
        
        elif name == "count_documents":
            index = arguments["index"]
            query = arguments.get("query", {"match_all": {}})
            
            result = es_client.count(index=index, query=query)
            
            return [TextContent(
                type="text",
                text=json.dumps({
                    "count": result["count"]
                }, indent=2)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except Exception as e:
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
