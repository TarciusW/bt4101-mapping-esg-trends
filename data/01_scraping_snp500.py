from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from snp_500_scraping_funcs import *

df = pd.DataFrame()
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        if 'DS_Store' in f or 'gitignore' in f:
            continue
        # read each file and concat them into a dataframe
        file = open(f, "r", encoding="utf8").read()
        df = pd.concat([df, pd.DataFrame({'File Name': [filename], 'Text': [file]})])
current_tickers = get_current_tickers()  # read file input to see what companies have already been scraped for
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
to_remove = ['SPGI', 'LRCX', 'TWTR', 'FRC', 'SBNY']  # add those that CIK cannot be found in edgar db
for i in to_remove:
    if i in tickers_left:
        tickers_left.remove(i)  # drop tickers as cannot locake CIK number in database
stocks_df = get_CIK_from_tickers(driver, tickers_left)
stocks_df = get_10_reports(driver, stocks_df)
print(f"Data was scraped for {len(current_tickers)} companies")
print("Done..!")
