from http.server import BaseHTTPRequestHandler
import json

members = {}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        if 'status' in self.path:
            self.wfile.write(json.dumps({"members": list(members.values()), "total": len(members), "message": "ABAN BOME 3-in-1 Live"}).encode())
        else:
            self.wfile.write(json.dumps({"status": "ABAN BOME 3-in-1 API Live", "endpoints": ["/api?action=register", "/api?action=sweep", "/api?action=status"]}).encode())

    def do_POST(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        length = int(self.headers.get('content-length', 0))
        body = self.rfile.read(length).decode() if length else '{}'
        try:
            data = json.loads(body)
        except:
            data = {}
        
        # Register
        if 'register' in self.path or data.get('name'):
            import uuid
            member_id = f"ABAN-{str(uuid.uuid4())[:8].upper()}"
            member = {
                "memberId": member_id,
                "name": data.get('name','Guest'),
                "phone": data.get('phone',''),
                "location": data.get('location','Aburi'),
                "type": data.get('memberType','Student'),
                "kg": 0,
                "earned": 0
            }
            members[member_id] = member
            self.wfile.write(json.dumps({"success": True, "memberId": member_id, "message": f"Welcome {member['name']}! You are now ABAN BOME Member", "member": member}).encode())
        # Sweep
        elif 'sweep' in self.path or data.get('weight'):
            weight = float(data.get('weight',1))
            reward = weight * 5
            self.wfile.write(json.dumps({"success": True, "message": f"Sweep recorded! Earned GHC{reward}", "reward": reward, "kg": weight, "points": int(weight*2)}).encode())
        else:
            self.wfile.write(json.dumps({"success": True, "message": "Received"}).encode())
