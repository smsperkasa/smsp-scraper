

from selenium import webdriver
from selenium.webdriver.common.by import By  # Import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time

import logger



def initialize_driver():
    try:
        options = webdriver.ChromeOptions()
        user_data_dir = r"C:\Users\asus\AppData\Local\Google\Chrome\User Data"
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument("profile-directory=Profile 20")

        # #preventing bot detection
        # options.add_argument('--disable-blink-features=AutomationControlled')
        # # simulate a full-screen window to ensure all content loads correctly
        # options.add_argument('--window-size=1920,1080')
        # #define user agent to spoofing
        # options.add_argument('--user-agent=Mozilla/5.0 ...')

        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print("Error initializing WebDriver:", e)
        return None

 
def ticks_period_1day(driver,page):
        try:
            #change ticks to 1 day
            button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//button[contains(@aria-label, '1 minute')]")
                )
            )
            button.click()
            logger.info(f"Clicked ticks 1 day chart button on trading view iron ore")
            
            #change interval on 1 day
            button = WebDriverWait(driver, 2).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//button[contains(@aria-label, '1 day in 1 minute intervals')]")
                )
            )
            
            button.click()
            logger.info(f"Clicked interval 1 day chart button on trading view iron ore")
        except:
            logger.warning(f"Failed to interval full chart button on trading view iron ore")  
              
def click_full_chart(driver,page):
        try:
            #to get the desired data, expand to full chart
            button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, f"//button[contains(@class, 'apply-common-tooltip lightButton-bYDQcOkp noContent-bYDQcOkp withStartSlot-bYDQcOkp secondary-PVWoXu5j gray-PVWoXu5j medium-bYDQcOkp typography-regular16px-bYDQcOkp')]")
                )
            )
            button.click()
            logger.info(f"Clicked full chart button on trading view iron ore")
        except:
            logger.warning(f"Failed to click full chart button on trading view iron ore")  
def get_ironore_fromcanvas(driver):


    driver.get("https://www.tradingview.com/chart/HJhYShlJ/?symbol=SGX%3AFEF1%21")
    canvas = WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, "canvas"))
    )    
    actions = ActionChains(driver)
    for x in range(x_start, x_end + 1, x_step):
        # Move to the canvas and then offset to the desired coordinates
        actions.move_to_element_with_offset(canvas, x, fixed_y).perform()
        time.sleep(1)  # Wait for tooltip or data to appear

        # Attempt to locate the tooltip or data element (if any)
        try:
            tooltip = driver.find_element(By.CSS_SELECTOR, ".tooltip-class")  # Update selector
            print(f"Data at ({x}, {fixed_y}): {tooltip.text}")
        except:
            print(f"No tooltip found at ({x}, {fixed_y})")
    # Define a fixed y-coordinate
    # to get the opportunity close data, only dynamically moves on x-coordinate
    fixed_y = 150  # Example y-coordinate

    # Define the range of x-coordinates to move along the x-axis
    x_start = 50  # Starting x-coordinate
    x_end = 500   # Ending x-coordinate
    x_step = 50   # Step size for each move
    
    for x in range(x_start, x_end + 1, x_step):
        # Move to the canvas and then offset to the desired coordinates
        actions.move_to_element_with_offset(canvas, x, fixed_y).perform()
        time.sleep(1)  # Wait for tooltip or data to appear

        # Inject JavaScript to get canvas data or tooltip info
        script = """
        var canvas = document.querySelector('canvas');
        var ctx = canvas.getContext('2d');
        // Replace with your code to extract specific data if available
        return canvas.toDataURL();  // Example: returns base64 encoded image data
        """
        data_url = driver.execute_script(script)
        print(f"Data at ({x}, {fixed_y}): {data_url}")

        # Reset actions for the next iteration
        actions.reset_actions()

driver = initialize_driver()             
get_ironore_fromcanvas(driver)