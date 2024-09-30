import os
import pandas as pd
from drop_function import drop_columns
from sklearn.model_selection import train_test_split

directory = r"C:\Users\Dell\meme_RACAI\split_data"

if not os.path.exists('sent1_split'):
    os.makedirs('sent1_split')

if not os.path.exists('sent2_split'):
    os.makedirs('sent2_split')


def store_data(folder, file, content, drop_list):
    df = drop_columns(content, drop_list)
    df.to_csv(os.path.join(folder, file), index=True)


# for name in os.listdir(directory):
#     # Open file
#     with open(os.path.join(directory, name)) as f:
#         print(f"Content of '{name}'")
#         df = pd.read_csv(f)
#         store_data('sent1_split', name, df, ['Sentiment2', 'lex_prediction2', 'confidence2'])
#         store_data('sent2_split', name, df,  ['Sentiment1', 'lex_prediction1', 'confidence1'])


# df.to_csv('feature_df.csv', index=True)
df = pd.read_csv('feature_df.csv')

train_df, temp_df = train_test_split(df, test_size=0.3, random_state=42)
dev_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

names = ['dev_df.csv', 'test_df.csv', 'train_df.csv']
dataframes = [dev_df, test_df, train_df]
for i in range(0, 3):
    name = names[i]
    df = dataframes[i]
    store_data('sent1_split', name, df, ['Sentiment2', 'lex_prediction2', 'confidence2'])
    store_data('sent2_split', name, df, ['Sentiment1', 'lex_prediction1', 'confidence1'])

