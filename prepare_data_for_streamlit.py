import pandas as pd
import numpy as np

data_en = pd.read_csv("/Users/roman/GitHub/m4d/models/eegnet_extended.csv")

data_en["lpf"] = data_en["lpf"].fillna(0).astype(int).astype(str)
data_en["lpf"] = data_en["lpf"].replace("0", "None")
data_en["hpf"] = data_en["hpf"].fillna(0).astype(float).astype(str)
data_en["hpf"] = data_en["hpf"].replace("0.0", "None")

for col in data_en.columns:
    if col != "accuracy":
        data_en[col] = data_en[col].astype(str)
        data_en[col] = data_en[col].replace("nan", "None")


data_en = data_en.groupby([col for col in data_en.columns if col not in ['accuracy', 'subject']])['accuracy'].mean().reset_index()
data_en["accuracy"] = np.float32(data_en["accuracy"])

data_tr = pd.read_csv("/Users/roman/GitHub/m4d/models/sliding_tsums_extended.csv").drop(columns=['forking_path'])
data_tr["lpf"] = data_tr["lpf"].fillna(0).astype(int).astype(str)
data_tr["lpf"] = data_tr["lpf"].replace("0", "None")
data_tr["hpf"] = data_tr["hpf"].fillna(0).astype(float).astype(str)
data_tr["hpf"] = data_tr["hpf"].replace("0.0", "None")


data_en["decoder"] = "EEGNet"
data_tr["decoder"] = "Time-Resolved"
data_en["performance"] = data_en["accuracy"]
data_tr["performance"] = data_tr["tsum"]
data_en.drop(columns=["accuracy"], inplace=True)
data_tr.drop(columns=["tsum"], inplace=True)
data_both = pd.concat([data_en, data_tr], ignore_index=True)

data_both = data_both.where(pd.notnull(data_both), "None")

# lookup table for the values
lookup = {"emc": "Ocular artifact correction",
          "hpf": "High-pass filter",
          "lpf": "Low-pass filter",
          "mac": "Muscle artifact correction",
          "base": "Baseline interval",
          "ref": "Reference electrode(s)",
          "det": "Detrending",
          "ar": "Autoreject",
          "int": "Interpolate",
          "intrej": "Int. or reject",
          "ica": "ICA",
          "6": "6 Hz",
          "20": "20 Hz",
          "45": "45 Hz",
          "0.1": "0.1 Hz",
          "0.5": "0.5 Hz",
          }

# recode the column  names
data_both = data_both.rename(columns=lookup)

# recode some column values with lookup table
data_both['Autoreject'] = data_both['Autoreject'].replace(lookup)
data_both['Ocular artifact correction'] = data_both['Ocular artifact correction'].replace(lookup)
data_both['Muscle artifact correction'] = data_both['Muscle artifact correction'].replace(lookup)
data_both["High-pass filter"] = data_both["High-pass filter"].replace(lookup)
data_both["Low-pass filter"] = data_both["Low-pass filter"].replace(lookup)

data_both.to_csv("/Users/roman/GitHub/m4d/streamlit/performances.csv", index=False)