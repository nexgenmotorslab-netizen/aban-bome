from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import sqlite3, os, random, time, json
from datetime import datetime

app = FastAPI(title="ABAN BOME Real Backend - Micro-Bank at Your Doorstep")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
DB_PATH = "/tmp/aban_real.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS members (id TEXT PRIMARY KEY, name TEXT, phone TEXT, loc TEXT, type TEXT, kg REAL DEFAULT 0, earned REAL DEFAULT 0, kakra REAL DEFAULT 0, points INTEGER DEFAULT 10, skill TEXT, applied TEXT DEFAULT '[]', created REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS fund (id INTEGER PRIMARY KEY, amount REAL DEFAULT 12450, inv_pool REAL DEFAULT 8000)''')
    c.execute('''CREATE TABLE IF NOT EXISTS projects (id INTEGER PRIMARY KEY, votes INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS reports (id INTEGER PRIMARY KEY AUTOINCREMENT, issue TEXT, loc TEXT, time TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS sweeps (id INTEGER PRIMARY KEY AUTOINCREMENT, member_id TEXT, kg REAL, sales REAL, sweeper_share REAL, gov_share REAL, fund_share REAL, area TEXT, time TEXT)''')
    c.execute("SELECT COUNT(*) as cnt FROM fund")
    if c.fetchone()["cnt"] == 0:
        c.execute("INSERT INTO fund (id, amount, inv_pool) VALUES (1, 12450, 8000)")
    c.execute("SELECT COUNT(*) as cnt FROM projects")
    if c.fetchone()["cnt"] == 0:
        for i, v in enumerate([312,234,189,156]):
            c.execute("INSERT INTO projects (id, votes) VALUES (?,?)", (i, v))
    conn.commit()
    conn.close()
init_db()

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
    waste_type: Optional[str] = "Plastic"
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
    return {"status":"ABAN BOME Real Backend Live","docs":"/docs","fund":"/api/fund"}

@app.get("/api/docs")
def docs():
    return {"message":"Use /docs for Swagger"}

@app.post("/api/members")
def create_member(m: MemberIn):
    member_id = "ABAN-" + os.urandom(3).hex().upper()
    conn = get_db()
    c = conn.cursor()
    kakra_init = m.investAmt if m.type=="Business" else 0
    c.execute("INSERT INTO members VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", (member_id, m.name, m.phone, m.loc, m.type, 0, kakra_init, kakra_init, 10, m.skill, json.dumps([]), time.time()))
    if m.type=="Business" and m.investAmt>0:
        c.execute("UPDATE fund SET amount = amount +?, inv_pool = inv_pool +? WHERE id=1", (m.investAmt*0.2, m.investAmt))
    conn.commit()
    conn.close()
    return {"id": member_id, "name": m.name, "type": m.type, "loc": m.loc, "kakra": kakra_init}

@app.get("/api/members")
def list_members():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM members ORDER BY created DESC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.get("/api/members/{member_id}")
def get_member(member_id: str):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM members WHERE id=?", (member_id,))
    r = c.fetchone()
    conn.close()
    if not r:
        return {"error":"Not found"}
    m = dict(r)
    m["applied"] = json.loads(m["applied"])
    m["dividend"] = round(m["kakra"]*0.1 + m["kg"]*3*0.4*0.05,2)
    m["contribution"] = round(m["kg"]*3*0.2 + m["kakra"],2)
    return m

@app.post("/api/sweep")
def do_sweep(s: SweepIn):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM members WHERE id=?", (s.member_id,))
    if not c.fetchone():
        conn.close()
        return {"error":"Member not found"}
    total_sales = s.kg * 3
    sweeper_share = total_sales * 0.4
    gov_share = total_sales * 0.4
    fund_share = total_sales * 0.2
    c.execute("UPDATE members SET kg=kg+?, earned=earned+?, points=points+? WHERE id=?", (s.kg, sweeper_share, int(s.kg*2), s.member_id))
    c.execute("UPDATE fund SET amount=amount+? WHERE id=1", (fund_share,))
    c.execute("INSERT INTO sweeps (member_id, kg, sales, sweeper_share, gov_share, fund_share, area, time) VALUES (?,?,?,?,?,?,?,?)", (s.member_id, s.kg, total_sales, sweeper_share, gov_share, fund_share, s.area, datetime.now().isoformat()))
    conn.commit()
    c.execute("SELECT amount FROM fund WHERE id=1")
    fund_amt = c.fetchone()["amount"]
    conn.close()
    return {"total_sales":total_sales,"you_40":sweeper_share,"gov_40":gov_share,"fund_20":fund_share,"fund_now":fund_amt}

