import sys
from datetime import datetime
import os
import json 

import pandas as pd

from models.currency_converter import CurrencyConverter
from models.sheet_uploader import SheetUploader
from models.smsp_scraper import SMSPScraper
from models.snowflake_uploader import SnowflakeUploader


smsp_scraper = SMSPScraper()
snowflake_uploader = SnowflakeUploader()
# currency_converter = CurrencyConverter()


def perform_daily_scraping():
    iron_ore_price = smsp_scraper.scrape_trading_view_iron_ore_price()
            
            # Check if the iron_ore_price is a string (error message) or a numeric value
    #convert the iron_ore_price to a float
    iron_ore_price = float(iron_ore_price)
    
    #initialize the snowflake_df for iron ore price
    snowflake_df = pd.DataFrame(
    snowflake_currency_data,
    columns=[
        "AS_OF",
        "VALUE",
        "SOURCE",
        "UNIT",
        "TYPE",
        ],
    )
    
    #append the iron ore price to the snowflake_df
    snowflake_df.append(
        [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            iron_ore_price,
            "tradingview.com",
            "USD/tonne",
            "Iron Ore",
        ],
    )   
    
    #upload the iron ore price to the snowflake_df
    snowflake_uploader.upload_data_to_snowflake(
        "RAW", "EXTERNAL_INDICATORS", "IRON_ORE_INDICATORS", snowflake_df
    )
    
    #next, upload the currency exchange rates to the snowflake_df
    currency_converter = CurrencyConverter()
    if isinstance(iron_ore_price, (int, float)):
        print(f"IRONORE CURRENT PRICE: {iron_ore_price} USD/tonne")
        snowflake_data = []
    latest_cny_converter = currency_converter.get_exchange_rates_latest(
        "CNY", "IDR"
    )
    
    latest_usd_converter = currency_converter.get_exchange_rates_latest(
        "USD", "IDR"
    )
    
    snowflake_currency_data = [
        [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "USD/IDR", 
            latest_usd_converter,
            "Yahoo Finance"
        ],
        [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "CNY/IDR", 
            latest_cny_converter,
            "Yahoo Finance"
        ]
    ]
    
    snowflake_df = pd.DataFrame(
    snowflake_currency_data,
    columns=[
        "AS_OF",
        "CURRENCY_EXCHANGE",
        "VALUE",
        "SOURCE",
        ],
    )
    
    snowflake_uploader.upload_data_to_snowflake(
        "RAW", "EXTERNAL_INDICATORS", "CURRENCIES", snowflake_df
    )
    
    #then, scrape the sina steel rebar price
    script_dir = os.path.dirname(os.path.abspath(__file__))
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
        stored_json["currencies"]["last-stored-date"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(file_path, 'w') as file:
            json.dump(stored_json, file, indent=4)  # `indent=4` for pretty printing
    
    sina_price_cny = smsp_scraper.scrape_sina_price_specific()
    sina_price_idr = sina_price_cny * latest_cny_converter
    snowflake_data = []
    snowflake_data.append(
        [
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "-",
            "Besi Beton",
            "SMSP Scraper",
            "Competitor",
            "Factory",
            "sina",
            "China",
            0,
            1,
            0,
            sina_price_idr,
            "Scraped by SMSP Scraper",
        ],
    )
    
    snowflake_df = pd.DataFrame(
    snowflake_data,
    columns=[
            "AS_OF",
            "SKU_NUMBER",
            "PRODUCT",
            "RECORDED_BY",
            "TYPE",
            "INDUSTRY",
            "SOURCE",
            "LOCATION",
            "WEIGHT",
            "QUANTITY",
            "PRICE_INCLUDE_TAX_PER_UNIT",
            "PRICE_INCLUDE_TAX_PER_KG",
            "NOTES",
        ],
    )
    
    snowflake_uploader.upload_data_to_snowflake(
        "RAW", "EXTERNAL_INDICATORS", "CHINESE_REBAR_TRADINGS", snowflake_df
    )
    juragan_prices = smsp_scraper.scrape_juragan_material_price()
    snowflake_data = []

    for juragan_price in juragan_prices:
        snowflake_data.append(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                iron_ore_price,
                "Iron Ore",
                "tradingview.com",
                "USD/tonne",
            ]
        )
        
        snowflake_df = pd.DataFrame(
            snowflake_data,
            columns=[
                "AS_OF",
                "VALUE",
                "TYPE",
                "SOURCE",
                "UNIT",
            ],
        )
        
        snowflake_uploader.upload_data_to_snowflake(
            "RAW", "EXTERNAL_INDICATORS", "IRON_ORE_INDICATORS", snowflake_df
        )
    else:
        print(f"Error in iron ore price: {iron_ore_price}")
    
    
