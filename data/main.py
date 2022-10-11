import pandas as pd

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time


def get_snp_500_tickers() -> list:
    # Get SNP 500 Tickers
    driver.get('https://stockmarketmba.com/stocksinthesp500.php')
    ticker_soup = BeautifulSoup(driver.page_source, 'html.parser')
    tickers_row = ticker_soup.find_all("tr", {"role": "row"})
    tickers = []
    for row in tickers_row:
        tickers.append(row.contents[0].get_text())
    return tickers


def get_CIK_from_tickers(tickers: list) -> pd.DataFrame:
    # get_ticker_CIK_mapping_online
    driver.get('https://www.sec.gov/include/ticker.txt')
    cik_mapping_soup = BeautifulSoup(driver.page_source, 'html.parser')
    cik_mapping_words = cik_mapping_soup.get_text()
    cik_mapping_words = cik_mapping_words.split()
    cik_dict = {}
    for i in range(0, len(cik_mapping_words), 2):
        if cik_mapping_words[i] == "brk-b":
            cik_dict['BRK.B'] = cik_mapping_words[i + 1]
        elif cik_mapping_words[i] == "bf-b":
            cik_dict['BF.B'] = cik_mapping_words[i + 1]
        else:
            cik_dict[cik_mapping_words[i].upper()] = cik_mapping_words[i + 1]
    ciks = []
    # map current tickers
    for i in tickers:
        ciks.append(cik_dict[i])

    tickers_df = pd.DataFrame({"Tickers": tickers, "CIK Number": ciks})
    return tickers_df


def get_10_reports_func(CIK: str) -> pd.DataFrame:
    reports = []
    dates = []
    driver.get(f'https://www.sec.gov/edgar/browse/?CIK={CIK}')
    ### Scrape 10K / 10Q forms
    # driver.get('https://www.sec.gov/edgar/browse/?CIK=1411579')
    driver.find_element_by_xpath('//*[@id="filingsStart"]/div[2]/div[3]/h5').click()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('//*[@id="filingsStart"]/div[2]/div[3]/div/button[1]').click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    document_links = soup.find_all("tr", {"role": "row"})
    links = []
    for link in document_links:
        if link.find("a", {"class": "document-link"}) == None:
            continue
        else:
            links.append(link.find("a",{"class":"document-link"}))
            dates.append(link.find("a",{"data-column":"Reporting Date"}).attrs['data-export'])
    for link in links:
        driver.get(f"https://www.sec.gov/{link.attrs['href']}")
        time.sleep(0.1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        reports.append(soup.get_text())

    test = pd.DataFrame({"Date":dates,"Report":reports})

    return test


def get_10_reports(df: pd.DataFrame) -> pd.DataFrame:
    reports = pd.DataFrame()
    for i, j in df.iterrows():
        reports_df = get_10_reports_func(j['CIK Number'])
        reports_df['Ticker'] = j['Tickers']
        reports_df['CIK Number'] = j['CIK Number']
        reports = pd.concat(reports,reports_df)
    return reports


if __name__ == "__main__":
    print("Launching webdriver...")

    chrome_options = Options()
    # chrome_options.add_argument("--disable-extensions")
    # chrome_options.add_argument("--disable-gpu")
    #chrome_options.add_argument("--headless")
    driver = webdriver.Chrome('C:/Users/Tarci/Documents/nus/Y4/FYP/chromedriver.exe',options=chrome_options)
    tickers = get_snp_500_tickers()
    tickers = tickers[1:3]
    stocks_df = get_CIK_from_tickers(tickers)
    stocks_df = get_10_reports(stocks_df)
    print("Done...!")
