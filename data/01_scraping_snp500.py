from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from snp_500_scraping_funcs import *
import json

current_tickers = get_current_tickers()
print("Collecting SNP 500 Data...")
print("Launching webdriver....")
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome('C:/Users/Tarci/Documents/nus/Y4/FYP/chromedriver.exe', options=chrome_options)
tickers_full = get_snp_500_tickers(driver)
tickers = tickers_full[1:]  # Change this line to determine how many stocks to scrape out of the snp 500
tickers_left = list(filter(lambda x: x not in current_tickers, tickers))
stocks_df = get_CIK_from_tickers(driver, tickers_left)
stocks_df = get_10_reports(driver, stocks_df)
print("Done..!")
