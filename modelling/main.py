from data_preprocessing_funcs import *
from modelling_funcs import *
import matplotlib.pyplot as plt

# Importing & Preprocessing Data and saving it to pickle files (Dataframe with tokens)
# sgx = preprocess_sgx_files()
# sgx.to_pickle('sgx.pkl')
"""
snp = preprocess_snp_files()
snp.to_pickle(snp.pkl)
"""

"""
#Modelling quantitative Trends
sgx = pd.read_pickle('sgx.pkl')
sgx_quant = model_tokens_BOW(sgx)
sgx_quant.to_pickle('sgx_quant.pkl')
"""

# Export Results of Trends
sgx_quant = pd.read_pickle('sgx_quant.pkl')
sgx_quant.drop(columns=['Tokens']).to_csv('sgx_quant_results.csv')
print("")
