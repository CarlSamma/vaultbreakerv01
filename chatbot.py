import os
import json
import tweepy
from openai import OpenAI

def get_x_client():
    token_file = 'x_token.json'
    if os.path.exists(token_file):
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
                # In Tweepy for OAuth 2.0 User Context, the access_token is passed as the bearer_token parameter
                return tweepy.Client(bearer_token=token_data['access_token'])
        except Exception as e:
            print(f"Error loading {token_file}: {e}")
    else:
        print("Note: x_token.json not found. X posting features will be disabled. Run setup_x_auth.py first.")
    
    return None

def main():
    # X API Credentials
    API_KEY = os.getenv("X_API_KEY", "YOUR_API_KEY")
    API_SECRET = os.getenv("X_API_SECRET", "YOUR_API_SECRET")
    BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "YOUR_BEARER_TOKEN")
    
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Please set the XAI_API_KEY environment variable.")
        return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )
    
    # Initialize X client
    x_client = get_x_client()

    print("Simple Grok Chatbot with x_search tool and X post functionality.")
    print("Type 'exit' to quit.")
    if x_client:
        print("Type 'post <message>' to post a tweet directly to X.\n")

    messages = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        # Handle X posting command
        if user_input.lower().startswith("post "):
            tweet_content = user_input[5:].strip()
            if tweet_content:
                if x_client:
                    try:
                        print(f"Attempting to post: '{tweet_content}'...")
                        response = x_client.create_tweet(text=tweet_content, user_auth=False)
                        print(f"✅ Post successful! Tweet ID: {response.data['id']}\n")
                    except Exception as e:
                        print(f"❌ Failed to post to X: {e}\n")
                else:
                    print("X Client is not initialized. Please run setup_x_auth.py first.\n")
            else:
                print("Please provide a message to post.\n")
            continue

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.responses.create(
                model="grok-4.3",
                input=messages,
                tools=[{"type": "x_search"}],
            )

            # Robust response extraction for xAI Responses API
            if hasattr(response, 'output_text') and response.output_text:
                assistant_message = response.output_text
            elif response.output:
                try:
                    assistant_message = response.output[0].content[0].text
                except (AttributeError, IndexError, TypeError):
                    assistant_message = str(response.output)
            else:
                assistant_message = "No response received."
            print(f"Grok: {assistant_message}\n")

            messages.append({"role": "assistant", "content": assistant_message})

        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()