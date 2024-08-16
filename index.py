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
            datetime.now().date().strftime("%Y-%m-%d"),
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
    juragan_prices = smsp_scraper.scrape_juragan_material_price()
    for juragan_price in juragan_prices:
        snowflake_data.append(
            [
                datetime.now().date().strftime("%Y-%m-%d"),
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
                datetime.now().date().strftime("%Y-%m-%d"),
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
    sbg_prices = smsp_scraper.scrape_sbg_price()
    for sbg_price in sbg_prices:
        snowflake_data.append(
            [
                datetime.now().date().strftime("%Y-%m-%d"),
                sbg_price[0],
                sbg_price[1],
                "SMSP Scraper",
                "Competitor",
                "Distributor",
                "Super Bangun Jaya",
                "Tangerang",
                0,
                1,
                sbg_price[2],
                0,
                "Scraped by SMSP Scraper",
            ],
        )
    artha_beton_prices = smsp_scraper.scrape_artha_beton_price()
    for artha_beton_price in artha_beton_prices:
        snowflake_data.append(
            [
                datetime.now().date().strftime("%Y-%m-%d"),
                "-",
                artha_beton_price["product"],
                "SMSP Scraper",
                "Supplier",
                "Factory",
                "Artha Beton",
                "Sumatra Selatan",
                0,
                1,
                artha_beton_price["price"],
                0,
                "Scraped by SMSP Scraper",
            ],
        )
    siskaperbapo_prices = smsp_scraper.scrape_siskaperbapo_price()
    for siskaperbapo_price in siskaperbapo_prices:
        snowflake_data.append(
            [
                datetime.now().date().strftime("%Y-%m-%d"),
                "-",
                siskaperbapo_price["product"],
                "SMSP Scraper",
                "Supplier",
                "Factory",
                "Siskaperbapo",
                "Jawa Timur",
                0,
                1,
                siskaperbapo_price["price"],
                0,
                "Scraped by SMSP Scraper",
            ],
        )
    nss_prices = smsp_scraper.scrape_niaga_sinar_sentosa_price()
    for nss_price in nss_prices:
        snowflake_data.append(
            [
                datetime.now().date().strftime("%Y-%m-%d"),
                "-",
                nss_price["product"],
                "SMSP Scraper",
                "Competitor",
                "Distributor",
                "Niaga Sinar Sentosa",
                "Jawa Barat",
                0,
                1,
                nss_price["price"],
                0,
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
    print(snowflake_df)
    snowflake_uploader.upload_data_to_snowflake(
        "RAW", "GOOGLE_SHEET_PRICING", "EXTERNAL_PRICE_SCRAPE", snowflake_df
    )


def test():
    smsp_scraper = SMSPScraper()
    snowflake_uploader = SnowflakeUploader()
    snowflake_data = []
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
        "MARTS", "DEVELOPMENT", "EXTERNAL_PRICE_SCRAPE", snowflake_df
    )


def temp():
    external_price_scrape_df = pd.read_csv("external_price_scrape.csv")
    snowflake_uploader.upload_data_to_snowflake(
        "RAW", "GOOGLE_SHEET_PRICING", "EXTERNAL_PRICE_SCRAPE", external_price_scrape_df
    )


if __name__ == "__main__":
    perform_daily_scraping()
    # test()
    # temp()
