from data_preprocessing_funcs import *
from modelling_funcs import *


# Importing & Preprocessing Data and saving it to pickle files (Dataframe with tokens)
#sgx = preprocess_sgx_files()
#sgx.to_pickle('sgx.pkl')
"""
snp = preprocess_snp_files()
snp.to_pickle(snp.pkl)
"""

sgx = pd.read_pickle('sgx.pkl')
model_tokens_BOW(sgx)

## ESG Word List
#esg_dict = get_esg_wordlist()

print("")
