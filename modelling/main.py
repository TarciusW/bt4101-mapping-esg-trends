import pandas as pd
from data_preprocessing_funcs import *
from modelling_funcs import *
from ESGBERT import *
import swifter
from tqdm import tqdm
import numpy as np

# Importing & Preprocessing Data and saving it to pickle files (Dataframe with tokens)
# sgx = preprocess_sgx_files()
# sgx.to_pickle('sgx.pkl')

#snp = preprocess_snp_files()
#snp.to_pickle('snp.pkl')

sgx_ann = preprocess_sgx_annual_files()
sgx_ann.to_pickle('sgx_ann.pkl')

"""
# Modelling quantitative Trends
sgx = pd.read_pickle('sgx.pkl')
sgx_quant = model_tokens_BOW(sgx)
sgx_quant.to_pickle('sgx_quant.pkl')
"""

#snp = pd.read_pickle('snp.pkl')
#snp_quant = model_tokens_BOW(snp)
#snp_quant.to_pickle('snp_quant.pkl')

""" SNP TOKEN REDUCING """
"""
snp_quant = pd.read_pickle('snp_quant.pkl')
snp_quant = snp_quant[6000:6800]
snp_quant = tag_report_type(snp_quant)
snp_quant = reduce_snp_tokens(snp_quant)
snp_quant['Sentences'] = snp_quant['Tokens_ESGB'].apply(lambda x: join_sentences(x))
tqdm.pandas(total=len(snp_quant))
snp_bert = snp_quant['Sentences'].progress_apply(lambda x: ESGBERT_clf(x))
snp_bert = pd.concat(snp_bert.tolist()).reset_index().drop(columns=['index'])
snp_quant_bert = snp_quant.join(snp_bert)
snp_quant_bert.to_pickle('snp_quant_bert_6000_6800.pkl')
"""

# Export Results of Trends

# sgx_quant_1 = pd.read_pickle('sgx_quant_bert_0_700.pkl')
# sgx_quant_2 = pd.read_pickle('sgx_quant_bert_700.pkl')
# sgx_quant = pd.concat([sgx_quant_1, sgx_quant_2])

"""
sgx_quant = pd.read_pickle('sgx_quant.pkl')
sgx_quant_processed = extract_companies_with_trend(sgx_quant)
sgx_quant_processed.to_excel('sgx_quant_results.xlsx')
# ARA Trust Management has 5 files, 1 of it has (Cache) in the file name so doesn't count. manually remove.
# sgx_quant_processed = sgx_quant_processed[sgx_quant_processed['Company Name'] != 'ARA TRUST MANAGEMENT']
# sgx_quant_processed.to_excel('sgx_quant_results.xlsx')
"""

# Export Results of Trends
#
# snp_quant_results = extract_substantial_companies(snp_quant, 5)
# snp_quant_results.to_excel('snp_quant_results.xlsx')
# snp_quant_processed = extract_companies_with_trend(snp_quant)

print("")

""" ESGBERT """
"""
sgx_quant = pd.read_pickle('sgx_quant.pkl')

sgx_quant['Sentences'] = sgx_quant['Tokens'].apply(lambda x: join_sentences(x))
sgx_quant = sgx_quant.drop([253, 707, 709, 738, 781, 1028])
sgx_quant = sgx_quant[700:]
tqdm.pandas(total=len(sgx_quant))
sgx_bert = sgx_quant['Sentences'].progress_apply(lambda x: ESGBERT_clf(x))
sgx_bert = pd.concat(sgx_bert.tolist()).reset_index().drop(columns=['index'])
sgx_quant_bert = sgx_quant.join(sgx_bert)
sgx_quant_bert.to_pickle('sgx_quant_bert_700.pkl')
"""
""" END ESGBERT """
