from datetime import datetime

import gspread
import yfinance as yf
from google.oauth2.service_account import Credentials
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium_stealth import stealth


class SMSPScraper:
    def __init__(self):
        self.driver = None
        self.initialize_driver()

    def initialize_driver(self):
        chrome_options = wd.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--ignore-certificate_errors")
        chrome_options.add_argument("--mute-audio")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_experimental_option("detach", True)
        self.driver = wd.Chrome(options=chrome_options)
        stealth(
            self.driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

    def scrape_sina_price_specific(self):
        self.driver.get("https://finance.sina.com.cn/futures/quotes/RB0.shtml")

        try:
            price_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "span.real-price.price.green")
                )
            )
            return price_element.text
        except Exception as _:
            return "Unavailable"


class SheetUploader:
    def __init__(self):
        self.sheet = None
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = Credentials.from_service_account_file(
            "credentials.json", scopes=self.scopes
        )
        self.client = gspread.authorize(self.creds)
        self.sheet_id = "15TermcNQYeUueb1L4HT7Lfa7_IjdjHTZv4-H1ijNC2M"
        self.workbook = self.client.open_by_key(self.sheet_id)

    def upload_data(self, sheet_name, data):
        """
        NOTE: omit the first element of the data list if it is a date
        """
        sheet = self.workbook.worksheet(sheet_name)
        new_row_index = len(sheet.get_all_values()) + 1
        current_date = datetime.now().date()
        res_date = [current_date.strftime("%Y-%m-%d")]
        res = res_date + data
        sheet.insert_row(res, new_row_index)


class CurrencyConverter:

    def get_exchange_rates_historical(self, base, target, start_date, end_date):
        base_target = f"{base}{target}=X"
        historical_data = yf.download(base_target, start=start_date, end=end_date)
        return historical_data

    def get_exchange_rates_latest(self, base, target):
        base_target = f"{base}{target}=X"
        data = yf.download(base_target, period="1d", interval="1m")
        current_rate = data["Close"].iloc[-1]
        return current_rate


if __name__ == "__main__":
    smsp_scraper = SMSPScraper()
    sheet_uploader = SheetUploader()
    currency_converter = CurrencyConverter()
    sina_price_cny = smsp_scraper.scrape_sina_price_specific()
    sina_price_idr = sina_price_cny * currency_converter.get_exchange_rates_latest(
        "CNY", "IDR"
    )
    sheet_uploader.upload_data(
        "External Price Scrape",
        [
            "-",
            "Besi Beton",
            "SMSP Scraper",
            "Competitor",
            "Factory",
            "sina",
            "China",
            "-",
            "-",
            sina_price_idr,
            "Scraped by SMSP Scraper",
        ],
    )
