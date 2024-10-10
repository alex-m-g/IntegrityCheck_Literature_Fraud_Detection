from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import os

# Define the websites you want to scrape
websites = [
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2023%2F10%2F10-2024%2F10%2F10',  # 2023-2024
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2022%2F10%2F10-2023%2F10%2F10',  # 2022-2023
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2019%2F10%2F10-2022%2F10%2F10',  # 2019-2022
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2013%2F10%2F10-2019%2F10%2F10',  # 2013-2019
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2002%2F10%2F10-2013%2F10%2F10',  # 2002-2013
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2000%2F10%2F10-2002%2F10%2F10'   # 2000-2002
]

# Set Chrome options for headless mode
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run Chrome in headless mode
chrome_options.add_argument("--no-sandbox")  # Required in some environments
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems

# Create a Service object using WebDriver Manager
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

wait = WebDriverWait(driver, 10)

def num_pages():  # Get the number of pages
    number_of_pages = driver.find_element(By.CLASS_NAME, 'of-total-pages')
    return int((number_of_pages.text).replace('of', '').strip())

def code_scrape(number_of_pages, pmid_list):
    for i in range(number_of_pages):
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'docsum-pmid')))
        pmid_code = driver.find_elements(By.CLASS_NAME, 'docsum-pmid')
        for code in pmid_code:
            try:
                code_int = int(code.text)
                if code_int not in pmid_list:
                    pmid_list.append(code_int)
            except ValueError:
                continue
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'next-page-btn')))
            next_button.click()
            wait.until(EC.url_contains(f"page={i + 2}"))
        except Exception:
            break

# Save to CSV
def save_to_csv(pmid_list, filename):
    df = pd.DataFrame(pmid_list, columns=["PMID"])
    output_dir = 'output'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    df.to_csv(os.path.join(output_dir, filename), index=False)
    print(f"PMID list saved to {os.path.join(output_dir, filename)}")

def main():
    pmid_list_master = []
    for website in websites:
        driver.get(website)
        try:
            number_of_pages = num_pages()
            print(f"Scraping {number_of_pages} pages from {website}")
            code_scrape(number_of_pages, pmid_list_master)
        except Exception as e:
            print(f"Error on {website}: {e}")
        print(f"Finished scraping {website}")
    
    save_to_csv(pmid_list_master, 'pmid_list_master.csv')

if __name__ == "__main__":
    main()

driver.quit()
