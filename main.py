import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, StandardScaler
from sklearn.metrics import r2_score
import tensorflow as tf
from tensorflow import keras

train = 'https://raw.githubusercontent.com/jwillekes18/ML-Porto-Seguro-s-Safe-Drive-Prediction/main/train.csv'
train = pd.read_csv(train)
test = 'https://raw.githubusercontent.com/jwillekes18/ML-Porto-Seguro-s-Safe-Drive-Prediction/main/test.csv'
test = pd.read_csv(test)

XtrainComplete = train.drop('target', axis=1)
ytrainComplete = train['target']
XtestComplete = test

# create train test split
from sklearn.model_selection import train_test_split

X = train.drop('target', axis=1)
y = train['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=101)

from sklearn.metrics import classification_report, confusion_matrix

# evaluate predicitions
predictionsCoin = np.random.randint(0, 2, y_test.shape)
print(classification_report(y_test, predictionsCoin))
print(confusion_matrix(y_test, predictionsCoin))

import scipy.stats

scipy.stats.chi2.sf(50.3, 1)

# GRIDSEARCH for random forest
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier

rfc = RandomForestClassifier(random_state=42)
param_grid = {
    'n_estimators': [100, 200, 400, 800],
    'max_features': ['auto', 'sqrt', 'log2'],
    'min_samples_split': [1, 5, 20, 40],
    'max_depth': [2, 5, 10, 50],
    'criterion': ['gini', 'entropy']
}
CV_rfc = GridSearchCV(estimator=rfc, param_grid=param_grid, cv=3, verbose=2)
CV_rfc.fit(X_train, y_train)
print(CV_rfc.best_params_)
print(CV_rfc.best_score_)

from sklearn.ensemble import RandomForestClassifier

rfc_best = RandomForestClassifier(criterion='gini',
                                  max_depth=10,
                                  max_features='log2',
                                  min_samples_split=40,
                                  n_estimators=200,
                                  random_state=42)
from sklearn.metrics import classification_report, confusion_matrix

rfc_best.fit(X_train, y_train)
# evaluate predicitions
predictions = rfc_best.predict(X_test)
print(classification_report(y_test, predictions))
print(confusion_matrix(y_test, predictions))

# Gridsearch for boosted trees
from sklearn.ensemble import AdaBoostClassifier
from sklearn.model_selection import GridSearchCV
from sklearn.tree import DecisionTreeClassifier

param_grid = {
    'n_estimators': [10, 50, 100, 200],
    'learning_rate': [1, 0.5],
    'base_estimator__max_features': ['auto', 'sqrt', 'log2'],
    'base_estimator__min_samples_split': [2, 10, 40],
    'base_estimator__max_depth': [2, 5, 10, None],
    'base_estimator__criterion': ['gini', 'entropy'],

}

DTC = DecisionTreeClassifier(random_state=42)

ABC = AdaBoostClassifier(base_estimator=DTC)

# run grid search
CV_ABC = GridSearchCV(ABC, param_grid=param_grid, scoring='accuracy', cv=3, verbose=2)
CV_ABC.fit(X_train, y_train)
print(CV_ABC.best_params_)
print(CV_ABC.best_score_)

from sklearn.ensemble import AdaBoostClassifier
from sklearn.tree import DecisionTreeClassifier

DTC = DecisionTreeClassifier(random_state=42,
                             criterion="entropy",
                             max_depth=2,
                             max_features='auto',
                             min_samples_split=40)

ABC_best = AdaBoostClassifier(base_estimator=DTC, n_estimators=50, learning_rate=0.5)
from sklearn.metrics import classification_report, confusion_matrix

ABC_best.fit(X_train, y_train)
# evaluate predicitions
predictions = ABC_best.predict(X_test)
print(classification_report(y_test, predictions))
print(confusion_matrix(y_test, predictions))

from keras.callbacks import EarlyStopping
import tensorflow
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Activation

# Best NN
# Create param_grid dependables.
layers = [16, 8, 8]  # number of neurons based on Deepa (2013) = 4 for input = 91.
initializers = 'normal'
activations = 'relu'  # avoids vanishing gradient problem
optimizers = 'RMSprop'
dropouts = 0.5
batch_size = 256
epochs = 300

# Include Callback function to avoid overfitting
stopper = EarlyStopping(monitor='accuracy', patience=10, verbose=2)
fit_params = dict(callbacks=[stopper])

bestNN = Sequential()
for i, nodes in enumerate(layers):
    if i == 0:
        bestNN.add(Dense(nodes, kernel_initializer=initializers, input_dim=X_train.shape[1]))
        bestNN.add(Activation(activations))
        bestNN.add(Dropout(dropouts))
    else:
        bestNN.add(Dense(nodes))
        bestNN.add(Activation(activations))
        bestNN.add(Dropout(dropouts))
bestNN.add(
    Dense(units=1, kernel_initializer=initializers, activation='sigmoid'))  # Sigmoid in final layer --> add research
bestNN.compile(optimizer=optimizers, loss='binary_crossentropy', metrics=['accuracy'])
bestNN.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, **fit_params)