@app.post("/api/kakra/collect")
def collect_single(k: KakraIn):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM members WHERE id=?", (k.member_id,))
    if not c.fetchone():
        conn.close()
        return {"error":"Member not found"}
    amt = round(random.uniform(0.07,0.97),2)
    c.execute("UPDATE members SET kakra=kakra+?, earned=earned+?, points=points+1 WHERE id=?", (amt, amt, k.member_id))
    c.execute("UPDATE fund SET amount=amount+? WHERE id=1", (amt,))
    c.execute("SELECT amount FROM fund WHERE id=1")
    fund_amt = c.fetchone()["amount"]
    conn.commit()
    conn.close()
    return {"collected":amt,"fund_now":fund_amt}

@app.post("/api/kakra/night-crawl")
def night_crawl():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM members")
    members = c.fetchall()
    if not members:
        conn.close()
        return {"error":"No members yet"}
    total=0
    logs=[]
    for mm in members:
        momo = round(random.uniform(0.01,0.90),2)
        air = round(random.uniform(0.01,0.20),2)
        data = round(random.uniform(0.02,0.40),2)
        summ = round(momo+air+data,2)
        total+=summ
        c.execute("UPDATE members SET kakra=kakra+?, earned=earned+?, points=points+1 WHERE id=?", (summ, summ, mm["id"]))
        logs.append({"name":mm["name"],"loc":mm["loc"],"total":summ})
    c.execute("UPDATE fund SET amount=amount+? WHERE id=1", (total,))
    c.execute("SELECT amount FROM fund WHERE id=1")
    fund_amt = c.fetchone()["amount"]
    conn.commit()
    conn.close()
    return {"message":f"Collected GHC {total:.2f} from {len(members)} accounts","total_collected":round(total,2),"fund_now":fund_amt,"details":logs[:10]}

@app.get("/api/fund")
def get_fund():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM fund WHERE id=1")
    fund = dict(c.fetchone())
    c.execute("SELECT COUNT(*), SUM(kg), SUM(kakra) FROM members")
    cnt, sumkg, sumkakra = c.fetchone()
    c.execute("SELECT * FROM projects ORDER BY id")
    projects = [dict(r) for r in c.fetchall()]
    conn.close()
    return {"fund":fund["amount"],"inv_pool":fund["inv_pool"],"members":cnt or 0,"total_kg":sumkg or 0,"total_kakra":sumkakra or 0,"projects":projects}

@app.post("/api/vote")
def vote(v: VoteIn):
    conn=get_db()
    c=conn.cursor()
    c.execute("SELECT points FROM members WHERE id=?", (v.member_id,))
    r=c.fetchone()
    if not r or r["points"]<1:
        conn.close()
        return {"error":"Need 1 point"}
    c.execute("UPDATE projects SET votes=votes+1 WHERE id=?", (v.project_id,))
    c.execute("UPDATE members SET points=points-1 WHERE id=?", (v.member_id,))
    conn.commit()
    c.execute("SELECT votes FROM projects WHERE id=?", (v.project_id,))
    new_votes=c.fetchone()["votes"]
    conn.close()
    return {"new_votes":new_votes}

@app.post("/api/apply-job")
def apply_job(j: JobIn):
    conn=get_db()
    c=conn.cursor()
    c.execute("SELECT points, applied FROM members WHERE id=?", (j.member_id,))
    r=c.fetchone()
    if not r or r["points"]<5:
        conn.close()
        return {"error":"Need 5 points"}
    applied=json.loads(r["applied"])
    applied.append(j.skill)
    c.execute("UPDATE members SET points=points-5, skill=?, applied=? WHERE id=?", (j.skill, json.dumps(applied), j.member_id))
    conn.commit()
    conn.close()
    return {"message":f"Applied for {j.skill}"}

@app.post("/api/report")
def report(r: ReportIn):
    conn=get_db()
    c=conn.cursor()
    c.execute("INSERT INTO reports (issue, loc, time) VALUES (?,?,?)", (r.issue, r.loc, datetime.now().isoformat()))
    conn.commit()
    conn.close()
    return {"message":"Reported"}

@app.get("/api/reports")
def get_reports():
    conn=get_db()
    c=conn.cursor()
    c.execute("SELECT * FROM reports ORDER BY id DESC LIMIT 10")
    rows=[dict(r) for r in c.fetchall()]
    conn.close()
    return rows

@app.get("/api/leaderboard")
def leaderboard():
    conn=get_db()
    c=conn.cursor()
    c.execute("SELECT * FROM members ORDER BY (kakra + kg) DESC LIMIT 10")
    rows=[dict(r) for r in c.fetchall()]
    conn.close()
    return rows
