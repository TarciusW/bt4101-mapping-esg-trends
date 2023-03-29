import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer
from collections import Counter
from tqdm import tqdm
import pymannkendall as mk
import numpy as np
from bs4 import BeautifulSoup
import requests
import random


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


def split_esg_df(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """ takes in a whole market dataframe and returns 3 dataframes split by E, S and G scores
    to be put into mann-kendall test"""
    e_df = df[['Ticker', 'Quarter', 'Company Name', 'E %']].copy()
    s_df = df[['Ticker', 'Quarter', 'Company Name', 'S %']].copy()
    g_df = df[['Ticker', 'Quarter', 'Company Name', 'G %']].copy()
    return e_df, s_df, g_df


def mann_kendall_test(df: pd.DataFrame, type: str) -> pd.DataFrame:
    """takes in the specific E, S or G DF and runs the mann-kendall test on the dataframe"""
    df_list = df.groupby(['Company Name', 'Quarter']).sum()[f"{type} %"].groupby('Company Name').apply(
        list).reset_index()
    df_list['Result'] = df_list[f"{type} %"].apply(lambda x: mk.original_test(x, alpha=0.1).h)
    df_list['Strength'] = df_list[f"{type} %"].apply(lambda x: mk.original_test(x, alpha=0.1).s)
    return df_list


def extract_companies_with_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    input: Whole market data with specific E / S / G scores (choose 1)
    uses pymankendall to test for the presence of a trend for scores over time for E, S & G scores, only keeps companies
    with significant trend
    """
    # extract companies with at least 4 data points, as required by mann-kendall test
    df = extract_substantial_companies(df, 5)
    df.copy().sort_values(by=['Company Name', 'Quarter'], inplace=True)
    e_df, s_df, g_df = split_esg_df(df)
    e_df = mann_kendall_test(e_df, "E")
    e_df.rename(columns={"Result": "E_Trend", "Strength": "E_Strength"}, inplace=True)
    s_df = mann_kendall_test(s_df, "S")
    s_df.rename(columns={"Result": "S_Trend", "Strength": "S_Strength"}, inplace=True)
    g_df = mann_kendall_test(g_df, "G")
    g_df.rename(columns={"Result": "G_Trend", "Strength": "G_Strength"}, inplace=True)
    df = df.merge(e_df[['Company Name', 'E_Trend', 'E_Strength']], on='Company Name', how='inner')
    df = df.merge(s_df[['Company Name', 'S_Trend', 'S_Strength']], on='Company Name', how='inner')
    df = df.merge(g_df[['Company Name', 'G_Trend', 'G_Strength']], on='Company Name', how='inner')
    return df


def normalize_trend_strength(trends):
    series_mean = np.mean(trends)
    series_sd = np.std(trends)
    normalized_numbers = [(x - series_mean) / series_sd for x in trends]
    return normalized_numbers


def scrape_company_descriptions(df: pd.DataFrame, market: str) -> pd.DataFrame:
    ticker_descriptions = pd.DataFrame()
    failed_tickers = []
    unique_tickers = df['Ticker'].unique()
    for ticker in tqdm(unique_tickers):
        try:
            user_agents_list = [
                'Mozilla/5.0 (iPad; CPU OS 12_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.83 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
            ]
            if market == 'sg':
                page = requests.get('https://sg.finance.yahoo.com/quote/' + ticker + '.SI/profile',
                                    headers={'User-Agent': random.choice(user_agents_list)})
            else:
                page = requests.get('https://sg.finance.yahoo.com/quote/' + ticker + '/profile',
                                    headers={'User-Agent': random.choice(user_agents_list)})
            soup = BeautifulSoup(page.content, 'html.parser')
            desc = soup.find('section', attrs={'class': 'quote-sub-section Mt(30px)'}).contents[1].text
            sentences = desc.split('. ')
            first_three_sentences = '. '.join(sentences[:3]) + '.'
            ticker_descriptions = pd.concat(
                [ticker_descriptions, pd.DataFrame({"Ticker": [ticker], "Description": [first_three_sentences]})])
        except:
            failed_tickers.append(ticker)
    ticker_descriptions.reset_index(drop=True, inplace=True)
    df = df.merge(ticker_descriptions, how='left', on='Ticker').fillna('No Description Found')
    return df
