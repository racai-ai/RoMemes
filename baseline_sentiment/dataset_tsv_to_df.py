import pandas as pd
import os

df = pd.read_csv("metadata.tsv", sep='\t', header=0)
# print(df.to_string())
# df.drop(['Source', 'URL', 'Image'], axis=1, inplace=True)
folder_path = 'path_to_your_folder/text'
text_list = []
for i in df['ID']:
    file_name = "00"+str(i)
    file_path = "text/" + file_name + ".txt"
    if os.path.isfile(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            text_list.append(content)
# df['text'] = text_list
print(text_list[0])

df.insert(df.columns.get_loc('ID') + 1, 'Text', text_list)
print(df.to_string())
df.to_csv('romemes.csv', index=True)