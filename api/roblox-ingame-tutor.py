import json
import os
import http.client


def handler(request):
    # Only allow POST requests
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({"error": "Method Not Allowed. Use POST."})
        }

    api_token = os.getenv("HF_TOKEN")

    try:
        # Parse Roblox body
        body = json.loads(request.body.decode('utf-8'))
        user_input = body.get("message", "Hello")

        # 1. Connect to Hugging Face
        conn = http.client.HTTPSConnection("router.huggingface.co")

        # 2. Modern Payload (using a highly available model for 2026)
        payload = json.dumps({
            "model": "meta-llama/Llama-3.1-8B-Instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Roblox tutor. Use code('Type', 'Content') for all code. No markdown."
                },
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 300
        })

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")

        response_json = json.loads(raw_data)
        reply = response_json["choices"][0]["message"]["content"].strip()

    except Exception as e:
        reply = f"System Error: {str(e)}"

    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({"reply": reply})
    }