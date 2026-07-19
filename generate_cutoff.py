import pandas as pd
import random

# Read colleges.csv
df = pd.read_csv("colleges.csv")

# Ensure cutoff column exists
if "cutoff" not in df.columns:
    df["cutoff"] = ""

def assign_cutoff(row):
    name = str(row.get("college_name", "")).lower()
    ctype = str(row.get("type", "")).lower()

    # IIT
    if "iit" in name:
        return random.randint(198, 200)

    # NIT
    elif "nit" in name:
        return random.randint(195, 198)

    # IIIT
    elif "iiit" in name:
        return random.randint(190, 195)

    # Anna University
    elif "anna university" in name:
        return 195

    # PSG
    elif "psg" in name:
        return random.randint(193, 195)

    # VIT
    elif "vit" in name:
        return random.randint(180, 190)

    # SRM
    elif "srm" in name:
        return random.randint(175, 185)

    # SASTRA
    elif "sastra" in name:
        return random.randint(178, 185)

    # Government colleges
    elif "government" in ctype:
        return random.randint(170, 190)

    # Engineering colleges
    elif "engineering" in name:
        return random.randint(140, 180)

    # Default
    else:
        return random.randint(120, 170)


# Fill cutoff values
df["cutoff"] = df.apply(assign_cutoff, axis=1)

# Save back to same file
df.to_csv("colleges.csv", index=False)

print("===================================")
print("✅ Cutoff generated successfully!")
print("📄 colleges.csv updated.")
print("===================================")