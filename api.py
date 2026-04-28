import os
import json
import hashlib
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from groq import Groq
from core.crypto_layer import EpistemicVault
from core.engine import TheGuard

# Load the .env file
load_dotenv()

# Map custom GROQ variable to GROQ_API_KEY if needed
if os.environ.get("GROQ") and not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = os.environ.get("GROQ").strip('"').strip("'")

app = FastAPI(title="Aegis Clinical API")

# Add CORS to allow frontend to communicate during dev
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def generate_dynamic_hypothesis(client, data_content):
    prompt = f"""
    You are an AI Medical Analyst operating under strict deterministic supervision.
    Analyze the following patient medical file content:
    ---
    {data_content}
    ---
    Determine the primary objective of this file and the underlying clinical hypothesis.
    The objective should fundamentally relate to diagnosing a medical condition or monitoring patient status.
    
    Return ONLY a JSON object with this exact structure:
    {{
        "objective": "Diagnose medical condition / Assess vitals",
        "clinical_hypothesis": "Sepsis secondary to...",
        "required_criteria": ["qSOFA score >= 2", "Lactate > 2.0 mmol/L"],
        "confidence": "HIGH",
        "status": "PENDING_CALCULATION"
    }}
    """
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "You are a clinical JSON generator. Output only valid JSON."},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.0
    )
    return json.loads(response.choices[0].message.content)


@app.post("/api/upload_medical_file")
async def upload_medical_file(file: UploadFile = File(...)):
    if not os.environ.get("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")

    content = await file.read()
    text_content = content.decode('utf-8')
    
    # Simple parse: we assume the text contains some vitals like Lactate, Systolic_BP, Respiratory_Rate, etc.
    # We will try to parse JSON if it is JSON, otherwise just pass the raw text to LLM
    try:
        parsed_vitals = json.loads(text_content)
    except json.JSONDecodeError:
        parsed_vitals = {"raw_text": text_content} # Fallback for unstructured text
    
    patient_id = "UPLOADED_PATIENT"

    # Initialize core modules
    client = Groq()
    vault = EpistemicVault()
    guard = TheGuard(vault)

    # 1. Cryptographic Ingestion
    data_hash = vault.ingest_patient_data(patient_id, parsed_vitals)

    # 2. LLM Objective & Hypothesis
    hypothesis_json = generate_dynamic_hypothesis(client, text_content)

    # 3. Watchdog (Guard) Verification
    # TheGuard calculate_true_sepsis checks for qSOFA and Lactate. We can pass it.
    guard_result = guard.calculate_true_sepsis(data_hash)

    return {
        "status": "success",
        "hash": data_hash,
        "llm_result": hypothesis_json,
        "guard_verified": guard_result,
        "vitals_parsed": parsed_vitals
    }

class ChatRequest(BaseModel):
    message: str
    context: str

@app.post("/api/chat")
async def chat_with_ai(req: ChatRequest):
    if not os.environ.get("GROQ_API_KEY"):
        raise HTTPException(status_code=500, detail="GROQ_API_KEY not configured")
    
    client = Groq()
    
    system_prompt = f"""
You are Diagnostyx AI, a highly advanced clinical assistant operating under a deterministic Python watchdog (Guard AI).
You must analyze the patient's medical query based on the following mock medical history:
- Patient: Maria Gonzalez, 52 y/o.
- Chronic Conditions: Hypertension, Type 2 Diabetes.
- Family History: Cardiomyopathy (Father), Type 2 Diabetes (Mother).
- Allergies: Penicillin, Sulfa drugs (Cross-reactivity risk with Cephalosporins).
- Current Meds: Metformin 500mg (2x daily), Lisinopril 10mg (1x daily), Atorvastatin 20mg (1x daily).
- Recent Reports: 
  - [1] ECG Report (Apr 2026): Elevated resting heart rate of 92 bpm, irregular patterns.
  - [2] HbA1c Test (Mar 2026): 7.2%.
  - [3] Lipid Panel (Feb 2026): Normal ranges on Atorvastatin.
- Vitals: BP 138/88, HR 92 bpm, Temp 37.1°C.

When answering, ALWAYS act as an Explainable AI (XAI). Cite the data you use using bracketed numbers (e.g. [1], [2]) that correspond to specific reports or data points from the list above. Keep answers concise, empathetic, and professional.
"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": req.message}
        ],
        temperature=0.2
    )
    
    return {"reply": response.choices[0].message.content}
