from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import time, random
import os

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DB = {"members": {}, "fund": 12450.0, "inv_pool": 8000.0, "total_kg": 0.0, "total_kakra": 0.0, "projects": [{"id":0,"votes":312},{"id":1,"votes":234},{"id":2,"votes":189},{"id":3,"votes":156}], "reports": []}

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
    return {"ok": True, "fund": DB["fund"]}

@app.get("/api/fund")
def get_fund():
    return {"fund": DB["fund"], "inv_pool": DB["inv_pool"], "members": len(DB["members"]), "total_kg": DB["total_kg"], "total_kakra": DB["total_kakra"], "projects": DB["projects"]}

@app.post("/api/members")
def create_member(m: MemberIn):
    mid = "ABAN-" + os.urandom(2).hex().upper()
    DB["members"][mid] = {"id": mid, "name": m.name, "phone": m.phone, "loc": m.loc, "type": m.type, "kg": 0, "earned": 0, "kakra": m.investAmt or 0, "points": 10, "skill": m.skill, "applied": []}
    if m.type == "Business" and m.investAmt:
        DB["fund"] += m.investAmt * 0.2
        DB["inv_pool"] += m.investAmt
    return {"id": mid, "name": m.name, "type": m.type, "loc": m.loc}

@app.get("/api/members/{member_id}")
def get_one(member_id: str):
    return DB["members"].get(member_id, {"error": "Not found"})

@app.post("/api/sweep")
def sweep(s: SweepIn):
    if s.member_id not in DB["members"]:
        return {"error": "Member not found"}
    total = s.kg * 3
    DB["members"][s.member_id]["kg"] += s.kg
    DB["members"][s.member_id]["earned"] += total*0.4
    DB["fund"] += total*0.2
    DB["total_kg"] += s.kg
    return {"total_sales": total, "you_40": total*0.4, "gov_40": total*0.4, "fund_20": total*0.2, "fund_now": DB["fund"]}

@app.post("/api/kakra/night-crawl")
def night_crawl():
    total = 0
    for mm in DB["members"].values():
        add = round(random.uniform(0.1, 1.0), 2)
        mm["kakra"] += add
        total += add
    DB["fund"] += total
    return {"message": f"Collected GHC {total:.2f} from {len(DB['members'])}", "fund_now": DB["fund"]}

@app.post("/api/kakra/collect")
def collect(k: KakraIn):
    add = round(random.uniform(0.1, 0.9), 2)
    if k.member_id in DB["members"]:
        DB["members"][k.member_id]["kakra"] += add
        DB["fund"] += add
    return {"collected": add, "fund_now": DB["fund"]}

@app.post("/api/vote")
def vote(v: VoteIn):
    for p in DB["projects"]:
        if p["id"] == v.project_id:
            p["votes"] += 1
            return {"new_votes": p["votes"]}
    return {"error": "not found"}

@app.post("/api/apply-job")
def job(j: JobIn):
    return {"message": f"Applied for {j.skill}"}

@app.post("/api/report")
def rep(r: ReportIn):
    DB["reports"].append({"issue": r.issue, "loc": r.loc})
    return {"message": "Reported"}

@app.get("/api/reports")
def get_rep():
    return DB["reports"]

@app.get("/api/leaderboard")
def lead():
    return list(DB["members"].values())[:10]
