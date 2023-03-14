import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from modelling_funcs import *
import torch
from datetime import datetime


def join_sentences(list):
    # Create an empty list to store the combined strings
    combined_strings = []

    # Loop through the input list, starting at the 10th index and ending 10 indexes before the end
    for i in range(10, len(list) - 10, 10):
        # Combine the previous 10 and next 10 elements of the input list, separated by a space
        # and append the result to the combined_strings list
        combined_strings.append(" ".join(list[i - 10:i + 10]))

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


def ESGBERT_clf(text_list: list) -> pd.DataFrame:
    tokenizer = AutoTokenizer.from_pretrained("nbroad/ESG-BERT", use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained("nbroad/ESG-BERT")

    #tokenizer = AutoTokenizer.from_pretrained("ppsingh/esg-bert-sector-classifier")
    #model = AutoModelForSequenceClassification.from_pretrained("ppsingh/esg-bert-sector-classifier")

    def ESGBERT(text, model, tokenizer):
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
        inputs = tokenizer(text, return_tensors='pt')
        with torch.no_grad():
            logits = model(**inputs).logits
        result = model.config.id2label[logits.argmax().item()]
        result_loss = logits.max().item()
        result_mapped = esg_labels_map[result]
        # if (result_mapped == 'G' and float(result_loss) < 3) or (result_mapped == 'S' and float(result_loss) < 1):
        # result_mapped = "NIL"
        return [result, result_loss, result_mapped]

    final_df = pd.DataFrame()
    result_df = pd.DataFrame()
    for item in text_list:
        interim_df = pd.DataFrame(list(map(ESGBERT, item, [model], [tokenizer])))
        interim_df.rename(columns={0: 'Label', 1: "Score", 2: 'ESG'}, inplace=True)
        result_df = pd.concat([result_df, interim_df])
    percentage_df = pd.DataFrame(columns=["E", "S", "G"])
    percentage_df = pd.concat(
        [percentage_df, pd.DataFrame(result_df['ESG'].value_counts().astype(int)).transpose()]).fillna(0)
    percentage_df['Total'] = percentage_df.sum(axis=1)
    final_df['E % BERT'] = percentage_df['E'] / percentage_df['Total'] * 100
    final_df['S % BERT'] = percentage_df['S'] / percentage_df['Total'] * 100
    final_df['G % BERT'] = percentage_df['G'] / percentage_df['Total'] * 100
    final_df['E BERT'] = percentage_df['E']
    final_df['S BERT'] = percentage_df['S']
    final_df['G BERT'] = percentage_df['G']
    final_df['Total BERT'] = percentage_df['Total']
    return final_df.reset_index().drop(columns=['index'])
