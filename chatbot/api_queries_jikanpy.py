from jikanpy import Jikan
import random
import re
import requests
import json  
import time

jikan = Jikan()
JIKAN_URL = "https://api.jikan.moe/v4"

# pre process our response
def query_filter(query_result: list[str]) -> list[str]:
  output = []
  for each in query_result:
    resu = re.sub(r'\[.*', "", each)  # remove [Written by...]
    resu = re.sub(r'\(.*\n', "", resu)  # remove (Source ...)
    resu = re.sub(r'\(.*', "", resu)  # remove (Source ...)
    resu = re.sub(r'.*:.*\n', "", resu)  # remove additional info
    output.append(resu)
  return output

# check whether the query is possible
def possible_query(result) -> bool:
  return result["pagination"]["items"]["count"] != 0

# all queries from the api
# followed the documentation: https://jikanpy.readthedocs.io/en/latest/
def query(command: str, arguments="") -> list[str]:

  # query 1: about character _
  if command.lower() == "characters":
    result = jikan.search("characters", arguments)
    return [result["data"][0]['about']] if possible_query(result) else []
  
  # query 2: about anime _    
  elif command.lower() == "anime":
    result = jikan.search("anime", arguments)
    return [result["data"][0]["synopsis"]] if possible_query(result) else []
  
  # query 3: genres from anime _
  elif command.lower() == "genres":
    start = ["Sure thing: ", "Here you go: ", "Of course: "]
    result = jikan.search("anime", arguments)

    if not possible_query(result): return []

    ans = ""
    for genre in result["data"][0]['genres']:
      if ans != "": ans += ", "
      ans += genre['name']
    return random.choice(start) + ans + "."      
          
  # query 4: ask for a recommendation
  elif command.lower() == 'recommendations':
    result = jikan.recommendations(type='anime')
    rand = random.randint(0, len(result['data'])-1)
    ans = []
    for anime in result['data'][rand]['entry']:
      ans.append(anime['title'])
    ans.append(result['data'][rand]['content'])
    ans_string = f"Why don't you try watching '{ans[0]}' and '{ans[1]}'? {ans[2]}"
    return ans_string
  
  # query 5: return an anime from the season
  elif command.lower() == 'season':
    start = ["A new anime is ", "Here you go: ", "A lastest anime sensation: "]
    result = jikan.seasons(extension='now')

    if not possible_query(result): return []

    rand = random.randint(0, len(result['data'])-1)
    return random.choice(start) + result['data'][rand]['title'] + "."
             
  # query 6: return the top _ anime 
  # for now i am always return top 1
  elif command.lower() == 'top':
    start = ["The top one is: ", "Here you go: ", "The most epic anime ever: "]
    top = int(arguments)
    items = 0
    page = 1
    result = jikan.top(type='anime', page=page)
    while possible_query(result):
      items += result["pagination"]["items"]["count"]
      if top > items:
        page += 1
        top -= items
        result = jikan.top(type='anime', page=page)
      else:
        return random.choice(start) + result['data'][top-1]['title'] + "."
    return []
  
  # query 7: anime similar to anime _ 
  elif command.lower() == 'similar':
    start = ["You should try ", "I recommend ", "A great choice is "]
    result = jikan.search('anime', arguments)

    if not possible_query(result): return []
    
    anime_id = result['data'][0]["mal_id"]
    time.sleep(0.5)
    res = requests.get(f'{JIKAN_URL}/anime/{anime_id}/recommendations')
    result = json.loads(res.text)
    try:
      rand = random.randint(0, len(result['data'])-1)
      return random.choice(start) + result['data'][rand]['entry']['title'] + "."
    except (UnicodeDecodeError, ValueError):
      return ["Sorry, I can't recommend you a similar anime."]

  else:
    return ["I don't know the answer."]


## query (1) - quem é o personagem _ ?:
# resultado = query("characters", "luffy")
# resultado = query_filter(resultado)
# print(*resultado)

## query (2) - sobre o que é o anime _ ?
# resultado = query("anime", "one piece")
# print(resultado)
# resultado = query_filter(resultado)
# print(*resultado)

## query (3) - qual o gênero do anime _ ?
# print(*query("genres", "one piece"))

## query (4) - me recomende dois animes.
# print(query("recommendations"))

## query (5) - me fale um anime da temporada
# resultado = query("season")
# resultado = query_filter(resultado)
# print(resultado)

## query (6) - qual o anime top _ ?
# print(*query("top", "1"))

## query (7) - recomendacao de animes similares ao anime _ ?
# print(query("similar", "black cover"))