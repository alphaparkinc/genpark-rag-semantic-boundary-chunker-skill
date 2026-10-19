"""Example usage for RAG Semantic Boundary Chunker."""
from client import RagSemanticBoundaryChunker
import json

doc = """# System Architecture Guide

The system uses event-driven pub-sub for message passing.

## Database Layer

PostgreSQL with pgvector for hybrid BM25 and vector search.

```sql
SELECT * FROM documents ORDER BY embedding <=> $1 LIMIT 10;
```

## Cache Invalidation

Cache keys are computed using Blake2b hashing of normalized prompts.
"""

chunks = RagSemanticBoundaryChunker.chunk_text(doc, max_chunk_tokens=30, overlap_tokens=5)
print(json.dumps(chunks, indent=2))
