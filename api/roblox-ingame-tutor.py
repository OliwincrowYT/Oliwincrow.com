import json
import os
import http.client


# Vercel looks for this specific 'handler' function
def handler(request):
    # Check if the request is a POST (Roblox and your test script use POST)
    if request.method != 'POST':
        return {
            'statusCode': 405,
            'body': json.dumps({"reply": "Error: Send a POST request."})
        }

    # Get your token from Vercel Environment Variables
    api_token = os.getenv("HF_TOKEN")

    try:
        # 1. Parse the incoming JSON body
        # request.body is used in Vercel Python runtimes
        body_data = json.loads(request.body.decode('utf-8'))
        user_input = body_data.get("message", "hi")

        # 2. Prepare the Hugging Face Router connection
        conn = http.client.HTTPSConnection("router.huggingface.co")

        # 3. Use Qwen 2.5 (Stable & Fast)
        payload = json.dumps({
            "model": "Qwen/Qwen2.5-72B-Instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "You are a Roblox tutor. Rules: Be concise. No markdown. Use code('Type', 'Content') for code blocks."
                },
                {"role": "user", "content": user_input}
            ],
            "max_tokens": 400
        })

        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json"
        }

        # 4. Fire request to AI
        conn.request("POST", "/v1/chat/completions", payload, headers)
        res = conn.getresponse()
        raw_data = res.read().decode("utf-8")

        response_json = json.loads(raw_data)

        if "choices" in response_json:
            reply = response_json["choices"][0]["message"]["content"].strip()
        else:
            reply = f"AI Error: {response_json.get('error', 'Check HF Token/Model availability')}"

    except Exception as e:
        reply = f"System Error: {str(e)}"

    # 5. Return JSON back to the requester
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'  # Allows Roblox to see the response
        },
        'body': json.dumps({"reply": reply})
    }