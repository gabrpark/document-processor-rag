import os
from supabase import create_client
import statistics
import tiktoken
import openai

# Initialize Supabase client
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

# Initialize OpenAI client
openai_key = os.getenv('OPENAI_API_KEY')
openai_client = openai.Client(api_key=openai_key)

# Fetch data from the table
# response = supabase.table('fb_group_posts').select('raw_post').execute()
# GPT-4 Turbo pricing per 1M tokens (updated pricing)
INPUT_PRICE_PER_1M = 10.00   # $10.00 per 1M input tokens
OUTPUT_PRICE_PER_1M = 30.00  # $30.00 per 1M output tokens


def count_tokens(text, model="gpt-4-turbo-preview"):
    """Count tokens for a given text using tiktoken"""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def process_posts():
    # Fetch posts from Supabase
    response = supabase.table('fb_group_posts').select('raw_post').execute()

    token_stats = []
    cost_stats = []

    system_prompt = """Convert the following Facebook post into structured JSON format. 
    Include fields like: text_content, links, hashtags, mentions, and any other relevant metadata."""

    for record in response.data:
        if not record['raw_post']:
            continue

        raw_post = record['raw_post']

        # Count input tokens (system prompt + raw post)
        input_tokens = count_tokens(system_prompt + raw_post)

        try:
            # Make API call to GPT-4
            completion = openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": raw_post}
                ]
            )

            # Get token usage from response
            output_tokens = completion.usage.completion_tokens
            total_tokens = completion.usage.total_tokens

            # Calculate cost using updated pricing (per 1M tokens)
            input_cost = (input_tokens / 1_000_000) * INPUT_PRICE_PER_1M
            output_cost = (output_tokens / 1_000_000) * OUTPUT_PRICE_PER_1M
            total_cost = input_cost + output_cost

            token_stats.append({
                'input_tokens': input_tokens,
                'output_tokens': output_tokens,
                'total_tokens': total_tokens
            })
            cost_stats.append(total_cost)

        except Exception as e:
            print(f"Error processing post: {e}")
            continue

    # Calculate averages
    if token_stats:
        avg_input_tokens = statistics.mean(
            [stat['input_tokens'] for stat in token_stats])
        avg_output_tokens = statistics.mean(
            [stat['output_tokens'] for stat in token_stats])
        avg_total_tokens = statistics.mean(
            [stat['total_tokens'] for stat in token_stats])
        avg_cost = statistics.mean(cost_stats)
        total_cost = sum(cost_stats)

        print("\nToken Usage Statistics:")
        print(f"Average Input Tokens: {avg_input_tokens:.2f}")
        print(f"Average Output Tokens: {avg_output_tokens:.2f}")
        print(f"Average Total Tokens: {avg_total_tokens:.2f}")

        print(f"\nCost Statistics:")
        print(f"Average Cost per Post: ${avg_cost:.6f}")
        print(f"Total Cost for {len(token_stats)} posts: ${total_cost:.6f}")

        # Calculate estimated cost for 1000 posts
        estimated_cost_1k = avg_cost * 1000
        print(f"Estimated Cost for 1000 posts: ${estimated_cost_1k:.2f}")

        # Additional statistics
        print(f"\nRange Statistics:")
        print(f"Min Total Tokens: {
              min(stat['total_tokens'] for stat in token_stats)}")
        print(f"Max Total Tokens: {
              max(stat['total_tokens'] for stat in token_stats)}")
        print(f"Min Cost: ${min(cost_stats):.6f}")
        print(f"Max Cost: ${max(cost_stats):.6f}")


if __name__ == "__main__":
    process_posts()
