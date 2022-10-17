from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from snp_500_scraping_funcs import *
import json


print("Collecting SNP 500 Data...")
print("Launching webdriver....")
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome('C:/Users/Tarci/Documents/nus/Y4/FYP/chromedriver.exe', options=chrome_options)
tickers_full = get_snp_500_tickers(driver)
tickers = tickers_full[1:20]  # Change this line to determine how many stocks to scrape out of the snp 500
with open('snp_500_reports.json', 'r') as openfile:
    stocks_json = json.loads(openfile.read())
current_tickers = list(stocks_json.keys())
while len(current_tickers) < len(tickers):
    tickers_left = list(filter(lambda x: x not in current_tickers, tickers))
    stocks_df = get_CIK_from_tickers(driver, tickers_left)
    stocks_df = get_10_reports(driver, stocks_df)
    stocks_dict = convert_df_to_dict(stocks_df, stocks_json)
    stocks_json = stocks_dict
    current_tickers = list(stocks_json.keys())
    with open("snp_500_reports.json", "w") as outfile:
        json.dump(stocks_dict, outfile)
    print(f"End of run...! Data is currently scraped for {len(list(stocks_dict.keys()))} stocks out of "
          f"{len(tickers)}")
