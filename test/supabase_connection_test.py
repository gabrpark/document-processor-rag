import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables
load_dotenv()

# Get Supabase credentials
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


def main():
    try:
        print("\nConnecting to Supabase...")
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

        print("\nFetching first 5 rows...")
        response = supabase.table('fb_group_posts').select(
            "*").limit(5).execute()

        if response.data:
            print(f"\nFound {len(response.data)} rows")
            for row in response.data:
                print("\nRow ID:", row.get('id'))
                print("Created at:", row.get('created_at'))
        else:
            print("\nNo data found. Please check:")
            print("1. RLS is either disabled or has proper policies")
            print("2. Table actually contains data")
            print("3. Using correct table name (fb_group_posts)")

    except Exception as e:
        print(f"\nError occurred:")
        print(f"Type: {type(e)}")
        print(f"Message: {str(e)}")


if __name__ == "__main__":
    main()
