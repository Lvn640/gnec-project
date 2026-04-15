from fastapi import FastAPI, HTTPException, Header, Depends
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta, timezone

app = FastAPI(title="Aegis ZSP Proxy")
SECRET_KEY = "aegis_cryptographic_signing_key_v3"

# The forensic justification object you designed
class AccessRequest(BaseModel):
    requested_endpoint: str
    target_patient_id: str
    justification: str
    requested_scope: str
    requested_duration: int

@app.post("/request_access")
def request_access(req: AccessRequest):
    # 1. Log the encounter for HIPAA/Audit compliance
    print(f"\n[ZSP AUDIT LOG] Access Request Received:")
    print(f"  -> Target: {req.target_patient_id}")
    print(f"  -> Justification: {req.justification}")
    
    # 2. Issue a Time-Bounded JWT
    expiration = datetime.now(timezone.utc) + timedelta(seconds=req.requested_duration)
    token_data = {
        "sub": req.target_patient_id,
        "scope": req.requested_scope,
        "exp": expiration
    }
    
    token = jwt.encode(token_data, SECRET_KEY, algorithm="HS256")
    print(f"[ZSP PROXY] Token issued. Self-destructing in {req.requested_duration} seconds.")
    
    return {"access_token": token, "expires_in": req.requested_duration}

@app.get("/Epic_LIS_Labs/{patient_id}")
def get_labs(patient_id: str, authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="ERR_ZSP_VIOLATION: No token provided.")
    
    token = authorization.split(" ")[1]
    
    try:
        # 3. Cryptographically verify the token and its expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        
        if payload["sub"] != patient_id:
            raise HTTPException(status_code=403, detail="ERR_ZSP_VIOLATION: Token not scoped for this patient.")
        if payload["scope"] != "READ_ONLY_METABOLIC":
            raise HTTPException(status_code=403, detail="ERR_ZSP_VIOLATION: Invalid scope.")
            
        # If token is valid, return the mocked data
        print(f"[ZSP PROXY] Valid token processed for {patient_id}.")
        return {"Lactate": 3.4, "Systolic_BP": 95, "Respiratory_Rate": 24, "GCS": 15}
        
    except jwt.ExpiredSignatureError:
        print("[ZSP PROXY] REJECTED: Token expired.")
        raise HTTPException(status_code=401, detail="ERR_ZSP_VIOLATION: Token self-destructed.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="ERR_ZSP_VIOLATION: Cryptographic signature invalid.")

