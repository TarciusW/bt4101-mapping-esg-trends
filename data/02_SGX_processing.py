import pandas as pd
import os

directory = '.\SGX'

df = pd.DataFrame()
# iterate over files in
# that directory
for filename in os.listdir(directory):
    f = os.path.join(directory, filename)
    # checking if it is a file
    if os.path.isfile(f):
        if 'DS_Store' in f or 'gitignore' in f:
            continue
        file = open(f, "r",encoding="utf8").read()
        df = pd.concat([df,pd.DataFrame({'File Name':[filename],'Text':[file]})])
df['Company Name'] = (df['File Name'].apply(lambda x: x.split(' (')))
df['Company Name'] = df['Company Name'].apply(lambda x: x[0])
df['Date'] = (df['File Name'].apply(lambda x: x.split(' ('))).apply(lambda x: x[1][0:7])


print("")