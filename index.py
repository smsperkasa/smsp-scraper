import sys
from datetime import datetime

import pandas as pd

from models.currency_converter import CurrencyConverter
from models.sheet_uploader import SheetUploader
from models.smsp_scraper import SMSPScraper
from models.snowflake_uploader import SnowflakeUploader


smsp_scraper = SMSPScraper()
snowflake_uploader = SnowflakeUploader()
currency_converter = CurrencyConverter()

def perform_daily_scraping():
    sina_price_cny = smsp_scraper.scrape_sina_price_specific()
    sina_price_idr = sina_price_cny * currency_converter.get_exchange_rates_latest(
        "CNY", "IDR"
    )
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
                "-",
                juragan_price["product"],
                "SMSP Scraper",
                "Competitor",
                "Distributor",
                "Jurangan Material",
                "Jakarta",
                juragan_price["weight"],
                1,
                juragan_price["price"],
                juragan_price["price"] / juragan_price["weight"],
                "Scraped by SMSP Scraper",
            ],
        )
    histeel_prices = smsp_scraper.scrape_histeel_price()
    for histeel_price in histeel_prices:
        snowflake_data.append(
            [
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "-",
                histeel_price["product"],
                "SMSP Scraper",
                "Competitor",
                "Distributor",
                "Hi Steel",
                "Surabaya",
                0,
                1,
                histeel_price["price"],
                0,
                "Scraped by SMSP Scraper",
            ],
        )
    # sbg_prices = smsp_scraper.scrape_sbg_price()
    # for sbg_price in sbg_prices:
    #     snowflake_data.append(
    #         [
    #             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #             sbg_price[0],
    #             sbg_price[1],
    #             "SMSP Scraper",
    #             "Competitor",
    #             "Distributor",
    #             "Super Bangun Jaya",
    #             "Tangerang",
    #             0,
    #             1,
    #             sbg_price[2],
    #             0,
    #             "Scraped by SMSP Scraper",
    #         ],
    #     )
    # artha_beton_prices = smsp_scraper.scrape_artha_beton_price()
    # for artha_beton_price in artha_beton_prices:
    #     snowflake_data.append(
    #         [
    #             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #             "-",
    #             artha_beton_price["product"],
    #             "SMSP Scraper",
    #             "Supplier",
    #             "Factory",
    #             "Artha Beton",
    #             "Sumatra Selatan",
    #             0,
    #             1,
    #             artha_beton_price["price"],
    #             0,
    #             "Scraped by SMSP Scraper",
    #         ],
    #     )
    # siskaperbapo_prices = smsp_scraper.scrape_siskaperbapo_price()
    # for siskaperbapo_price in siskaperbapo_prices:
    #     snowflake_data.append(
    #         [
    #             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    #             "-",
    #             siskaperbapo_price["product"],
    #             "SMSP Scraper",
    #             "Supplier",
    #             "Factory",
    #             "Siskaperbapo",
    #             "Jawa Timur",
    #             0,
    #             1,
    #             siskaperbapo_price["price"],
    #             0,
    #             "Scraped by SMSP Scraper",
    #         ],
    #     )
    # nss_prices = smsp_scraper.scrape_niaga_sinar_sentosa_price()
    # for nss_price in nss_prices:
    #     snowflake_data.append(
    #         [
    #             datetime.now().date().strftime("%Y-%m-%d"),
    #             "-",
    #             nss_price["product"],
    #             "SMSP Scraper",
    #             "Competitor",
    #             "Distributor",
    #             "Niaga Sinar Sentosa",
    #             "Jawa Barat",
    #             0,
    #             1,
    #             nss_price["price"],
    #             0,
    #             "Scraped by SMSP Scraper",
    #         ],
    #     )
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
    print(snowflake_df)
    snowflake_uploader.upload_data_to_snowflake(
        "RAW", "GOOGLE_SHEET_PRICING", "EXTERNAL_PRICE_SCRAPE", snowflake_df
    )
    
    indonesia_macroeconomics = smsp_scraper.scrape_trading_economics_macroeconomics()      
    snowflake_df = pd.DataFrame(
        indonesia_macroeconomics,
        columns=[
            "AS_OF",
            "SOURCE",
            "TYPE",
            "VALUE",
            "UNIT",
        ],
    )
    snowflake_uploader.upload_data_to_snowflake(
        "RAW", "EXTERNAL_INDICATORS", "INDONESIA_INDICATORS", snowflake_df
    )
    
    iron_ore_historical = smsp_scraper.sgx_ironore_price()
    if (len(iron_ore_historical) != 0):
        snowflake_df = pd.DataFrame(
            iron_ore_historical,
            columns=[
                "AS_OF",
                "SOURCE",
                "TYPE",
                "VALUE",
                "UNIT",
            ],
        )
        snowflake_uploader.upload_data_to_snowflake(
            "RAW", "EXTERNAL_INDICATORS", "IRON_ORE_INDICATORS", snowflake_df
        )
    
    

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
    try:
        smsp_scraper = SMSPScraper()
        indonesia_indicator = smsp_scraper.scrape_trading_economics_macroeconomics()
        # histeel = smsp_scraper.scrape_histeel_price()
        # sina = smsp_scraper.scrape_sina_price_specific()
        # juragan = smsp_scraper.scrape_juragan_material_price()
        # niaga = smsp_scraper.scrape_niaga_sinar_sentosa_price()
        # siska = smsp_scraper.scrape_siskaperbapo_price()

        historical_ironore = smsp_scraper.sgx_ironore_price()
        print("IRONORE CURRENT PRICE",'\n',historical_ironore, '\n')
        print("INDONESIA INDICATOR",'\n',indonesia_indicator, '\n')
        # print("HISTEEL IRON PRICE",'\n',histeel, '\n')
        # print("SINA IRON PRICE",'\n',sina, '\n')
        # print("JURAGAN IRON PRICE",'\n',juragan, '\n')
        # print("NIAGA IRON PRICE",'\n',niaga, '\n')
        # print("SISKA IRON PRICE",'\n',siska, '\n')

    except Exception as e:
        print(e)
    
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

if __name__ == "__main__":
    perform_daily_scraping()
    # test()
