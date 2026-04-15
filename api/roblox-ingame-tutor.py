import json
import os
import http.client


def handler(request):
    # 1. Handle CORS (So your HTML site can talk to your API)
    if request.method == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type'
            },
            'body': ''
        }

    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({"reply": "Error: Use POST"})
        }

    api_token = os.getenv("HF_TOKEN")

    try:
        # 2. Parse Input
        body = json.loads(request.body.decode('utf-8'))
        user_input = body.get("message", "hi")

        # 3. Request to AI
        conn = http.client.HTTPSConnection("router.huggingface.co")
        payload = json.dumps({
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "messages": [
                {"role": "system", "content": "You are a Roblox tutor. No markdown. Use code('Type', 'Content')"},
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 400
        })

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        response_json = json.loads(res.read().decode("utf-8"))

        reply = response_json["choices"][0]["message"]["content"].strip()

    except Exception as e:
        reply = f"Error: {str(e)}"

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({"reply": reply})
    }