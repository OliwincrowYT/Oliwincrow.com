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
            # Parse Roblox input
            user_input = json.loads(body.decode('utf-8')).get("message", "Hello")

            # 1. New Router Endpoint
            conn = http.client.HTTPSConnection("router.huggingface.co")

            # 2. Modern Chat Format
            payload = json.dumps({
                "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "messages": [
                    {"role": "system", "content": "You are a Roblox Luau expert tutor. Be concise. From now on, do not use Markdown code blocks. If you need to provide code, use the format: code('LanguageName', 'The code content here'). Do not include backticks."},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 150,
                "stream": False
            })

            headers = {
                "Authorization": f"Bearer {api_token}",
                "Content-Type": "application/json"
            }

            # 3. Requesting via /v1/chat/completions (OpenAI compatible)
            conn.request("POST", "/v1/chat/completions", payload, headers)
            res = conn.getresponse()
            raw_data = res.read().decode("utf-8")

            # Safety check: Is the response actually JSON?
            try:
                response_json = json.loads(raw_data)
                if "choices" in response_json:
                    reply = response_json["choices"][0]["message"]["content"].strip()
                else:
                    reply = f"AI Error: {response_json.get('error', 'Unknown response format')}"
            except:
                reply = f"Server sent non-JSON response: {raw_data[:100]}"

        except Exception as e:
            reply = f"Python System Error: {str(e)}"

        # Final response to Roblox
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"reply": reply}).encode('utf-8'))