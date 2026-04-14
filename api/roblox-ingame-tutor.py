from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # 1. Read the length of the data
        content_length = int(self.headers.get('Content-Length', 0))

        # 2. Parse the JSON sent from Roblox
        body = self.rfile.read(content_length)
        data = json.loads(body)
        user_message = data.get("message", "").lower()

        # 3. Logic: This is where the "Teaching" happens
        # You can expand this with more keywords or an AI API call
        reply = ""

        if "error" in user_message:
            reply = "I see you're having an error. Check your 'Output' window in Studio; usually, the red text tells you exactly which line is broken!"
        elif "wait" in user_message:
            reply = "Pro tip: In Roblox Luau, use 'task.wait()' instead of 'wait()'. It is much more efficient and reliable!"
        elif "touch" in user_message or "kill" in user_message:
            reply = "To detect a touch, use: script.Parent.Touched:Connect(function(hit) ... end)"
        else:
            reply = "I'm your Luau tutor! Ask me about errors, events, or how to structure your scripts."

        # 4. Send the response back to Roblox
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        # Crucial for Roblox to accept the response
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        response_data = {"reply": reply}
        self.wfile.write(json.dumps(response_data).encode('utf-8'))
        return