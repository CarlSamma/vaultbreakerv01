import json
import os
import base64
import hmac
import hashlib
import time
import urllib.parse
import requests
from helpers.tool import Tool, Response


class TwitterPostTool(Tool):
    """
    Twitter Post Tool - Publish reply tweets via OAuth 1.0a (user context).
    Uses Twitter API v2 POST /2/tweets endpoint.
    """

    TWEET_URL = "https://api.twitter.com/2/tweets"

    def _load_credentials(self):
        creds = {}
        secrets_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", ".a0proj", "secrets.env"
        )
        try:
            with open(secrets_path, "r") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        key, val = line.split("=", 1)
                        creds[key.strip()] = val.strip()
        except FileNotFoundError:
            pass
        # Also check env vars
        for k in ["X_CONSUMER_KEY", "X_CONSUMER_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]:
            if k not in creds:
                env_val = os.environ.get(k, "")
                if env_val:
                    creds[k] = env_val
        return creds

    def _build_oauth_header(self, method, url, creds, params=None):
        """Build OAuth 1.0a Authorization header."""
        oauth_params = {
            "oauth_consumer_key": creds["X_CONSUMER_KEY"],
            "oauth_nonce": base64.b64encode(os.urandom(32)).decode().replace("+", "").replace("/", "").replace("=", ""),
            "oauth_signature_method": "HMAC-SHA1",
            "oauth_timestamp": str(int(time.time())),
            "oauth_token": creds["X_ACCESS_TOKEN"],
            "oauth_version": "1.0",
        }

        # Merge all params for signature
        all_params = dict(oauth_params)
        if params:
            all_params.update(params)

        # Build signature base string
        sorted_params = "&".join(
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(str(v), safe='')}"
            for k, v in sorted(all_params.items())
        )
        base_string = f"{method.upper()}&{urllib.parse.quote(url, safe='')}&{urllib.parse.quote(sorted_params, safe='')}"

        signing_key = f"{urllib.parse.quote(creds['X_CONSUMER_SECRET'], safe='')}&{urllib.parse.quote(creds['X_ACCESS_TOKEN_SECRET'], safe='')}"
        signature = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha1).digest()
        ).decode()

        oauth_params["oauth_signature"] = signature

        header_parts = ", ".join(
            f'{urllib.parse.quote(k, safe="")}="{urllib.parse.quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )
        return f"OAuth {header_parts}"

    async def execute(self, **kwargs):
        reply_to_tweet_id = kwargs.get("reply_to_tweet_id", "")
        text = kwargs.get("text", "")

        if not text:
            return Response(
                message="ERROR: Missing 'text' argument. Provide tweet content.",
                break_loop=False,
            )

        creds = self._load_credentials()
        required = ["X_CONSUMER_KEY", "X_CONSUMER_SECRET", "X_ACCESS_TOKEN", "X_ACCESS_TOKEN_SECRET"]
        missing = [k for k in required if k not in creds or not creds[k]]
        if missing:
            return Response(
                message=f"ERROR: Missing Twitter credentials: {', '.join(missing)}. Check secrets.env.",
                break_loop=False,
            )

        payload = {"text": text}
        if reply_to_tweet_id:
            payload["reply"] = {"in_reply_to_tweet_id": reply_to_tweet_id}

        auth_header = self._build_oauth_header("POST", self.TWEET_URL, creds)
        headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
        }

        try:
            resp = requests.post(
                self.TWEET_URL,
                headers=headers,
                json=payload,
                timeout=30,
            )

            if resp.status_code not in (200, 201):
                return Response(
                    message=f"ERROR: Twitter API returned {resp.status_code}: {resp.text[:500]}",
                    break_loop=False,
                )

            data = resp.json()
            tweet_id = data.get("data", {}).get("id", "unknown")
            result = {
                "status": "success",
                "tweet_id": tweet_id,
                "text": text,
                "reply_to": reply_to_tweet_id or None,
                "url": f"https://x.com/i/status/{tweet_id}" if tweet_id != "unknown" else None,
            }

            return Response(
                message=json.dumps(result, indent=2, ensure_ascii=False),
                break_loop=False,
            )

        except requests.exceptions.Timeout:
            return Response(
                message="ERROR: Twitter API request timed out after 30s.",
                break_loop=False,
            )
        except Exception as e:
            return Response(
                message=f"ERROR: Twitter post failed: {str(e)}",
                break_loop=False,
            )
