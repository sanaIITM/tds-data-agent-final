import pandas as pd

# Test with financial data
print("=== FINANCIAL DATA TEST ===")
df_financial = pd.read_csv('financial_data.csv')
print(df_financial.head())

first_value = df_financial.shape[0]
second_value = "Analysis"
for col in df_financial.columns:
    if df_financial[col].dtype == 'object':
        most_common = df_financial[col].mode()
        if len(most_common) > 0:
            second_value = str(most_common.iloc[0]).lower()
            break

third_value = 0.5
numeric_cols = df_financial.select_dtypes(include=['number']).columns
if len(numeric_cols) > 0:
    avg_val = df_financial[numeric_cols[0]].mean()
    max_val = df_financial[numeric_cols[0]].max()
    min_val = df_financial[numeric_cols[0]].min()
    if max_val > min_val:
        third_value = round((avg_val - min_val) / (max_val - min_val), 3)

print(f"Financial data response: [{first_value}, \"{second_value}\", {third_value}, \"<image>\"]")
print()

# Test with gender data focusing on Gender column
print("=== GENDER DATA TEST (Gender focus) ===")
df_gender = pd.read_csv('gender_data.csv')

# Find most common gender specifically
gender_mode = df_gender['Gender'].mode().iloc[0].lower()
print(f"Most common gender: {gender_mode}")

# Calculate female ratio
female_count = (df_gender['Gender'] == 'Female').sum()
total_count = len(df_gender)
female_ratio = round(female_count / total_count, 3)

print(f"Gender-focused response: [{female_count}, \"{gender_mode}\", {female_ratio}, \"<image>\"]")
