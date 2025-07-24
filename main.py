import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import parse_qs
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

previous_id = None
conversation = []  # List of (role, text)

# Load HTML template
with open("index.html", "r") as f:
    HTML_TEMPLATE = f.read()


class ChatHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self._respond(render_html())

    def do_POST(self):
        global previous_id, conversation

        # Parse input
        length = int(self.headers.get("Content-Length"))
        body = self.rfile.read(length).decode()
        params = parse_qs(body)
        
        # Check if clear button was pressed (prioritize clear over message)
        if "clear" in params and params.get("clear", [""])[0] == "1":
            # Clear conversation and reset previous_id
            global conversation, previous_id
            conversation = []
            previous_id = None
            # Redirect to refresh the page and show cleared state
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        user_input = params.get("message", [""])[0]
        
        # If no message provided and not clearing, just redirect back
        if not user_input.strip():
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        # Add user input to conversation
        conversation.append(("user", user_input))

        # Call Responses API
        response = client.responses.create(
            model="gpt-4o",
            input=user_input,
            previous_response_id=previous_id,
            tools=[{"type": "web_search"}]
        )
        previous_id = response.id

        # Extract reply
        reply = ""
        for output in response.output:
            if hasattr(output, "content"):
                for block in output.content:
                    if block.type == "output_text":
                        reply += block.text.strip() + "\n"
            elif output.type == "function_response" and output.name == "web_search":
                for res in output.response.get("results", []):
                    reply += f"{res.get('title', '')}: {res.get('snippet', '')} ({res.get('url', '')})\n"

        conversation.append(("assistant", reply.strip()))

        self._respond(render_html())

    def _respond(self, html: str):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(html.encode())


def render_html():
    """Render the chat history into HTML."""
    history = ""
    for role, msg in conversation:
        who = "You" if role == "user" else "Assistant"
        history += f"<p><strong>{who}:</strong><br>{msg.replace(chr(10), '<br>')}</p>\n"

    return HTML_TEMPLATE.replace("{{ chat_history }}", history)


if __name__ == "__main__":
    print("Serving on http://localhost:8000 ...")
    server = HTTPServer(("localhost", 8000), ChatHandler)
    server.serve_forever()
