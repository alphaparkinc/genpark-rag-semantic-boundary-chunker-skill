"""MCP Server for RAG Semantic Boundary Chunker.
100% Python Standard Library JSON-RPC.
"""
import sys
import json
from client import RagSemanticBoundaryChunker

def main():
    while True:
        line = sys.stdin.readline()
        if not line:
            break
        try:
            req = json.loads(line)
            method = req.get("method")
            msg_id = req.get("id")

            if method == "tools/list":
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {
                        "tools": [
                            {
                                "name": "chunk_text",
                                "description": "Chunk text documents preserving markdown headers, code fences, and paragraphs",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "text": {"type": "string", "description": "Source document text"},
                                        "max_chunk_tokens": {"type": "integer", "default": 200},
                                        "overlap_tokens": {"type": "integer", "default": 30}
                                    },
                                    "required": ["text"]
                                }
                            }
                        ]
                    }
                }
            elif method == "tools/call":
                args = req.get("params", {}).get("arguments", {})
                text = args.get("text", "")
                max_tokens = args.get("max_chunk_tokens", 200)
                overlap = args.get("overlap_tokens", 30)
                res = RagSemanticBoundaryChunker.chunk_text(text, max_chunk_tokens=max_tokens, overlap_tokens=overlap)
                resp = {
                    "jsonrpc": "2.0",
                    "id": msg_id,
                    "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
                }
            else:
                resp = {"jsonrpc": "2.0", "id": msg_id, "error": {"code": -32601, "message": "Method not found"}}
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stdout.write(json.dumps({"jsonrpc": "2.0", "error": {"code": -32000, "message": str(e)}}) + "\n")
            sys.stdout.flush()

if __name__ == "__main__":
    main()
