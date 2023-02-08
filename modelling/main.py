import pandas as pd

from data_preprocessing_funcs import *
from modelling_funcs import *

# Importing & Preprocessing Data and saving it to pickle files (Dataframe with tokens)
# sgx = preprocess_sgx_files()
# sgx.to_pickle('sgx.pkl')

# snp = preprocess_snp_files()
# snp.to_pickle('snp.pkl')

"""
#Modelling quantitative Trends
sgx = pd.read_pickle('sgx.pkl')
sgx_quant = model_tokens_BOW(sgx)
sgx_quant.to_pickle('sgx_quant.pkl')
"""

"""
snp = pd.read_pickle('snp.pkl')
snp_quant = model_tokens_BOW(snp)
snp_quant.to_pickle('snp_quant.pkl')
"""

"""
sgx_quant = pd.read_pickle('sgx_quant.pkl')
sgx_quant_processed = extract_companies_with_trend(sgx_quant)
#
"""

# Export Results of Trends
"""
sgx_quant = pd.read_pickle('sgx_quant.pkl')
sgx_quant_processed = extract_substantial_companies(sgx_quant, 5)
# ARA Trust Management has 5 files, 1 of it has (Cache) in the file name so doesnt count. manually remove.
sgx_quant_processed = sgx_quant_processed[sgx_quant_processed['Company Name'] != 'ARA TRUST MANAGEMENT']
sgx_quant_processed.to_excel('sgx_quant_results.xlsx')
"""


# Export Results of Trends
snp_quant = pd.read_pickle('snp_quant.pkl')
snp_quant_results = extract_substantial_companies(snp_quant, 5)
snp_quant_results.to_excel('snp_quant_results.xlsx')
snp_quant_processed = extract_companies_with_trend(snp_quant)

print("")
