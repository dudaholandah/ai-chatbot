import re
import numpy as np
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from nltk.corpus import wordnet as wn

# nltk.download('stopwords')

def pre_processing(text : str) -> str:
  # stopwords_nltk = stopwords.words('english')
  lemmatizer = WordNetLemmatizer()
  
  # remove special characters and numbers
  word = re.sub(r'[\s!%*~\^´`=+<\[\]?&$:;@#.0-9()\/\"\'_-]+', " ", text)
  word = lemmatizer.lemmatize(word)
  word = word.strip()

  return word