import os
import time
import requests
import json
from dotenv import load_dotenv
from groq import Groq

# Load the .env file
load_dotenv()

# Map your custom 'GROQ' variable to the standard 'GROQ_API_KEY' if needed
if os.environ.get("GROQ") and not os.environ.get("GROQ_API_KEY"):
    os.environ["GROQ_API_KEY"] = os.environ.get("GROQ").strip('"').strip("'")

# Import all our sovereign micro-components
from core.crypto_layer import EpistemicVault
from core.engine import TheGuard, generate_clinical_hypothesis
from core.hitl_interceptor import HumanInTheLoopGate
from core.context_manager import RollingContextEngine

def run_aegis_pipeline():
    print("="*60)
    print("  INITIALIZING AEGIS-CLINICAL V3 MASTER PIPELINE")
    print("="*60)

    # 0. Initialize core systems
    if not os.environ.get("GROQ_API_KEY"):
        print("[SYSTEM FAULT] GROQ_API_KEY environment variable not set in .env. Aborting.")
        return

    client = Groq()
    vault = EpistemicVault()
    guard = TheGuard(vault)
    hitl_gate = HumanInTheLoopGate()
    context_engine = RollingContextEngine()
    
    patient_id = "MRN-847291"
    
    # --- PHASE 1: CRYPTOGRAPHIC INGESTION ---
    print("\n>>> PHASE 1: SECURING BASELINE DATA")
    # This represents the raw HL7/FHIR data hitting our system
    raw_vitals = {"Lactate": 3.4, "Systolic_BP": 95, "Respiratory_Rate": 24, "GCS": 15}
    data_hash = vault.ingest_patient_data(patient_id, raw_vitals)
    print(f"[VAULT] Data locked. Immutable Hash: {data_hash[:16]}...")

    # --- PHASE 2: ZERO STANDING PRIVILEGE ACCESS ---
    print("\n>>> PHASE 2: REQUESTING JIT ENCOUNTER TOKEN")
    justification = {
      "requested_endpoint": "Epic_LIS_Labs",
      "target_patient_id": patient_id,
      "justification": "Initial intake evaluation. Checking metabolic baseline.",
      "requested_scope": "READ_ONLY_METABOLIC",
      "requested_duration": 5
    }
    
    try:
        res_token = requests.post("http://127.0.0.1:8000/request_access", json=justification)
        token = res_token.json()["access_token"]
        print(f"[ZSP PROXY] Access Granted. Ephemeral Token: {token[:15]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        res_data = requests.get(f"http://127.0.0.1:8000/Epic_LIS_Labs/{patient_id}", headers=headers)
        retrieved_vitals = res_data.json()
        print(f"[ZSP PROXY] Secure Data Retrieval Successful.")
    except Exception as e:
        print(f"[SYSTEM FAULT] API Proxy unreachable or access denied: {e}")
        print("Make sure your uvicorn server is running in the background!")
        return

    # --- PHASE 3: CONTEXT BOUNDING ---
    print("\n>>> PHASE 3: COMPRESSING CONTEXT WINDOW")
    # We bind the verified data to its hash in the AI's memory
    context_engine.add_verified_finding(f"Metabolic Panel: {retrieved_vitals}", data_hash)
    llm_payload = context_engine.generate_llm_payload()

    # --- PHASE 4: DIAGNOSTIC HYPOTHESIS ---
    print("\n>>> PHASE 4: LLM HYPOTHESIS GENERATION")
    llm_json = generate_clinical_hypothesis(client, patient_id, llm_payload)
    print(json.dumps(llm_json, indent=2))

    # --- PHASE 5: DETERMINISTIC ENFORCEMENT ---
    print("\n>>> PHASE 5: AXIOMATIC GUARD INTERCEPTION")
    if guard.calculate_true_sepsis(data_hash):
        print("[GUARD] VERDICT: PASS. Mathematical criteria met.")
        
        # --- PHASE 6: HUMAN-IN-THE-LOOP ---
        print("\n>>> PHASE 6: ESCALATING TO ATTENDING PHYSICIAN")
        action = "INITIATE_SEPSIS_PROTOCOL" if llm_json["clinical_hypothesis"] else "UNKNOWN_ACTION"
        
        hitl_gate.request_authorization(
            agent_name="Aegis-Diagnostician-v3",
            action=action,
            target=patient_id,
            justification=f"Math verified on hash {data_hash[:8]}. {llm_json['required_criteria']}"
        )
    else:
        print("[GUARD] VERDICT: ERR_DETERMINISTIC_VIOLATION. Action blocked.")

if __name__ == "__main__":
    run_aegis_pipeline()

