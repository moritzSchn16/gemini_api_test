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
    prompt = """
            Describe the following time series in 10 categories you choose yourself. 
            Every category should be describe in one word.
            Don't use Frequency, Units and Type as categories. 
            Describe also how the time series values develop and also give value ranges in percentages not totals.
            Output a json format.
    """

    example = """
    The json keys on the json must and only can be "time_series_description", "development" and"value_ranges".
    
    like in this example:
    
    {
      "time_series_description": {
        "Volatility": "Low",
        "Trend": "Downward",
        "Stability": "Unstable",
        "Pattern": "Stepwise",
        "Seasonality": "None",
        "Cycles": "None",
        "Autocorrelation": "High",
        "Predictability": "High",
        "Extremes": "Present",
        "Anomaly": "Present"
      },
      "development": "The time series shows a generally downward trend with several distinct steps or plateaus of constant values.  It starts with a relatively high value, then experiences a series of stepwise decreases, with each step lasting for a considerable period.",
      "value_ranges": {
        "100-112%": "Initial phase",
        "90-100%": "Second phase",
        "75-90%": "Third phase",
        "50-75%": "Fourth phase",
        "60-70%": "Fifth phase"
      }
    }
    
    No other keys or structure is allowed.
    And here is the time series you should describe:
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
                        {"text": f"{prompt}{timeseries}"}
                    ]
                }
            ]
        }

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
                json_string = json_string.replace("```json", "")
                json_string = json_string.replace("description", "time_series_description")
                json_string = json_string.replace("time_series_descriptions", "time_series_description")
                json_string = json_string.replace("ValueRanges", "value_ranges")
                json_string = json_string.replace("valueRanges", "value_ranges")
                json_string = json_string.replace("value_range", "value_ranges")
                json_string = json_string.replace("value_rangess", "value_ranges")
                json_string = json_string.replace("```", "")

                #print(json_string)

                data = json.loads(json_string)

                # Add file name to the data
                data['file_name'] = file_name
                print(data)
                # Convert `value_ranges` to a DataFrame
                value_ranges_data = [data['value_ranges']]

                print(data)

                if initial:
                    # Convert `time_series_description` to a DataFrame
                    ts_description_df = pd.DataFrame([data])

                    # Create value_ranges DataFrame
                    value_ranges_df = pd.DataFrame(value_ranges_data)

                    initial = False
                else:
                    # Append new time_series_description and value_ranges data to the DataFrames
                    ts_description_df = pd.concat([ts_description_df, pd.DataFrame([data])],
                                                  ignore_index=True)

                    # Append value ranges data
                    value_ranges_df = pd.concat([value_ranges_df, pd.DataFrame(value_ranges_data)], ignore_index=True)

                # Display the DataFrames
                print("Time Series Description DataFrame:")
                print(ts_description_df, end="\n\n")

                print("Value Ranges DataFrame:")
                print(value_ranges_df)

                # Save the DataFrames to CSV files
                ts_description_df.to_csv('ts_description_df.csv', index=False)
                value_ranges_df.to_csv('value_ranges_df.csv', index=False)

                break  # Break if code executes successfully

            except Exception as e:
                attempts += 1
                print(f"Attempt {attempts} failed: {e}")
                if attempts == max_attempts:
                    print("Max attempts reached. Code failed.")



