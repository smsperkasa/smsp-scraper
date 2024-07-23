import pandas as pd
import yfinance as yf

from index import SheetUploader

cnyusd_data = yf.download("CNYUSD=X", start="2022-12-13", end="2022-12-31")
usdidr_data = yf.download("USDIDR=X", start="2022-12-13", end="2022-12-31")
cnyusd_data = cnyusd_data["Close"]
usdidr_data = usdidr_data["Close"]
historical_data = pd.DataFrame(cnyusd_data * usdidr_data, columns=["Close"])
sheet_uploader = SheetUploader()

for i, r in historical_data.iterrows():
    date_str = i.strftime("%Y-%m-%d")
    sheet_uploader.upload_data_raw(
        "Yuan", [date_str, "SMSP Scraper", "Yahoo Finance", r["Close"], "-"]
    )
