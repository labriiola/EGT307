#import
import pandas as pd
import os

# Folder where all 12 station CSV files are stored
data_folder = "data"

# List of all 12 station file names
station_files = [
    "PRSA_Data_Aotizhongxin_20130301-20170228.csv",
    "PRSA_Data_Changping_20130301-20170228.csv",
    "PRSA_Data_Dingling_20130301-20170228.csv",
    "PRSA_Data_Dongsi_20130301-20170228.csv",
    "PRSA_Data_Guanyuan_20130301-20170228.csv",
    "PRSA_Data_Gucheng_20130301-20170228.csv",
    "PRSA_Data_Huairou_20130301-20170228.csv",
    "PRSA_Data_Nongzhanguan_20130301-20170228.csv",
    "PRSA_Data_Shunyi_20130301-20170228.csv",
    "PRSA_Data_Tiantan_20130301-20170228.csv",
    "PRSA_Data_Wanliu_20130301-20170228.csv",
    "PRSA_Data_Wanshouxigong_20130301-20170228.csv"
]

# Empty list to collect each station's table before combining
all_data = []

# Read each file one at a time and add it to the list
for file_name in station_files:
    file_path = os.path.join(data_folder, file_name)
    station_df = pd.read_csv(file_path)
    all_data.append(station_df)
    print(f"Loaded {file_name}: {len(station_df)} rows")

# Stack all 12 tables into one combined table
combined_df = pd.concat(all_data, ignore_index=True)

print("Combined dataset shape:", combined_df.shape)
print(combined_df.head())


# --- STEP 2: Check and clean missing values ---

print("\nMissing values per column before cleaning:")
print(combined_df.isnull().sum())

# Fill missing pollutant/weather readings using the previous valid reading
# This makes sense for hourly sensor data, since air quality doesn't jump
# instantly - the last known value is a reasonable stand-in for a gap
columns_to_fill = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3",
                    "TEMP", "PRES", "DEWP", "RAIN", "WSPM", "wd"]

combined_df[columns_to_fill] = combined_df[columns_to_fill].ffill()
combined_df[columns_to_fill] = combined_df[columns_to_fill].bfill()

print("\nMissing values per column after cleaning:")
print(combined_df.isnull().sum())

# --- STEP 3: Convert PM2.5 into risk categories ---

def classify_risk(pm25_value):
    if pm25_value <= 35:
        return "Good"
    elif pm25_value <= 75:
        return "Moderate"
    elif pm25_value <= 150:
        return "Unhealthy"
    else:
        return "Hazardous"

combined_df["risk_level"] = combined_df["PM2.5"].apply(classify_risk)

print("\nRisk level counts:")
print(combined_df["risk_level"].value_counts())

# Save the cleaned, labeled dataset so the next script doesn't need
# to redo steps 1-3 every time
combined_df.to_csv("cleaned_data.csv", index=False)
print("\nSaved cleaned_data.csv")