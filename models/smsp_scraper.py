import re

from selenium import webdriver as wd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium_stealth import stealth

from logger.logging_config import logger


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

    def collect_hrefs_from_pagination(self, store, should_include, should_not_include):
        try:
            a_elements = self.driver.find_elements(By.TAG_NAME, "a")
            rets = [a.get_attribute("href") for a in a_elements]
            logger.info(f"Successfully obtained hrefs from pagination for {store}")
            for include in should_include:
                rets = [ret for ret in rets if include in ret]
            for not_include in should_not_include:
                rets = [ret for ret in rets if not_include not in ret]
            return rets
        except:
            logger.warning(f"Failed to obtain hrefs from pagination")
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
                        "price": float(
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
                        "price": float(
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

        ret = self.collect_hrefs_from_pagination("Juragan Material", ["produk", "besi-beton"], [])

        for page in range(2, 8):
            self.scrape_juragan_move_to_next_page(page)
            ret += self.collect_hrefs_from_pagination("Juragan Material", ["produk", "besi-beton"], [])

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
                        "price": float(
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
                logger.info(f"Succeeded scraping for {beton_option["product"]}")
            except:
                logger.warning(f"Failed to scrape for {beton_option["product"]}")
        return ret
    
    def scrape_niaga_sinar_sentosa_price_pages(self, product_links):
        ret = []
        
        for product_link in product_links:
            try:
                self.driver.get(product_link)
                
                product_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.CSS_SELECTOR,
                            "h1.product_title.entry-title"
                        )
                    )
                )
                
                
                price_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (
                            By.XPATH,
                            "/html/body/div[1]/div[5]/div[2]/div/div/div[2]/div[1]/div[2]/p[2]/span/bdi"
                        )
                    )
                )
                
                ret.append(
                    {
                        "product": product_element.text.replace("Harga ", "").replace("Jual ", ""),
                        "price":
                            float(price_element.text.replace("Rp", "").replace(".", "")),
                    }
                )
                
                logger.info(
                    f"Successfully scraped Niaga Sinar Sentosa page for {product_link}"
                )
            except:
                logger.warning(
                    f"Failed to scrape Niaga Sinar Sentosa page for {product_link}"
                )
        
        return ret

    def scrape_niaga_sinar_sentosa_price(self):
        self.driver.get("https://www.niagasinarsentosa.co.id/product-category/besi/besi-beton/?per_page=64")
        
        ret = self.collect_hrefs_from_pagination("Niaga Sinar Sentosa", ["besi-beton"], ["product-category", "per-page"])
        
        return self.scrape_niaga_sinar_sentosa_price_pages(ret)
    
    def scrape_trading_view_iron_ore_price(self):
        try:
            self.driver.get("https://www.tradingview.com/symbols/SGX-FEF1!/")
            
            price_element = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[3]/div[4]/div[2]/div[1]/div[1]/div/div/div/div[3]/div[1]/div/div[1]/span[1]/span")))
            
            res = price_element.text
            
            logger.info(f"Successfully scraped iron ore from TradingView with price {res}")
            
            return float(res)
        
        except:
            logger.warning(f"Failed to scrape iron ore price from TradingView")
        
