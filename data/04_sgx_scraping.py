from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.select import Select
import pandas as pd
from bs4 import BeautifulSoup
from tqdm import tqdm
import time
import os

directory = './SGX_Annual'


def get_current_tickers():
    files = os.listdir(directory)
    # remove .gitignore
    files = files[1:]
    # extract first word (ticker)
    tickers = [name.split(' ').pop(0) for name in files]
    # remove duplicates
    tickers = list(dict.fromkeys(tickers))
    # remove last ticker to repull, in case not all dates pulled
    return tickers[:-1]


def get_STI_company_names(driver) -> list:
    # Get SNP 500 Tickers
    print("Scraping STI Companies...")
    driver.get('https://sginvestors.io/analysts/sti-straits-times-index-constituents-target-price')
    ticker_soup = BeautifulSoup(driver.page_source, 'html.parser')
    tickers_row = ticker_soup.find_all("td", {"class": "text-primary"})
    company_names = list(map(lambda x: x.contents[0].text.split('(')[0], tickers_row))
    print("... done!")
    return company_names


def get_10_reports_func(driver, CIK: str, Ticker: str) -> pd.DataFrame:
    reports = []
    dates = []
    driver.get(f'https://www.sec.gov/edgar/browse/?CIK={CIK}')
    time.sleep(1)
    # Scrape 10K / 10Q forms
    # specific company for debugging
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
    for i in range(len(links)):
        while True:
            try:
                if 'ix?doc' in links[i].attrs['href']:
                    driver.get(f"https://www.sec.gov/{links[i].attrs['href']}")
                    time.sleep(1)
                    driver.find_element_by_xpath('//*[@id="menu-dropdown-link"]/span[1]').click()
                    soup = BeautifulSoup(driver.page_source, 'html.parser')
                    links[i] = soup.find("a", {"id": "form-information-html"})
                driver.get(f"https://www.sec.gov/{links[i].attrs['href']}")
                time.sleep(1)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                with open(f"{directory}/{Ticker} {dates[i]}.txt", "w", encoding="utf-8") as text_file:
                    text_file.write(soup.get_text())
            except:
                print(f"Error accessing {Ticker} {dates[i]}! retrying...")
            else:
                break

        reports.append(soup.get_text())
    test = pd.DataFrame({"Date": dates, "Report": reports})
    return test


def get_STI_reports(driver, companies) -> pd.DataFrame:
    print("Scraping STI reports...")
    for company in companies:
        driver.get(f'https://www.sgx.com/securities/annual-reports-related-documents')
        search_box = driver.find_element_by_xpath(
            '//*[@id="page-container"]/template-base/div/div/sgx-widgets-wrapper/widget-filter-listing/widget-filter-listing-financial-reports/section/div[1]/sgx-filter-bar/sgx-input-select/label/span[2]/input')
        search_box.send_keys(f"{company}")
        driver.implicitly_wait(5)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        search_options = soup.find_all("sgx-select-picker-option")
        search_options_labels = list(map(lambda x: x.get_text().strip(), search_options))
        search_options[search_options_labels.index(company)]


        print("")

    """
    for i, j in tqdm(df.iterrows()):
        print(f"\nScraping STI reports for {j['Tickers']}...")
        reports_df = get_10_reports_func(driver, j['CIK Number'], j['Tickers'])
        reports_df['Ticker'] = j['Tickers']
        reports_df['CIK Number'] = j['CIK Number']
        reports = pd.concat([reports, reports_df])
    print("... done!")
    """
    return reports


current_tickers = get_current_tickers()

print("Collecting STI Data...")
print("Launching webdriver....")
chrome_options = Options()
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-gpu")
driver = webdriver.Chrome(ChromeDriverManager().install())
companies_full = get_STI_company_names(driver)
tickers_left = list(filter(lambda x: x not in current_tickers, companies_full))
get_STI_reports(driver, tickers_left)
