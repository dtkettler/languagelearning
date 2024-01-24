import sqlite3
import json
from google.cloud import firestore
from google.cloud.firestore import FieldFilter
import configparser
from abc import ABC, abstractmethod


class Persistence(ABC):

    @abstractmethod
    def get_scenarios(self):
        pass

    @abstractmethod
    def get_scenario_details(self, id):
        pass

    @abstractmethod
    def add_scenario(self, scenario):
        pass

    @abstractmethod
    def vote_scenario(self, id, vote):
        pass


def get_persistence_layer():
    config = configparser.ConfigParser()
    config.read('config.ini')
    persistence = config['DEFAULT']['persistence']

    if persistence == "sqlite":
        return PersistenceSQLite()
    elif persistence == "firestore":
        return PersistenceFirestore()
    else:
        return None

class PersistenceSQLite(Persistence):
    def __init__(self):
        self.con = sqlite3.connect("results.db", check_same_thread=False)
        self.cur = self.con.cursor()

        self.cur.execute("CREATE TABLE IF NOT EXISTS scenarios(name, goal, json, votes)")

    def get_scenarios(self):
        res = self.cur.execute("SELECT rowid, name, goal, votes FROM scenarios ORDER BY votes, rowid DESC LIMIT 20")

        scenarios = []
        for row in res.fetchall():
            scenarios.append({'id': row[0],
                              'name': row[1],
                              'goal': row[2],
                              'votes': row[3]})
        return scenarios

    def get_scenario_details(self, id):
        intid = int(id)
        try:
            res = self.cur.execute("SELECT rowid, name, goal, json, votes FROM scenarios where rowid = {}".format(intid))
        except:
            print("Not a valid ID")
            return []

        for row in res.fetchall():
            return {'id': row[0],
                    'name': row[1],
                    'goal': row[2],
                    'json': json.loads(row[3]),
                    'votes': row[4]}

    def add_scenario(self, scenario):
        data = ({'name': scenario['name'], 'goal': scenario['goal'], 'json': scenario['json'], 'votes': 0})
        self.cur.execute("INSERT INTO scenarios VALUES (:name, :goal, :json, :votes)", data)
        self.con.commit()
        res = self.cur.execute("SELECT last_insert_rowid()")
        id = res.fetchall()[0][0]

        return id

    def vote_scenario(self, id, vote):
        return

class PersistenceFirestore(Persistence):
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('keys.ini')
        project = config['DEFAULT']['firestore_project']

        self.db = firestore.Client(project=project)

    def get_messages(self, id=None):
        if id:
            doc_ref = self.db.collection("results").document(id)
            doc = doc_ref.get()
            if doc.exists:
                result = doc.to_dict()
                result["id"] = doc.id
                results = [result]
            else:
                print("Not a valid ID")
                return []

        else:
            docs = self.db.collection("results").order_by("timestamp", direction=firestore.Query.DESCENDING).limit(20).stream()
            #docs = self.db.collection("results").limit(20).stream()

            results = []
            for doc in docs:
                result = doc.to_dict()
                result["id"] = doc.id
                results.append(result)

        return results

    def put_message(self, question, result, url):
        data = ({'claim': question, 'result': result, 'url': url, "timestamp": firestore.SERVER_TIMESTAMP})

        update_time, ref = self.db.collection("results").add(data)
        id = ref.id

        return id

    def check_for_article(self, url):
        doc_ref = self.db.collection("articles").where(filter=FieldFilter("url", "==", url))
        docs = doc_ref.get()
        for doc in docs:
            result = doc.to_dict()
            return result["text"]

        return None

    def upload_article(self, url, text):
        data = ({'url': url, 'text': text, "timestamp": firestore.SERVER_TIMESTAMP})

        update_time, ref = self.db.collection("articles").add(data)
