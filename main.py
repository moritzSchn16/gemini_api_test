import os

import google.generativeai as genai
import requests
import json
import pandas as pd
from io import StringIO

if __name__ == "__main__":
    initial = True
    # Define the API endpoint and your API key
    api_key = "AIzaSyABYvacy34rs3DoX377_NEJtX6G7yyqftI"  # Replace with your actual API key
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"

    # Define the headers
    headers = {
        "Content-Type": "application/json"
    }

    prompt = """Describe the following time series in the categories Volatility, Trend, Stability, Pattern, Seasonality, Cycles, Autocorrelation, Predicatbility, Extremes and Anomaly. 
            Every category should be describe in one word.
            Describe also how the time series values develop and also give value ranges in percentages not totals.
    """

    example = """
    Use this JSON schema:    
    
    values = {'Volatility': str,'Trend': str, 'Stability': str, 'Pattern': str, 'Seasonality': str, 'Cycles': str, 'Autocorrelation': str,  'Predictability': str,  'Extremes': str, 'Anomaly': str,   'development': list[str],   'value_ranges': list[str]}
    Return: values
    
        
    """
    folder_path = "/Users/moritzschneider/PycharmProjects/keepa/best_product/full_ts"
    # Iterate over all files in the folder
    for file_name in os.listdir(folder_path):
        # Construct full file path
        file_path = os.path.join(folder_path, file_name)

        # Check if the file is a CSV
        if file_name.endswith('.csv'):
            print(f"Processing file: {file_name}")

            # Load the CSV file into a DataFrame
            try:
                df = pd.read_csv(file_path)

                selected_df = df[['date', 'price']]

                # Convert the DataFrame to a string using StringIO
                output_string = StringIO()
                selected_df.to_string(output_string, index=False)
                string_df = str(selected_df)
                print(str(string_df))
            except Exception as e:
                print(f"Error reading {file_name}: {e}")


        timeseries = f"""
            {string_df}
      
        """

        # Define the payload
        payload = {
            "contents": [
                {
                    "parts": [
                        {"text": f"{prompt}{example}{timeseries}"}
                    ]
                }
            ]
        }

        print(payload)

        max_attempts = 5
        attempts = 0

        while attempts < max_attempts:
            try:
                # Make the POST request
                response = requests.post(url, headers=headers, json=payload)

                # Check the response status
                if response.status_code == 200:
                    response.json()['candidates'][0]['content']['parts'][0]['text']
                else:
                    print("Error:", response.status_code, response)

                # Parse the response JSON
                json_string = response.json()['candidates'][0]['content']['parts'][0]['text']
                print(json_string)

                # DataFrame erstellen
                df = pd.DataFrame([json_string])

                # Tabelle anhängen (z. B. an eine existierende CSV-Datei)
                csv_file = 'table_new.csv'

                try:
                    # Datei existiert bereits, neue Daten anhängen
                    existing_df = pd.read_csv(csv_file)
                    combined_df = pd.concat([existing_df, df], ignore_index=True)
                except FileNotFoundError:
                    # Datei existiert noch nicht, nur neuen DataFrame speichern
                    combined_df = df

                # Speichern der Tabelle
                combined_df.to_csv(csv_file, index=False)

                print("JSON-Daten erfolgreich in die Tabelle eingefügt!")
            except:
                print('fail')