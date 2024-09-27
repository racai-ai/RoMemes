import argparse
import spacy
from nltk.stem import WordNetLemmatizer
from base_sentiment_analysis.translate_function import translate
import os
import json
from collections import Counter
from sklearn.preprocessing import MultiLabelBinarizer
import pandas as pd
from drop_functions import drop_columns
from sklearn.model_selection import train_test_split


# Load data
df = pd.read_csv("romemes.csv")
df.drop(['Unnamed: 0', 'ID', 'Extension', 'Width', 'Height', 'Channels', 'Mime',
         'ImageFileSize', 'TextSizeChar', 'TextSizeBytes'], axis=1, inplace=True)
sentiment2_english = ['anger', 'fear', 'joy', 'love', 'sadness', 'surprise']

nlp = spacy.load("en_core_web_sm")
lemmatizer = WordNetLemmatizer()

with open('en_lex.json', 'r') as file:
    data_dict = json.load(file)


def most_common_emotion(lst):
    """
    :param lst:
    :return: most common emotion
    """
    if not lst:
        return None
    counter = Counter(lst)
    most_common = counter.most_common(1)
    return most_common[0][0]


def create_features_en(text_list):
    """
        Create features from translated memes and returns them as lists.
        :return feature_lists = {
            'len_values': [...],
            'period_ratio': [...],
            'question_ratio': [...],
            'exclamation_ratio': [...],
            'ellipses_ratio': [...],
            'lex_prediction1': [...],
            'confidence1': [...],
            'lex_prediction2': [...],
            'confidence2': [...],
        }
        """
    print("Generating features...")

    def lemmatize(text):
        text = nlp(text)
        lemma_list = [token.lemma_ for token in text]
        return lemma_list

    punct_list = ['.', '?', '!', '..', '...', '....', '.....']

    feature_lists = {
        'len_values': [],
        'period_ratio': [],
        'question_ratio': [],
        'exclamation_ratio': [],
        'ellipses_ratio': [],
        'lex_prediction1': [],
        'confidence1': [],
        'lex_prediction2': [],
        'confidence2': [],
    }

    for text in text_list:
        lemmas = lemmatize(text)
        feature_lists['len_values'].append(len(lemmas))
        punctuation = {
            'period': 0.0,
            'question': 0.0,
            'exclamation': 0.0,
            'ellipses': 0.0,
        }
        sentiment1 = {
            'positive': 0.0,
            'negative': 0.0,
        }
        sentiment2 = {
            'anger': 0.0,
            'trust': 0.0,
            'fear': 0.0,
            'joy': 0.0,
            'sadness': 0.0,
            'surprise': 0.0,
        }

        for item in lemmas:
            if item in data_dict:  # if item in lexicon
                for key in sentiment1:
                    sentiment1[key] += data_dict[item][key]
                for key in sentiment2:
                    sentiment2[key] += data_dict[item][key]
            else:
                if item in punct_list:

                    punctuation_map = {
                        '.': 'period',
                        '?': 'question',
                        '!': 'exclamation'
                    }

                    if item in punctuation_map:
                        punctuation[punctuation_map[item]] += 1
                    elif item in {'..', '...', '....', '.....'}:
                        punctuation['ellipses'] += 1

        total_punctuation = (sum(punctuation[item] for item in punctuation))
        if total_punctuation:
            for key in punctuation:
                punctuation[key] /= total_punctuation
        feature_lists['period_ratio'].append(punctuation['period'])
        feature_lists['question_ratio'].append(punctuation['question'])
        feature_lists['exclamation_ratio'].append(punctuation['exclamation'])
        feature_lists['ellipses_ratio'].append(punctuation['ellipses'])

        total_sentiment1 = (sentiment1['positive'] + sentiment1['negative'])
        max_sentiment1 = (max(sentiment1['positive'], sentiment1['negative']))
        if sentiment1['positive'] == sentiment1['negative'] or max_sentiment1 < 2:
            feature_lists['lex_prediction1'].append('Neutral')
            feature_lists['confidence1'].append('1.0')
        else:
            if sentiment1['positive'] == max_sentiment1:
                feature_lists['lex_prediction1'].append('Positive')
            else:
                feature_lists['lex_prediction1'].append('Negative')
            feature_lists['confidence1'].append(max_sentiment1 / total_sentiment1)

        emotions = sentiment2_english  # = ['anger', 'fear','joy', 'love','sadness', 'surprise']
        love = (sentiment2['joy'] + sentiment2['trust']) / 2
        values = [sentiment2['anger'], sentiment2['fear'], sentiment2['joy'], love, sentiment2['sadness'],
                  sentiment2['surprise']]
        max_sentiment2 = max(values)
        total_sentiment2 = sum(values)
        if total_sentiment2:
            feature_lists['lex_prediction2'].append(
                [emotion for (emotion, value) in zip(emotions, values) if value == max_sentiment2])
            feature_lists['confidence2'].append(max_sentiment2 / total_sentiment2)
        else:
            feature_lists['lex_prediction2'].append([most_common_emotion(df['Sentiment2'].tolist()).lower()])
            feature_lists['confidence2'].append(0.2)

    max_len = max(feature_lists['len_values'])

    feature_lists['len_values'] = [value / max_len for value in feature_lists['len_values']]

    return feature_lists


