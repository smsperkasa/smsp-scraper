import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By  # Import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def initialize_driver():
    try:
        options = webdriver.ChromeOptions()
        # browser run in headless mode
        options.add_argument('--headless=new')
        #disable gpu for preventing website get render
        options.add_argument('--disable-gpu')
        #preventing website run on sandbox
        options.add_argument('--no-sandbox')
        #preventing bot detection
        options.add_argument('--disable-blink-features=AutomationControlled')
        # simulate a full-screen window to ensure all content loads correctly
        options.add_argument('--window-size=1920,1080')
        #define user agent to spoofing
        options.add_argument('--user-agent=Mozilla/5.0 ...')

        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print("Error initializing WebDriver:", e)
        return None

def getActualValueFromMetric(rows, index):
    try:
        row = rows[index]
        cells = row.find_all('td')
        value = cells[1].text.strip()
        return value
    except Exception as e:
        print(f"Error extracting value from row {index}:", e)
        return None

def print_result(source, type, value, unit):
    try:
        print("AS_OF:", datetime.now())
        print("SOURCE:", source)
        print("TYPE:", type)
        print("VALUE:", value)
        print("UNIT:", unit, '\n')
    except Exception as e:
        print("Error printing result:", e)

def get_data(driver, url):
    try:
        # Navigate to the website
        driver.get(url)
        
        # wait for all elements in page present
        WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, 'table-hover')))

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Extract the tables
        tables = soup.find_all('table', {'class': 'table table-hover'})
        if tables:
            first_table = tables[0]
            second_table = tables[1]

            first_rows = first_table.find_all('tr')
            second_rows = second_table.find_all('tr')

            stock_market = getActualValueFromMetric(first_rows, 1)
            gdp_growth_rate = getActualValueFromMetric(second_rows, 1)
            inflation_rate = getActualValueFromMetric(second_rows, 4)
            interest_rate = getActualValueFromMetric(second_rows, 6)
            manufacturing_pmi = getActualValueFromMetric(second_rows, 9)

            print_result("Trading Economics Website", "Stock Market", stock_market, "points")
            print_result("Trading Economics Website", "GDP Growth Rate", gdp_growth_rate, "%")
            print_result("Trading Economics Website", "Inflation Rate", inflation_rate, "%")
            print_result("Trading Economics Website", "Interest Rate", interest_rate, "%")
            print_result("Trading Economics Website", "Manufacturing PMI", manufacturing_pmi, "points")
        else:
            print("Table not found")
            print(tables)
    except Exception as e:
        print("Error retrieving data from the website:", e)
        

def main():
    try:
        url = 'https://tradingeconomics.com/indonesia/forecast'
        driver = initialize_driver()
        if driver:
            get_data(driver, url)
            driver.quit()
    except Exception as e:
        print("Error in main function:", e)

if __name__ == "__main__":
    main()
