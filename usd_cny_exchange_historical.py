from models.currency_converter import CurrencyConverter
from models.snowflake_uploader import SnowflakeUploader
from logger.logging_config import logger
from datetime import datetime
import pandas as pd
import os
import json

#read cny idr historical data
script_dir = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_dir, 'USD_CNY_Historical_Value.csv')

currency_converter = CurrencyConverter()

# Convert string to datetime
start_date = datetime.strptime("2021-01-01", "%Y-%m-%d")
end_date = datetime.now()
historical_usd_cny = currency_converter.get_exchange_rates_historical("USD", "CNY", start_date, end_date)

snowflake_lst = [
    {
        "AS_OF"  : pd.to_datetime(date),
        "CURRENCY_EXCHANGE" : "USD/CNY",
        "VALUE" : data["Close"],
        "SOURCE" : "Yahoo Finance"
    }
    for date, data in historical_usd_cny.iterrows()
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
#add time to date
snowflake_df["AS_OF"] = snowflake_df["AS_OF"].apply(lambda x: x.replace(hour=0, minute=0, second=0))

snowflake_df.to_csv(file_path)
