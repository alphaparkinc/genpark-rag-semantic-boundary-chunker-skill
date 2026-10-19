"""RAG Semantic Boundary Chunker.
100% Python Standard Library.
"""
import re

class RagSemanticBoundaryChunker:
    """Semantic boundary preserving text chunker for RAG systems."""

    @staticmethod
    def chunk_text(text: str, max_chunk_tokens: int = 200, overlap_tokens: int = 30, preserve_headers: bool = True) -> dict:
        lines = text.split("\n")
        blocks = []
        curr_block = []
        in_code_fence = False
        current_headers = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("```"):
                in_code_fence = not in_code_fence
                curr_block.append(line)
                if not in_code_fence:
                    blocks.append(("\n".join(curr_block), list(current_headers)))
                    curr_block = []
                continue

            if in_code_fence:
                curr_block.append(line)
                continue

            header_match = re.match(r'^(#{1,6})\s+(.*)$', stripped)
            if header_match:
                if curr_block:
                    blocks.append(("\n".join(curr_block), list(current_headers)))
                    curr_block = []
                level = len(header_match.group(1))
                title = header_match.group(2)
                current_headers = [h for h in current_headers if h["level"] < level]
                current_headers.append({"level": level, "title": title})
                curr_block.append(line)
                continue

            if not stripped:
                if curr_block:
                    blocks.append(("\n".join(curr_block), list(current_headers)))
                    curr_block = []
                continue

            curr_block.append(line)

        if curr_block:
            blocks.append(("\n".join(curr_block), list(current_headers)))

        def estimate_tokens(t: str) -> int:
            return max(1, len(t.split()))

        chunks = []
        acc_text = []
        acc_tokens = 0
        acc_headers = []

        for b_text, b_headers in blocks:
            b_tokens = estimate_tokens(b_text)
            if acc_tokens + b_tokens > max_chunk_tokens and acc_text:
                full_chunk_text = "\n\n".join(acc_text)
                breadcrumbs = " > ".join([h["title"] for h in acc_headers]) if preserve_headers else ""
                chunks.append({
                    "chunk_id": len(chunks),
                    "token_count": acc_tokens,
                    "header_breadcrumbs": breadcrumbs,
                    "content": full_chunk_text
                })
                overlap_text = []
                overlap_count = 0
                for item in reversed(acc_text):
                    t_cnt = estimate_tokens(item)
                    if overlap_count + t_cnt <= overlap_tokens:
                        overlap_text.insert(0, item)
                        overlap_count += t_cnt
                    else:
                        break
                acc_text = list(overlap_text)
                acc_tokens = overlap_count

            acc_text.append(b_text)
            acc_tokens += b_tokens
            acc_headers = b_headers

        if acc_text:
            breadcrumbs = " > ".join([h["title"] for h in acc_headers]) if preserve_headers else ""
            chunks.append({
                "chunk_id": len(chunks),
                "token_count": acc_tokens,
                "header_breadcrumbs": breadcrumbs,
                "content": "\n\n".join(acc_text)
            })

        return {
            "total_chunks": len(chunks),
            "chunks": chunks,
            "diagnostics": {
                "max_chunk_tokens": max_chunk_tokens,
                "overlap_tokens": overlap_tokens
            }
        }
