from hashlib import sha224
from datetime import datetime
class Database:
    urls = {}
    entries = {}
    def get_url(self, idx):
        if idx in self.urls:
            return self.urls[idx]['url'], self.urls[idx]['token']
        else:
            return None, None
    
    def url_from_token(self, token):
        for d in self.urls:
            if self.urls[d]['token'] == token:
                return d 
    def add_url(self, url):
        idx = sha224(url.encode('utf-8')).hexdigest()
        token = sha224(('view:' + idx).encode('utf-8')).hexdigest()
        self.urls[idx] = {
            'url': url,
            'token': token,
        }
        self.entries[token] = []
        new_url = '/view/' + idx
        return new_url, token
    def add_entry(self, token, agent=None, ip=None):
        if token in self.entries:
            self.entries[token].append([datetime.now().isoformat(), agent, ip])
            print(self.entries[token])
    def get_entries(self, token):
        if token in self.entries:
            return self.entries[token]
        else:
            return None


import pymongo
import os, dotenv
dotenv.load_dotenv()
MONGODB_URL = os.getenv('MONGODB_URL')
class MDatabase:
    client = pymongo.MongoClient(MONGODB_URL)
    db = client.image_viewer
    ims = db.ims
    evl = db.evl
    def add_url(self, url):
        idx = sha224(url.encode('utf-8')).hexdigest()
        token = sha224(('view:' + idx).encode('utf-8')).hexdigest()
        self.ims.insert_one({
            'url': url,
            'token': token,
            'idx': idx,
        })
        new_url = '/view/' + idx
        return new_url, token
    def add_entry(self, token, agent=None, ip=None):
        self.evl.insert_one({
            'token': token,
            'agent': agent,
            'ip': ip,
            'time': datetime.now().isoformat(),
        })
    def get_url(self, idx):
        document = self.ims.find_one({'idx': idx})
        if document is None:
            return None, None
        else:
            return document['url'], document['token']
    def get_entries(self, token):
        doucments = self.evl.find({'token': token})
        if doucments is None:
            return None
        else:
            return [[doc['time'], doc['agent'], doc['ip']] for doc in doucments]
    def url_from_token(self, token):
        document = self.ims.find_one({'token': token})
        if document is None:
            return None
        else:
            return document['idx']


db = MDatabase()