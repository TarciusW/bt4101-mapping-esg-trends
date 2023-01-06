import pandas as pd
import os
import string
import regex
import nltk
from tqdm import tqdm
from nltk.stem import WordNetLemmatizer
from string import digits
import pickle

sgx_directory = '../data/SGX'
snp_directory = '../data/SNP500'


def get_files(path: str) -> pd.DataFrame:
    df = pd.DataFrame()
    for filename in tqdm(os.listdir(path)):
        f = os.path.join(path, filename)
        # checking if it is a file
        if os.path.isfile(f):
            if 'DS_Store' in f or 'gitignore' in f:
                continue
            # read each file and concat them into a dataframe
            file = open(f, "r", encoding="utf8").read()

            file = preprocess_text(file)

            df = pd.concat([df, pd.DataFrame({'File Name': [filename], 'Tokens': [file]})])
    return df


def preprocess_text(text: str) -> str:
    """ preprocessing pipeline for text files to have it ready for modelling. takes in the raw text file as input
     and returns the list of tokens for modelling

     Step 1: Remove punctuations from text
     Step 2: Make all text lowercase using string.lower() inbuilt function
     Step 3: remove all stopwords (words that have no meaning) from tokens
     Step 4: lemmatize words to their base form
     Step 5: Remove numbers from tokens
     Step 6: Remove empty tokens
     """

    # remove punctuations and newline characters
    def remove_punctuation(text):
        punctuationFree = "".join([i for i in text if i not in string.punctuation])
        punctuationFree = regex.sub(r'\n', '', punctuationFree)
        return punctuationFree

    def tokenization(text):
        tokens = regex.split(r"\s+", text)
        return tokens

    def remove_stopwords(text):
        output = [i for i in text if i not in nltk.corpus.stopwords.words('english')]
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
    text = remove_stopwords(text)
    text = lemmatizer(text)
    text = remove_numbers(text)
    text = remove_empty_elements(text)
    return text


def preprocess_sgx_files() -> pd.DataFrame:
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
        try:
            return company_names_dict[name].split('SGX:')[1][:-1]
        except KeyError:
            return 'Not Available'

    df['Ticker'] = df['Company Name'].apply(lambda x: map_ticker(x))

    # Convert Date to Quarter
    df['Quarter'] = pd.PeriodIndex(pd.to_datetime(df['Date']), freq='Q')
    print("Done...!")
    return df[['Ticker', 'Quarter', 'Token', 'Company Name', 'File Name', 'Date']]


def preprocess_snp_files() -> pd.DataFrame:
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
    return df[['Ticker', 'Quarter', 'Token', 'Company Name', 'File Name', 'Date']]


def get_esg_wordlist() -> pd.DataFrame:
    return pd.read_excel('../data/ESG Word List/BaierBerningerKiesel_ESG-Wordlist_2020_July22.xlsx',
                         sheet_name='ESG-Wordlist')
