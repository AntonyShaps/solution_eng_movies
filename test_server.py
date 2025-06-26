#!/usr/bin/env python3
import http.server
import socketserver
import sys

PORT = 8501

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'''
        <html>
        <head><title>Test Server</title></head>
        <body>
        <h1>Test Server Running on Port 8501</h1>
        <p>This confirms the proxy is working!</p>
        </body>
        </html>
        ''')

if __name__ == "__main__":
    with socketserver.TCPServer(("127.0.0.1", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Server running at http://127.0.0.1:{PORT}")
        httpd.serve_forever()