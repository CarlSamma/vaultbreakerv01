# Grok Chatbot with x_search

Simple Python chatbot to chat with Grok (xAI) using the official API and the `x_search` tool for real-time X/Twitter data.

## Prerequisites

- Python 3.8+
- XAI API key (get one at https://console.x.ai/)

## Installation

1. Clone or download this repository:
   ```bash
   git clone <your-repo-url>
   cd grok_task
   ```

2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set your API key:
   ```bash
   # Windows (Command Prompt)
   set XAI_API_KEY=your_api_key_here

   # Windows (PowerShell)
   $env:XAI_API_KEY="your_api_key_here"

   # macOS / Linux
   export XAI_API_KEY=your_api_key_here
   ```

## Usage

Run the chatbot:
```bash
python chatbot.py
```

If `x_token.json` is missing but `x_tokens.txt` is present with OAuth2 credentials, the chatbot will now load the access token directly from `x_tokens.txt`.

Type your messages and press Enter. Grok will respond and automatically use the `x_search` tool when it needs real-time information from X.

Type `exit` to quit.

## How it works

- Uses the OpenAI-compatible Responses API at `https://api.x.ai/v1`
- Always includes the `x_search` tool so Grok can search X posts when relevant
- Maintains full conversation history