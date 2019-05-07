from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_selection import SelectKBest, f_classif
import pandas as pd
import numpy as np
import torch
from torch import optim, Tensor, nn, argmax

mini_batch_size = 100


'''
This function takes the path to a csv file as input. It splits the found dataframe into labelled and unlabelled data, ignoring the rows with label value 2. 638 labelled samples are removed in order to have length divisible by 100. The labelled data is split into train and test data. The labels are transformed to a torch tensor. The text is extracted as a feature, stopwords removed and a tf-idf vectorization is performed. The 10000 best features are then extracted using the f-value test. Finally the features are transformed to a pytorch tensor and returned.
'''
def data_preparation(path):
    df = pd.read_csv(path, index_col='link')
    unlabelled_data = df[df['label'].isnull()]
    labelled_data = df[(df['label'] == 1) | (df['label'] == 0)]
    labelled_data = labelled_data[:-638]
    train_data, test_data = train_test_split(labelled_data, test_size=0.2)
    x_train = train_data.text
    y_train = Tensor(train_data.label.values).type(torch.LongTensor)
    x_test = test_data.text
    y_test = Tensor(test_data.label.values).type(torch.LongTensor)
    kwargs = {'ngram_range': (1, 2),'strip_accents': 'unicode','decode_error': 'replace',
              'analyzer': 'word','min_df': 2,'stop_words':'english'}
    vectorizer = TfidfVectorizer(**kwargs)
    x_train = vectorizer.fit_transform(x_train)
    x_test = vectorizer.transform(x_test)
    selector = SelectKBest(f_classif, k=min(10000, x_train.shape[1]))
    selector.fit(x_train, y_train)
    x_train = Tensor(selector.transform(x_train).astype('float32').toarray())
    x_test = Tensor(selector.transform(x_test).astype('float32').toarray())
    unlabelled = Tensor(selector.transform(vectorizer.transform(unlabelled_data.text)).astype('float32').toarray())
    return x_train, y_train, x_test, y_test, unlabelled_data, unlabelled


'''
Function that trains the neural network model. Cross entropy is chosen as a loss function, with learning rate 0.001. Adam is chosen as optimizer. For each epoch, the data is forwarded through the model in batches and then the gradient is backpropagated, adapting the model weights. '''
def training(model, train_input, train_target):
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr = 0.001,)
    nb_epochs = 100
    for e in range(nb_epochs):
        if e % 10 == 0:
            print('Epoch: ' + str(e))
        for b in range(0, train_input.size(0), mini_batch_size):
            output = model(train_input.narrow(0, b, mini_batch_size))
            loss = criterion(output, train_target.narrow(0, b, mini_batch_size))
            model.zero_grad()
            loss.backward()
            optimizer.step()
            

'''
This function calculates the number of errors made given the correct labels. It forwards the input data through the network, compares the output to the true labels and counts the number of occured errors.
'''
def compute_nb_errors(model, data_input, data_target):
    model = model.eval()
    nb_data_errors = 0
    for b in range(0, data_input.size(0), mini_batch_size):
        output = model(data_input.narrow(0, b, mini_batch_size))
        _, predicted_classes = torch.max(output, 1)
        for k in range(mini_batch_size):
            if data_target[b + k] != predicted_classes[k]:
                nb_data_errors = nb_data_errors + 1
    return nb_data_errors


'''
This function forwards the input data through the network and adds the resulting prediction to the dataframe of the input data.
'''
def predict(unlabelled_data, unlabelled, model, path_sink):
    model.eval()
    labels = []
    for i in range(0, unlabelled.size(0)):
        labels.append(int(argmax(model(unlabelled[i]))))    
    unlabelled_data['label'] = labels
    unlabelled_data.to_csv(path_sink)