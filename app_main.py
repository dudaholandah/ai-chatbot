from flask import Flask, render_template, request, jsonify

from chatbot import chatbot

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'

@app.route("/api/chat", methods=["GET", "POST"])
def chat():
  content = request.json
  question = content.get("question", "")
  answer = chatbot.get_answer(question)
  return {"answer": answer}


@app.route('/')
def index():
  return render_template('index.html')


if __name__ == '__main__':
  app.run(debug=True)
