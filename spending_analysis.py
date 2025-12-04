import pandas as pd
import matplotlib.pyplot as plt

file_path = "data/pesa.xlsx"

# Load the DEPARTMENT-LEVEL sheet with ALL columns
df_raw = pd.read_excel(file_path, sheet_name="Table_1_7")

print("Raw department sheet preview:")
print(df_raw.head(12))

# ---- CLEANING FOR MULTI-YEAR DATA ----

# Skip first 4 messy rows
# Keep:
#  - Column 0  -> Department name
#  - Columns 1 to last-1 -> Year columns
df = df_raw.iloc[4:, :].copy()

# Manually rename columns (department + years)
df.columns = [
    "Department",
    "2020–21",
    "2021–22",
    "2022–23",
    "2023–24",
    "2024–25",
    "2025–26"
]

# Drop rows where department name is missing
df = df.dropna(subset=["Department"])

# Convert ALL year columns to numbers
for col in df.columns[1:]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# Reset index
df = df.reset_index(drop=True)

print("\nCleaned multi-year department data:")
print(df.head(10))

# ---- FILTER TO HEALTH, EDUCATION, DEFENCE ----

df_core = df[
    df["Department"].str.contains("Health|Education|Defence", case=False, na=False)
].copy()

print("\nHealth, Education & Defence (all years):")
print(df_core)

# ---- PREPARE DATA FOR TREND PLOTTING ----

# Manually assign financial year labels
years = [
    "2020–21",
    "2021–22",
    "2022–23",
    "2023–24",
    "2024–25",
    "2025–26"
]
# ---- MULTI-YEAR TREND CHART ----

plt.figure()

for _, row in df_core.iterrows():
    plt.plot(years, row[1:], marker="o", label=row["Department"])

plt.ylabel("£ million")
plt.title("UK Administration Budgets – Health vs Education vs Defence (Trends)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()
plt.show()

