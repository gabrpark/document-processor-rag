# scripts/process_documents.py
from pinecone import Pinecone
from src.processor.uploader import PineconeUploader
from src.processor.embedder import Embedder
from src.processor.chunker import DocumentChunker
import asyncio
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
import logging
from datetime import datetime, UTC
import sys
from pathlib import Path
import time

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    def __init__(self):
        # Load environment variables
        load_dotenv()

        # Initialize Pinecone first to get dimension
        self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "default-index")

        # Get index dimension
        index_info = self.pinecone.describe_index(self.index_name)
        self.dimension = index_info.dimension
        logger.info(f"Index dimension: {self.dimension}")

        # Initialize components
        self.chunker = DocumentChunker(
            chunk_size=500,
            chunk_overlap=50
        )
        self.embedder = Embedder(
            dimension=self.dimension,
            batch_size=100
        )
        self.uploader = PineconeUploader(
            api_key=os.getenv("PINECONE_API_KEY"),
            index_name=self.index_name,
            dimension=self.dimension
        )

    async def process_text(
        self,
        text: str,
        metadata: Optional[Dict] = None,
        namespace: Optional[str] = None
    ):
        try:
            # Step 1: Chunk the document
            logger.info("Chunking document...")
            chunks = self.chunker.split(text, metadata)
            logger.info(f"Created {len(chunks)} chunks")

            # Step 2: Create embeddings
            logger.info("Creating embeddings...")
            chunk_texts = [chunk.text for chunk in chunks]
            embeddings = await self.embedder.embed_texts(chunk_texts)
            logger.info(f"Created {len(embeddings)} embeddings")

            # Step 3: Prepare vectors for Pinecone
            vectors = [
                {
                    "id": f"{chunk.doc_id}_{chunk.chunk_index}",
                    "values": embedding,
                    "metadata": chunk.metadata
                }
                for chunk, embedding in zip(chunks, embeddings)
            ]

            # Step 4: Upload to Pinecone
            logger.info("Uploading to Pinecone...")
            await self.uploader.upload_vectors(vectors, namespace)
            logger.info("Upload complete")

            return {
                "success": True,
                "doc_id": chunks[0].doc_id if chunks else None,
                "chunks_processed": len(chunks),
                "timestamp": datetime.now(UTC).isoformat()
            }

        except Exception as e:
            logger.error(f"Error processing document: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now(UTC).isoformat()
            }

    async def process_file(
        self,
        file_path: str,
        additional_metadata: Optional[Dict] = None,
        namespace: Optional[str] = None
    ):
        try:
            logger.info(f"Processing file: {file_path}")
            # Check if file exists
            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Read the file
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()

            # Add file-specific metadata
            metadata = {
                "source": file_path,
                "filename": os.path.basename(file_path),
                "processed_at": datetime.now(UTC).isoformat(),
                **(additional_metadata or {})
            }

            # Process the text
            return await self.process_text(text, metadata, namespace)

        except Exception as e:
            logger.error(f"Error processing file {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "file": file_path,
                "timestamp": datetime.now(UTC).isoformat()
            }


async def main():
    # Initialize processor
    processor = DocumentProcessor()

    # Example usage with a test file
    test_file = "sample.txt"

    # Create a test file if it doesn't exist
    if not os.path.exists(test_file):
        with open(test_file, 'w') as f:
            f.write(
                "This is a test document for processing. It will be split into chunks and embedded.")

    result = await processor.process_file(
        file_path=test_file,
        additional_metadata={
            "category": "documentation",
            "language": "english",
            "version": "1.0"
        },
        namespace="docs"
    )

    print("Processing result:", result)

if __name__ == "__main__":
    asyncio.run(main())
