import json
from http.server import BaseHTTPRequestHandler

# This is your AI's "Local Brain"
KNOWLEDGE_BASE = {
    "hello": "Greetings! I am the Oliwincrow Tutor. What are we scripting today?",
    "remoteevent": "RemoteEvents are used to let the Client talk to the Server. Remember: Never trust the client!",
    "nil": "A 'nil' error usually means you're trying to use something that doesn't exist. Check your variable names!",
    "wait": "Don't use wait()! Use task.wait() instead—it's much more efficient for the Roblox task scheduler.",
    "help": "I can help with: RemoteEvents, Nil errors, task.wait, and basic Luau syntax."
}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode('utf-8'))
            user_input = data.get("message", "").lower()

            # AI Logic: Search for keywords in the user's message
            reply = "I'm not sure about that specific topic yet. Try asking about 'RemoteEvents' or 'nil' errors!"

            for keyword, response in KNOWLEDGE_BASE.items():
                if keyword in user_input:
                    reply = response
                    break

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()

            self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))

        except Exception as e:
            self.send_response(500)
            self.end_headers()
            self.wfile.write(f"Internal Error: {str(e)}".encode())

    def do_GET(self):
        # Keeps your browser test working
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"AI Tutor is online and waiting for POST requests.")