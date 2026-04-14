import json
import os
import http.client
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # SECURE: Grab the token from Vercel's environment
        api_token = os.getenv("HF_TOKEN")

        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            user_input = json.loads(body.decode('utf-8')).get("message", "")

            conn = http.client.HTTPSConnection("api-inference.huggingface.co")

            # Change the model here if you want (Mistral and Llama 3 are popular/free)
            model_id = "mistralai/Mistral-7B-Instruct-v0.3"

            payload = json.dumps({
                "inputs": f"<s>[INST] You are a Roblox Luau expert. Answer shortly: {user_input} [/INST]",
                "parameters": {"max_new_tokens": 150}
            })

            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }

            conn.request("POST", f"/models/{model_id}", payload, headers)
            res = conn.getresponse()
            response_data = json.loads(res.read().decode("utf-8"))

            # Hugging Face usually returns a list
            if isinstance(response_data, list):
                full_text = response_data[0].get('generated_text', "")
                reply = full_text.split("[/INST]")[-1].strip()
            else:
                reply = "The AI is currently loading or busy. Try again in a second!"

        except Exception as e:
            reply = f"System Error: {str(e)}"

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))