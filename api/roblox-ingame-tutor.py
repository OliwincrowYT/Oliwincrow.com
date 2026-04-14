import os
import json
from http.server import BaseHTTPRequestHandler


class handler(BaseHTTPRequestHandler):
    print('started')

    def do_GET(self):
        # this looks for hi.txt in the same folder as this script
        base_path = os.path.dirname(__file__)
        file_path = os.path.join(base_path, 'hi.txt')

        try:
            # Check if the file exists before trying to open it
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = "System Error: 'hi.txt' is missing from the api folder."
        except Exception as e:
            content = f"Python Error: {str(e)}"

        # Send Headers (Essential for Roblox)
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Write the content from the text file to the response
        self.wfile.write(content.encode('utf-8'))

    def do_POST(self):
        """If you ever want to send data TO the server later"""
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({"status": "POST active"}).encode())