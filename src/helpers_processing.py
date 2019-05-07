import pandas as pd
import copy
pd.options.mode.chained_assignment = None


'''
Function takes as argument path to json file. It reads the json file. For the content found in result for each
element, it stocks the arguments, the displaylink, link, snippet and title. The function further merges the title and the snippet, removing the Nan values and splits the arguments into two columns. The function finally
saves the csv file to the place specified in the constructor.
'''
def json_to_csv(path_source, path_sink):
    json = pd.read_json(path_source, lines=True)
    df = pd.DataFrame()
    for i in range(len(json)):
        element = pd.DataFrame(json.loc[i].result)
        element['args'] = json.loc[i].args['q']
        element['date'] = pd.to_datetime(json.loc[i].date['$date']).date()
        element = element.set_index(['link'])
        temp = pd.DataFrame(element[['displayLink', 'snippet', 'title', 'args']])
        df = df.append(temp)
    df['args_split'] = df.args.str.split('+')
    args = df['args_split'].apply(pd.Series)
    df['first'] = args[0]
    df['drug'] = args[1]
    df = df[~df['title'].isnull()]
    df = df[~df['snippet'].isnull()]
    df['text'] = df['snippet'] + ' ' + df['title']
    df = df.drop(columns=['snippet','title','args', 'args_split'])
    df.to_csv(path_sink)


'''
Function takes a csv file as source, creates a new column called count, which counts the number of occurrences
per display link. The last link and snippet is kept, the displaylink is kept as index and the column displaylink
is dropped. Finally the csv file is saved to the specified place.
'''
def unique_display_link(path_source, path_sink):
    df = pd.read_csv(path_source)
    df['count'] = 1
    df['count'] = df['count'].groupby(df['displayLink']).transform('sum')
    df.drop_duplicates(subset=['displayLink'], keep='last', inplace=True)
    df.sort_values(by='count', ascending=False, inplace=True)
    df.index.names = ['index']
    df = df[['displayLink', 'text', 'first', 'drug', 'count']]
    df.index = df.displayLink
    df = df.drop(columns=['displayLink'])
    df.to_csv(path_sink)


'''
Function takes as argument path to csv file containing 1m most popular websites from alexa and path to csv source.
It first takes the most_popular websites, extracts the domain name, keeps only the first 1000, which are longer 
than 5 characters and joins them on '|'. The function then removes all elements from the source, which contain
one of the 1000 words extracted from the most popular websites in the display link.
'''
def remove_most_popular(path_source, path_sink, most_popular):
    most_popular_websites = list(pd.read_csv(most_popular, header=None).loc[:, 1].values)
    most_popular_websites = [x.split('.')[0] for x in most_popular_websites]
    most_popular_websites = [x for x in most_popular_websites if len(x) >= 5]
    most_popular_websites = most_popular_websites[:1000]
    most_popular_websites = '|'.join(most_popular_websites)
    drug_websites = pd.read_csv(path_source, index_col=['displayLink'])
    drug_websites_filtered = drug_websites[~drug_websites.index.str.contains(most_popular_websites)]
    drug_websites_filtered.to_csv(path_sink)
    drug_websites_filtered


'''
Helper function to facilitate labeling. The dataframe at the path gets red and the label at index i is set to p.
'''
def labeling(path, i, l='NaN'):
    df = pd.read_csv(path , index_col='displayLink')
    print(df.index[i])
    df['label'].iloc[i] = l
    df.to_csv(path)


'''
Function takes labelled unique displayLink dataframe and unlabelled original csv file, merges the label column and
returns dataframe containing only the link, the snippet, the first argument, the drug and the label. 
'''
def expand_labels(path_labels_unique, path_source, path_sink):
    labels_unique = pd.read_csv(path_labels_unique, index_col= 'displayLink')
    df = pd.read_csv(path_source, index_col='displayLink')
    df['label'] = labels_unique['label']
    df = df[['link', 'text', 'first', 'drug', 'label']]
    df.to_csv(path_sink)
    
    
'''
After having predicted the label for each link, this function groups by the display link and counts the occurrences. It further counts the label and creates a column called ratio, which contains the ratio between the sum of the labels and the occurences. The index of the dataframe is set to the display link, then the dataframe is sorted by the ratio and by the label count. This way at the top of the dataframe are those display links, which occured often and which were labelled always as 1. At the bottom of the dataframe are those display links, which owere never labelled as an illegal webshop.
'''
def unique_display_link_prediction(path_source, path_sink):
    df = pd.read_csv(path_source)
    df = copy.deepcopy(df)
    df['count'] = 1
    df['count'] = df['count'].groupby(df['displayLink']).transform('sum')
    df['label_count'] = df['label'].groupby(df['displayLink']).transform('sum')
    df['ratio'] = df['label_count']/ df['count'] 
    df.drop_duplicates(subset=['displayLink'], keep='last', inplace=True)
    df.sort_values(by=['ratio','label_count'], ascending=[False,False], inplace=True)
    df.index.names = ['index']
    df = df[['displayLink', 'text', 'first', 'drug', 'count', 'label', 'ratio','label_count']]
    df.index = df.displayLink
    df = df.drop(columns=['displayLink'])
    df.to_csv(path_sink)