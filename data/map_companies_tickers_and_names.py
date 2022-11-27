import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

sgx_directory = './SGX'
snp_directory = './SNP500'


def process_sgx_files():
    """
     takes in all files and finds tickers. writes new CSV containing mapping of name to ticker
    """
    try:
        scraped = pd.read_csv('sgx_mapping.csv')
        already_scraped = scraped['Company Name'].unique()
    except:
        already_scraped = []
    sgx_name = []
    sgx_ticker = []
    df = pd.DataFrame()
    for filename in os.listdir(sgx_directory):
        f = os.path.join(sgx_directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            if 'DS_Store' in f or 'gitignore' in f:
                continue
            # read each file and concat them into a dataframe
            file = open(f, "r", encoding="utf8").read()
            df = pd.concat([df, pd.DataFrame({'File Name': [filename], 'Text': [file]})])
    # file name cleaning, removing (1), (2) (3) from end of name
    df['File Name'] = df['File Name'].str.replace(" (1)", '', regex=False) \
        .str.replace(" (2)", '', regex=False) \
        .str.replace(" (3)", '', regex=False)

    # extracting company name
    df['Company Name'] = (df['File Name'].apply(lambda x: x.split(' (')))
    df['Company Name'] = df['Company Name'].apply(lambda x: x[0])
    # get tickers using company name
    chrome_options = Options()
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('C:/Users/Tarci/Documents/nus/Y4/FYP/chromedriver.exe', options=chrome_options)
    driver.get('https://sginvestors.io/sgx/stock/')
    company_names = df['Company Name'].unique()
    company_dict = {}
    for i in company_names:
        if i in already_scraped:
            continue
        try:
            print(f"getting ticker for {i}...")
            driver.find_element_by_xpath('//*[@id="gsc-i-id1"]').send_keys(i)
            driver.find_element_by_xpath('//*[@id="___gcse_0"]/div/div/form/table/tbody/tr/td[2]/button').click()
            WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CLASS_NAME, "gs-title")))
            sgx_soup = BeautifulSoup(driver.page_source, 'html.parser')
            search_links = sgx_soup.find_all('a', {"class": "gs-title"})
            driver.get(search_links[0].attrs['href'])
            page_soup = BeautifulSoup(driver.page_source, 'html.parser')
            page_title = page_soup.find_all('h3', {'itemprop': 'headline'})
            company_dict[i] = page_title[0].text
        except:
            driver.get('https://sginvestors.io/sgx/stock/')
            print(f"could not find results for {i}...")

    for i in company_dict.keys():
        sgx_name.append(i)
        sgx_ticker.append(company_dict[i])

    sg_df = pd.DataFrame({'Company Name': sgx_name, 'Ticker': sgx_ticker})
    sg_df = pd.concat([sg_df, scraped])
    sg_df.to_csv('sgx_mapping.csv', index=False)
    return


def process_snp_files():
    # raw file from https://www.barchart.com/stocks/indices/sp/sp500?viewName=main&page=all
    raw = pd.read_csv('snp500_map_raw.csv')
    df = pd.DataFrame()
    for filename in os.listdir(snp_directory):
        f = os.path.join(snp_directory, filename)
        # checking if it is a file
        if os.path.isfile(f):
            if 'DS_Store' in f or 'gitignore' in f:
                continue
            # read each file and concat them into a dataframe
            file = open(f, "r", encoding="utf8").read()
            df = pd.concat([df, pd.DataFrame({'File Name': [filename]})])

    # find out what companies we have
    current_tickers = (df['File Name'].apply(lambda x: x.split(' ')[0]).unique())

    # compare with companies that we have in the current mapping, find out any companies not inside
    to_map = []
    for i in current_tickers:
        if i not in raw['Symbol'].tolist():
            to_map.append(i)

    # We find that only ticker `NLOK` is not in the map downloaded online
    # NLOK has rebranded as GEN from Nov 8 Onward, but since data is pulled from 27 Oct, we will be using the old name
    # NLOK : NortonLifeLock Inc.

    raw = raw.append({'Symbol': 'NLOK', 'Name': 'NortonLifeLock Inc'},ignore_index=True)
    print("")
    raw.to_csv('snp_mapping.csv')

process_snp_files()
# process_remaining_sgx_files()
print("Done...!")
