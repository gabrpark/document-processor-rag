import os
from supabase import create_client
import statistics
import argparse
import matplotlib.pyplot as plt
import seaborn as sns

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)


def process_posts(single_id=None, id_range=None, visualize=False):
    # Prepare query based on input type
    query = supabase.table('fb_group_posts').select('id,reconstructed_post')

    if single_id is not None:
        query = query.eq('id', single_id)
    elif id_range is not None:
        from_id, to_id = id_range
        query = query.gte('id', from_id).lte('id', to_id)

    response = query.execute()

    # Rest of the processing
    lengths = []
    for record in response.data:
        if record['reconstructed_post']:
            lengths.append(len(record['reconstructed_post']))

    if lengths:
        avg_length = statistics.mean(lengths)
        median_length = statistics.median(lengths)
        min_length = min(lengths)
        max_length = max(lengths)

        ranges = {}
        for length in lengths:
            range_start = (length // 100) * 100
            range_end = range_start + 99
            range_key = f"{range_start}-{range_end}"
            ranges[range_key] = ranges.get(range_key, 0) + 1

        # Print header based on query type
        if single_id is not None:
            print(f"\nPost Length Statistics for ID {single_id} (characters):")
        else:
            print(f"\nPost Length Statistics for IDs {
                  id_range[0]}-{id_range[1]} (characters):")

        print(f"Average Length: {avg_length:.2f}")
        print(f"Median Length: {median_length}")
        print(f"Minimum Length: {min_length}")
        print(f"Maximum Length: {max_length}")

        print("\nLength Distribution:")
        # Sort ranges by the numeric start of each range
        sorted_ranges = sorted(
            ranges.items(), key=lambda x: int(x[0].split('-')[0]))
        for range_key, count in sorted_ranges:
            print(f"{range_key} chars: {count} posts")

        if visualize:
            plt.figure(figsize=(12, 6))

            plt.subplot(1, 2, 1)
            sns.histplot(lengths, bins=20)
            title_id = f"ID {single_id}" if single_id else f"IDs {
                id_range[0]}-{id_range[1]}"
            plt.title(f'Post Length Distribution ({title_id})')
            plt.xlabel('Length (characters)')
            plt.ylabel('Count')

            plt.subplot(1, 2, 2)
            sns.boxplot(y=lengths)
            plt.title('Post Length Box Plot')
            plt.ylabel('Length (characters)')

            plt.tight_layout()
            plt.show()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Analyze post length statistics')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--id', type=int,
                       help='Single ID to analyze')
    group.add_argument('--id-range', nargs=2, type=int, metavar=('FROM', 'TO'),
                       help='ID range (e.g., --id-range 1 5 for IDs 1 through 5)')
    parser.add_argument('--visualize', action='store_true',
                        help='Show visualization plots')

    args = parser.parse_args()

    # Set defaults if no arguments provided
    if args.id is None and args.id_range is None:
        args.id_range = [1, 50]

    process_posts(
        single_id=args.id,
        id_range=args.id_range,
        visualize=args.visualize
    )
