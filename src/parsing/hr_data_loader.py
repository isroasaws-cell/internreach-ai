import pandas as pd

def load_hr_contacts(path="data/hr_contacts.xlsx"):
    df = pd.read_excel(path)
    df.columns = [c.strip() for c in df.columns]
    required = ["HR Name", "HR Email", "Company Name", "Domain"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    records = []
    for _, row in df.iterrows():
        records.append({
            "hr_name": str(row["HR Name"]).strip(),
            "hr_email": str(row["HR Email"]).strip(),
            "company": str(row["Company Name"]).strip(),
            "domain": str(row["Domain"]).strip(),
            "website": str(row.get("Company Website", "")).strip(),
        })
    print(f"Loaded {len(records)} HR contacts")
    return records