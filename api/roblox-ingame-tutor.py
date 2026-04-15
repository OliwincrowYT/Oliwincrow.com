import json
import os
import http.client


def handler(request):
    # Vercel provides the 'request' object automatically.
    # Roblox uses POST, so we reject anything else.
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({"reply": "Error: Method Not Allowed. Use POST."})
        }

    api_token = os.getenv("HF_TOKEN")

    try:
        # 1. Parse the message sent from Roblox
        body = json.loads(request.body.decode('utf-8'))
        user_input = body.get("message", "hi")

        # 2. Setup connection to Hugging Face Router
        conn = http.client.HTTPSConnection("router.huggingface.co")

        # 3. Use Qwen 2.5 (It's currently the most reliable on the HF Router)
        payload = json.dumps({
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Roblox tutor. Rules: Be concise. No markdown backticks. Use code('Type', 'Content') for code."
                },
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 400
        })

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        # 4. Fire the request
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")

        response_json = json.loads(raw_data)

        if "choices" in response_json:
            reply = response_json["choices"][0]["message"]["content"].strip()
        else:
            # This will help us debug 'Not supported by provider' errors
            reply = f"AI Error: {response_json.get('error', 'Unknown Error')}"

    except Exception as e:
        reply = f"System Error: {str(e)}"

    # 5. Return the response in a format Vercel understands
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({"reply": reply})
    }