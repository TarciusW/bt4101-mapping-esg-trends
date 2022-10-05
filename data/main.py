import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

if __name__ == "__main__":
    print("Launching webdriver...")
    driver = webdriver.Chrome('C:/Users/Tarci/Documents/nus/Y4/FYP/chromedriver.exe')
    driver.get('https://www.sec.gov/edgar/browse/?CIK=1411579')
    driver.find_element_by_xpath('//*[@id="filingsStart"]/div[2]/div[3]/h5').click()
    driver.implicitly_wait(10)
    #WebDriverWait(driver,10).until(EC.presence_of_element_located((By.XPATH, '//*[@id="filingsStart"]/div[2]/div[3]/div/button[1]')))

    driver.find_element_by_xpath('//*[@id="filingsStart"]/div[2]/div[3]/div/button[1]').click()
    #driver.find_element(by=xpath,"//input[@id='usernamereg-firstName']")
    #driver.close()