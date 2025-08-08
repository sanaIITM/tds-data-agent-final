import pandas as pd

# Test the dynamic array logic with gender data
df = pd.read_csv('gender_data.csv')
print("Dataset:")
print(df)
print()

# First value: count of records
first_value = df.shape[0]
print(f"First value (record count): {first_value}")

# Second value: most common categorical value
second_value = "Analysis"
for col in df.columns:
    if df[col].dtype == 'object':  # categorical column
        most_common = df[col].mode()
        if len(most_common) > 0:
            second_value = str(most_common.iloc[0]).lower()
            print(f"Most common value in {col}: {second_value}")
            break

# Third value: calculated metric (normalized average)
third_value = 0.5
numeric_cols = df.select_dtypes(include=['number']).columns
if len(numeric_cols) > 0:
    avg_val = df[numeric_cols[0]].mean()
    max_val = df[numeric_cols[0]].max()
    min_val = df[numeric_cols[0]].min()
    if max_val > min_val:
        third_value = round((avg_val - min_val) / (max_val - min_val), 3)
    print(f"Normalized average of {numeric_cols[0]}: {third_value}")

print()
print(f"Expected array response: [{first_value}, \"{second_value}\", {third_value}, \"<base64_image>\"]")
