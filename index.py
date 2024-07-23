import logging
import re
from datetime import datetime

import gspread
import pandas as pd
import yfinance as yf
from google.oauth2.service_account import Credentials
from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium_stealth import stealth
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

import config

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    style="%",
    datefmt="%Y-%m-%d %H:%M",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


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
        # self.driver = wd.Remote(command_executor="http://localhost:4444/wd/hub", options=chrome_options)

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
        try:
            self.driver.get("https://finance.sina.com.cn/futures/quotes/RB0.shtml")
            price_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (
                        By.CSS_SELECTOR,
                        "span.real-price.price.green, span.real-price.price.red",
                    )
                )
            )
            res = price_element.text
            logger.info(f"Scraped for Sina with price {res}")
            return float(res)
        except Exception as _:
            logger.warning("Failed to scrape for Sina")
            return 0

    def scrape_juragan_move_to_next_page(self, page):
        try:
            button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//button[contains(@aria-label, 'page {str(page)}')]")
                )
            )
            button.click()
            logger.info(f"Moved to page {page} for Juragan Material")
        except:
            logger.warning(f"Failed to move to page {page} for Juragan Material")

    def collect_hrefs_from_pagination(self):
        try:
            a_elements = self.driver.find_elements(By.TAG_NAME, "a")
            rets = [a.get_attribute("href") for a in a_elements]
            logger.info("Successfully obtained hrefs from pagination")
            return [ret for ret in rets if "produk" in ret and "besi-beton" in ret]
        except:
            logger.warning("Failed to obtain hrefs from pagination")
            return []

    def scrape_histeel_price_pages(self, product_links):
        ret = []

        for product_link in product_links:
            try:
                self.driver.get(product_link)
                price_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "span.woocommerce-Price-amount.amount")
                    )
                )
                product_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR, "h1.product_title.entry-title")
                    )
                )
                ret.append(
                    {
                        "product": product_element.text,
                        "price": int(
                            price_element.text.replace("Rp ", "").replace(",", "")
                        ),
                    }
                )
                logger.info(f"Successfully scraped Histeel page for {product_link}")
            except Exception as _:
                logger.warning(f"Failed to scrape Histeel page for {product_link}")

        return ret

    def scrape_juragan_material_price_pages(self, product_links):
        ret = []
        for product_link in product_links:
            try:
                self.driver.get(product_link)
                product_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/main/div[2]/div[1]/div[2]/div[1]/div/h1",
                        )
                    )
                )
                price_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/main/div[2]/div[1]/div[2]/div[1]/div/div[1]/p",
                        )
                    )
                )
                weight_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div/main/div[2]/div[1]/div[2]/div[2]/div[2]/div/div[5]/p[2]",
                        )
                    )
                )
                ret.append(
                    {
                        "product": product_element.text,
                        "price": int(
                            price_element.text.replace("Rp ", "").replace(".", "")
                        ),
                        "weight": float(
                            re.search(r"/\s*([\d,]+)\s*Kg", weight_element.text)
                            .group(1)
                            .replace(",", ".")
                        ),
                    }
                )
                logger.info(
                    f"Successfully scraped Juragan Material page for {product_link}"
                )
            except Exception as _:
                logger.warning(
                    f"Failed to scrape Juragan Material page for {product_link}"
                )

        return ret

    def scrape_juragan_material_price(self):
        self.driver.get(
            "https://juraganmaterial.id/kategori/besi-beton-and-wiremesh/besi-beton"
        )

        ret = self.collect_hrefs_from_pagination()

        for page in range(2, 8):
            self.scrape_juragan_move_to_next_page(page)
            ret += self.collect_hrefs_from_pagination()

        return self.scrape_juragan_material_price_pages(ret)

    def scrape_histeel_price(self):
        self.driver.get("https://histeel.co.id/product-tag/distributor-besi-surabaya/")

        ret = []

        try:
            div_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "div.mf-product-details")
                )
            )
            logger.info("Obtained product details for Histeel")
        except:
            logger.warning("Failed to obtain product details for Histeel")
            return ret

        for i, div in enumerate(div_elements):
            try:
                h2_element = div.find_element(
                    By.CSS_SELECTOR, "h2.woo-loop-product__title"
                )
                product_element = h2_element.find_element(By.TAG_NAME, "a")

                price_span = div.find_element(By.CSS_SELECTOR, "span.price")
                try:
                    price_element = price_span.find_element(
                        By.CSS_SELECTOR, "ins > span.woocommerce-Price-amount.amount"
                    )
                    logger.info(f"Discounted price for Histeel product {str(i)}")
                except:
                    price_element = price_span.find_element(
                        By.CSS_SELECTOR, "span.woocommerce-Price-amount.amount"
                    )
                    logger.info(f"Normal price for Histeel product {str(i)}")
                ret.append(
                    {
                        "product": product_element.text,
                        "price": int(
                            price_element.text.replace("Rp ", "").replace(",", "")
                        ),
                    }
                )
                logger.info(f"Successfully scraped product {str(i)} for Histeel")
            except:
                logger.warning(f"Failed to scraped product {str(i)} for Histeel")

        return ret

    def scrape_sbg_price(self):
        self.driver.get("https://bestseller.superbangunjaya.com/best-product/besi/")

        ret = [[]]
        count = 0

        try:
            data_elements = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "td.tg-7zrl"))
            )
            logger.info("Obtained product details for SBG")
        except:
            logger.warning("Failed to obtain product details for SBG")
            return []

        for data_element in data_elements:
            curr = data_element.text
            if curr != "":
                ret[-1].append(curr.replace(".", ""))

            count += 1

            if count == 3:
                count = 0
                ret.append([])

        return ret[:-2]

    def scrape_iron_ore_price(self):
        pass

    def scrape_artha_beton_price(self):
        self.driver.get(
            "https://arthabeton.co.id/product/harga-besi-beton-jual-per-kg-perbatang/"
        )

        product_name_price_xpaths = (
            [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[14]/span[{str(i)}]"
                for i in range(2, 13, 1)
            ]
            + [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[16]/span[{str(i)}]"
                for i in range(1, 8, 1)
                if i != 4
            ]
            + [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[18]/span[{str(i)}]"
                for i in range(1, 4, 1)
            ]
            + [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[20]/span[{str(i)}]"
                for i in range(1, 4, 1)
            ]
            + [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[22]/span[{str(i)}]"
                for i in range(1, 5, 1)
            ]
            + [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[24]/span[{str(i)}]"
                for i in range(1, 4, 1)
            ]
            + [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[26]/span[{str(i)}]"
                for i in range(1, 3, 1)
            ]
            + [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[28]/span[{str(i)}]"
                for i in range(1, 3, 1)
            ]
            + [
                f"/html/body/div[1]/div/div/div/div[2]/div[3]/div[1]/p[30]/span[{str(i)}]"
                for i in range(1, 4, 1)
            ]
        )

        ret = []

        for i, product_name_price_xpath in enumerate(product_name_price_xpaths):
            try:
                product_price_name_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            product_name_price_xpath,
                        )
                    )
                )
                price_name = product_price_name_element.text.split(":")
                ret.append(
                    {
                        "product": price_name[0],
                        "price": price_name[1]
                        .replace(" Rp ", "")
                        .replace(".", "")
                        .split(" ")[0],
                    }
                )
                logger.info(f"Successfully scraped for Artha Beton product {str(i)}")
            except:
                logger.warning(f"Failed to scrape for Artha Beton product {str(i)}")

        return ret

    def scrape_siskaperbapo_price(self):
        self.driver.get("https://siskaperbapo.jatimprov.go.id/")

        ret = []
        beton_options = []
        try:
            select_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "select#komoditas.form-control")
                )
            )
            select = Select(select_element)
            for option in select.options:
                product = option.text
                if "Besi Beton" in product:
                    beton_options.append(
                        {"product": product, "value": option.get_attribute("value")}
                    )

            logger.info("Successfully located select tag for Siskaperbapo")
        except:
            logger.warning("Failed to locate select tag for Siskaperbapo")
            return ret

        for beton_option in beton_options:
            try:
                select.select_by_value(beton_option["value"])
                self.driver.implicitly_wait(4)
                price_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "/html/body/div[1]/div[4]/div[1]/div[1]/div/div/b[2]")
                    )
                )
                ret.append(
                    {"product": beton_option["product"], "price": float(price_element.text.replace("Rp", "").replace(",-", "").replace(".", ""))}
                )
                logging.info(f"Succeeded scraping for {beton_option["product"]}")
            except:
                logging.warning(f"Failed to scrape for {beton_option["product"]}")
        return ret


