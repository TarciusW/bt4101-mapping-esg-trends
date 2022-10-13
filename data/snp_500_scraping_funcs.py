import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import time

def get_snp_500_tickers(driver) -> list:
    # Get SNP 500 Tickers
    print("Scraping S&P 500 Tickers...")
    driver.get('https://stockmarketmba.com/stocksinthesp500.php')
    ticker_soup = BeautifulSoup(driver.page_source, 'html.parser')
    tickers_row = ticker_soup.find_all("tr", {"role": "row"})
    tickers = []
    for row in tickers_row:
        tickers.append(row.contents[0].get_text())
    print("... done!")
    return tickers


def get_CIK_from_tickers(driver, tickers: list) -> pd.DataFrame:
    print("Mapping Tickers to CIK Numbers...")
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
    print("... done!")
    return tickers_df


def get_10_reports_func(driver, CIK: str) -> pd.DataFrame:
    reports = []
    dates = []
    driver.get(f'https://www.sec.gov/edgar/browse/?CIK={CIK}')
    time.sleep(1)
    # Scrape 10K / 10Q forms
    # driver.get('https://www.sec.gov/edgar/browse/?CIK=1411579')
    driver.find_element_by_xpath('//*[@id="filingsStart"]/div[2]/div[3]/h5').click()
    driver.implicitly_wait(5)
    driver.find_element_by_xpath('//*[@id="filingsStart"]/div[2]/div[3]/div/button[1]').click()
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    document_links = soup.find_all("tr", {"role": "row"})
    links = []
    for link in document_links:
        if link.find("a", {"class": "document-link"}) is None:
            continue
        else:
            links.append(link.find("a", {"class": "document-link"}))
            dates.append(link.find("a", {"data-column": "Reporting Date"}).attrs['data-export'])
    for link in links:
        if 'ix?doc' in link.attrs['href']:
            driver.get(f"https://www.sec.gov/{link.attrs['href']}")
            time.sleep(1)
            driver.find_element_by_xpath('//*[@id="menu-dropdown-link"]/span[1]').click()
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            link = soup.find("a", {"id": "form-information-html"})
        driver.get(f"https://www.sec.gov/{link.attrs['href']}")
        time.sleep(1)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        reports.append(soup.get_text())
    test = pd.DataFrame({"Date": dates, "Report": reports})
    return test


def get_10_reports(driver, df: pd.DataFrame) -> pd.DataFrame:
    print("Scraping 10-K/10-Q reports...")
    reports = pd.DataFrame()
    for i, j in tqdm(df.iterrows()):
        try:
            print(f"\nScraping 10-Q/10-Q reports for {j['Tickers']}...")
            reports_df = get_10_reports_func(driver, j['CIK Number'])
        except:
            print(f"Something went wrong while scraping reports for {j['Tickers']}, saving reports scraped so far...")
            return reports
        else:
            reports_df['Ticker'] = j['Tickers']
            reports_df['CIK Number'] = j['CIK Number']
            reports = pd.concat([reports, reports_df])
    print("... done!")
    return reports


def convert_df_to_dict(df: pd.DataFrame, stock_dict: dict) -> dict:
    if df.empty:
        return stock_dict
    tickers_list = df['Ticker'].unique().tolist()
    for ticker in tickers_list:
        ticker_dict = {}
        ticker_df = df[df['Ticker'] == ticker]
        for index, row in ticker_df.iterrows():
            ticker_dict[row['Date']] = row['Report']
        stock_dict[ticker] = ticker_dict
    return stock_dict
