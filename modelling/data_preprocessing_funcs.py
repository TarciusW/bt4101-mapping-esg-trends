import pandas as pd
import os
import string
import regex
import nltk
from nltk.stem import WordNetLemmatizer

sgx_directory = '../data/SGX'
snp_directory = '../data/SNP500'


def get_files(path):
    df = pd.DataFrame()
    for filename in os.listdir(path):
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
     Step 5: Remove numbers from tokens"""

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
        result = []
        for i in text:
            try:
                int(i)
            except:
                result.append(i)
            else:
                continue
        return result

    text = remove_punctuation(text)
    text = text.lower()
    text = tokenization(text)
    text = remove_stopwords(text)
    text = lemmatizer(text)
    text = remove_numbers(text)
    return text


def get_sgx_files():
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
    return df[['Ticker', 'Quarter', 'Text', 'Company Name', 'File Name', 'Date']]


def get_snp_files():
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
    return df[['Ticker', 'Quarter', 'Text', 'Company Name', 'File Name', 'Date']]


def get_esg_wordlist():
    return pd.read_excel('../data/ESG Word List/BaierBerningerKiesel_ESG-Wordlist_2020_July22.xlsx',
                         sheet_name='ESG-Wordlist')
