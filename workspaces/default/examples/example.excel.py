import pandas as pd
import matplotlib.pyplot as plt

# 1. Load the data
# Replace 'your_file.xlsx' with your actual filename
df = pd.read_excel('resources/example.xlsx')

# 2. Basic Inspection
print("--- Data Preview ---")
print(df.head())

print("\n--- Column Info ---")
print(df.info())

# 3. Basic Analytics: Summary Statistics
print("\n--- Descriptive Statistics ---")
print(df.describe())

# 4. Data Transformation (Example: Grouping by Category)
# Let's assume you have a 'Category' and an 'Amount' column
if 'Category' in df.columns and 'Amount' in df.columns:
    summary = df.groupby('Category')['Amount'].sum().sort_values(ascending=False)
    print("\n--- Total Amount by Category ---")
    print(summary)
    
    # 5. Visualization
    summary.plot(kind='bar', title='Spending by Category', ylabel='Amount', color='skyblue')
    plt.xticks(rotation=45)
    plt.show()
else:
    print("\nNote: Change 'Category' and 'Amount' in the code to match your Excel column names.")