import pandas as pd
import numpy as np
import chardet

# gathering CSV files in list
file_paths = [
    "data/file1.csv",
    "data/file2.csv",
    'data/file3.csv',
    'data/file4.csv'
]

# checking CSV file encoding
with open(file_paths[0], 'rb') as f:
    result = chardet.detect(f.read())

# joining all CSV into one dataframe
df_all = pd.DataFrame()

for path in file_paths:

    df_temp = pd.read_csv(path, encoding=result['encoding'])
    df_all = pd.concat([df_all, df_temp])

# adding additional columns and casting transaction_timestamp_gmt column to timestamp
df_all['transaction_type'] = np.where(df_all['transaction_amount']>=0, 'purchase', 'refund')
df_all['is_valid'] = np.where(df_all['status_code']!=4, True, False)
df_all['transaction_timestamp_gmt'] = pd.to_datetime(df_all['transaction_timestamp_gmt'])

# unfilter below line to exclude not valid transactions
df_all = df_all[df_all['is_valid']==True]

# Q1 How many transactions were carried out by a person named Lucia?

df_q1 = df_all[df_all['card_full_details'].str.contains('Lucia ')==1]
# used 'Lucia ' as 'Lucia' was returning also Luciana's

print(f'Q1: {len(df_q1)} transactions were carried out by a person named Lucia')

# Q2 How many transactions were carried out on 3rd January 2024?

df_q2 = df_all[df_all['transaction_timestamp_gmt'].dt.strftime('%Y-%m-%d')=='2024-01-03']

print(f'Q2: {len(df_q2)} transactions were carried out on 3rd January 2024')

# Q3 How many refunds were carried out on 4th January 2024?

df_q3 = df_all[(df_all['transaction_timestamp_gmt'].dt.strftime('%Y-%m-%d')=='2024-01-04')
                & (df_all['transaction_type']=='refund')]

print(f'Q3: {len(df_q3)} refunds were carried out on 4th January 2024')

# Q4 Which credit card had the most transactions?

df_q4 = df_all.copy()
# adding card issuer and card number columns
df_q4['card_issuer'] = df_q4['card_full_details'].apply(lambda x: x.split(' ')).str[0]
df_q4['card_info'] = df_q4['card_full_details'].apply(lambda x: x.split('\\n')).str[2]
df_q4['card_number'] = df_q4['card_info'].apply(lambda x: x.split(' ')).str[0]

# below code could be used if number of unique card numbers != number of all rows
# df_q4 = df_q4[['card_number', 'transaction_identifier']]\
#             .groupby('card_number').count().reset_index()
# df_q4.rename(columns={'transaction_identifier':'trans_count'}, inplace=True)
# df_q4 = df_q4.sort_values(by='trans_count', ascending=False)

print(f"""
    Q4:
    All rows in dataset: {len(df_all)}
    Unique credit card numbers: {len(df_q4['card_number'].unique())}
    Unique card issuers: {len(df_q4['card_issuer'].unique())}
    Every card had one transaction so there is no single card with the most transactions
    """)
