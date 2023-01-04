from data_preprocessing_funcs import *
import nltk
import regex
import string

# Importing & Preprocessing Data
## Text Data
sgx = get_sgx_files()
snp = get_snp_files()

## ESG Word List
esg_dict = get_esg_wordlist()


print("")
