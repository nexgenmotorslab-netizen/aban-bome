from http.server import BaseHTTPRequestHandler
import json
class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Access-Control-Allow-Methods','GET,POST,OPTIONS')
        self.send_header('Access-Control-Allow-Headers','Content-Type')
        self.end_headers()
    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"status":"ABAN BOME 3-in-1 LIVE","message":"API Working"}).encode())
    def do_POST(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin','*')
        self.send_header('Content-type','application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"success":True,"memberId":"ABAN-"+__import__('uuid').uuid4().hex[:6].upper(),"message":"Synced to cloud"}).encode())