def generate_features(language, df):

    if language == 'EN':
        if not os.path.exists('translated_df.csv'):
            text_list = translate(df)
        else:
            df = pd.read_csv("translated_df.csv")
            text_list = df['Text'].tolist()
            df.drop(['Unnamed: 0'], axis=1, inplace=True)
        features = create_features_en(text_list)
        for key in features:
            df[key] = features[key]
        def encode_and_concat(dataframe, feature_columns):
            mlb = MultiLabelBinarizer()
            encoded_dfs = []

            for col in feature_columns:
                encoded_df = pd.DataFrame(mlb.fit_transform(dataframe[col]),
                                          columns=[f"{col}_{cls}" for cls in mlb.classes_])
                encoded_dfs.append(encoded_df)

            # dataframe = dataframe.drop(feature_columns, axis=1)
            df_encoded = pd.concat([dataframe] + encoded_dfs, axis=1)

            return df_encoded

        df['Political'] = df['Political'].map({'Yes': 1, 'No': 0})
        df['TextUppercase'] = df['TextUppercase'].map({'Yes': 1, 'No': 0})
        df['TextLowercase'] = df['TextLowercase'].map({'Yes': 1, 'No': 0})
        df['Complexity'] = [[value] for value in df['Complexity']]
        df['Real_Fake'] = [[value] for value in df['Real_Fake']]
        df['lex_prediction1'] = [[value] for value in df['lex_prediction1']]


        features_for_encoding = ['Complexity', 'Real_Fake', 'lex_prediction1', 'lex_prediction2']
        df = encode_and_concat(df, features_for_encoding)

        bert1_df = pd.read_json('../EN/bert_pred_s1.json')
        bert2_df = pd.read_json('../EN/bert_pred_s2.json')

        df['bert_s1'] = bert1_df['predicted_label']
        df['bert_s2'] = bert2_df['predicted_label']
        df['bert_s1'] = [[value] for value in df['bert_s1']]
        df['bert_s2'] = [[value] for value in df['bert_s2']]
        df = encode_and_concat(df, ['bert_s1', 'bert_s2'])


        sentiment1_map = {'Neutral': 0, 'Positive': 1, 'Negative': 2}
        sentiment2_map = {'anger': 0, 'fear': 1, 'joy': 2, 'love': 3, 'sadness': 4, 'surprise': 5}

        df['Sentiment1'] = df['Sentiment1'].map(sentiment1_map)
        df['Sentiment2'] = df['Sentiment2'].map(sentiment2_map)

        # to add them at the end of the dataframe
        df1 = df.pop('Sentiment1')
        df2 = df.pop('Sentiment2')
        df['Sentiment1'] = df1
        df['Sentiment2'] = df2

        df.to_csv('en_feature_df.csv', index=True)





def bert_split(language, df):
    
    folder1_path = language + '/' + 'sent1_split_' + language
    folder2_path = language + '/' + 'sent2_split_' + language

    if not os.path.exists(language):
        os.makedirs(language)
    if not os.path.exists(folder1_path):
        os.makedirs(folder1_path)
    if not os.path.exists(folder2_path):
        os.makedirs(folder2_path)

    def store_data(folder, file, content, drop_list, label):
        df = drop_columns(content, drop_list)
        list = df['Text']
        df.drop(['Text'], axis=1, inplace=True)
        df['text'] = list
        list = df[label]
        df.drop([label], axis=1, inplace=True)
        df['label'] = list
        df.to_csv(os.path.join(folder, file), index=True)

    train_df, temp_df = train_test_split(df, test_size=0.2, random_state=42)
    dev_df, test_df = train_test_split(temp_df, test_size=0.5, random_state=42)

    names = ['dev_df.csv', 'test_df.csv', 'train_df.csv']
    dataframes = [dev_df, test_df, train_df]
    for i in range(0, 3):
        name = names[i]
        df = dataframes[i]
        store_data(folder1_path, name, df, ['Unnamed: 0', 'Sentiment2'], 'Sentiment1')
        store_data(folder2_path, name, df, ['Unnamed: 0', 'Sentiment1'], 'Sentiment2')



# Set up argparse
def main():
    parser = argparse.ArgumentParser(description="Process feature and BERT generation for Romanian and English ")

    # Add arguments for the feature flags and bert flags
    parser.add_argument('--feat_ro', action='store_true', help="Generate features for Romanian (RO)")
    parser.add_argument('--feat_en', action='store_true', help="Generate features for English (EN)")
    parser.add_argument('--bert_ro', action='store_true', help="Perform BERT split for Romanian (RO)")
    parser.add_argument('--bert_en', action='store_true', help="Perform BERT split for English (EN)")

    args = parser.parse_args()

    if args.feat_en:
        generate_features('EN', df)

    if args.bert_ro:
        bert_split('RO', df)
    if args.bert_en:
        bert_split('EN', df)


# Run the script
if __name__ == "__main__":
    main()