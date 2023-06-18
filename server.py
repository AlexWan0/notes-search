from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import json
from search import Search

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

def blackbox_function(content):
    return search_api.do_search(content)

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('message')
def handle_message(data):
    print(data)
    output = blackbox_function(data)
    emit('response', json.dumps(output))

if __name__ == '__main__':
    search_api = Search()
    print('search loaded')

    socketio.run(app)
