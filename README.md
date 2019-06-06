# Website Classification for identifying illicit markets

This repository contains the project for classifying websites in collaboration with the ESC. It is an optional semester project in Data Science COM-508.

## Google tutorial
https://developers.google.com/machine-learning/guides/text-classification/

## Result
The analysis resulted in 652 suspected illicit websites. The csv file containing the domain links of these websites can be found under /data/suspected.csv.

## Dependencies
- pandas 0.24.1
- scikit-learn 0.20.2
- numpy 1.15.4
- pytorch 1.0.1
- matplotlib 3.0.2
- seaborn 0.9.0
- jupyterlab 0.35.4

## How to run
- Install dependencies
- put original google.json file in folder /data/
- Open and run /src/webshop_classification.ipynb
- /data/labelled_unique.csv can be replaced with other labelled data

## Possible further work
- There are roughly 650 display names labelled with 1. These could further be investigated by hand
- The resulting adapted dataset could then be used to retrain the multilayer perceptron
- In a next step the actual html code of the websites could be analyzed instead of just the snippet

