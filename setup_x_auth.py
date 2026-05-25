import sys
import os
import tweepy
from x_auth_helpers import parse_x_tokens_txt, write_x_token_json

# This must match EXACTLY what you put in the X Developer Portal for the Callback URI
REDIRECT_URI = "http://localhost"


def get_client_secrets():
    tokens_txt = parse_x_tokens_txt()
    client_id = os.getenv("X_CLIENT_ID") or tokens_txt.get("oauth2_client_id")
    client_secret = os.getenv("X_CLIENT_SECRET") or tokens_txt.get("oauth2_client_secret")
    return client_id, client_secret, tokens_txt


def main():
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    client_id, client_secret, tokens_txt = get_client_secrets()

    if os.path.exists('x_token.json') and '--force' not in sys.argv:
        print("x_token.json already exists. Use '--force' to regenerate from x_tokens.txt if needed.")
        return

    if tokens_txt.get('oauth1_access_token') or tokens_txt.get('oauth2_access_token'):
        write_x_token_json(tokens_txt)
        print("✅ x_token.json created from x_tokens.txt.")
        print("You can now use 'chatbot.py' to post to X.")
        return

    if not client_id or not client_secret:
        print("Missing X client credentials.")
        print("Set X_CLIENT_ID and X_CLIENT_SECRET, or provide OAuth2 keys in x_tokens.txt.")
        return

    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=REDIRECT_URI,
        scope=["tweet.read", "tweet.write", "users.read", "offline.access"]
    )

    print("=== X/Twitter OAuth 2.0 Authentication ===")
    print("1. Please click the following URL to authorize the app:")
    print(oauth2_user_handler.get_authorization_url())
    print("\n2. After you authorize, you will be redirected to an empty page (or an error page) on localhost.")
    print("3. Copy the ENTIRE URL from your browser's address bar.")
    
    authorization_response = input("\nPaste the FULL URL here: ").strip()

    try:
        access_token = oauth2_user_handler.fetch_token(authorization_response)
        if client_id:
            access_token['oauth2_client_id'] = client_id
        if client_secret:
            access_token['oauth2_client_secret'] = client_secret
        write_x_token_json(access_token)
        print("\n✅ Authentication successful! Tokens saved to 'x_token.json'.")
        print("You can now use 'chatbot.py' to post tweets.")
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")


if __name__ == "__main__":
    main()
