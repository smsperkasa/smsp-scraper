import requests
import json
import os
from models.snowflake_uploader import SnowflakeUploader
import pandas as pd

url = "https://api.sgx.com/derivatives/v1.0/history/symbol/FEFV24"
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'global.json')

snowflake_uploader = SnowflakeUploader()

response = requests.get(url)
if response.status_code == 200:
# Parse JSON response
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            stored_json = json.load(file)
    data = response.json()['data']
    
    last_stored_date = data[-1]["record-date"]
    stored_json["ironore"]["last-stored-date"] = last_stored_date + " 16:00:00"
    # Write the updated data back to the JSON file
    with open(file_path, 'w') as file:
        json.dump(stored_json, file, indent=4)  # `indent=4` for pretty printing
    
    selected_data = [
                {
                    "AS OF": pd.to_datetime(item["record-date"] + " 16:00"),
                    "SOURCE": "sgx.com",
                    "TYPE": "IRON ORE CLOSE PRICE",
                    "VALUE" : item["daily-settlement-price"],
                    "UNIT": "USD/tonne"
                }
                for item in data
            ]
    snowflake_df = pd.DataFrame(
    selected_data,
    columns=[
        "AS OF",
        "SOURCE",
        "TYPE",
        "VALUE",
        "UNIT",
        ],
    )
    
    # print(snowflake_df)
    
    # snowflake_uploader.upload_data_to_snowflake(
    #     "RAW", "EXTERNAL_INDICATOR", "IRON_ORE_INDICATOR", snowflake_df
    # )
    