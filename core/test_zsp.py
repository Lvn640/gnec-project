import requests
import time

print("--- TESTING ZERO STANDING PRIVILEGE (ZSP) ---")

# 1. The AI Agent attempts to access the EMR Database WITHOUT a token (BOOTS BLIND)
print("\n[AGENT] Attempting direct read of Epic_LIS_Labs without token...")
res_fail = requests.get("http://127.0.0.1:8000/Epic_LIS_Labs/MRN-847291")
print(f"[EMR RESPONSE]: {res_fail.status_code} - {res_fail.json()}")

# 2. The AI Agent submits the formal forensic justification object
justification_payload = {
  "requested_endpoint": "Epic_LIS_Labs",
  "target_patient_id": "MRN-847291",
  "justification": "Evaluating HYP-002: Sepsis. Need recent Lactate values.",
  "requested_scope": "READ_ONLY_METABOLIC",
  "requested_duration": 2  # Token lives for exactly 2 seconds
}

print("\n[AGENT] Submitting Justification Object to ZSP Proxy...")
res_token = requests.post("http://127.0.0.1:8000/request_access", json=justification_payload)
token = res_token.json()["access_token"]
print(f"[AGENT] Received ephemeral token: {token[:15]}...")

# 3. The AI Agent uses the valid token immediately
headers = {"Authorization": f"Bearer {token}"}
print("\n[AGENT] Attempting read with valid token...")
res_success = requests.get("http://127.0.0.1:8000/Epic_LIS_Labs/MRN-847291", headers=headers)
print(f"[EMR RESPONSE]: {res_success.status_code} - {res_success.json()}")

# 4. The AI Agent tries to use the token after the encounter scope expires
print("\n[SYSTEM] Waiting 3 seconds for token to self-destruct...")
time.sleep(3)

print("\n[AGENT] Attempting read with expired token...")
res_expired = requests.get("http://127.0.0.1:8000/Epic_LIS_Labs/MRN-847291", headers=headers)
print(f"[EMR RESPONSE]: {res_expired.status_code} - {res_expired.json()}")

