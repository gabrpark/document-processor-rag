import os
import json
import argparse
import logging
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FacebookPostConverter:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        self._init_supabase()

    def _init_supabase(self):
        """Initialize Supabase client."""
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not all([supabase_url, supabase_key]):
            raise EnvironmentError(
                "Missing required environment variables.\n"
                "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file."
            )

        self.supabase = create_client(supabase_url, supabase_key)

    def convert_json_to_text(self, json_data: dict) -> str:
        """Convert JSON structure to readable text format."""
        text_parts = []

        for post in json_data.get('data', []):
            # Add post content
            author = post.get('author', 'Unknown')
            message = post.get('message', '')
            created_time = post.get('created_time', '')

            text_parts.append(f"Post by {author} on {created_time}:")
            text_parts.append(message)

            # Process comments
            comments = post.get('comments', {}).get('data', [])
            for comment in comments:
                comment_author = comment.get('author', 'Unknown')
                comment_message = comment.get('message', '')
                comment_time = comment.get('created_time', '')

                text_parts.append(
                    f"\nComment by {comment_author} on {comment_time}:")
                text_parts.append(comment_message)

                # Process replies
                replies = comment.get('comments', {}).get('data', [])
                for reply in replies:
                    reply_author = reply.get('author', 'Unknown')
                    reply_message = reply.get('message', '')
                    reply_time = reply.get('created_time', '')

                    text_parts.append(
                        f"\nReply by {reply_author} on {reply_time}:")
                    text_parts.append(reply_message)

        return '\n\n'.join(text_parts)

    def build_query(self, args: argparse.Namespace):
        """Build Supabase query based on constraints."""
        query = self.supabase.table('fb_group_posts') \
            .select('id, processed_post_json, created_at') \
            .not_.is_('processed_post_json', 'null')

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

        # Option to only process records without reconstructed_post
        if args.unprocessed_only:
            query = query.is_('reconstructed_post', 'null')

        # Apply order
        query = query.order('id', desc=False)

        return query

    def process_posts(self, args: argparse.Namespace) -> tuple[int, int]:
        """Process posts and store reconstructed text."""
        try:
            # Build and execute query
            query = self.build_query(args)
            response = query.execute()

            if not response.data:
                logger.info("No posts found matching the criteria")
                return 0, 0

            logger.info(f"Found {len(response.data)} posts to process")

            success_count = 0
            error_count = 0

            for post in response.data:
                try:
                    logger.info(f"Processing post {
                                post['id']} (created at {post['created_at']})")

                    # Convert JSON to text
                    text = self.convert_json_to_text(
                        post['processed_post_json'])

                    # Update Supabase
                    self.supabase.table('fb_group_posts') \
                        .update({
                            'reconstructed_post': text,
                            'reconstructed_at': datetime.now(timezone.utc).isoformat()
                        }) \
                        .eq('id', post['id']) \
                        .execute()

                    success_count += 1
                    logger.info(f"Successfully processed post {post['id']}")

                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing post {
                                 post['id']}: {str(e)}")
                    continue

            return success_count, error_count

        except Exception as e:
            logger.error(f"Error in batch processing: {str(e)}")
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
        description='Convert Facebook post JSON to text'
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

    # Processing options
    parser.add_argument(
        '--unprocessed-only',
        action='store_true',
        help='Only process posts that haven\'t been reconstructed yet'
    )

    return parser.parse_args()


def main():
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

        # Initialize converter
        converter = FacebookPostConverter()

        # Process posts
        logger.info("Starting post reconstruction...")
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
        if args.unprocessed_only:
            logger.info("- Processing only unprocessed posts")

        success_count, error_count = converter.process_posts(args)

        # Print results
        logger.info("\nProcessing complete:")
        logger.info(f"Successfully processed: {success_count}")
        logger.info(f"Errors: {error_count}")

    except Exception as e:
        logger.error(f"Fatal error: {str(e)}")


if __name__ == "__main__":
    main()
