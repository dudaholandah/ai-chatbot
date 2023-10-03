import random
import json
import pickle
import numpy as np
import os
import nltk
from nltk.stem import WordNetLemmatizer
import tensorflow as tf
# from preprocessing import pre_processing
# import api_queries_jikanpy as api_queries
from . import preprocessing
from . import api_queries_jikanpy as api_queries

# env variables
SEP = os.path.sep + 'data\\'
DIR_PATH = os.path.dirname(os.path.realpath(__file__)) + SEP
INTENTS_PATH = DIR_PATH + "intents.json"
WORDS_PATH = DIR_PATH + "words.pkl"
CLASSES_PATH = DIR_PATH + "classes.pkl"
CHAT_MODEL_PATH = DIR_PATH + "chatbot_model.h5"

lemmatizer = WordNetLemmatizer()
intents = json.loads(open(INTENTS_PATH).read())    
words = pickle.load(open(WORDS_PATH, 'rb'))        
classes = pickle.load(open(CLASSES_PATH, 'rb'))    
model = tf.keras.models.load_model(CHAT_MODEL_PATH)  

# function to test if the word is a noun
def is_noun(pos: str) -> bool:
  nltk.download('averaged_perceptron_tagger', quiet=True)
  nltk.download('tagsets', quiet=True)
  return pos[:2] == 'NN' or pos[:2] == 'NNP'

# return every noun in a sentence
def get_nouns(sentence: str) -> str:
  string_nouns = ''
  tokenized = nltk.word_tokenize(sentence)
  
  nouns = [word for (word, pos) in nltk.pos_tag(tokenized) if is_noun(pos)]
  for each in nouns:
    if each == "anime": continue
    string_nouns = string_nouns + " " + each

  print(nouns)
  return string_nouns

# tokenize and preprocess
def clean_up_sentence(sentence: str) -> list[str]:
  sentence_words = nltk.word_tokenize(sentence)
  sentence_words = [preprocessing.pre_processing(word) for word in sentence_words]
  return sentence_words

# transform a sentence to a bag of words
def bag_of_words(sentence: str) -> type(np):
  sentence_words = clean_up_sentence(sentence)
  bag = [0] * len(words)
  for each_word in sentence_words:
    for i, word in enumerate(words):
      if word == each_word:
        bag[i] = 1
  return np.array(bag)

# predict a class (intent) from a given sentence
def predict_class(sentence: str) -> list:   
  bow = bag_of_words(sentence)
  result = model.predict(np.array([bow]), verbose=0)[0]  
  ERROR_THRESHOLD = 0.20 
  results = [[i, r] for i, r in enumerate(result) if r > ERROR_THRESHOLD]
  results.sort(key=lambda x: x[1], reverse=True)
  return_list = []
  for r in results:
    return_list.append({'intent': classes[r[0]], 'probability': str(r[1])})
  return return_list

# return a random response for the most probable question
def get_response(intents_list, intents_json) -> str:
  tag = intents_list[0]['intent']
  list_intents = intents_json['intents']
  result = ''
  for each in list_intents:
    if each['tag'] == tag:
      result = random.choice(each['responses'])
      break
  return result

# return the answer to a given question
def get_answer(question: str) -> str:
  answer = ""
  intent = predict_class(question)
  res = get_response(intent, intents)

  # here we call the predicted query 
  if 'tag' in res:
    # these queries require a noun as second argument
    # we are using the first noun only 
    if res[4:] == "genres" or res[4:] == "similar":
      str_nouns = get_nouns(question)  
      if len(str_nouns) > 1:
        answer = api_queries.query(res[4:],str_nouns)
      else:
        answer = "Sorry, can you say it again? Please use capital letters on proper nouns."
    # similar to last queries
    # these queries responses need to be pre processed 
    if res[4:] == "characters" or res[4:] == "anime":
      str_nouns = get_nouns(question)  
      if len(str_nouns) > 1:
        answer = api_queries.query_filter(api_queries.query(res[4:], str_nouns))
      else:
        answer = "Sorry, can you say it again? Please use capital letters on proper nouns."
    # these queries only require one argument      
    elif res[4:] == "recommendations" or res[4:] == "season":
      answer = api_queries.query(res[4:])
    # this query needs a number as second argument
    # for now we always use number 1 (top 1 anime)
    elif res[4:] == "top":
      answer = api_queries.query(res[4:], 1)
  else:
    answer = res

  if type(answer) == list:
    if answer[0] == "\n":
      answer = "Sorry, can you say it again? Please use capital letters on proper nouns."
    elif len(answer) == 0:
      answer = ""
    else:
      answer = answer[0]
  
  return answer

def run_chatbot():
  print("Chatbot running...")

  while True:
    question = input()
    print(get_answer(question))

if __name__ == "__main__":
  run_chatbot()