class SnowflakeUploader:
    def upload_data_to_snowflake(self, database, schema, table, df):  # pragma: no cover
        """
        Utility: Uploads df to Snowflake, specifies database, schema, and table
        """
        logger = logging.getLogger("kpi")
        url_post = URL(
            account=config.ACCOUNT,
            user=config.USER,
            password=config.PASSWORD,
            warehouse=config.WAREHOUSE,
            database=database,
        )

        try:
            engine_post = create_engine(url_post)
            with engine_post.begin() as conn:
                df.to_sql(
                    table, con=conn, schema=schema, if_exists="append", index=False
                )
            logger.info("Uploaded to Snowflake successfully")
        except:
            logger.warning("Cannot upload to Snowflake")


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

    def upload_data_raw(self, sheet_name, data):
        sheet = self.workbook.worksheet(sheet_name)
        new_row_index = len(sheet.get_all_values()) + 1
        sheet.insert_row(data, new_row_index)


class CurrencyConverter:

    def get_exchange_rates_historical(self, base, target, start_date, end_date):
        base_target = f"{base}{target}=X"
        historical_data = yf.download(base_target, start=start_date, end=end_date)
        logging.info(
            f"Obtained historical data for {base} to {target} from {start_date} to {end_date}"
        )
        return historical_data

    def get_exchange_rates_latest(self, base, target):
        base_target = f"{base}{target}=X"
        data = yf.Ticker(base_target)
        today_data = data.history(period="1d")
        current_rate = today_data["Close"].iloc[0]
        logging.info(f"Obtained today's currency rate from {base} to {target}")
        return float(current_rate)


def perform_daily_scraping():
    smsp_scraper = SMSPScraper()
    snowflake_uploader = SnowflakeUploader()
    currency_converter = CurrencyConverter()
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


def test():
    smsp_scraper = SMSPScraper()
    snowflake_uploader = SnowflakeUploader()
    siskaperbapo_prices = smsp_scraper.scrape_siskaperbapo_price()
    snowflake_data = []
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


if __name__ == "__main__":
    # perform_daily_scraping()
    test()
