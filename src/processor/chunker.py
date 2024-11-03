# src/processor/chunker.py
from dataclasses import dataclass
from typing import List, Dict, Optional
import uuid
from datetime import datetime
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter


@dataclass
class Chunk:
    text: str
    metadata: Dict
    chunk_index: int
    doc_id: str


class DocumentChunker:
    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
    ):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=self.token_count,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

    def token_count(self, text: str) -> int:
        """Count tokens using tiktoken for accurate chunking"""
        encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
        return len(encoding.encode(text))

    def split(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        doc_id: Optional[str] = None
    ) -> List[Chunk]:
        """Split document into chunks with metadata"""
        if doc_id is None:
            doc_id = str(uuid.uuid4())

        # Create base metadata
        base_metadata = {
            "doc_id": doc_id,
            "timestamp": datetime.utcnow().isoformat(),
            **(metadata or {})
        }

        # Split text into chunks
        chunks = self.text_splitter.split_text(text)

        # Create Chunk objects
        return [
            Chunk(
                text=chunk,
                metadata={
                    **base_metadata,
                    "chunk_index": i,
                    "chunk_size": len(chunk),
                    "token_count": self.token_count(chunk),
                    "text": chunk  # Store text in metadata for retrieval
                },
                chunk_index=i,
                doc_id=doc_id
            )
            for i, chunk in enumerate(chunks)
        ]
