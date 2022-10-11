import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

if __name__ == "__main__":
    print("Launching webdriver...")
    driver = webdriver.Chrome('C:/Users/Tarci/Documents/nus/Y4/FYP/chromedriver.exe')
    driver.get('https://www.sec.gov/edgar/browse/?CIK=1411579')
    driver.find_element_by_xpath('//*[@id="filingsStart"]/div[2]/div[3]/h5').click()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('//*[@id="filingsStart"]/div[2]/div[3]/div/button[1]').click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    document_links = soup.find_all("a", {"class": "document-link"})
    links = []
    for link in document_links:
        if "10k" in link.attrs['aria-describedby'] or "10q" in link.attrs['aria-describedby']:
            links.append(link)
    text = []

    for link in links:
        driver.get(f"https://www.sec.gov/{link.attrs['href']}")
        time.sleep(0.1)
        soup = BeautifulSoup(driver.page_source,'html.parser')
        text.append(soup.get_text())
    """
    driver.get(f"https://www.sec.gov/{links[0].attrs['href']}")
    time.sleep(0.01)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    test = soup.get_text()
    """

    print("Done...!")