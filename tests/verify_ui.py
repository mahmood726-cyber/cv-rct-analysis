import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def verify_dashboard():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Opening Dashboard at http://localhost:8501...")
        driver.get("http://localhost:8501")
        
        wait = WebDriverWait(driver, 30)
        title = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1")))
        print(f"Dashboard title found: {title.text}")

        # 1. Check Initial Metrics
        print("Verifying Initial Metrics...")
        metric_values = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[@data-testid='stMetricValue']")))
        initial_trials = metric_values[0].text
        print(f"Initial Metrics -> Total: {initial_trials}")
        assert initial_trials == "5"

        # 2. Test Multiselect Filter
        print("Testing Sub-Domain Filter (Heart Failure)...")
        ms_container = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='stMultiSelect']")))
        ms_container.click()
        time.sleep(1)
        
        hf_option = wait.until(EC.element_to_be_clickable((By.XPATH, "//li[contains(., 'Heart Failure')]")))
        hf_option.click()
        print("Heart Failure selected.")
        
        # Click the title to close the multiselect dropdown
        title.click()
        time.sleep(2)
        
        # Verify filtered metric
        metric_values = driver.find_elements(By.XPATH, "//div[@data-testid='stMetricValue']")
        filtered_total = metric_values[0].text
        print(f"Filtered Total: {filtered_total}")
        assert filtered_total == "1"

        # 3. Test Radio Filter
        print("Testing Publication Status Filter (Unpublished Only)...")
        # Use JS click if standard click is intercepted
        unpub_option = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@data-testid='stRadio']//p[contains(text(), 'Unpublished Only')]")))
        driver.execute_script("arguments[0].click();", unpub_option)
        print("Unpublished Only selected via JS.")
        time.sleep(3)
        
        metric_values = driver.find_elements(By.XPATH, "//div[@data-testid='stMetricValue']")
        combined_filtered = metric_values[0].text
        print(f"Combined Filter Total: {combined_filtered}")
        assert combined_filtered == "0"

        print("All automated UI verifications passed successfully!")

    except Exception as e:
        print(f"Selenium verification failed: {e}")
        driver.save_screenshot("selenium_error.png")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    verify_dashboard()
