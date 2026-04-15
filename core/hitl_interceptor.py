
import time
from datetime import datetime, timezone

class HumanInTheLoopGate:
    def request_authorization(self, agent_name: str, action: str, target: str, justification: str) -> bool:
        print("\n" + "="*55)
        print(" 🚨 AEGIS CLINICAL AUTHORIZATION REQUEST 🚨")
        print("="*55)
        print(f"Agent:         {agent_name}")
        print(f"Action:        {action}")
        print(f"Target:        {target}")
        print(f"Justification: {justification}")
        print("Risk Class:    HIGH - REQUIRES MD SIGNATURE")
        print("="*55)
        
        while True:
            response = input("\nAction Required -> Type APPROVE or DENY: ").strip().upper()
            
            if response == "APPROVE":
                print("\n[SYSTEM] Attending MD Authorization: GRANTED.")
                print("[SYSTEM] Taking pre-execution 'before-state' EMR snapshot...")
                time.sleep(1) # Simulating database operation
                
                print(f"[SYSTEM] EXECUTING {action} ON TARGET {target}...")
                time.sleep(1)
                
                print("[SYSTEM] Taking post-execution 'after-state' EMR snapshot...")
                print("[SYSTEM] Cryptographic baseline secured. Protocol active.")
                return True
                
            elif response == "DENY":
                print("\n[SYSTEM] Attending MD Authorization: DENIED.")
                rationale = input("SYSTEM LOCK: Please input clinical rationale for denial: ").strip()
                
                timestamp = datetime.now(timezone.utc).isoformat()
                print(f"\n[SYSTEM] Action aborted. Logged to immutable EMR graph:")
                print(f"         -> Denial Rationale: '{rationale}'")
                print(f"         -> Timestamp: {timestamp}")
                return False
                
            else:
                print("INVALID INPUT. You must type exactly APPROVE or DENY.")

# --- Quick Test of the Interceptor ---
if __name__ == "__main__":
    gate = HumanInTheLoopGate()
    
    # Simulating the exact payload from your architectural design
    gate.request_authorization(
        agent_name="Aegis-Diagnostician-v3",
        action="INITIATE_SEPSIS_PROTOCOL",
        target="MRN-847291",
        justification="Lactate 3.4, qSOFA 2, HR 115. Mathematical criteria met."
    )

