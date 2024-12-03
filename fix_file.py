import pandas as pd
import re

df = pd.read_csv("files/table_new.csv")
df = df.drop(df.index[-1])

def clean_column_names(col_name):
    # Use regex to remove non-alphabetic characters
    clean_name = re.sub(r'[^a-zA-Z]', '', col_name)
    clean_name = clean_name.replace('pythonvalues','')
    return clean_name

df.columns = [clean_column_names(col) for col in df.columns]

# Spalten mit gleichen Namen identifizieren
columns = df.columns
unique_columns = columns.unique()

# Zusammenführen der Spalten mit gleichen Namen
for col in unique_columns:
    if (columns == col).sum() > 1:  # Falls es doppelte Spalten gibt
        # Alle Spalten mit diesem Namen finden
        cols_to_merge = df.loc[:, columns == col]
        # Neue Spalte: Nimm den ersten nicht leeren Wert aus den Duplikaten
        df[col] = cols_to_merge.bfill(axis=1).iloc[:, 0]  # Backfill entlang der Zeilen

# Duplizierte Spalten entfernen
df = df.loc[:, ~columns.duplicated()]

df.to_csv("table_new_fixed.csv")