# Constants
INPUT_TOKENS_PER_POST = 1300  # Total input tokens for each post
ESTIMATED_OUTPUT_TOKENS = 900  # Estimated output tokens for JSON format
# SYSTEM_PROMPT_TOKENS = 1187    # One-time system prompt tokens

# GPT-4 Turbo pricing per 1M tokens
INPUT_PRICE_PER_1M = 10.00   # $10.00 per 1M input tokens
OUTPUT_PRICE_PER_1M = 30.00  # $30.00 per 1M output tokens


def estimate_costs(num_posts):
    # Calculate total tokens
    # System prompt only once
    total_input_tokens = (num_posts * INPUT_TOKENS_PER_POST)
    total_output_tokens = num_posts * ESTIMATED_OUTPUT_TOKENS

    # Calculate costs
    input_cost = (total_input_tokens / 1_000_000) * INPUT_PRICE_PER_1M
    output_cost = (total_output_tokens / 1_000_000) * OUTPUT_PRICE_PER_1M
    total_cost = input_cost + output_cost

    # Calculate per-post averages
    avg_cost = total_cost / num_posts

    print(f"\nEstimates for {num_posts:,} posts:")
    print(f"Total Input Tokens: {
          total_input_tokens:,} (including one-time system prompt)")
    print(f"Total Output Tokens: {total_output_tokens:,}")
    print(f"Input Cost: ${input_cost:.2f}")
    print(f"Output Cost: ${output_cost:.2f}")
    print(f"Total Cost: ${total_cost:.2f}")
    print(f"Average Cost per Post: ${avg_cost:.4f}")


if __name__ == "__main__":
    print("Cost Estimation for GPT-4 Turbo")
    print("================================")
    # print(f"System Prompt Tokens (one-time): {SYSTEM_PROMPT_TOKENS}")
    print(f"Input Tokens per Post: {INPUT_TOKENS_PER_POST}")
    print(f"Estimated Output Tokens per Post: {ESTIMATED_OUTPUT_TOKENS}")

    # Estimate for different batch sizes
    for num_posts in [100, 600, 1200]:
        estimate_costs(num_posts)
