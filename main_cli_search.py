import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_chatbot():
    print("Chatbot with Web Search!")
    print("Type 'exit' to quit.\n")

    previous_id = None

    while True:
        user_input = input("You: ")
        if user_input.strip().lower() == "exit":
            break

        response = client.responses.create(
            model="gpt-4o",
            input=user_input,
            previous_response_id=previous_id,
            tools=[{"type": "web_search"}]  # or "web_search_preview"
        )

        previous_id = response.id

        for output in response.output:
            # Case 1: Normal assistant message
            if hasattr(output, "content"):
                for block in output.content:
                    if block.type == "output_text":
                        print("Assistant:", block.text.strip())

            # Case 2: Tool response — e.g. web_search
            elif output.type == "function_response" and output.name == "web_search":
                results = output.response.get("results", [])
                if results:
                    print("\n🔎 Web search results:")
                    for res in results:
                        title = res.get("title", "Untitled")
                        snippet = res.get("snippet", "")
                        url = res.get("url", "")
                        print(f"- {title}\n  {snippet}\n  {url}\n")
                else:
                    print("\n🔎 Web search returned no results.\n")

        print()

if __name__ == "__main__":
    run_chatbot()
