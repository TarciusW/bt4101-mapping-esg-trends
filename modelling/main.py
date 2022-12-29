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

test = sgx[sgx['Ticker'] == '5TG']
text = test['Text'].to_string()


def remove_punctuation(text):
    punctuationfree = "".join([i for i in text if i not in string.punctuation])
    return punctuationfree

text = remove_punctuation(text)


print("")
