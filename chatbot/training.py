import os
import random
import json
import pickle
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
from preprocessing import pre_processing

# env variables
SEP = os.path.sep + 'data\\'
DIR_PATH = os.path.dirname(os.path.realpath(__file__)) + SEP
INTENTS_PATH = DIR_PATH + "intents.json"
WORDS_PATH = DIR_PATH + "words.pkl"
CLASSES_PATH = DIR_PATH + "classes.pkl"
CHAT_MODEL_PATH = DIR_PATH + "chatbot_model.h5"

# load training data
intents = json.loads(open(INTENTS_PATH).read())

words = []
classes = []
documents = []
ignore_letters = ['?', '!', '.', ',']

# iterating through intents json
for intent in intents['intents']:
  for pattern in intent['patterns']:
    word_list = nltk.word_tokenize(pattern)
    words.extend(word_list)
    documents.append((word_list, intent['tag']))
    if intent['tag'] not in classes:
      classes.append(intent['tag'])

# pre process our words
lemmatizer = WordNetLemmatizer()
words = [pre_processing(word) for word in words]
words = sorted(set(words))

classes = sorted(set(classes))

pickle.dump(words, open(WORDS_PATH, 'wb'))
pickle.dump(classes, open(CLASSES_PATH, 'wb'))

# create bag of words
training = []
output_empty = [0] * len(classes)

for document in documents:
  bag = []
  word_patterns = document[0]
  word_patterns = [pre_processing(word) for word in word_patterns]
  for word in words:
    bag.append(1) if word in word_patterns else bag.append(0)

  output_row = list(output_empty)
  output_row[classes.index(document[1])] = 1
  training.append(bag + output_row)


# preparing training data
random.shuffle(training)
training = np.array(training)

train_X = training[:, :len(words)]
train_y = training[:, len(words):]

# building the neural network
model = tf.keras.Sequential()
model.add(tf.keras.layers.Dense(128, input_shape=(len(train_X[0]),), activation='relu'))
model.add(tf.keras.layers.Dropout(0.5)) # prevent overfitting
model.add(tf.keras.layers.Dense(64, activation='relu'))
model.add(tf.keras.layers.Dropout(0.5))
model.add(tf.keras.layers.Dense(len(train_y[0]), activation='softmax'))
sgd = tf.keras.optimizers.SGD(learning_rate=0.01, momentum=0.9, nesterov=True) # optimizer
model.compile(loss='categorical_crossentropy', optimizer=sgd, metrics=['accuracy']) # compile

# training step
model.fit(train_X, train_y, epochs=200, batch_size=5, verbose=1)
model.save(CHAT_MODEL_PATH)
print('Done')