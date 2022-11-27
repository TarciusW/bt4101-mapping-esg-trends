import pandas as pd
import os

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
            df = pd.concat([df, pd.DataFrame({'File Name': [filename], 'Text': [file]})])
    return df


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
