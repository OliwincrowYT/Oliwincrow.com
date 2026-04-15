import json
import os
import http.client


def handler(request):
    # Retrieve HF Token from Vercel Environment Variables
    api_token = os.getenv("HF_TOKEN")

    # Parse the incoming request body from Roblox
    try:
        body = json.loads(request.body.decode('utf-8'))
        user_input = body.get("message", "Hello")
    except Exception:
        user_input = "Hello"

    # 1. Connect to the Hugging Face Router
    conn = http.client.HTTPSConnection("router.huggingface.co")

    # 2. Prepare the payload
    # Using Mistral-7B as it has extremely high availability on the router
    payload = json.dumps({
        "model": "mistralai/Mistral-7B-Instruct-v0.2",
        "messages": [
            {
                "role": "system",
                "content": "You are a Roblox tutor. Rules: Be concise. No markdown blocks. Use code('Type', 'Content') for code."
            },
            {"role": "user", "content": user_input}
        ],
        "max_tokens": 300,
        "stream": False
    })

    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json"
    }

    try:
        # 3. Requesting via OpenAI-compatible endpoint
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")

        response_json = json.loads(raw_data)

        if "choices" in response_json:
            reply = response_json["choices"][0]["message"]["content"].strip()
        else:
            # Catch the specific "Provider" or "Model" errors from HF
            error_detail = response_json.get('error', 'Unknown Router Error')
            reply = f"AI Error: {error_detail}"

    except Exception as e:
        reply = f"Python System Error: {str(e)}"

    # 4. Return formatted JSON to Roblox
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({"reply": reply})
    }