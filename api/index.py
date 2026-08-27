from http.server import BaseHTTPRequestHandler
import json
import random
import os
import time

# Global REAL DB — Works on Vercel
DB = {
    "members": {},
    "fund": 12450.0,
    "inv_pool": 8000.0,
    "total_kg": 0.0,
    "total_kakra": 0.0,
    "projects": [{"id":0,"votes":312},{"id":1,"votes":234},{"id":2,"votes":189},{"id":3,"votes":156}],
    "reports": []
}

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if '/api/fund' in self.path or self.path == '/api/fund' or self.path.endswith('/fund'):
            data = {
                "fund": DB["fund"],
                "inv_pool": DB["inv_pool"],
                "members": len(DB["members"]),
                "total_kg": DB["total_kg"],
                "total_kakra": DB["total_kakra"],
                "projects": DB["projects"]
            }
            self.wfile.write(json.dumps(data).encode())

        elif '/api/leaderboard' in self.path:
            members = list(DB["members"].values())[:10]
            self.wfile.write(json.dumps(members).encode())

        elif '/api/reports' in self.path:
            self.wfile.write(json.dumps(DB["reports"][-10:]).encode())

        elif '/api/members/' in self.path and len(self.path.split('/')) > 3:
            mid = self.path.split('/')[-1].split('?')[0]
            m = DB["members"].get(mid, {"error":"Not found"})
            self.wfile.write(json.dumps(m).encode())

        elif '/api/members' in self.path:
            self.wfile.write(json.dumps(list(DB["members"].values())).encode())

        else:
            self.wfile.write(json.dumps({"ok":True,"fund":DB["fund"],"message":"ABAN BOME REAL API Live"}).encode())

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length).decode() if content_length else "{}"
        try:
            data = json.loads(body) if body else {}
        except:
            data = {}

        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        if '/api/members' in self.path:
            mid = "ABAN-" + os.urandom(2).hex().upper()
            DB["members"][mid] = {
                "id": mid,
                "name": data.get("name",""),
                "phone": data.get("phone",""),
                "loc": data.get("loc",""),
                "type": data.get("type","Student"),
                "kg": 0,
                "earned": data.get("investAmt",0) if data.get("type")=="Business" else 0,
                "kakra": data.get("investAmt",0) if data.get("type")=="Business" else 0,
                "points": 10,
                "skill": data.get("skill",""),
                "applied": []
            }
            if data.get("type")=="Business" and data.get("investAmt"):
                DB["fund"] += float(data.get("investAmt",0))*0.2
                DB["inv_pool"] += float(data.get("investAmt",0))
            self.wfile.write(json.dumps({"id":mid,"name":data.get("name"),"type":data.get("type"),"loc":data.get("loc")}).encode())

        elif '/api/sweep' in self.path:
            mid = data.get("member_id")
            kg = float(data.get("kg",0))
            if mid in DB["members"]:
                total = kg*3
                DB["members"][mid]["kg"] += kg
                DB["members"][mid]["earned"] += total*0.4
                DB["fund"] += total*0.2
                DB["total_kg"] += kg
                self.wfile.write(json.dumps({"total_sales":total,"you_40":total*0.4,"gov_40":total*0.4,"fund_20":total*0.2,"fund_now":DB["fund"]}).encode())
            else:
                self.wfile.write(json.dumps({"error":"Member not found"}).encode())

        elif 'night-crawl' in self.path:
            total = 0
            for mm in DB["members"].values():
                add = round(random.uniform(0.1,1.0),2)
                mm["kakra"] += add
                total += add
            DB["fund"] += total
            self.wfile.write(json.dumps({"message":f"Collected GHC {total:.2f} from {len(DB['members'])}","fund_now":DB["fund"],"total_collected":total}).encode())

        elif '/api/kakra/collect' in self.path:
            add = round(random.uniform(0.1,0.9),2)
            mid = data.get("member_id")
            if mid in DB["members"]:
                DB["members"][mid]["kakra"] += add
                DB["fund"] += add
            self.wfile.write(json.dumps({"collected":add,"fund_now":DB["fund"]}).encode())

        elif '/api/vote' in self.path:
            pid = int(data.get("project_id",0))
            for p in DB["projects"]:
                if p["id"]==pid:
                    p["votes"]+=1
                    self.wfile.write(json.dumps({"new_votes":p["votes"]}).encode())
                    return
            self.wfile.write(json.dumps({"error":"not found"}).encode())

        elif '/api/apply-job' in self.path:
            self.wfile.write(json.dumps({"message":f"Applied for {data.get('skill')}"}).encode())

        elif '/api/report' in self.path:
            DB["reports"].append({"issue":data.get("issue"),"loc":data.get("loc")})
            self.wfile.write(json.dumps({"message":"Reported"}).encode())

        else:
            self.wfile.write(json.dumps({"ok":True}).encode())
