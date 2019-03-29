import pandas as pd
pd.options.mode.chained_assignment = None

def printer(df,i,p='NaN'):
    print(df.index[i])
    df['label'].iloc[i] = p
    df.to_csv('../Data/labelled.csv')