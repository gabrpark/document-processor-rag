import os
import argparse
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client


def load_environment():
    """Load environment variables."""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')

    if not all([supabase_url, supabase_key]):
        raise EnvironmentError(
            "Missing required environment variables.\n"
            "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file."
        )

    return supabase_url, supabase_key


def parse_date(date_str: str) -> datetime:
    """Parse date string into datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError(
            "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
        )


def get_posts(supabase, args):
    """Retrieve posts based on specified constraints."""
    try:
        query = supabase.table('fb_group_posts').select(
            'id, raw_post, created_at')

        # Apply ID constraints
        if args.id:
            query = query.eq('id', args.id)
        elif args.id_from and args.id_to:
            query = query.gte('id', args.id_from).lte('id', args.id_to)

        # Apply date constraints
        if args.date_from:
            query = query.gte('created_at', args.date_from)
        if args.date_to:
            query = query.lte('created_at', args.date_to)

        # Apply last days constraint
        if args.last_days:
            end_date = datetime.now(timezone.utc)
            start_date = end_date - timedelta(days=args.last_days)
            query = query.gte('created_at', start_date.isoformat())

        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Error retrieving posts: {str(e)}")
        return []


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Retrieve Facebook posts with constraints')

    # ID-based constraints
    id_group = parser.add_mutually_exclusive_group()
    id_group.add_argument(
        '--id',
        type=int,
        help='Retrieve specific post by ID'
    )
    id_group.add_argument(
        '--id-range',
        nargs=2,
        type=int,
        metavar=('FROM', 'TO'),
        help='Retrieve posts within ID range (inclusive)'
    )

    # Date-based constraints
    date_group = parser.add_mutually_exclusive_group()
    date_group.add_argument(
        '--date-range',
        nargs=2,
        metavar=('FROM', 'TO'),
        help='Retrieve posts within date range (ISO format: YYYY-MM-DDTHH:MM:SSZ)'
    )
    date_group.add_argument(
        '--last-days',
        type=int,
        help='Retrieve posts from the last N days'
    )

    return parser.parse_args()


def main():
    """Main function."""
    try:
        # Parse arguments
        args = parse_arguments()

        # Process ID range if provided
        if args.id_range:
            args.id_from, args.id_to = args.id_range
        else:
            args.id_from = args.id_to = None

        # Process date range if provided
        if args.date_range:
            args.date_from = parse_date(args.date_range[0])
            args.date_to = parse_date(args.date_range[1])
        else:
            args.date_from = args.date_to = None

        # Load environment variables
        supabase_url, supabase_key = load_environment()

        # Initialize Supabase client
        supabase = create_client(supabase_url, supabase_key)

        # Get posts
        posts = get_posts(supabase, args)

        # Print posts
        print(f"\nFound {len(posts)} posts\n")
        for post in posts:
            print(f"Post ID: {post['id']}")
            print(f"Created at: {post['created_at']}")
            print("Raw post content:")
            print(post['raw_post'])
            print("-" * 80 + "\n")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