#     sina_price_cny = smsp_scraper.scrape_sina_price_specific()
#     sina_price_idr = sina_price_cny * currency_converter.get_exchange_rates_latest(
#         "CNY", "IDR"
#     )
#     snowflake_data = []
#     snowflake_data.append(
#         [
#             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "-",
#             "Besi Beton",
#             "SMSP Scraper",
#             "Competitor",
#             "Factory",
#             "sina",
#             "China",
#             0,
#             1,
#             0,
#             sina_price_idr,
#             "Scraped by SMSP Scraper",
#         ],
#     )
    
#     snowflake_df = pd.DataFrame(
#     snowflake_data,
#     columns=[
#             "AS_OF",
#             "SKU_NUMBER",
#             "PRODUCT",
#             "RECORDED_BY",
#             "TYPE",
#             "INDUSTRY",
#             "SOURCE",
#             "LOCATION",
#             "WEIGHT",
#             "QUANTITY",
#             "PRICE_INCLUDE_TAX_PER_UNIT",
#             "PRICE_INCLUDE_TAX_PER_KG",
#             "NOTES",
#         ],
#     )
    
#     snowflake_uploader.upload_data_to_snowflake(
#         "RAW", "EXTERNAL_INDICATORS", "CHINESE_REBAR_TRADINGS", snowflake_df
#     )
#     juragan_prices = smsp_scraper.scrape_juragan_material_price()
#     snowflake_data = []

#     for juragan_price in juragan_prices:
#         snowflake_data.append(
#             [
#                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "-",
#                 juragan_price["product"],
#                 "SMSP Scraper",
#                 "Competitor",
#                 "Distributor",
#                 "Jurangan Material",
#                 "Jakarta",
#                 juragan_price["weight"],
#                 1,
#                 juragan_price["price"],
#                 juragan_price["price"] / juragan_price["weight"],
#                 "Scraped by SMSP Scraper",
#             ],
#         )
#     histeel_prices = smsp_scraper.scrape_histeel_price()
#     for histeel_price in histeel_prices:
#         snowflake_data.append(
#             [
#                 datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#                 "-",
#                 histeel_price["product"],
#                 "SMSP Scraper",
#                 "Competitor",
#                 "Distributor",
#                 "Hi Steel",
#                 "Surabaya",
#                 0,
#                 1,
#                 histeel_price["price"],
#                 0,
#                 "Scraped by SMSP Scraper",
#             ],
#         )
#     # sbg_prices = smsp_scraper.scrape_sbg_price()
#     # for sbg_price in sbg_prices:
#     #     snowflake_data.append(
#     #         [
#     #             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     #             sbg_price[0],
#     #             sbg_price[1],
#     #             "SMSP Scraper",
#     #             "Competitor",
#     #             "Distributor",
#     #             "Super Bangun Jaya",
#     #             "Tangerang",
#     #             0,
#     #             1,
#     #             sbg_price[2],
#     #             0,
#     #             "Scraped by SMSP Scraper",
#     #         ],
#     #     )
#     # artha_beton_prices = smsp_scraper.scrape_artha_beton_price()
#     # for artha_beton_price in artha_beton_prices:
#     #     snowflake_data.append(
#     #         [
#     #             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     #             "-",
#     #             artha_beton_price["product"],
#     #             "SMSP Scraper",
#     #             "Supplier",
#     #             "Factory",
#     #             "Artha Beton",
#     #             "Sumatra Selatan",
#     #             0,
#     #             1,
#     #             artha_beton_price["price"],
#     #             0,
#     #             "Scraped by SMSP Scraper",
#     #         ],
#     #     )
#     # siskaperbapo_prices = smsp_scraper.scrape_siskaperbapo_price()
#     # for siskaperbapo_price in siskaperbapo_prices:
#     #     snowflake_data.append(
#     #         [
#     #             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#     #             "-",
#     #             siskaperbapo_price["product"],
#     #             "SMSP Scraper",
#     #             "Supplier",
#     #             "Factory",
#     #             "Siskaperbapo",
#     #             "Jawa Timur",
#     #             0,
#     #             1,
#     #             siskaperbapo_price["price"],
#     #             0,
#     #             "Scraped by SMSP Scraper",
#     #         ],
#     #     )
#     # nss_prices = smsp_scraper.scrape_niaga_sinar_sentosa_price()
#     # for nss_price in nss_prices:
#     #     snowflake_data.append(
#     #         [
#     #             datetime.now().date().strftime("%Y-%m-%d"),
#     #             "-",
#     #             nss_price["product"],
#     #             "SMSP Scraper",
#     #             "Competitor",
#     #             "Distributor",
#     #             "Niaga Sinar Sentosa",
#     #             "Jawa Barat",
#     #             0,
#     #             1,
#     #             nss_price["price"],
#     #             0,
#     #             "Scraped by SMSP Scraper",
#     #         ],
#     #     )
#     snowflake_df = pd.DataFrame(
#         snowflake_data,
#         columns=[
#             "AS_OF",
#             "SKU_NUMBER",
#             "PRODUCT",
#             "RECORDED_BY",
#             "TYPE",
#             "INDUSTRY",
#             "SOURCE",
#             "LOCATION",
#             "WEIGHT",
#             "QUANTITY",
#             "PRICE_INCLUDE_TAX_PER_UNIT",
#             "PRICE_INCLUDE_TAX_PER_KG",
#             "NOTES",
#         ],
#     )
#     print(snowflake_df)
#     snowflake_uploader.upload_data_to_snowflake(
#         "RAW", "GOOGLE_SHEET_PRICING", "EXTERNAL_PRICE_SCRAPE", snowflake_df
#     )
    
