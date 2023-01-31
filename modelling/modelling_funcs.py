import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from tqdm import tqdm


def model_tokens_BOW(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes in a df with the tokens and text files and runs the BOW model
    """
    df.reset_index(inplace=True)
    df.drop(columns='index', inplace=True)
    vectorizer = CountVectorizer()
    results_df = vectorizer.fit_transform(df['Tokens'].apply(lambda x: ' '.join(x)))
    test_df = pd.DataFrame(results_df.toarray(), columns=vectorizer.get_feature_names_out())
    esg_dict = get_esg_wordlist()
    result = pd.DataFrame()
    for index, row in tqdm(test_df.iterrows(), total=test_df.shape[0]):
        row = row.reset_index()
        row.rename(columns={'index': 'Word'}, inplace=True)
        #esg_dict = get_esg_wordlist()
        esg_dict_row = esg_dict[['Word', 'Topic']].merge(row, how='left', on='Word').fillna(0)
        # Topic Score
        topic_score = esg_dict_row.groupby('Topic').sum(numeric_only=True)
        result = pd.concat([result, topic_score.transpose()])
        # Category Score (to-do)
        # category_score = esg_dict[['Topic', 'Category',0]].groupby(['Topic', 'Category']).sum()
    df = df.join(result)
    df['Total'] = df['Tokens'].apply(lambda x: len(x))
    df['E %'] = df['Environmental'] * 100 / df['Total']
    df['S %'] = df['Social'] * 100 / df['Total']
    df['G %'] = df['Governance'] * 100 / df['Total']
    return df


def get_esg_wordlist() -> pd.DataFrame:
    """
    loads the ESG word list to be used in this project.
    """
    return pd.read_excel('../data/ESG Word List/BaierBerningerKiesel_ESG-Wordlist_2020_July22.xlsx',
                         sheet_name='ESG-Wordlist')


def extract_substantial_companies(df: pd.DataFrame, n_periods: int) -> pd.DataFrame:
    """takes in a dataframe of the sgx sustainability reports and only keeps companies with at least n data points to
    look for trends"""
    company_names = df['Company Name'].tolist()
    company_names = Counter(company_names)
    substantial_names = list({x: count for x, count in company_names.items() if count >= n_periods}.keys())
    substantial_companies_df = df[df['Company Name'].isin(substantial_names)]
    return substantial_companies_df
