import pandas as pd
import os
import json
import hashlib
import time
from groq import Groq
from dotenv import load_dotenv

# Import our sovereign logic modules
from core.crypto_layer import EpistemicVault
from core.engine import TheGuard, generate_clinical_hypothesis
from core.hitl_interceptor import HumanInTheLoopGate
from core.context_manager import RollingContextEngine

# 1. INITIALIZATION
load_dotenv()
if os.environ.get("GROQ"):
    os.environ["GROQ_API_KEY"] = os.environ.get("GROQ").strip('"').strip("'")

client = Groq()
vault = EpistemicVault()
guard = TheGuard(vault)
hitl = HumanInTheLoopGate()
context_engine = RollingContextEngine()

def run_exhaustive_audit(sample_size=100):
    print("\n" + "="*60)
    print(" 🛡️  AEGIS-CLINICAL V4: EXHAUSTIVE FORENSIC AUDIT START")
    print("="*60)
    
    # 2. DATA INGESTION
    if not os.path.exists("data/Dataset.csv"):
        print("[ERROR] Dataset.csv not found in data/ folder.")
        return

    print("[SYSTEM] Loading Master ICU Ledger (86MB)...")
    df = pd.read_csv("data/Dataset.csv")
    
    # We focus on the high-signal rows: Patients with confirmed Sepsis 
    # to see if we can catch the moment they crashed.
    target_data = df[df['SepsisLabel'] == 1].sample(n=sample_size)
    
    stats = {"total": 0, "guard_alerts": 0, "llm_confirmations": 0, "vetoes": 0}

    # 3. THE FORENSIC LOOP
    for _, row in target_data.iterrows():
        stats["total"] += 1
        p_id = str(int(row['Patient_ID']))
        hour = row['Hour']
        
        # Mapping Real Headers to Aegis Schema
        vitals = {
            "Lactate": row['Lactate'] if pd.notnull(row['Lactate']) else 1.0,
            "Systolic_BP": row['SBP'] if pd.notnull(row['SBP']) else 120,
            "Respiratory_Rate": row['Resp'] if pd.notnull(row['Resp']) else 16,
            "GCS": 15 # Assuming alert unless otherwise noted
        }

        # 4. DETERMINISTIC CALCULATION (qSOFA)
        # qSOFA = 1pt for SBP <= 100, 1pt for Resp >= 22
        qsofa_score = 0
        if vitals["Systolic_BP"] <= 100: qsofa_score += 1
        if vitals["Respiratory_Rate"] >= 22: qsofa_score += 1

        # 5. THE INFERENCE TRIGGER
        # We only call the LLM if the math looks dangerous (qSOFA >= 1)
        if qsofa_score >= 1 or vitals["Lactate"] > 2.0:
            stats["guard_alerts"] += 1
            print(f"\n[!] BREACH DETECTED: Patient {p_id} at Hour {hour}")
            print(f"    Math: qSOFA={qsofa_score}/2 | Lactate={vitals['Lactate']}")
            
            # Cryptographic Anchoring
            row_hash = hashlib.sha256(json.dumps(vitals, sort_keys=True).encode()).hexdigest()
            vault.ingest_patient_data(p_id, vitals)
            
            # Rolling Context Injection
            context_engine.add_verified_finding(f"Vitals at Hr {hour}: {vitals}", row_hash)
            payload = context_engine.generate_llm_payload()

            # LLM Analysis (Groq Llama-3.3-70b)
            print(f"    [LLM] Requesting clinical hypothesis for Patient {p_id}...")
            hypothesis = generate_clinical_hypothesis(client, p_id, payload)
            
            # 6. HUMAN-IN-THE-LOOP INTERCEPTION
            if hypothesis["clinical_hypothesis"]:
                stats["llm_confirmations"] += 1
                approved = hitl.request_authorization(
                    agent_name="Aegis-Scribe-V4",
                    action="INITIATE_SEPSIS_BUNDLE",
                    target=p_id,
                    justification=f"Forensic Audit Hr {hour}. Hash: {row_hash[:8]}. {hypothesis['clinical_hypothesis']}"
                )
                if approved:
                    print(f"    [SUCCESS] Intervention Logged for Patient {p_id}")
            else:
                stats["vetoes"] += 1
                print(f"    [VETO] LLM dismissed the physiological spike as non-septic.")

    # 7. FINAL REPORT
    print("\n" + "="*60)
    print(" 📊 FINAL FORENSIC AUDIT REPORT")
    print("="*60)
    print(f"Total Records Scanned:     {stats['total']}")
    print(f"Physiological Alerts:      {stats['guard_alerts']}")
    print(f"Clinical Confirmations:    {stats['llm_confirmations']}")
    print(f"AI Vetoes:                 {stats['vetoes']}")
    print("="*60)

if __name__ == "__main__":
    run_exhaustive_audit(sample_size=15) # Start with 15 real patients

