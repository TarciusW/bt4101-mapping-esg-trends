import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from modelling_funcs import *
import torch
from datetime import datetime


def join_sentences(token_list):
    # Create an empty list to store the combined strings
    combined_strings = []

    # Loop through the input list, starting at the 10th index and ending 10 indexes before the end
    for i in range(0, len(token_list) - 10, 5):
        # Combine the previous 10 and next 10 elements of the input list, separated by a space
        # and append the result to the combined_strings list
        combined_strings.append(" ".join(token_list[i:i + 10]))

    # Return the list of combined strings
    return combined_strings


def tag_report_type(df):
    tickers = df['Ticker'].unique()
    final_df = pd.DataFrame()
    for i in tickers:
        ticker_df = df[df['Ticker'] == i].copy()
        # ticker_df['Date'] = ticker_df['Date'].apply(lambda x: datetime.strptime(x, '%Y-%m-%d').date())
        # report_stats = ticker_df['Total'].describe()
        ticker_df['Report Type'] = ticker_df['Total'].apply(
            lambda x: 'Annual' if x > ticker_df['Total'].describe()['75%'] else 'Quarterly')
        final_df = pd.concat([final_df, ticker_df])
    return final_df


def reduce_snp_tokens(df):
    # need to find out which companies report before year end which companies report annual after year end
    df.loc[:, 'Tokens_ESGB'] = None
    for index, row in df.iterrows():
        text = df.loc[index, 'Tokens']
        try:
            # Annual Reports, need to take item 1 to 7
            # first, find all "business" for start index
            item_1_business_indexes = [i for i, j in enumerate(text) if 'business' in j]
            # next, check if token before is '1' and token after is 'overview'
            start_index = [i for i in item_1_business_indexes if 'item' in text[i - 1] or 'item' in text[i]]
            item_7A_qualitative_indexes = [i for i, j in enumerate(text) if 'qualitative' in j]
            end_index = [i for i in item_7A_qualitative_indexes if
                         'disclosure' in text[i + 1] or 'disclosure' in text[i]]
            if start_index[0] > 5000 or end_index[-1] < 5000:
                raise Exception
            text = text[start_index[0]:end_index[-1]]
            df.loc[:, 'Tokens_ESGB'].loc[index] = text
        except:
            try:
                # quarterly reports, need to take item 2 until item 6
                item_2_mdna = [i for i, j in enumerate(text) if 'discussion' in j]
                start_index = [i for i in item_2_mdna if 'analysis' in text[i + 1]]
                # item_6_exhibit = [i for i, j in enumerate(text) if 'exhibit' in j]
                # end_index = [i for i in item_6_exhibit if 'item' in text[i - 1]]
                text = text[start_index[1]:]
                df.loc[:, 'Tokens_ESGB'].loc[index] = text
            except:
                print(f"Dropping row {index} because failed to reduce tokens...")
                df.drop(index, inplace=True)
    return df


def ESGBERT(text_list, model, tokenizer):
    result_df = pd.DataFrame()
    esg_labels_map = {
        'Business_Ethics': "G",
        'Data_Security': "G",
        'Access_And_Affordability': "S",
        'Business_Model_Resilience': "G",
        'Competitive_Behavior': "G",
        'Critical_Incident_Risk_Management': "G",
        'Customer_Welfare': "S",
        'Director_Removal': "G",
        'Employee_Engagement_Inclusion_And_Diversity': "S",
        'Employee_Health_And_Safety': "S",
        'Human_Rights_And_Community_Relations': "S",
        'Labor_Practices': "S",
        'Management_Of_Legal_And_Regulatory_Framework': "G",
        'Physical_Impacts_Of_Climate_Change': "E",
        'Product_Quality_And_Safety': "S",
        'Product_Design_And_Lifecycle_Management': "G",
        'Selling_Practices_And_Product_Labeling': "G",
        'Supply_Chain_Management': "G",
        'Systemic_Risk_Management': "G",
        'Waste_And_Hazardous_Materials_Management': "E",
        'Water_And_Wastewater_Management': "E",
        'Air_Quality': "E",
        'Customer_Privacy': "S",
        'Ecological_Impacts': "E",
        'Energy_Management': "E",
        'GHG_Emissions': "E"
    }
    for sentence in text_list:
        inputs = tokenizer(sentence, return_tensors='pt')
        with torch.no_grad():
            logits = model(**inputs).logits
        result = model.config.id2label[logits.argmax().item()]
        result_loss = logits.max().item()
        result_mapped = esg_labels_map[result]
        result_df = pd.concat([result_df, pd.DataFrame(
            {"sentence": [sentence], "result": [result], "result loss": [result_loss],
             "result mapped": [result_mapped]})])
    return result_df


def ESGBERT_clf(df: pd.DataFrame) -> pd.DataFrame:
    tokenizer = AutoTokenizer.from_pretrained("nbroad/ESG-BERT", use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained("nbroad/ESG-BERT")
    final_df = pd.DataFrame()
    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        result_df = ESGBERT(row['sentences'], model, tokenizer)
        result_df['Company Name'] = row['Company Name']
        result_df['Date'] = row['Date']
        result_df['Data Source'] = row['Data Source']
        final_df = pd.concat([final_df, result_df])
    return final_df.reset_index().drop(columns=['index'])
