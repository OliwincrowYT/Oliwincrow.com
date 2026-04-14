import json
import os
import http.client
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        api_token = os.getenv("HF_TOKEN")
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            user_input = json.loads(body.decode('utf-8')).get("message", "")
            conn = http.client.HTTPSConnection("router.huggingface.co")

            # Use a smaller/faster model for quicker "wake up" times
            model_id = "mistralai/Mistral-7B-Instruct-v0.3"

            payload = json.dumps({
                "inputs": f"<s>[INST] You are a Roblox Luau expert. Answer shortly: {user_input} [/INST]",
                "parameters": {
                    "max_new_tokens": 150,
                    "return_full_text": False
                },
                "options": {
                    "wait_for_model": True  # <--- THIS IS THE FIX
                }
            })

            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }

            # We increase the timeout because loading a model takes time
            conn.request("POST", f"/models/{model_id}", payload, headers)
            res = conn.getresponse()
            response_data = json.loads(res.read().decode("utf-8"))

            if isinstance(response_data, list) and len(response_data) > 0:
                reply = response_data[0].get('generated_text', "").strip()
            elif "error" in response_data:
                reply = f"AI Status: {response_data['error']}"
            else:
                reply = "The system is silent. Try asking again."

        except Exception as e:
            reply = f"System Error: {str(e)}"

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))