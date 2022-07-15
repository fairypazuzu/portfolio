import pandas as pd
from sklearn import tree
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import cross_val_score

df = pd.read_csv('frombase7-cleaned9.csv').drop('num_class', axis=1)
X = df.drop(['class', 'id', 'popularity', 'genre'], axis=1)
Y = df['class']


clf = tree.DecisionTreeClassifier()
k = int(round(len(df)*0.7))
clf.fit(X[0:k], Y[0:k])

cm = confusion_matrix(Y[k:], clf.predict(X[k:]))
accuracy = accuracy_score(Y[k:], clf.predict(X[k:]))
precision = precision_score(Y[k:], clf.predict(X[k:]), average=None)
recall = recall_score(Y[k:], clf.predict(X[k:]), average=None)
print(cm)
print(accuracy, precision, recall)

scores = cross_val_score(clf, X, Y, cv=10)
print(scores)