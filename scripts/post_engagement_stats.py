import os
from supabase import create_client
import argparse
from collections import Counter, defaultdict
import json

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)


class SkippedRecords:
    def __init__(self):
        self.null_json = []
        self.invalid_json = []
        self.missing_data = []
        self.empty_data = []

    def print_report(self):
        print("\nSkipped Records Report:")
        print("----------------------")
        if self.null_json:
            print(
                f"Null JSON field - IDs: {', '.join(map(str, sorted(self.null_json)))}")
        if self.invalid_json:
            print(
                f"Invalid JSON format - IDs: {', '.join(map(str, sorted(self.invalid_json)))}")
        if self.missing_data:
            print(
                f"Missing 'data' field - IDs: {', '.join(map(str, sorted(self.missing_data)))}")
        if self.empty_data:
            print(
                f"Empty 'data' array - IDs: {', '.join(map(str, sorted(self.empty_data)))}")


def count_nested_comments(comments):
    """Recursively count comments and their authors"""
    engagement_counts = Counter()

    for comment in comments.get('data', []):
        if comment.get('author'):
            engagement_counts[comment['author']] += 1

        # Recursively count nested comments
        nested_counts = count_nested_comments(
            comment.get('comments', {'data': []}))
        engagement_counts.update(nested_counts)

    return engagement_counts


def analyze_post_authors(single_id=None, id_range=None):
    # Prepare query for posts
    query = supabase.table('fb_group_posts').select('id,processed_post_json')

    if single_id is not None:
        query = query.eq('id', single_id)
    elif id_range is not None:
        from_id, to_id = id_range
        query = query.gte('id', from_id).lte('id', to_id)

    response = query.execute()

    print(f"\nFetched {len(response.data)} records")

    # Count posts per author
    author_posts = Counter()
    unknown_post_ids = []
    total_posts = 0
    skipped = SkippedRecords()

    for record in response.data:
        record_id = record.get('id', 'Unknown ID')

        if not record['processed_post_json']:
            skipped.null_json.append(record_id)
            continue

        post_data = record['processed_post_json']
        # If it's a string, parse it
        if isinstance(post_data, str):
            try:
                post_data = json.loads(post_data)
            except json.JSONDecodeError:
                skipped.invalid_json.append(record_id)
                continue

        # Check for data field
        if not isinstance(post_data, dict) or 'data' not in post_data:
            skipped.missing_data.append(record_id)
            continue

        # Check for empty data array
        if not post_data['data']:
            skipped.empty_data.append(record_id)
            continue

        total_posts += 1
        post = post_data['data'][0]  # Get the first post
        author = post.get('author', '')
        if author == "Unknown":
            unknown_post_ids.append(record_id)
        author_posts[author] += 1

    print("\nPost Authors Statistics:")
    print("------------------------")
    print(f"Total Posts Analyzed: {total_posts}")
    if not author_posts:
        print("No authors found in the data")
    else:
        for author, count in sorted(author_posts.items(), key=lambda x: (-x[1], x[0])):
            print(f"{author}: {count} posts")

    if unknown_post_ids:
        print("\nPosts with 'Unknown' Author:")
        print(f"IDs: {', '.join(map(str, sorted(unknown_post_ids)))}")

    skipped.print_report()


def analyze_total_engagement(single_id=None, id_range=None):
    # Prepare query for posts with comments
    query = supabase.table('fb_group_posts').select('id,processed_post_json')

    if single_id is not None:
        query = query.eq('id', single_id)
    elif id_range is not None:
        from_id, to_id = id_range
        query = query.gte('id', from_id).lte('id', to_id)

    response = query.execute()

    print(f"\nFetched {len(response.data)} records for engagement analysis")

    # Count all engagements (posts + comments)
    engagement_counts = Counter()
    total_posts = 0
    skipped = SkippedRecords()

    # Process each post and its comments
    for record in response.data:
        record_id = record.get('id', 'Unknown ID')

        if not record['processed_post_json']:
            skipped.null_json.append(record_id)
            continue

        post_data = record['processed_post_json']
        # If it's a string, parse it
        if isinstance(post_data, str):
            try:
                post_data = json.loads(post_data)
            except json.JSONDecodeError:
                skipped.invalid_json.append(record_id)
                continue

        # Check for data field
        if not isinstance(post_data, dict) or 'data' not in post_data:
            skipped.missing_data.append(record_id)
            continue

        # Check for empty data array
        if not post_data['data']:
            skipped.empty_data.append(record_id)
            continue

        total_posts += 1
        post = post_data['data'][0]  # Get the first post

        # Count the post author
        author = post.get('author', '')
        engagement_counts[author] += 1

        # Count all comments
        if 'comments' in post:
            comment_counts = count_nested_comments(post['comments'])
            engagement_counts.update(comment_counts)

    print("\nTotal Engagement Statistics (Posts + All Comments):")
    print("------------------------------------------------")
    print(f"Total Posts Analyzed: {total_posts}")
    if not engagement_counts:
        print("No engagement data found")
    else:
        for author, count in sorted(engagement_counts.items(), key=lambda x: (-x[1], x[0])):
            if author:  # Skip empty author names if any
                print(f"{author}: {count} engagements")

    skipped.print_report()


def analyze_engagement(single_id=None, id_range=None):
    analyze_post_authors(single_id, id_range)
    analyze_total_engagement(single_id, id_range)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze post authors and engagement statistics')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--id', type=int,
                       help='Single ID to analyze')
    group.add_argument('--id-range', nargs=2, type=int, metavar=('FROM', 'TO'),
                       help='ID range (e.g., --id-range 1 5 for IDs 1 through 5)')

    args = parser.parse_args()

    # Set defaults if no arguments provided
    if args.id is None and args.id_range is None:
        args.id_range = [1, 50]

    analyze_engagement(
        single_id=args.id,
        id_range=args.id_range
    )