#     indonesia_macroeconomics = smsp_scraper.scrape_trading_economics_macroeconomics()      
#     snowflake_df = pd.DataFrame(
#         indonesia_macroeconomics,
#         columns=[
#             "AS_OF",
#             "SOURCE",
#             "TYPE",
#             "VALUE",
#             "UNIT",
#         ],
#     )
#     snowflake_uploader.upload_data_to_snowflake(
#         "RAW", "EXTERNAL_INDICATORS", "INDONESIA_INDICATORS", snowflake_df
#     )
    
#     iron_ore_historical = smsp_scraper.sgx_ironore_price()
#     if (len(iron_ore_historical) != 0):
#         snowflake_df = pd.DataFrame(
#             iron_ore_historical,
#             columns=[
#                 "AS_OF",
#                 "SOURCE",
#                 "TYPE",
#                 "VALUE",
#                 "UNIT",
#             ],
#         )
#         snowflake_uploader.upload_data_to_snowflake(
#             "RAW", "EXTERNAL_INDICATORS", "IRON_ORE_INDICATORS", snowflake_df
#         )
    
    

# @app.route('/test', methods=['POST'])
# def test():
#     smsp_scraper = SMSPScraper()
#     snowflake_uploader = SnowflakeUploader()
#     snowflake_data = []
#     snowflake_df = pd.DataFrame(
#         snowflake_data,
#         columns=[
#             "AS_OF",
#             "SKU_NUMBER",
#             "PRODUCT",
#             "RECORDED_BY",
#             "TYPE",
#             "INDUSTRY",
#             "SOURCE",
#             "LOCATION",
#             "WEIGHT",
#             "QUANTITY",
#             "PRICE_INCLUDE_TAX_PER_UNIT",
#             "PRICE_INCLUDE_TAX_PER_KG",
#             "NOTES",
#         ],
#     )
#     snowflake_uploader.upload_data_to_snowflake(
#         "MARTS", "DEVELOPMENT", "EXTERNAL_PRICE_SCRAPE", snowflake_df
#     )


# @app.route('/temp', methods=['POST'])
# def temp():
#     try:

#         is_error_indonesia_indicator, indonesia_indicator = smsp_scraper.scrape_trading_economics_macroeconomics()
#         is_error_iron_ore, iron_ore = smsp_scraper.scrape_trading_view_iron_ore_price()
        
#         if is_error_indonesia_indicator or is_error_iron_ore:
#             message = indonesia_indicator if is_error_indonesia_indicator else iron_ore
#             print("iron ore:",'\n', iron_ore)
#             print("indonesia indicator", '\n', indonesia_indicator)
#             # return jsonify({"status": "ERROR", "message": message}), 500
#         else:
#             print("iron ore:",'\n', iron_ore)
#             print("indonesia indicator", '\n', indonesia_indicator)            # return jsonify({"status": "OK"}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

def test():
    """
    Test SMSP Scraper
    """
    print("\nInitialized SMSPScraper")
    
    # snowflake_uploader = SnowflakeUploader()
    # snowflake_data = []
    # snowflake_df = pd.DataFrame(
    #     snowflake_data,
    #     columns=[
    #         "AS_OF",
    #         "SOURCE",
    #         "TYPE",
    #         "VALUE",
    #         "UNIT",
    #     ],
    # )
    # snowflake_uploader.upload_data_to_snowflake(
    #     "RAW", "EXTERNAL_INDICATORS", "IRON_ORE_INDICATOR", snowflake_df
    # )
    
# def test_currency():
#     latest_cny_converter = currency_converter.get_exchange_rates_latest(
#         "CNY", "IDR"
#     )
    
#     latest_usd_converter = currency_converter.get_exchange_rates_latest(
#         "USD", "IDR"
#     )
    
#     snowflake_currency_data = [
#         [
#             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "USD/IDR", 
#             latest_usd_converter,
#             "Yahoo Finance"
#         ],
#         [
#             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
#             "CNY/IDR", 
#             latest_cny_converter,
#             "Yahoo Finance"
#         ]
#     ]
    
#     snowflake_df = pd.DataFrame(
#     snowflake_currency_data,
#     columns=[
#         "AS_OF",
#         "CURRENCY_EXCHANGE",
#         "VALUE",
#         "SOURCE",
#         ],
#     )
    
#     print(snowflake_df)

if __name__ == "__main__":
    perform_daily_scraping()
    # test()
    # test_currency()