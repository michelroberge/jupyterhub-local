#!/usr/bin/env python3
"""
Script: connect-postgresql.py
Description: Connects to a PostgreSQL database, loads the table bm010115 into pandas,
             and performs basic exploratory data analysis with visualizations.
"""

import os
import yaml
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from sqlalchemy import create_engine, text
from tqdm import tqdm
from connectors.postgres import get_engine

engine = get_engine("staging")

# ----------------------------
# Load table into pandas
# ----------------------------
schema_name = "integrite_donnee_full"
table_name = "iv00102"

print(f"Loading table {table_name} from database...")

df = pd.read_sql_query(f"select * from {schema_name}.{table_name} LIMIT 100", con=engine)

print(f"Table loaded. Shape: {df.shape}")

# ----------------------------
# Basic Exploratory Data Analysis
# ----------------------------
print("\n--- Data Overview ---")
print(df.head())
print("\n--- Data Info ---")
print(df.info())
print("\n--- Missing Values ---")
print(df.isnull().sum())
print("\n--- Descriptive Statistics ---")
print(df.describe(include="all"))

# ----------------------------
# Simple Visualizations
# ----------------------------

# Histogram of numeric columns
numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
for col in tqdm(numeric_cols, desc="Plotting histograms"):
    plt.figure()
    sns.histplot(df[col].dropna(), kde=True)
    plt.title(f"Distribution of {col}")
    plt.xlabel(col)
    plt.ylabel("Count")
    plt.tight_layout()
    plt.show()

# Correlation heatmap
if len(numeric_cols) > 1:
    plt.figure(figsize=(10, 8))
    sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm")
    plt.title("Correlation Heatmap")
    plt.tight_layout()
    plt.show()

# Optional: interactive scatter plot with Plotly
if len(numeric_cols) >= 2:
    fig = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1], title=f"{numeric_cols[0]} vs {numeric_cols[1]}")
    fig.show()

print("Analysis complete.")
