import pandas as pd
import os
import string
import regex
import nltk
from tqdm import tqdm
from nltk.stem import WordNetLemmatizer
from string import digits
import fitz
from bs4 import BeautifulSoup

sgx_directory = '../data/SGX'
snp_directory = '../data/SNP500'
sgx_annual_directory = '../data/SGX_Annual'


def get_files(path: str) -> pd.DataFrame:
    """
    Iterates through the specified directory and processes the text files in that directory.
    Runs the text files through a text preprocessing pipeline before saving to a dataframe.
    Returns a dataframe with file name + file text (saved as a list of words)
    """
    df = pd.DataFrame()
    cachedStopWords = nltk.corpus.stopwords.words('english')

    for filename in tqdm(os.listdir(path)):
        f = os.path.join(path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            if 'DS_Store' in f or 'gitignore' in f:
                continue
            # read each file and concat them into a dataframe
            file = open(f, "r", encoding="utf8").read()

            file = preprocess_text(file, cachedStopWords)

            df = pd.concat([df, pd.DataFrame({'File Name': [filename], 'Tokens': [file]})])
    return df


def get_sgx_ann_files(path: str) -> pd.DataFrame:
    df = pd.DataFrame()
    cachedStopWords = nltk.corpus.stopwords.words('english')
    for filename in tqdm(os.listdir(path)):
        f = os.path.join(path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            doc = fitz.open(f)
            doc_string = ""
            for i in doc:
                html = i.get_text("html")
                soup = BeautifulSoup(html, 'html.parser')
                doc_string += soup.get_text()
            pdf_string = preprocess_text(doc_string, cachedStopWords)
            year = filename[-8:-4]
            company_name = filename[:-9]
            df = pd.concat([df, pd.DataFrame(
                {"Company": company_name, "Year": year, "Tokens": [pdf_string], "Filename": filename})])
    return df


def preprocess_text(text: str, cachedStopWords: list) -> str:
    """ preprocessing pipeline for text files to have it ready for modelling. takes in the raw text file as input
     and returns the list of tokens for modelling

     Step 1: Remove punctuations from text, replace with whitespace
     Step 2: Make all text lowercase using string.lower() inbuilt function
     Step 3: remove all stopwords (words that have no meaning) from tokens
     Step 4: lemmatize words to their base form
     Step 5: Remove numbers from tokens (including digits within words)
     Step 6: Remove empty tokens
     """

    # remove punctuations and newline characters
    def remove_punctuation(text):
        # punctuationFree = " ".join([i for i in text if i not in string.punctuation])
        punctuationFree = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))
        punctuationFree = regex.sub(r'\n', ' ', punctuationFree)
        return punctuationFree

    def tokenization(text):
        tokens = regex.split(r"\s+", text)
        return tokens

    def remove_stopwords(text, stopwords):
        output = [i for i in text if i not in stopwords]
        return output

    def lemmatizer(text):
        lemm_text = [WordNetLemmatizer().lemmatize(word) for word in text]
        return lemm_text

    def remove_numbers(text):
        """Removes digit elements and digits in strings"""
        result = []
        for i in text:
            try:
                int(i)
            except:
                result.append(i)
            else:
                continue
        return list(map(lambda x: x.translate(str.maketrans('', '', digits)), result))

    def remove_empty_elements(text):
        return list(filter(lambda x: x != '', text))

    text = remove_punctuation(text)
    text = text.lower()
    text = tokenization(text)
    text = remove_stopwords(text, cachedStopWords)
    text = lemmatizer(text)
    text = remove_numbers(text)
    text = remove_empty_elements(text)
    return text


def preprocess_sgx_files() -> pd.DataFrame:
    """
    Wrapper function to process SGX files. uses get_files() and returns a dataframe of the relevant SGX information
    """
    print("Extracting & Preprocessing SGX Sustainability Reports...")
    df = get_files(sgx_directory)
    # file name cleaning, removing (1), (2) (3) from end of name
    df['File Name'] = df['File Name'].str.replace(" (1)", '', regex=False) \
        .str.replace(" (2)", '', regex=False) \
        .str.replace(" (3)", '', regex=False)

    # extracting company name
    df['Company Name'] = (df['File Name'].apply(lambda x: x.split(' (')))
    df['Company Name'] = df['Company Name'].apply(lambda x: x[0])

    # extracting report date (yyyy-mm)
    df['Date'] = (df['File Name'].apply(lambda x: x.split(' ('))).apply(
        lambda x: x[1][0:7] if len(x) == 2 else x[2][0:7])

    # Add Ticker
    company_names = pd.read_csv('../data/Company Mappings/sgx_mapping.csv')
    company_names_dict = {}
    for i, j in company_names.iterrows():
        company_names_dict[j['Company Name']] = j['Ticker']

    def map_ticker(name):
        """
        function to map tickers within the SGX sustainability reports context
        """
        try:
            return company_names_dict[name].split('SGX:')[1][:-1]
        except KeyError:
            return 'Not Available'

    df['Ticker'] = df['Company Name'].apply(lambda x: map_ticker(x))

    # Convert Date to Quarter
    df['Quarter'] = pd.PeriodIndex(pd.to_datetime(df['Date']), freq='Q')
    print("Done...!")
    return df[['Ticker', 'Quarter', 'Tokens', 'Company Name', 'File Name', 'Date']]


def preprocess_snp_files() -> pd.DataFrame:
    """
    Wrapper function to process SNP files. uses get_files() and returns a dataframe of the relevant SGX information
    """
    print("Extracting & Preprocessing SNP500 Annual / Quarterly Reports...")
    df = get_files(snp_directory)

    # Extract Ticker & Date
    df['Ticker'] = df['File Name'].apply(lambda x: x.split(' ')[0])
    df['Date'] = df['File Name'].apply(lambda x: x.split(' ')[1][:-4])

    # Map Company Name
    company_names = pd.read_csv('../data/Company Mappings/snp_mapping.csv')
    company_names_dict = {}
    for i, j in company_names.iterrows():
        company_names_dict[j['Symbol']] = j['Name']
    df['Company Name'] = df['Ticker'].apply(lambda x: company_names_dict[x])

    # Convert Date to Quarter
    df['Quarter'] = pd.PeriodIndex(pd.to_datetime(df['Date']), freq='Q')
    print("Done...!")
    return df[['Ticker', 'Quarter', 'Tokens', 'Company Name', 'File Name', 'Date']]


def preprocess_sgx_annual_files() -> pd.DataFrame:
    """
        Wrapper function to process SGX files. uses get_files() and returns a dataframe of the relevant SGX information
        """
    print("Extracting & Preprocessing SGX Annual Reports...")
    df = get_sgx_ann_files(sgx_annual_directory)
    sgx_ann_map = pd.read_excel('SGX mapping.xlsx')
    merged_df = df.merge(sgx_ann_map, how='left', left_on='Company', right_on='Company')

    # Extract Ticker & Date
    merged_df['Date'] = pd.to_datetime(merged_df['Year'])
    merged_df.rename(columns={"Filename": "FileName"}, inplace=True)
    # Convert Date to Quarter
    merged_df['Quarter'] = pd.PeriodIndex(pd.to_datetime(merged_df['Date']), freq='Q')
    print("Done...!")
    return merged_df[['Ticker', 'Quarter', 'Tokens', 'Company Name', 'FileName', 'Date']]
