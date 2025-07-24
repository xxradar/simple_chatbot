import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def run_chatbot():
    print("Welcome to the OpenAI Responses API chatbot!")
    print("Type 'exit' to quit.\n")

    response_id = None

    while True:
        user_input = input("You: ")
        if user_input.lower() == "exit":
            break

        try:
            response = client.responses.create(
                model="gpt-4o",
                input=user_input,
                previous_response_id=response_id,  # preserves context
                tools=[{"type": "web_search"}]  # optional tool
            )
            # Update response ID for continuity
            response_id = response.id

            # Print all returned content chunks
            for output in response.output:
                for content in output.content:
                    print(f"Assistant: {content.text.strip()}")
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    run_chatbot()

