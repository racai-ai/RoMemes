from deep_translator import GoogleTranslator
def translate(df):
    """
    Translates the texts and sentiment2 in the dataframe and converts it to a csv for future use (translated_df.csv)
    :return: translated_text_list
    """
    print("translating...")

    text_list = df['Text'].tolist()
    df['Original_text'] = text_list
    df.drop(['Text'], axis=1, inplace=True)
    translated_text_list = GoogleTranslator('ro', 'en').translate_batch(text_list)
    df['Text'] = translated_text_list

    df['Sentiment2'] = df['Sentiment2'].str.lower()

    print("translation complete.")
    df.to_csv('translated_df.csv', index=True)
    return translated_text_list
