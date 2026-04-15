import hashlib
import json
from datetime import datetime, timezone

class EpistemicVault:
    def __init__(self):
        # In a real app, this is a locked database. Here, it is our protected memory space.
        self._secure_ledger = {}

    def ingest_patient_data(self, patient_id: str, raw_data: dict) -> str:
        """
        Takes raw patient data, hashes it deterministically, and stores it securely.
        Returns the SHA-256 hash citation.
        """
        # Create a clean, sorted string representation to ensure consistent hashing
        data_string = json.dumps(raw_data, sort_keys=True)
        
        # Generate the SHA-256 hash
        data_hash = hashlib.sha256(data_string.encode('utf-8')).hexdigest()
        
        # Timestamp the ingestion
        timestamp = datetime.now(timezone.utc).isoformat()
        
        # Store in the vault (simulating our tamper-evident baseline)
        self._secure_ledger[data_hash] = {
            "patient_id": patient_id,
            "raw_data": raw_data,
            "timestamp": timestamp,
            "status": "IMMUTABLE"
        }
        
        return data_hash

    def retrieve_raw_data(self, data_hash: str) -> dict:
        """
        The ONLY way the AI or the Deterministic Guard can access data is by citing the exact hash.
        """
        if data_hash not in self._secure_ledger:
            raise ValueError("ERR_DETERMINISTIC_VIOLATION: Invalid or missing cryptographic citation.")
        
        return self._secure_ledger[data_hash]["raw_data"]

# --- Quick Test to verify the architecture ---
if __name__ == "__main__":
    vault = EpistemicVault()
    
    # Simulating a row from an ICU dataset
    sample_lab_row = {"Lactate": 3.4, "Systolic_BP": 95, "qSOFA_Score": 2}
    
    print("Ingesting data into the vault...")
    citation_hash = vault.ingest_patient_data("MRN-847291", sample_lab_row)
    
    print(f"Data secured. Immutable Hash: {citation_hash}")
    print("Retrieving via hash...")
    print(vault.retrieve_raw_data(citation_hash))

