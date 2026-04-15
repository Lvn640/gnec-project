import pandas as pd
import json

def mine_forensic_gallery():
    print("🛰️  MINING LOCAL DATASET FOR FORENSIC ARCHETYPES...")
    df = pd.read_csv("data/Dataset.csv")

    # 1. The Success: Clear physiological crash + True Sepsis
    success_case = df[(df['SepsisLabel'] == 1) & (df['SBP'] < 95) & (df['Resp'] > 22)].head(1)

    # 2. The Hero: Totally stable patient (to test AI hallucination/Guard Veto)
    # We pick someone who is definitely NOT septic.
    hero_case = df[(df['SepsisLabel'] == 0) & (df['SBP'] > 115) & (df['Resp'] < 18)].head(1)

    # 3. The Silent Breach: Vitals look fine, but Lactate is high
    silent_case = df[(df['SepsisLabel'] == 1) & (df['SBP'] > 105) & (df['Lactate'] > 3.5)].head(1)

    gallery = []
    for label, case in [("SUCCESS", success_case), ("WATCHDOG_HERO", hero_case), ("SILENT_BREACH", silent_case)]:
        if not case.empty:
            row = case.iloc[0]
            gallery.append({
                "archetype": label,
                "patient_id": str(int(row['Patient_ID'])),
                "hour": int(row['Hour']),
                "vitals": {
                    "SBP": float(row['SBP']),
                    "Resp": float(row['Resp']),
                    "Lactate": float(row['Lactate']) if pd.notnull(row['Lactate']) else 1.0
                },
                "ground_truth_sepsis": int(row['SepsisLabel'])
            })

    with open("data/forensic_gallery.json", "w") as f:
        json.dump(gallery, f, indent=4)
    
    print(f"✅ GALLERY CREATED: {len(gallery)} archetypes extracted to data/forensic_gallery.json")

if __name__ == "__main__":
    mine_forensic_gallery()

