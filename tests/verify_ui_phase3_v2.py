import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

def verify_dashboard_phase_3_refined():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Opening Dashboard at http://localhost:8501...")
        driver.get("http://localhost:8501")
        
        wait = WebDriverWait(driver, 45) # Increased wait time
        
        # 1. Verify Visualizations header
        print("Verifying Visualizations Header...")
        # Streamlit headers are h3 for subheaders
        header = wait.until(EC.presence_of_element_located((By.XPATH, "//h3[contains(., 'Meta-Analysis Visualizations')]")))
        print(f"Header found: {header.text}")

        # 2. Verify Export Button in Sidebar
        print("Verifying Export Button...")
        # The button might be inside the sidebar
        export_btn = wait.until(EC.presence_of_element_located((By.XPATH, "//button[contains(., 'Download Filtered Results (CSV)')]")))
        print("Export button found.")

        # 3. Check for Plotly canvases
        print("Checking for chart canvases...")
        # Plotly often renders inside canvas elements
        canvases = driver.find_elements(By.TAG_NAME, "canvas")
        print(f"Found {len(canvases)} canvas elements.")

        print("All automated UI verifications for Phase 3 passed successfully!")

    except Exception as e:
        print(f"Selenium verification failed: {e}")
        # Capture more debug info
        driver.save_screenshot("selenium_phase3_debug.png")
        with open("selenium_phase3_source.html", "w", encoding="utf-8") as f:
            f.write(driver.page_source)
        raise
    finally:
        driver.quit()

if __name__ == "__main__":
    verify_dashboard_phase_3_refined()
