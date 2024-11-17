# src/processor/embedder.py
import os
from typing import List, Dict, Tuple
import openai
from tenacity import retry, stop_after_attempt, wait_exponential
import asyncio
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Embedder:
    SUPPORTED_DIMENSIONS = {
        "text-embedding-ada-002": 1536,          # OpenAI ada-002
        "text-embedding-3-large": 3072,          # OpenAI text-embedding-3-large
        "text-embedding-3-small": 1536,          # OpenAI text-embedding-3-small
    }

    def __init__(
        self,
        dimension: int,
        batch_size: int = 100,
        max_retries: int = 3
    ):
        self.client = openai.AsyncOpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.batch_size = batch_size
        self.max_retries = max_retries

        # Select appropriate model based on dimension
        self.model = self._select_model(dimension)
        logger.info(f"Using embedding model: {self.model}")

    def _select_model(self, target_dimension: int) -> str:
        """Select appropriate embedding model based on dimension"""
        for model, dim in self.SUPPORTED_DIMENSIONS.items():
            if dim == target_dimension:
                return model

        supported_dims = list(self.SUPPORTED_DIMENSIONS.values())
        raise ValueError(
            f"No embedding model available for dimension {target_dimension}. "
            f"Supported dimensions are: {supported_dims}"
        )

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _create_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for a batch of texts with retry logic"""
        try:
            response = await self.client.embeddings.create(
                model=self.model,
                input=texts
            )
            return [embedding.embedding for embedding in response.data]
        except Exception as e:
            logger.error(f"Error creating embeddings: {str(e)}")
            raise

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for texts in batches"""
        all_embeddings = []
        total_batches = (len(texts) + self.batch_size - 1) // self.batch_size

        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            logger.info(f"Processing batch {batch_num}/{total_batches}")

            try:
                batch_embeddings = await self._create_embeddings_batch(batch)
                all_embeddings.extend(batch_embeddings)

                if i + self.batch_size < len(texts):
                    await asyncio.sleep(0.1)
            except Exception as e:
                logger.error(f"Error processing batch {batch_num}: {str(e)}")
                raise

        return all_embeddings


# class DocumentProcessor:
#     def __init__(self):
#         # Load environment variables
#         load_dotenv()

#         # Initialize Pinecone first to get dimension
#         self.pinecone = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
#         self.index_name = os.getenv("PINECONE_INDEX_NAME", "default-index")

#         # Get index dimension
#         index_info = self.pinecone.describe_index(self.index_name)
#         self.dimension = index_info.dimension
#         logger.info(f"Index dimension: {self.dimension}")

#         # Initialize components with correct dimension
#         self.chunker = DocumentChunker(
#             chunk_size=500,
#             chunk_overlap=50
#         )
#         self.embedder = Embedder(
#             dimension=self.dimension,
#             batch_size=100
#         )
#         self.uploader = PineconeUploader(
#             api_key=os.getenv("PINECONE_API_KEY"),
#             index_name=self.index_name,
#             dimension=self.dimension
#         )
