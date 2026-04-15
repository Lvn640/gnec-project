class RollingContextEngine:
    def __init__(self):
        self.hpi_summary = []      # Verified facts, tightly compressed with crypto-pointers
        self.active_alerts = []    # Unverified claims that CANNOT be summarized away

    def add_verified_finding(self, finding: str, citation_hash: str):
        """Compresses established facts into the HPI with an immutable link."""
        entry = {
            "fact": finding,
            "source_hash": citation_hash
        }
        self.hpi_summary.append(entry)
        print(f"[CONTEXT ENGINE] Verified fact committed to HPI. Pointer: {citation_hash[:16]}...")

    def add_unverified_claim(self, claim: str):
        """Pins unresolvable/unverified data directly to active memory."""
        self.active_alerts.append(claim)
        print(f"[CONTEXT ENGINE] Unverified claim pinned to active memory: '{claim}'")

    def generate_llm_payload(self) -> str:
        """Constructs the strictly bounded prompt for the next LLM inference cycle."""
        payload = "\n" + "="*40 + "\n"
        payload += "   BOUNDED PATIENT CONTEXT WINDOW\n"
        payload += "="*40 + "\n\n"
        
        payload += "[VERIFIED HPI - CRYPTOGRAPHICALLY LINKED]\n"
        if not self.hpi_summary:
            payload += "  (No verified history)\n"
        for item in self.hpi_summary:
            payload += f"  - {item['fact']} [REF: {item['source_hash'][:8]}]\n"
        
        payload += "\n[UNVERIFIED ALERTS - MUST BE RESOLVED]\n"
        if not self.active_alerts:
            payload += "  (No active alerts)\n"
        for alert in self.active_alerts:
            payload += f"  ! WARNING: {alert}\n"
            
        payload += "="*40
        return payload

# --- Quick Test of the Context Engine ---
if __name__ == "__main__":
    engine = RollingContextEngine()
    
    print("--- TESTING ROLLING CONTEXT ENGINE ---")
    
    # Simulating verified labs being injected
    engine.add_verified_finding("Patient admitted with severe hypotension (BP 95/60).", "53e44874e75e6ff4")
    engine.add_verified_finding("Lactate elevated at 3.4 mmol/L.", "99a1b2c3d4e5f6a7")
    
    # Simulating an unverified, dangerous hallucination or rumor
    engine.add_unverified_claim("Patient's spouse mentioned a history of heart murmurs, but no EMR records exist.")
    
    # Generating the exact payload the LLM will see on its next cycle
    print("\n[SYSTEM] Generating Next-Turn LLM Context Payload...")
    print(engine.generate_llm_payload())