# evaluate predicitions
from sklearn.metrics import classification_report, confusion_matrix

predictionsNN = bestNN.predict(X_test)
predictionsNN = predictionsNN > 0.5
print(classification_report(y_test, predictions))
print(confusion_matrix(y_test, predictions))

# mcneymar test NN vs random coin
results = np.zeros((2, 2))
y_test = np.array(y_test)
for i in range(0, predictionsCoin.size):
    if (predictionsCoin[i] == y_test[i] and predictionsNN[i] == y_test[i]):
        results[0, 0] = results[0, 0] + 1
    elif (predictionsCoin[i] != y_test[i] and predictionsNN[i] == y_test[i]):
        results[1, 0] = results[1, 0] + 1
    elif (predictionsCoin[i] == y_test[i] and predictionsNN[i] != y_test[i]):
        results[0, 1] = results[0, 1] + 1
    elif (predictionsCoin[i] != y_test[i] and predictionsNN[i] != y_test[i]):
        results[1, 1] = results[1, 1] + 1
    else:
        print('error')
print(results)

# Linear weights better?
from sklearn.metrics import classification_report, confusion_matrix

# predABC=ABC_best.predict_proba(X_test)
predRFC = rfc_best.predict_proba(X_test)
predNN = bestNN.predict(X_test)
# predNN_20_10=bestNN_20_10.predict(X_test)

# predABC=predABC[:,1].reshape((-1,1))
predRFC = predRFC[:, 1].reshape((-1, 1))
pred = (predNN + predRFC) / 2
predictions = pred > 0.5
print(classification_report(y_test, predictions))
print(confusion_matrix(y_test, predictions))

# Popular vote better?
from sklearn.metrics import classification_report, confusion_matrix

# predABC=ABC_best.predict(X_test)
predRFC = rfc_best.predict(X_test)
predNN = bestNN.predict(X_test)
predNN = predNN > 0.5
# predNN_20_10=bestNN_20_10.predict(X_test)
# predABC=predABC.reshape((-1,1))
predRFC = predRFC.reshape((-1, 1))

pred = (1 * predNN + predRFC) / 2
predictions = pred > 0.5
print(classification_report(y_test, predictions))
print(confusion_matrix(y_test, predictions))

# predicitions:
from keras.callbacks import EarlyStopping
import tensorflow
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import Dropout
from tensorflow.keras.layers import Activation

# Best NN
# Create param_grid dependables.
layers = [16, 8, 8]  # number of neurons based on Deepa (2013) = 4 for input = 91.
initializers = 'normal'
activations = 'relu'  # avoids vanishing gradient problem
optimizers = 'RMSprop'
dropouts = 0.5
batch_size = 256
epochs = 300

# Include Callback function to avoid overfitting
stopper = EarlyStopping(monitor='accuracy', patience=10, verbose=2)
fit_params = dict(callbacks=[stopper])

bestNN = Sequential()
for i, nodes in enumerate(layers):
    if i == 0:
        bestNN.add(Dense(nodes, kernel_initializer=initializers, input_dim=XtrainComplete.shape[1]))
        bestNN.add(Activation(activations))
        bestNN.add(Dropout(dropouts))
    else:
        bestNN.add(Dense(nodes))
        bestNN.add(Activation(activations))
        bestNN.add(Dropout(dropouts))
bestNN.add(
    Dense(units=1, kernel_initializer=initializers, activation='sigmoid'))  # Sigmoid in final layer --> add research
bestNN.compile(optimizer=optimizers, loss='binary_crossentropy', metrics=['accuracy'])
bestNN.fit(XtrainComplete, ytrainComplete, epochs=epochs, batch_size=batch_size, **fit_params)
predNN = bestNN.predict(XtestComplete)
predNN = predNN > 0.5
print(predNN)

for i in range(0, predNN.size):
    if (predNN[i]):
        print(1, end='')
    else:
        print(0, end='')
print(" ")
print("done")
