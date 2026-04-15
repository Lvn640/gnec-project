import os
import json
from groq import Groq
from core.crypto_layer import EpistemicVault

#from crypto_layer import EpistemicVault

# --- COMPONENT 7: The Guard (Deterministic State Machine) ---
class TheGuard:
    def __init__(self, vault: EpistemicVault):
        self.vault = vault

    def calculate_true_sepsis(self, data_hash: str) -> bool:
        """Bypasses LLM entirely, fetches raw cryptographic data, calculates math."""
        try:
            raw_data = self.vault.retrieve_raw_data(data_hash)
        except ValueError as e:
            print(f"\n[GUARD SHUTDOWN] {e}")
            return False
        
        # Strict Sepsis Math (qSOFA & Lactate)
        qsofa = 0
        if raw_data.get('Systolic_BP', 120) <= 100: qsofa += 1
        if raw_data.get('Respiratory_Rate', 16) >= 22: qsofa += 1
        if raw_data.get('GCS', 15) < 15: qsofa += 1
        
        lactate = raw_data.get('Lactate', 1.0)
        
        # Axiom 2: No AI action is trustworthy without deterministic math.
        is_valid = (qsofa >= 2) and (lactate > 2.0)
        
        print(f"\n[GUARD CALCULATOR] Executed independent math: qSOFA={qsofa}/3, Lactate={lactate} mmol/L.")
        return is_valid

# --- COMPONENT 1: The Diagnostician (LLM) ---
def generate_clinical_hypothesis(client, patient_id, vitals_summary):
    prompt = f"""
    You are Aegis-Diagnostician. Analyze these vitals for patient {patient_id}: {vitals_summary}
    Return ONLY a JSON object with this exact structure:
    {{
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
        temperature=0.0 # Zero creativity. We want deterministic outputs.
    )
    return json.loads(response.choices[0].message.content)

# --- EXECUTION PIPELINE ---
if __name__ == "__main__":
    if not os.environ.get("GROQ_API_KEY"):
        print("[SYSTEM FAULT] GROQ_API_KEY environment variable not set. Aborting.")
        exit(1)
        
    client = Groq()
    vault = EpistemicVault()
    guard = TheGuard(vault)
    
    # 1. Ingestion Layer
    patient_id = "MRN-847291"
    # These vitals trigger a valid Sepsis flag: SysBP <= 100, RR >= 22, Lactate > 2.0
    critical_vitals = {"Lactate": 3.4, "Systolic_BP": 95, "Respiratory_Rate": 24, "GCS": 15}
    
    print("--- AEGIS-CLINICAL V3 INITIALIZED ---")
    data_hash = vault.ingest_patient_data(patient_id, critical_vitals)
    print(f"[SYSTEM] Patient data hashed and locked. Citation: {data_hash[:16]}...")
    
    # 2. AI Hypothesis Generation
    print("\n[AI DIAGNOSTICIAN] Ingesting telemetry and formulating hypothesis...")
    # Notice we only give the AI a string summary, NOT the database access
    llm_json = generate_clinical_hypothesis(client, patient_id, str(critical_vitals))
    print(json.dumps(llm_json, indent=2))
    
    # 3. Deterministic Interception
    print("\n[SYSTEM] Intercepting JSON hypothesis. Firing Axiomatic Enforcement Engine...")
    
    if guard.calculate_true_sepsis(data_hash):
        print("[GUARD] VERDICT: PASS. Mathematical criteria met. Sepsis alert authorized for human review.")
    else:
        print("[GUARD] VERDICT: ERR_DETERMINISTIC_VIOLATION. Action blocked. AI hallucination or sub-threshold vitals detected.")

