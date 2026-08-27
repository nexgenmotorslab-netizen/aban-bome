from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time, random, json
from datetime import datetime

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# In-memory REAL DB — Works on Vercel (shared per instance)
DB = {
    "members": {},
    "fund": 12450.0,
    "inv_pool": 8000.0,
    "total_kg": 0.0,
    "total_kakra": 0.0,
    "projects": [{"id":0,"votes":312},{"id":1,"votes":234},{"id":2,"votes":189},{"id":3,"votes":156}],
    "reports": []
}

class MemberIn(BaseModel):
    name: str
    phone: str
    loc: str
    type: str = "Student"
    investAmt: Optional[float] = 0
    skill: Optional[str] = ""

class SweepIn(BaseModel):
    member_id: str
    kg: float
    area: Optional[str] = "Market"

class KakraIn(BaseModel):
    member_id: str

class VoteIn(BaseModel):
    member_id: str
    project_id: int

class JobIn(BaseModel):
    member_id: str
    skill: str

class ReportIn(BaseModel):
    issue: str
    loc: str

@app.get("/")
def root():
    return {"status":"ABAN BOME REAL Live on Vercel","fund":DB["fund"]}

@app.get("/api/fund")
def get_fund():
    return {
        "fund": DB["fund"],
        "inv_pool": DB["inv_pool"],
        "members": len(DB["members"]),
        "total_kg": DB["total_kg"],
        "total_kakra": DB["total_kakra"],
        "projects": DB["projects"]
    }

@app.post("/api/members")
def create_member(m: MemberIn):
    import os
    mid = "ABAN-" + os.urandom(3).hex().upper()
    DB["members"][mid] = {
        "id": mid,
        "name": m.name,
        "phone": m.phone,
        "loc": m.loc,
        "type": m.type,
        "kg": 0,
        "earned": m.investAmt if m.type=="Business" else 0,
        "kakra": m.investAmt if m.type=="Business" else 0,
        "points": 10,
        "skill": m.skill,
        "applied": [],
        "created": time.time()
    }
    if m.type=="Business" and m.investAmt>0:
        DB["fund"] += m.investAmt*0.2
        DB["inv_pool"] += m.investAmt
        DB["total_kakra"] += m.investAmt
    return {"id": mid, "name": m.name, "type": m.type, "loc": m.loc, "kakra": DB["members"][mid]["kakra"]}

@app.get("/api/members")
def list_members():
    return list(DB["members"].values())

@app.get("/api/members/{member_id}")
def get_member(member_id: str):
    if member_id not in DB["members"]:
        return {"error":"Not found - Create member first"}
    m = DB["members"][member_id].copy()
    m["dividend"] = round(m["kakra"]*0.1 + m["kg"]*3*0.4*0.05,2)
    m["contribution"] = round(m["kg"]*3*0.2 + m["kakra"],2)
    return m

@app.post("/api/sweep")
def do_sweep(s: SweepIn):
    if s.member_id not in DB["members"]:
        return {"error":"Member not found"}
    total = s.kg * 3
    you = total*0.4
    gov = total*0.4
    fund = total*0.2
    DB["members"][s.member_id]["kg"] += s.kg
    DB["members"][s.member_id]["earned"] += you
    DB["members"][s.member_id]["points"] += int(s.kg*2)
    DB["fund"] += fund
    DB["total_kg"] += s.kg
    return {"total_sales":total,"you_40":you,"gov_40":gov,"fund_20":fund,"fund_now":DB["fund"]}

@app.post("/api/kakra/collect")
def collect_single(k: KakraIn):
    if k.member_id not in DB["members"]:
        return {"error":"Member not found"}
    amt = round(random.uniform(0.07,0.97),2)
    DB["members"][k.member_id]["kakra"] += amt
    DB["members"][k.member_id]["earned"] += amt
    DB["members"][k.member_id]["points"] += 1
    DB["fund"] += amt
    DB["total_kakra"] += amt
    return {"collected":amt,"fund_now":DB["fund"]}

@app.post("/api/kakra/night-crawl")
def night_crawl():
    if not DB["members"]:
        return {"error":"No members yet - Create members first","fund_now":DB["fund"]}
    total=0
    details=[]
    for mid, mm in DB["members"].items():
        momo = round(random.uniform(0.01,0.90),2)
        air = round(random.uniform(0.01,0.20),2)
        data = round(random.uniform(0.02,0.40),2)
        summ = round(momo+air+data,2)
        total+=summ
        mm["kakra"] += summ
        mm["earned"] += summ
        mm["points"] += 1
        details.append({"name":mm["name"],"loc":mm["loc"],"total":summ})
    DB["fund"] += total
    DB["total_kakra"] += total
    return {"message":f"Collected GHC {total:.2f} from {len(DB['members'])} accounts","total_collected":round(total,2),"fund_now":DB["fund"],"details":details[:10]}

@app.post("/api/vote")
def vote(v: VoteIn):
    if v.member_id not in DB["members"]:
        return {"error":"Need valid ID"}
    if DB["members"][v.member_id]["points"]<1:
        return {"error":"Need 1 point - Sweep more!"}
    for p in DB["projects"]:
        if p["id"]==v.project_id:
            p["votes"]+=1
            DB["members"][v.member_id]["points"]-=1
            return {"new_votes":p["votes"]}
    return {"error":"Project not found"}

@app.post("/api/apply-job")
def apply_job(j: JobIn):
    if j.member_id not in DB["members"]:
        return {"error":"Member not found"}
    if DB["members"][j.member_id]["points"]<5:
        return {"error":"Need 5 points"}
    DB["members"][j.member_id]["points"]-=5
    DB["members"][j.member_id]["skill"]=j.skill
    DB["members"][j.member_id]["applied"].append(j.skill)
    return {"message":f"Applied for {j.skill} - Real application saved!"}

@app.post("/api/report")
def report(r: ReportIn):
    DB["reports"].append({"issue":r.issue,"loc":r.loc,"time":datetime.now().isoformat()})
    return {"message":"Reported - Real"}

@app.get("/api/reports")
def get_reports():
    return DB["reports"][-10:]

@app.get("/api/leaderboard")
def leaderboard():
    members = list(DB["members"].values())
    members.sort(key=lambda x: x["kakra"]+x["kg"], reverse=True)
    return members[:10]
