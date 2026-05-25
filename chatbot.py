import os
import json
import tweepy
from openai import OpenAI
from x_auth_helpers import load_x_token_json, parse_x_tokens_txt

def get_x_client():
    token_data = load_x_token_json()

    if not token_data:
        token_data = parse_x_tokens_txt()
        if token_data.get('oauth1_access_token') or token_data.get('oauth2_access_token'):
            print("Loaded X token data from x_tokens.txt.")

    if token_data.get('oauth1_consumer_key') and token_data.get('oauth1_consumer_secret') and token_data.get('oauth1_access_token') and token_data.get('oauth1_access_token_secret'):
        try:
            return tweepy.Client(
                consumer_key=token_data['oauth1_consumer_key'],
                consumer_secret=token_data['oauth1_consumer_secret'],
                access_token=token_data['oauth1_access_token'],
                access_token_secret=token_data['oauth1_access_token_secret'],
            ), True
        except Exception as e:
            print(f"Error initializing X client with OAuth1 credentials: {e}")
            return None, False

    if token_data.get('oauth2_client_id') and token_data.get('oauth2_client_secret') and token_data.get('oauth2_access_token'):
        try:
            return tweepy.Client(
                consumer_key=token_data['oauth2_client_id'],
                consumer_secret=token_data['oauth2_client_secret'],
                access_token=token_data['oauth2_access_token'],
            ), True
        except Exception as e:
            print(f"Error initializing X client with OAuth2 user token: {e}")
            return None, False

    if token_data.get('oauth2_access_token'):
        try:
            return tweepy.Client(access_token=token_data['oauth2_access_token']), False
        except Exception as e:
            print(f"Error initializing X client with access token: {e}")
            return None, False

    if token_data.get('bearer_token'):
        try:
            return tweepy.Client(bearer_token=token_data['bearer_token']), False
        except Exception as e:
            print(f"Error initializing X client with bearer token: {e}")
            return None, False

    print("Note: No valid X auth token was found. X posting features will be disabled.")
    print("Run setup_x_auth.py or provide OAuth1/OAuth2 credentials in x_tokens.txt.")
    return None, False

def main():
    # X API Credentials
    API_KEY = os.getenv("X_API_KEY", "YOUR_API_KEY")
    API_SECRET = os.getenv("X_API_SECRET", "YOUR_API_SECRET")
    BEARER_TOKEN = os.getenv("X_BEARER_TOKEN", "YOUR_BEARER_TOKEN")
    
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        api_key = input("Enter your XAI_API_KEY: ").strip()
        if not api_key:
            print("Missing XAI_API_KEY. Set the XAI_API_KEY environment variable or provide it when prompted.")
            return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )
    
    # Initialize X client
    x_client, x_user_auth = get_x_client()

    print("Simple Grok Chatbot with x_search tool and X post functionality.")
    print("Type 'exit' to quit.")
    if x_client:
        if x_user_auth:
            print("Type 'post <message>' to post a tweet directly to X.\n")
        else:
            print("X client is initialized only for search/app auth. Posting requires user auth credentials.\n")

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
                    if x_user_auth:
                        try:
                            print(f"Attempting to post: '{tweet_content}'...")
                            response = x_client.create_tweet(text=tweet_content, user_auth=True)
                            print(f"✅ Post successful! Tweet ID: {response.data['id']}\n")
                        except Exception as e:
                            print(f"❌ Failed to post to X: {e}\n")
                    else:
                        print("X client is initialized only for app auth. Post failed because user auth is required.\n")
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