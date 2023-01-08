import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer


def model_tokens_BOW(df: pd.DataFrame) -> pd.DataFrame:
    """
    Takes in a df with the tokens and text files and runs the BOW model
    """
    df.reset_index(inplace=True)
    df.drop(columns='index',inplace=True)
    vectorizer = CountVectorizer()
    results_df = vectorizer.fit_transform(df['Tokens'].apply(lambda x: ' '.join(x)))
    test_df = pd.DataFrame(results_df.toarray(), columns=vectorizer.get_feature_names_out())

    result = pd.DataFrame()
    for index, row in test_df.iterrows():
        row = row.reset_index()
        row.rename(columns={'index': 'Word'}, inplace=True)
        esg_dict = get_esg_wordlist()
        esg_dict = esg_dict[['Word', 'Topic']].merge(row, how='left', on='Word').fillna(0)
        # Topic Score
        topic_score = esg_dict.groupby('Topic').sum(numeric_only = True)
        result = pd.concat([result, topic_score.transpose()])
        # Category Score (to-do)
        # category_score = esg_dict[['Topic', 'Category',0]].groupby(['Topic', 'Category']).sum()
        print("")
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
