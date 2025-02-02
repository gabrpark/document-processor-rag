import os
import argparse
import logging
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client

from chunker import DocumentChunker, Chunk
from embedder import Embedder
from uploader import PineconeUploader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

VERSION = "1.0"
SOURCE = "facebook group"
CATEGORY = "post"

# Constants
DEFAULT_ENV = "dev"
DEFAULT_PREFIX = "fb"
DEFAULT_VERSION = "v1"


class TextProcessor:
    def __init__(self, namespace: str = None):
        # Load environment variables
        load_dotenv()
        self._init_clients()

        # Set namespace
        self.namespace = namespace or self._get_default_namespace()
        logger.info(f"Using namespace: {self.namespace}")

        # Initialize processors
        chunk_size = 500  # tokens
        chunk_overlap = 50  # tokens

        logger.info(f"Initializing chunker with size: {
                    chunk_size} tokens, overlap: {chunk_overlap} tokens")
        self.chunker = DocumentChunker(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap
        )

        self.embedder = Embedder(
            dimension=1536,  # for text-embedding-3-small
            batch_size=100
        )

        self.uploader = PineconeUploader(
            api_key=os.getenv('PINECONE_API_KEY'),
            index_name=os.getenv('PINECONE_INDEX_NAME'),
            dimension=1536,
            batch_size=100
        )

    def _get_default_namespace(self) -> str:
        """Get default namespace using format: {env}-{prefix}-{version}."""
        env = os.getenv('ENVIRONMENT', DEFAULT_ENV)
        prefix = os.getenv('NAMESPACE_PREFIX', DEFAULT_PREFIX)
        version = os.getenv('VERSION', DEFAULT_VERSION)

        return f"{env}-{prefix}-{version}"

    def _init_clients(self):
        """Initialize Supabase client and validate environment variables."""
        required_vars = {
            'SUPABASE_URL': os.getenv('SUPABASE_URL'),
            'SUPABASE_KEY': os.getenv('SUPABASE_KEY'),
            'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY'),
            'PINECONE_API_KEY': os.getenv('PINECONE_API_KEY'),
            'PINECONE_INDEX_NAME': os.getenv('PINECONE_INDEX_NAME')
        }

        missing_vars = [k for k, v in required_vars.items() if not v]
        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {
                                   ', '.join(missing_vars)}")

        self.supabase = create_client(
            required_vars['SUPABASE_URL'],
            required_vars['SUPABASE_KEY']
        )

    def build_query(self, args: argparse.Namespace):
        """Build Supabase query based on constraints."""
        query = self.supabase.table('fb_group_posts') \
            .select('id, reconstructed_post, created_at') \
            .not_.is_('reconstructed_post', 'null')

        # Apply ID constraints
        if args.id:
            query = query.eq('id', args.id)
        elif args.id_range:
            start_id, end_id = args.id_range
            query = query.gte('id', start_id).lte('id', end_id)

        # Apply date constraints
        if args.date_range:
            start_date, end_date = args.date_range
            query = query.gte('created_at', start_date).lte(
                'created_at', end_date)
        elif args.last_days:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=args.last_days)
            query = query.gte('created_at', start_date.isoformat())

        return query

    async def process_document(self, doc: Dict) -> tuple[int, int]:
        """Process a single document through the pipeline."""
        try:
            doc_id = str(doc['id'])
            logger.info(f"Processing document {doc_id}")

            # Create chunks
            chunks = self.chunker.split(
                text=doc['reconstructed_post'],
                metadata={
                    'doc_id': doc_id,
                    'created_at': doc['created_at'],
                    'category': CATEGORY,
                    'source': SOURCE,
                    'version': VERSION
                },
                doc_id=doc_id
            )

            # Get embeddings
            texts = [chunk.text for chunk in chunks]
            embeddings = await self.embedder.embed_texts(texts)

            # Prepare vectors for Pinecone
            vectors = []
            for chunk, embedding in zip(chunks, embeddings):
                vector = {
                    'id': f"{doc_id}-{chunk.chunk_index}",
                    'values': embedding,
                    'metadata': {
                        'category': CATEGORY,
                        'chunk_index': chunk.chunk_index,
                        'chunk_size': chunk.metadata['chunk_size'],
                        'doc_id': doc_id,
                        'created_at': doc['created_at'],
                        'source': SOURCE,
                        'text': chunk.text,
                        'token_count': chunk.metadata['token_count'],
                        'version': VERSION
                    }
                }
                vectors.append(vector)

            # Upload to Pinecone
            await self.uploader.upload_vectors(vectors, self.namespace)

            logger.info(f"Successfully processed document {
                        doc_id} into {len(chunks)} chunks")
            return len(chunks), 0  # chunks processed, errors

        except Exception as e:
            logger.error(f"Error processing document {doc_id}: {str(e)}")
            return 0, 1  # chunks processed, errors

    async def process_documents(self, args: argparse.Namespace) -> tuple[int, int]:
        """Process documents based on provided constraints."""
        try:
            # Build and execute query
            query = self.build_query(args)
            response = query.execute()

            if not response.data:
                logger.info("No documents found matching the criteria")
                return 0, 0

            logger.info(f"Found {len(response.data)} documents to process")

            total_chunks = 0
            total_errors = 0

            # Process each document
            for doc in response.data:
                chunks, errors = await self.process_document(doc)
                total_chunks += chunks
                total_errors += errors

            return total_chunks, total_errors

        except Exception as e:
            logger.error(f"Error in document processing: {str(e)}")
            return 0, 0


def parse_date(date_str: str) -> datetime:
    """Parse date string into datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError(
            "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
        )


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Process reconstructed posts into embeddings'
    )

    # ID-based constraints
    id_group = parser.add_mutually_exclusive_group()
    id_group.add_argument(
        '--id',
        type=int,
        help='Process specific post by ID'
    )
    id_group.add_argument(
        '--id-range',
        nargs=2,
        type=int,
        metavar=('FROM', 'TO'),
        help='Process posts within ID range (inclusive)'
    )

    # Date-based constraints
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '--date-range',
        nargs=2,
        metavar=('FROM', 'TO'),
        help='Process posts within date range (ISO format: YYYY-MM-DDTHH:MM:SSZ)'
    )
    date_group.add_argument(
        '--last-days',
        type=int,
        help='Process posts from the last N days'
    )

    # Namespace override (optional)
    parser.add_argument(
        '--namespace',
        type=str,
        help='Override default namespace (default: dev-fb-v1)'
    )

    return parser.parse_args()


async def main():
    """Main function."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Process date range if provided
        if args.date_range:
            args.date_range = (
                parse_date(args.date_range[0]),
                parse_date(args.date_range[1])
            )

        # Initialize processor
        processor = TextProcessor()

        # Process documents
        logger.info("Starting document processing...")
        logger.info(f"Using namespace: {processor.namespace}")
        logger.info("Constraints:")
        if args.id:
            logger.info(f"- Processing single ID: {args.id}")
        elif args.id_range:
            logger.info(
                f"- Processing ID range: {args.id_range[0]} to {args.id_range[1]}")
        if args.date_range:
            logger.info(
                f"- Processing date range: {args.date_range[0]} to {args.date_range[1]}")
        elif args.last_days:
            logger.info(f"- Processing last {args.last_days} days")

        chunks_processed, errors = await processor.process_documents(args)

        # Print results
        logger.info("\nProcessing complete:")
        logger.info(f"Chunks processed: {chunks_processed}")
        logger.info(f"Errors: {errors}")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
