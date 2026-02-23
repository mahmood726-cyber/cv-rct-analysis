import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def verify_dashboard_phase_3():
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
        
        # 1. Verify Visualizations appear
        print("Verifying Plotly Charts...")
        # Streamlit Plotly charts are in containers with class 'stPlotlyChart'
        charts = wait.until(EC.presence_of_all_elements_located((By.XPATH, "//div[contains(@class, 'stPlotlyChart')]")))
        print(f"Found {len(charts)} interactive charts.")
        assert len(charts) >= 2, f"Expected at least 2 charts, found {len(charts)}"

        # 2. Verify Export Button
        print("Verifying Export Button...")
        export_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Download Filtered Results (CSV)')]")))
        print("Export button found.")
        assert export_btn.is_displayed()

        print("All automated UI verifications for Phase 3 passed successfully!")

    except Exception as e:
        print(f"Selenium verification failed: {e}")
        driver.save_screenshot("selenium_phase3_error.png")
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    verify_dashboard_phase_3()
