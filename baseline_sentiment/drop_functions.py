def drop_columns(df, drop_list):
    columns_to_drop = []
    for prefix in drop_list:
        for col in df.columns:
            if col.startswith(prefix):
                columns_to_drop.append(col)
    df = df.drop(columns=columns_to_drop)
    return df

def drop_numbers(df):
    initial_len = len(df)
    dropped = 0
    for index, row in df.iterrows():
        if row['TextUppercase'] == 1 and row['TextLowercase'] == 1:
            df = df.drop(index)
            dropped += 1

    final_len = len(df)
    print(initial_len, dropped, final_len)
