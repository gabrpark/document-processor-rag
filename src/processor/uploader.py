# src/processor/uploader.py
from pinecone import Pinecone
from typing import List, Dict, Optional
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
import logging

logger = logging.getLogger(__name__)


class PineconeUploader:
    def __init__(
        self,
        api_key: str,
        index_name: str,
        dimension: int,
        batch_size: int = 100
    ):
        self.pc = Pinecone(api_key=api_key)
        self.index_name = index_name
        self.dimension = dimension
        self.batch_size = batch_size
        self.index = self.pc.Index(self.index_name)

    def _validate_vectors(self, vectors: List[Dict]) -> None:
        """Validate vector dimensions before upload"""
        for vector in vectors:
            if len(vector['values']) != self.dimension:
                raise ValueError(
                    f"Vector dimension mismatch. Expected {self.dimension}, "
                    f"got {len(vector['values'])}. Vector ID: {vector['id']}"
                )

    def ensure_index_exists(self):
        """Create index if it doesn't exist"""
        try:
            if self.index_name not in self.pc.list_indexes().names():
                logger.info(f"Creating index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.dimension,
                    metric="cosine",
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-west-2"
                    )
                )
                # Wait for index to be ready
                while True:
                    status = self.pc.describe_index(self.index_name)
                    if status.status['ready']:
                        break
                    logger.info("Waiting for index to be ready...")
                    time.sleep(5)
            else:
                # Verify dimension matches
                index_info = self.pc.describe_index(self.index_name)
                if index_info.dimension != self.dimension:
                    raise ValueError(
                        f"Index dimension mismatch. Expected {
                            self.dimension}, "
                        f"got {index_info.dimension}"
                    )
        except Exception as e:
            logger.error(f"Error ensuring index exists: {str(e)}")
            raise

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def upload_batch(
        self,
        vectors: List[Dict],
        namespace: Optional[str] = None
    ):
        """Upload a batch of vectors to Pinecone with retry logic"""
        try:
            # Validate vectors before upload
            self._validate_vectors(vectors)

            # Pinecone's upsert is synchronous
            self.index.upsert(
                vectors=vectors,
                namespace=namespace
            )
        except Exception as e:
            logger.error(f"Error uploading batch: {str(e)}")
            raise

    async def upload_vectors(
        self,
        vectors: List[Dict],
        namespace: Optional[str] = None
    ):
        """Upload vectors in batches"""
        self.ensure_index_exists()

        total_batches = (len(vectors) + self.batch_size - 1) // self.batch_size
        logger.info(f"Uploading {len(vectors)} vectors in {
                    total_batches} batches")

        for i in range(0, len(vectors), self.batch_size):
            batch = vectors[i:i + self.batch_size]
            batch_num = i // self.batch_size + 1
            logger.info(f"Uploading batch {batch_num}/{total_batches}")

            # Run the synchronous upload in a thread pool
            await asyncio.get_event_loop().run_in_executor(
                None,
                self.upload_batch,
                batch,
                namespace
            )

            if i + self.batch_size < len(vectors):
                await asyncio.sleep(0.1)

        logger.info("Upload complete")
