
import pandas as pd

# Load original dataset
df = pd.read_csv("alzheimers_disease_data.csv")

# Display first five records
print("First 5 records:")
print(df.head())

# Display dataset dimensions
print("\nDataset Shape:")
print(df.shape)

# Display column names
print("\nColumn Names:")
print(df.columns.tolist())

# Display missing values
print("\nMissing Values:")
print(df.isnull().sum())

# Display target distribution
print("\nDiagnosis Distribution:")
print(df["Diagnosis"].value_counts())

print("\nGender values:")
print(sorted(df["Gender"].unique()))

print("\nEthnicity values:")
print(sorted(df["Ethnicity"].unique()))

print("\nOther categorical values:")
for col in [
    "Smoking",
    "FamilyHistoryAlzheimers",
    "MemoryComplaints",
    "Forgetfulness"
]:
    print(col, sorted(df[col].unique()))