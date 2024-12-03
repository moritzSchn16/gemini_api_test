import pandas as pd

df = pd.read_csv('files/table_new_fixed.csv')

print(len(df))

# Count occurrences of 'None' per row

df = df.astype(str)
df = df.drop(columns=['Unnamed: 0'])


columns_to_strip = [
    'Volatility', 'Trend', 'Stability', 'Pattern',
    'Seasonality', 'Cycles', 'Autocorrelation', 'Predictability',
    'Extremes', 'Anomaly'
]


df[columns_to_strip] = df[columns_to_strip].apply(lambda col: col.str.replace(r'[^a-zA-Z]', '', regex=True))

# Apply .str.strip() to each specified column
df[columns_to_strip] = df[columns_to_strip].apply(lambda col: col.str.strip())

none_counts = df.isin(['None', None]).sum(axis=1)

# Filter rows with more than 5 'None' values
filtered_df = df[none_counts <= 5]

print(filtered_df)
print(len(filtered_df))

filtered_df.to_csv('files/table_new_fixed_filtered.csv')