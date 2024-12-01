import os
import json
import argparse
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from supabase import create_client
import openai


def load_environment():
    """Load environment variables."""
    load_dotenv()

    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    openai_key = os.getenv('OPENAI_API_KEY')

    if not all([supabase_url, supabase_key, openai_key]):
        raise EnvironmentError(
            "Missing required environment variables.\n"
            "Please ensure SUPABASE_URL, SUPABASE_KEY, and OPENAI_API_KEY are set in your .env file."
        )

    return supabase_url, supabase_key, openai_key


def parse_date(date_str: str) -> datetime:
    """Parse date string into datetime object."""
    try:
        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
    except ValueError:
        raise ValueError(
            "Invalid date format. Please use ISO format (YYYY-MM-DDTHH:MM:SSZ)"
        )


def get_completion(client: openai.Client, content: str, created_at: str) -> str | None:
    """Get JSON conversion from OpenAI."""
    try:
        system_prompt = """Task: Convert a raw Facebook post, including its comments and replies, into a structured JSON format.

Requirements:

	1.	Extract the following details:
	•	Post: Time, message, author
	•	Comments: Time, message, author
	•	Replies: Time, message, author
	2.	Convert all time values into ISODate time format.
	3.	Exclude any role information.

For example:

Post scraped at: 2024-11-30T13:14:00Z

Raw post: "Hi Stuart,

David, the Principal Customer Success Account Manager at Microsoft, replied my coffee chat request as below."

Comments:"
Stuart Bradley
Admin
Top contributor
Nice work!
Skipping the details - you mean not being interactive or acknowledging his comment?
1d
Reply
Jamie Yun
Author
Stuart Bradley Hi Stuart, thanks for the comment. Here is the drafted response:
Hi David, thanks for sharing your perspective.
21h
Reply
Stuart Bradley
Admin
Top contributor
Jamie Yun looks fine to me
20h
Reply
Jamie Yun
Author
Stuart Bradley Thanks, Stuart!
19h
Reply
Stuart Bradley
Admin
Top contributor
Jamie Yun this MSFT feedback is the biggest win so far in your chat.
16h
Reply



Stuart Bradley
Admin
Top contributor
Jamie Yun looks fine to me
20h
Reply
Jamie Yun
Author
Stuart Bradley Thanks, Stuart!
19h
Reply
Stuart Bradley
Admin
Top contributor
Jamie Yun this MSFT feedback is the biggest win so far in your chat.
16h
Reply"

Result: "{
    "data": [
        {
            "created_time": "2024-11-23T23:17:00Z",
            "message": "Hi Stuart,\n\nDavid, the Principal Customer Success Account Manager at Microsoft, replied my coffee chat request as below.",
            "author": "Jamie Yun",
            "comments": {
                "data": [
                    {
                        "created_time": "2024-11-22T23:17:00Z",
                        "message": "Nice work!\nSkipping the details - you mean not being interactive or acknowledging his comment?",
                        "author": "Stuart Bradley",
                        "comments": {
                            "data": [
                                {
                                    "created_time": "2024-11-23T02:17:00Z",
                                    "message": "Hi Stuart, thanks for the comment. Here is the drafted response:\nHi David, thanks for sharing your perspective.",
                                    "author": "Jamie Yun"
                                },
                                {
                                    "created_time": "2024-11-23T03:17:00Z",
                                    "message": "Jamie Yun looks fine to me",
                                    "author": "Stuart Bradley"
                                },
                                {
                                    "created_time": "2024-11-23T04:17:00Z",
                                    "message": "Thanks, Stuart!",
                                    "author": "Jamie Yun"
                                },
                                {
                                    "created_time": "2024-11-23T07:17:00Z",
                                    "message": "this MSFT feedback is the biggest win so far in your chat.",
                                    "author": "Stuart Bradley"
                                }
                            ]
                        }
                    }
                ]
            }
        }
    ]
}"""
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Post scraped at: {
                    created_at}\n\nRaw post: {content}"}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content
    except Exception as e:
        print(f"Error in OpenAI completion: {str(e)}")
        return None


def validate_json(json_str: str) -> dict | None:
    """Validate JSON string and return parsed dictionary."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"Invalid JSON: {str(e)}")
        return None


def get_posts(supabase, args):
    """Retrieve posts based on specified constraints."""
    try:
        query = supabase.table('fb_group_posts').select(
            'id, raw_post, created_at, processed_post_json, processed_at')

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

        # Filter based on processing status
        if args.unprocessed_only:
            query = query.is_('processed_post_json', 'null')
        elif not args.reprocess:
            # By default, only get unprocessed posts unless --reprocess is specified
            query = query.is_('processed_post_json', 'null')

        response = query.execute()
        return response.data
    except Exception as e:
        print(f"Error retrieving posts: {str(e)}")
        return []


def process_posts(supabase, openai_client, posts, args):
    """Process posts through OpenAI and update Supabase."""
    processed_count = 0
    skipped_count = 0
    error_count = 0

    for post in posts:
        # Check if post is already processed
        if post.get('processed_post_json') is not None:
            if args.reprocess:
                print(f"\nReprocessing post {
                      post['id']} (previously processed at {post.get('processed_at')})")
            else:
                print(f"\nSkipping post {
                      post['id']} (already processed at {post.get('processed_at')})")
                skipped_count += 1
                continue

        print(f"\nProcessing post {post['id']}...")

        # Get JSON from OpenAI
        json_str = get_completion(
            openai_client, post['raw_post'], post['created_at'])

        if json_str:
            # Validate JSON
            processed_json = validate_json(json_str)

            if processed_json:
                try:
                    # Prepare update data
                    update_data = {
                        'processed_post_json': processed_json,
                        'processed_at': datetime.now(timezone.utc).isoformat()
                    }

                    # Update database
                    result = supabase.table('fb_group_posts') \
                        .update(update_data) \
                        .eq('id', post['id']) \
                        .execute()

                    if result.data:
                        processed_count += 1
                        print(f"Successfully {
                              'reprocessed' if args.reprocess else 'processed'} post {post['id']}")
                    else:
                        error_count += 1
                        print(f"No update confirmation received for post {
                              post['id']}")

                except Exception as e:
                    error_count += 1
                    print(f"Error updating post {post['id']}: {str(e)}")
            else:
                error_count += 1
                print(f"Failed to validate JSON for post {post['id']}")
        else:
            error_count += 1
            print(f"Failed to get completion for post {post['id']}")

    return processed_count, skipped_count, error_count


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Retrieve and process Facebook posts')

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
    processing_group = parser.add_mutually_exclusive_group()
    processing_group.add_argument(
        '--unprocessed-only',
        action='store_true',
        help='Only process posts that have not been processed yet (default behavior)'
    )
    processing_group.add_argument(
        '--reprocess',
        action='store_true',
        help='Reprocess posts even if they have been processed before'
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
        supabase_url, supabase_key, openai_key = load_environment()

        # Initialize clients
        supabase = create_client(supabase_url, supabase_key)
        openai_client = openai.Client(api_key=openai_key)

        # Get posts
        posts = get_posts(supabase, args)
        print(f"\nFound {len(posts)} posts")

        # Process posts
        if posts:
            processed_count, skipped_count, error_count = process_posts(
                supabase, openai_client, posts, args)
            print(f"\nProcessing summary:")
            print(f"Successfully processed: {processed_count}")
            print(f"Skipped (already processed): {skipped_count}")
            print(f"Errors: {error_count}")
            print(f"Total posts considered: {len(posts)}")
        else:
            print("No posts to process")

    except Exception as e:
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
