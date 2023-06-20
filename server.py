from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
import threading
from colors import color
import html

from update import run_update
from search import Search

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

search_api = Search()

def query(content):
    return search_api.do_search(content)

# A global variable to keep track of whether the update function is already running
update_thread = None

def update():
    # Perform your update process here
    print(color('SERVER: Update function running in thread: ' + threading.current_thread().name, 'green'))
    run_update()
    print(color('SERVER: Done with update.', 'green'))

    # reinit search variable
    global search_api
    search_api = Search()

    # Once done, reset the global variable to indicate that the update process has completed
    global update_thread
    update_thread = None

def sanitize_output(data):
    for lst in data:
        for i in range(len(lst)):
            if lst[i] is None:
                continue

            lst[i] = html.escape(lst[i])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/update', methods=['POST'])
def handle_update():
    global update_thread
    # Check whether the update function is already running
    if update_thread is None or not update_thread.is_alive():
        update_thread = threading.Thread(target=update)
        update_thread.start()
        return jsonify({'message': 'Update process started.'}), 200
    else:
        print(color('SERVER: Update function already running -- ignoring request.', 'yellow'))
        return jsonify({'message': 'Update process already running.'}), 409

@socketio.on('message')
def handle_message(data):
    print(data)
    output = query(data)
    sanitize_output(output)
    emit('response', json.dumps(output))

if __name__ == '__main__':
    socketio.run(app)
