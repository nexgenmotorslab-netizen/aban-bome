from fastapi import FastAPI
from pydantic import BaseModel
import hashlib, uuid
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

members_db = {}
sweep_pool = {"total_swept": 0, "members_swept": {}}
skills_db = [
    {"id": "SK01", "name": "Digital Bookkeeping", "provider": "GEA + Assembly"},
    {"id": "SK02", "name": "Smart Farming", "provider": "KTU + MoFA"},
    {"id": "SK03", "name": "Liquid Soap & Pastries", "provider": "NVTI + YEA"},
]


class MemberRegister(BaseModel):
    full_name: str
    phone: str
    town: str
    type: str


class SweepRequest(BaseModel):
    phone: str
    momo_balance: float
    airtime_balance: float
    data_mb: float


@app.get("/api/")
def home():
    return {
        "status": "ABAN BOME 3-in-1 LIVE",
        "members": len(members_db),
        "pool": sweep_pool["total_swept"],
    }


@app.post("/api/membership/register")
def register(data: MemberRegister):
    mid = f"OKP-{datetime.now().year}-{str(uuid.uuid4())[:4].upper()}"
    members_db[data.phone] = {
        "member_id": mid,
        "trust_score": 10,
        "kakra_wallet": 0,
        "certificates": 0,
        **data.dict(),
    }
    return {
        "ok": True,
        "member_id": mid,
        "msg": f"Akwaaba {data.full_name}! OKP ID: {mid} | Kakra Wallet Opened",
    }


@app.post("/api/skills/certify")
def certify(phone: str, skill_id: str):
    m = members_db.get(phone)
    if not m:
        return {"error": "Register first"}
    m["certificates"] += 1
    m["trust_score"] += 40
    cert_hash = hashlib.sha256(f"{phone}{skill_id}".encode()).hexdigest()[:10]
    return {
        "cert_id": f"CERT-{cert_hash.upper()}",
        "issued_by": "GEA/YEA/KTU + Assembly + Gov Ghana",
        "qr": f"gov.gh/verify/{cert_hash}",
        "new_score": m["trust_score"],
        "loan_limit": m["trust_score"] * 30,
    }


@app.post("/api/kakra/sweep")
def sweep(data: SweepRequest):
    m = members_db.get(data.phone)
    if not m:
        return {"error": "Not member - register first"}
    momo_k = round(data.momo_balance - int(data.momo_balance), 2)
    air_k = round(data.airtime_balance - int(data.airtime_balance), 2)
    data_k = round(data.data_mb * 0.01, 2)
    total = round(momo_k + air_k + data_k, 2)
    if total < 0.1:
        total = 0
    m["kakra_wallet"] = round(m.get("kakra_wallet", 0) + total, 2)
    m["trust_score"] += 1
    sweep_pool["total_swept"] = round(sweep_pool["total_swept"] + total, 2)
    sweep_pool["members_swept"][data.phone] = round(
        sweep_pool["members_swept"].get(data.phone, 0) + total, 2
    )
    return {
        "swept_today": total,
        "your_wallet": m["kakra_wallet"],
        "score": m["trust_score"],
        "pool_total": sweep_pool["total_swept"],
        "msg": f"Wo kakra GH₵{total} akɔ Okuapeman Fund mu. 80% profit returns to you after 90 days.",
    }


@app.get("/api/dashboard")
def dash():
    return {
        "total_members": len(members_db),
        "total_swept": sweep_pool["total_swept"],
        "members_swept": sweep_pool["members_swept"],
        "all_members": list(members_db.values()),
    }
