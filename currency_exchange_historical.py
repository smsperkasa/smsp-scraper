from models.currency_converter import CurrencyConverter
from models.snowflake_uploader import SnowflakeUploader
from logger.logging_config import logger
from datetime import datetime
import pandas as pd
import os
import json

#read cny idr historical data
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'CNY_IDR_Historical_Value.csv')

cny_idr_pd = pd.read_csv(file_path)
cny_idr_pd[["AS_OF", "VALUE"]] = cny_idr_pd[["Date", "Price"]] 
cny_idr_pd["SOURCE"] = "Investing.com"
cny_idr_pd["CURRENCY_EXCHANGE"] = "CNY/IDR"
cny_idr_pd["VALUE"] = cny_idr_pd["VALUE"].str.replace(',', '').astype(float)
cny_idr_pd["AS_OF"] =  pd.to_datetime(cny_idr_pd["AS_OF"], format="%m/%d/%Y")

cny_idr_pd = cny_idr_pd.drop(["Open", "High", "Low", "Vol.", "Change %", "Date"], axis=1)

currency_converter = CurrencyConverter()
snowflake_uploader = SnowflakeUploader()

# Convert string to datetime
start_date = datetime.strptime("2021-01-01", "%Y-%m-%d")
end_date = datetime.now()
historical_usd_idr = currency_converter.get_exchange_rates_historical("USD", "IDR", start_date, end_date)

snowflake_lst = [
    {
        "AS_OF"  : pd.to_datetime(date),
        "CURRENCY_EXCHANGE" : "USD/IDR",
        "VALUE" : data["Close"],
        "SOURCE" : "Yahoo Finance"
    }
    for date, data in historical_usd_idr.iterrows()
]

snowflake_df = pd.DataFrame(
snowflake_lst,
columns=[
        "AS_OF",
        "CURRENCY_EXCHANGE",
        "VALUE",
        "SOURCE",
    ],
)



snowflake_df = pd.concat([snowflake_df, cny_idr_pd])

#add time to date
snowflake_df["AS_OF"] = snowflake_df["AS_OF"].apply(lambda x: x.replace(hour=0, minute=0, second=0))


print(snowflake_df)

snowflake_uploader.upload_data_to_snowflake(
    "RAW", "EXTERNAL_INDICATORS", "CURRENCIES", snowflake_df
)

file_path = os.path.join(script_dir, 'global.json')
if not os.path.isfile(file_path):
        # If the file does not exist, create a new global.json file
        with open(file_path, 'w') as f:
        # You can define the default content of the JSON file here
            default_data = {
                "currencies": 
                    { 
                        "last-stored-date": ""
                    }
                }  # Customize the content as needed
            json.dump(default_data, f, indent=4)

else:
    with open(file_path, 'r') as file:
        stored_json = json.load(file)
    if "currencies" not in stored_json:
        stored_json["currencies"] = {"last-stored-date": ""}
    stored_json["currencies"]["last-stored-date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(file_path, 'w') as file:
        json.dump(stored_json, file, indent=4)  # `indent=4` for pretty printing

