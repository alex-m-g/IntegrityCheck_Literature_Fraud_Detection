from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import chromedriver_autoinstaller
import csv

chromedriver_autoinstaller.install()
options = webdriver.ChromeOptions()
options.add_argument('--headless')

service = Service()
driver = webdriver.Chrome(service=service, options=options)
                     

# Define the websites
websites = [
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2023%2F10%2F10-2024%2F10%2F10',  # 2023-2024
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2022%2F10%2F10-2023%2F10%2F10',  # 2022-2023
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2019%2F10%2F10-2022%2F10%2F10',  # 2019-2022
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2013%2F10%2F10-2019%2F10%2F10',  # 2013-2019
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2002%2F10%2F10-2013%2F10%2F10',  # 2002-2013
    'https://pubmed.ncbi.nlm.nih.gov/?term=%22retracted+article%22+OR+%22retraction%22&filter=dates.2000%2F10%2F10-2002%2F10%2F10'   # 2000-2002
]


wait = WebDriverWait(driver, 20)

def num_pages():
    # Get the number of pages
    wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'of-total-pages')))
    print(driver.page_source)
    number_of_pages = driver.find_element(By.CLASS_NAME, 'of-total-pages')
    return int((number_of_pages.text).replace('of', '').strip())

def code_scrape(number_of_pages, pmid_list):
    for i in range(number_of_pages):
        # Wait for the PMIDs to load on the current page
        wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'docsum-pmid')))

        # Collect PMIDs from the current page
        pmid_codes = driver.find_elements(By.CLASS_NAME, 'docsum-pmid')

        for code in pmid_codes:
            try:
                code_int = int(code.text)
                if code_int not in pmid_list:
                    pmid_list.append(code_int)
            except ValueError:
                continue  # Skip if conversion fails

        # Click the 'Next' button to go to the next page
        try:
            next_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'next-page-btn')))
            next_button.click()
            wait.until(EC.url_contains(f"page={i + 2}"))
        except Exception:
            break


pmid_list_master = []

for website in websites:
    driver.get(website)
    number_of_pages = num_pages()  # Get the number of pages after loading the site
    code_scrape(number_of_pages, pmid_list_master)
    print(f"Finished scraping {website}")

    # Output the collected PMIDs
print("Collected PMIDs:", pmid_list_master)

# Saving the collected PMIDs into a CSV file
with open('./output/pmid_list_master.csv', 'w', newline='') as f:
    write = csv.writer(f)
    
    # Assuming pmid_list_master is a list of integers, each needs to be written as a row
    for pmid in pmid_list_master:
        write.writerow([pmid])  # Each PMID is written as a single-item list

# Close the driver
driver.quit()
