import os

import google.generativeai as genai
import requests
import json
import pandas as pd
from io import StringIO
import re

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
            Describe also how the time series values develop in three sentences and also give value ranges over time in percentages not totals.
            Do not use a comma.
    """

    example = """
    Use this JSON schema:    
    
    values = {'File_name':str, 'Volatility': str,'Trend': str, 'Stability': str, 'Pattern': str, 'Seasonality': str, 'Cycles': str, 'Autocorrelation': str,  'Predictability': str,  'Extremes': str, 'Anomaly': str,   'development': str,   'value_ranges': str}
    Return: values
    
    Only return the Return.    
    """
    folder_path = "/Users/moritzschneider/PycharmProjects/keepa/best_product/full_ts"
    # Iterate over all files in the folder
    dfs = []
    for file_name in os.listdir(folder_path):
        try:

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
                            {"text": f"{prompt}{example}{timeseries}The File_name is: {file_name}"}
                        ]
                    }
                ]
            }


            # Make the POST request
            response = requests.post(url, headers=headers, json=payload)

            # Check the response status
            if response.status_code == 200:
                response.json()['candidates'][0]['content']['parts'][0]

            else:
                print("Error:", response.status_code, response)

            # Parse the response JSON
            json_string = response.json()['candidates'][0]['content']['parts'][0]

            cleaned_text = re.sub(r'json', '', str(json_string))
            cleaned_text = re.sub(r'\\n', '', str(cleaned_text))
            cleaned_text = re.sub(r'\'text\'\:', '', str(cleaned_text))
            cleaned_text = re.sub(r'[^a-zA-Z0-9 \%\-,\[\]\'\-%:\s\\\']', '', str(cleaned_text))


            # Input-String
            #input_string = 'Volatility:Low,Trend:Downward,Stability:Unstable,Pattern:None,Seasonality:None,Cycles:None,Autocorrelation:High,Predictability:Low,Extremes:Mild,Anomaly:None,development:[Initialhighvalues,Gradualdecline],valueranges:[111-112%,61-62%]'
            input_string = cleaned_text


            def parse_input(input_string):
                    input_dict = {}

                    # Splitte den Input-String in Schlüssel-Wert-Paare
                    for key_value in input_string.split(','):
                        if ':' in key_value:
                            key, value = key_value.split(':', 1)

                            # Liste behandeln
                            if value.startswith('[') and value.endswith(']'):
                                value = value[1:-1].split(',')

                            input_dict[key] = value

                    return input_dict

            parsed_data = parse_input(input_string)  # Wandelt den String in ein Dictionary um
            df = pd.DataFrame([parsed_data])  # Erzeugt einen DataFrame aus dem Dictionary
            dfs.append(df)

            final_df = pd.concat(dfs, ignore_index=True)

            # Tabelle anhängen (z. B. an eine existierende CSV-Datei)
            csv_file = 'table_new.csv'

            try:
                # Datei existiert bereits, neue Daten anhängen
                existing_df = pd.read_csv(csv_file)
                combined_df = pd.concat([existing_df, final_df])
            except FileNotFoundError:
                # Datei existiert noch nicht, nur neuen DataFrame speichern
                combined_df = final_df

            # Speichern der Tabelle
            combined_df = combined_df.drop_duplicates()
            combined_df.to_csv(csv_file, index=False)

            print(combined_df)
            print("JSON-Daten erfolgreich in die Tabelle eingefügt!")

        except:
            print('Error',file_name)
