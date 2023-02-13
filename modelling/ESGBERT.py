import pandas as pd
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from modelling_funcs import *
import torch
from tqdm import tqdm

sgx_quant = pd.read_pickle('sgx_quant.pkl')
sgx_quant['Sentences'] = sgx_quant['Tokens'].apply(
    lambda y: [' '.join(x) for x in
               zip(y[0::9], y[1::9], y[2::9], y[3::9], y[4::9], y[5::9], y[6::9], y[7::9], y[8::9])])


def ESGBERT_clf(text_list: list) -> pd.DataFrame:
    tokenizer = AutoTokenizer.from_pretrained("nbroad/ESG-BERT", use_fast=True)
    model = AutoModelForSequenceClassification.from_pretrained("nbroad/ESG-BERT")

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
        if float(result_loss) < 6:
            result_mapped = "NIL"
        return [result, result_loss, result_mapped]

    result_df = pd.DataFrame()
    for i in tqdm(text_list, total=len(text_list)):
        result_df = pd.concat([result_df, pd.DataFrame(pd.Series(ESGBERT(i, model, tokenizer))).transpose()])
    result_df.rename(columns={0: 'Label', 1: "Score", 2: 'ESG'}, inplace=True)
    percentage_df = pd.DataFrame(result_df['ESG'].value_counts().astype(int)).transpose()
    percentage_df['Total'] = percentage_df.sum(axis=1)
    final_df = pd.DataFrame()
    final_df['E % BERT'] = percentage_df['E'] / percentage_df['Total'] * 100
    final_df['S % BERT'] = percentage_df['S'] / percentage_df['Total'] * 100
    final_df['G % BERT'] = percentage_df['G'] / percentage_df['Total'] * 100
    return result_df


ESGBERT_clf(sgx_quant['Sentences'][0])

"""
num_labels = len(model.config.id2label)
labels = torch.tensor([1])
loss = model(**inputs, labels=labels).loss
"""

"""
sgx_quant_processed['String'] = sgx_quant_processed['Tokens'].apply(lambda x: ' '.join(x))
sgx_quant_processed['BERT_Tokens'] = sgx_quant_processed['String'].apply(lambda x: tokenizer(x))
"""

print("")
