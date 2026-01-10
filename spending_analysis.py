import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

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



# ================================
# PERCENTAGE GROWTH CALCULATION (2020–21 to 2025–26)
# ================================

growth_df = df_core[["Department", "2020–21", "2025–26"]].copy()

# Calculate percentage growth
growth_df["Percent Change"] = (
    (growth_df["2025–26"] - growth_df["2020–21"]) / growth_df["2020–21"]
) * 100

# Round for readability
growth_df["Percent Change"] = growth_df["Percent Change"].round(2)

print("\nPercentage growth from 2020–21 to 2025–26:")
print(growth_df)

# Save results to CSV for GitHub
growth_df.to_csv("results/percentage_growth_2020_2025.csv", index=False)

# ================================
# BAR CHART: 2025–26 COMPARISON
# ================================

latest_values = df_core[["Department", "2025–26"]].copy()

fig1 = plt.figure()
plt.bar(latest_values["Department"], latest_values["2025–26"] / 1000)
plt.ylabel("£ billion (2025–26)")
plt.title("UK Administration Budgets – Health vs Education vs Defence (2025–26)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()

fig1.savefig("results/charts/department_comparison_2025.png", dpi=300)
plt.show()
plt.close(fig1)


# ================================
# MULTI-YEAR TREND CHART
# ================================

years = ["2020–21", "2021–22", "2022–23", "2023–24", "2024–25", "2025–26"]

fig2 = plt.figure()

for _, row in df_core.iterrows():
    plt.plot(years, row[1:], marker="o", label=row["Department"])

plt.ylabel("£ million")
plt.title("UK Administration Budgets – Health vs Education vs Defence (Trends)")
plt.xticks(rotation=45, ha="right")
plt.legend()
plt.tight_layout()

fig2.savefig("results/charts/department_trends.png", dpi=300)
plt.show()
plt.close(fig2)

# =====================================================
# INTERNATIONAL COMPARISON: COFOG (G7 PEERS)
# =====================================================

# Load COFOG per-capita data
cofog_df = pd.read_csv("data/cofog/g7_cofog_per_capita.csv")

# Clean strings (important)
cofog_df["Country"] = cofog_df["Country"].astype(str).str.strip()
cofog_df["Function"] = cofog_df["Function"].astype(str).str.strip()

print("\nCOFOG dataset loaded:")
print(cofog_df.head())

PEER_COUNTRIES = [
    "United Kingdom",
    "United States",
    "France",
    "Germany",
    "Japan"
]

df_peers = cofog_df[cofog_df["Country"].isin(PEER_COUNTRIES)].copy()

print("\nUK vs selected G7 peers (raw rows):")
print(df_peers)

wide_peers = df_peers.pivot(
    index="Function",
    columns="Country",
    values="Spending_Per_Capita_USD"
)

function_order = ["Health", "Education", "Defence"]
wide_peers = wide_peers.reindex(function_order)

print("\nWide peer comparison table:")
print(wide_peers)

x = np.arange(len(wide_peers.index))
bar_width = 0.15

plt.figure(figsize=(10, 6))

for i, country in enumerate(wide_peers.columns):
    plt.bar(
        x + i * bar_width,
        wide_peers[country],
        width=bar_width,
        label=country
    )

plt.xticks(x + bar_width * (len(wide_peers.columns) - 1) / 2, wide_peers.index)
plt.ylabel("Spending per capita (USD)")
plt.title("Government Functional Spending per Capita – UK vs Selected G7 Peers (COFOG, 2022)")
plt.legend()
plt.grid(axis="y", linestyle="--", alpha=0.3)
plt.tight_layout()

plt.savefig("results/charts/uk_vs_g7_peers_cofog_per_capita.png", dpi=300)
plt.show()

