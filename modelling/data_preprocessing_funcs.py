import pandas as pd
import os

directory = '..\data\SGX'


def get_sgx_files():
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

    return df
