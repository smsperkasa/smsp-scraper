from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
import time
import base64

import logger

def initialize_driver():
    try:
        options = webdriver.ChromeOptions()
        user_data_dir = r"C:\Users\asus\AppData\Local\Google\Chrome\User Data"
        options.add_argument(f"user-data-dir={user_data_dir}")
        options.add_argument("profile-directory=Profile 17")

        # Preventing bot detection (optional)
        # options.add_argument('--disable-blink-features=AutomationControlled')
        # Simulate a full-screen window to ensure all content loads correctly
        options.add_argument('--window-size=1920,1080')
        # Define user agent to spoofing (optional)
        # options.add_argument('--user-agent=Mozilla/5.0 ...')

        driver = webdriver.Chrome(options=options)
        return driver
    except Exception as e:
        print("Error initializing WebDriver:", e)
        return None

def get_ironore_fromcanvas(driver):
    try:
        # Ensure Chrome is open before navigating
        time.sleep(5)
        
        # Navigate to the desired URL
        driver.get("https://www.tradingview.com/chart/HJhYShlJ/?symbol=SGX%3AFEF1%21")

        # Wait for the canvas element to be present
        canvas = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "canvas"))
        )
        
        # Action chain to interact with the canvas
        actions = ActionChains(driver)
        
        # Define a fixed y-coordinate
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
            data_url = base64.b64decode(driver.execute_script(script))
            print(f"Data at ({x}, {fixed_y}):")

            # Reset actions for the next iteration
            actions.reset_actions()
    except Exception as e:
        print(f"An error occurred: {e}")

driver = initialize_driver()
if driver:
    get_ironore_fromcanvas(driver)
