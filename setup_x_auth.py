import tweepy
import json
import os

CLIENT_ID = os.getenv("X_CLIENT_ID", "YOUR_CLIENT_ID")
CLIENT_SECRET = os.getenv("X_CLIENT_SECRET", "YOUR_CLIENT_SECRET")

# This must match EXACTLY what you put in the X Developer Portal for the Callback URI
REDIRECT_URI = "http://localhost" 

def main():
    # Allow localhost to use http instead of https for local development
    os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

    oauth2_user_handler = tweepy.OAuth2UserHandler(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
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
        
        with open('x_token.json', 'w') as f:
            json.dump(access_token, f)
            
        print("\n✅ Authentication successful! Tokens saved to 'x_token.json'.")
        print("You can now use 'chatbot.py' to post tweets.")
    except Exception as e:
        print(f"\n❌ Authentication failed: {e}")

if __name__ == "__main__":
    main()
