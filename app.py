import os
import json
from flask import Flask, render_template, request, url_for, flash, redirect, session
from flask_session import Session
import redis
import configparser
import persistence

from gpt import GPT
from create_scenario import create_scenario
from conversation import create_conversation_response

app = Flask(__name__)
#mc = pylibmc.Client(["127.0.0.1"], binary=True, behaviors={"tcp_nodelay": True, "ketama": True})

app.secret_key = os.getenv('SECRET_KEY', default='BAD_SECRET_KEY')
#app.config['SESSION_TYPE'] = 'memcached'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True
#app.config['SESSION_MEMCACHED'] = mc
app.config['SESSION_REDIS'] = redis.from_url('redis://127.0.0.1:6379')

server_session = Session(app)

gpt_query = GPT()
persist = persistence.get_persistence_layer()

@app.route('/')
def index():
    scenarios = persist.get_scenarios()
    return render_template('index.html', scenarios=scenarios)

@app.route('/<scenario_id>', methods=('GET', 'POST'))
def scenario(scenario_id):

    if request.method == 'GET':
        scenario = persist.get_scenario_details(scenario_id)
        messages = []
        session['history'] = ""

        return render_template('scenario.html', name=scenario['name'], goal=scenario['goal'],
                                details=scenario['json'], messages=messages)

    try:
        user_message = request.form['response']

        scenario = persist.get_scenario_details(scenario_id)

        if 'history' in session and session['history']:
            messages = json.loads(session['history'].decode("UTF-8"))
        else:
            messages = []

        messages, goal_accomplished = create_conversation_response(scenario['json']['character'],
                                                                   scenario['json']['location'], scenario['goal'],
                                                                   scenario['json']['details'], user_message,
                                                                   messages, gpt_query)

        session['history'] = json.dumps(messages).encode("UTF-8")

        return render_template('scenario.html', name=scenario['name'], goal=scenario['goal'],
                               details=scenario['json'], messages=messages)

    except Exception as e:
        print("Exception: {}".format(e))

@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':

        name = request.form['name']
        goal = request.form['goal']
        details = request.form['details']

        if not name or not goal:
            flash('Name and goal are required!')
        else:
            try:
                if not details:
                    details = ""

                details = create_scenario(name, goal, details, gpt_query)
                print(details)
                #id = persist.put_message(question, result, url)
                id = persist.add_scenario({'name': name,
                                           'goal': goal,
                                           'json': json.dumps(details['details'])})

                print(id)
            except Exception as e:
                print("Exception: {}".format(e))
                id = ""

            return redirect(url_for('index') + "/{}".format(id))

    return render_template('create.html')

@app.route('/about/')
def about():
    return render_template('about.html')


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('config.ini')
    port = config['DEFAULT']['port']

    app.run(debug=True, host="0.0.0.0", port=port)
