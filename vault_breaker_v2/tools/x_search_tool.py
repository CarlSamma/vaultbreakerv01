import json
import os
import requests
from datetime import datetime, timedelta
from helpers.tool import Tool, Response


class XSearchTool(Tool):
    """
    X_Search Tool - Query Grok via OpenRouter with x_search capability.
    Monitors @hackingA0 tweets in real-time using Grok's X search.
    Follows GrokAnalyst pattern: POST to OpenRouter /api/v1/chat/completions
    with x_search tool enabled.
    """

    OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
    DEFAULT_MODEL = "x-ai/grok-4.3"
    TARGET_HANDLE = "hackingA0"

    def _get_api_key(self):
        key = os.environ.get("OPENROUTER_API_KEY", "")
        if not key:
            # Try loading from secrets.env
            secrets_path = os.path.join(
                os.path.dirname(__file__), "..", "..", "..", ".a0proj", "secrets.env"
            )
            try:
                with open(secrets_path, "r") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("OPENROUTER_API_KEY="):
                            key = line.split("=", 1)[1].strip()
                            break
            except FileNotFoundError:
                pass
        return key

    async def execute(self, **kwargs):
        query = kwargs.get("query", "")
        from_date = kwargs.get("from_date", "")
        to_date = kwargs.get("to_date", "")
        limit = kwargs.get("limit", "10")
        mode = kwargs.get("mode", "Latest")

        if not query:
            # Default: get recent tweets from target
            query = f"from:{self.TARGET_HANDLE}"

        api_key = self._get_api_key()
        if not api_key:
            return Response(
                message="ERROR: OPENROUTER_API_KEY not found. Set it in environment or secrets.env.",
                break_loop=False,
            )

        # Build search params following GrokAnalyst pattern
        x_search_tool = {
            "type": "x_search",
            "allowed_x_handles": [self.TARGET_HANDLE],
        }

        if from_date:
            x_search_tool["from_date"] = from_date
        else:
            # Default: last 7 days
            x_search_tool["from_date"] = (
                datetime.utcnow() - timedelta(days=7)
            ).strftime("%Y-%m-%d")

        if to_date:
            x_search_tool["to_date"] = to_date

        payload = {
            "model": self.DEFAULT_MODEL,
            "messages": [{"role": "user", "content": query}],
            "tools": [x_search_tool],
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
            "HTTP-Referer": "https://ai.studio/build",
            "X-Title": "VaultBreaker X-Search",
        }

        try:
            resp = requests.post(
                self.OPENROUTER_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )

            if not resp.ok:
                error_data = resp.json().catch({}) if hasattr(resp, "catch") else {}
                try:
                    error_data = resp.json()
                except Exception:
                    error_data = {}
                return Response(
                    message=f"ERROR: OpenRouter request failed ({resp.status_code}): {error_data.get('error', {}).get('message', resp.text[:200])}",
                    break_loop=False,
                )

            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            citations = data.get("citations", [])
            tool_calls = data.get("choices", [{}])[0].get("message", {}).get("tool_calls", [])

            # Extract results from tool_calls if present
            extracted_citations = []
            for tc in tool_calls:
                try:
                    name = tc.get("name", "") or tc.get("type", "")
                    if "x_search" in str(name).lower():
                        args = tc.get("arguments", {})
                        if isinstance(args, str):
                            args = json.loads(args)
                        if isinstance(args.get("results"), list):
                            extracted_citations.extend(args["results"])
                        if isinstance(args.get("citations"), list):
                            extracted_citations.extend(args["citations"])
                except Exception:
                    pass

            if extracted_citations:
                citations = extracted_citations

            result = {
                "content": content,
                "citations": citations,
                "tool_calls": tool_calls,
                "query": query,
                "target": self.TARGET_HANDLE,
                "timestamp": datetime.utcnow().isoformat(),
            }

            return Response(
                message=json.dumps(result, indent=2, ensure_ascii=False),
                break_loop=False,
            )

        except requests.exceptions.Timeout:
            return Response(
                message="ERROR: OpenRouter request timed out after 60s.",
                break_loop=False,
            )
        except Exception as e:
            return Response(
                message=f"ERROR: x_search failed: {str(e)}",
                break_loop=False,
            )
