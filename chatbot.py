import os
from openai import OpenAI

def main():
    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Please set the XAI_API_KEY environment variable.")
        return

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.x.ai/v1",
    )

    print("Simple Grok Chatbot with x_search tool. Type 'exit' to quit.\n")

    messages = []

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

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