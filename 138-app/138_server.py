# -*- coding:UTF-8 -*-
import json
import time

from datetime import datetime

from tornado.ioloop import IOLoop
from tornado.web import RequestHandler
from tornado.web import Application
from tornado.web import url
from tornado.web import asynchronous
from tornado.web import StaticFileHandler
from tornado import gen
from tornado.websocket import WebSocketHandler
from tornado.httpserver import HTTPServer

from motor import MotorClient
from motor import MotorCursor

from bson.objectid import ObjectId

from argparse import ArgumentParser

from core138 import logger


def make_message(msg, people, mentions):
    return {"from": people.name, "msg": unicode(msg), "mentions": mentions,
            "type": "message", "avatar": people.url,
            "datetime": int(time.time())}

@gen.coroutine
def load_people(db, name):
    for retries in range(5):
        people_json = yield db.people.find_one({"name": name})
        if people_json:
            break
    else:
        raise gen.Return(None)

    raise gen.Return(People.from_dict(db, people_json))

class People(object):

    def __init__(self, x, y, db, id=None, name=None, url=""):
        self.x = x
        self.y = y
        self.db = db
        self.name = name
        self.url = url
        self.id = id
        self._distance = 1000

    @gen.coroutine
    def save(self):
        self.id = yield self.db.people.save(self.to_dict())
        self.id = str(self.id)

    @gen.coroutine
    def neighbors(self):
        neighbor_query = self._neighbors_query()
        if isinstance(neighbor_query, MotorCursor):
            neighbor_query = neighbor_query.to_list(1000)
        neighbors_json = yield neighbor_query

        if "results" in neighbors_json:
            neighbors_json = neighbors_json["results"]

        neighbor_list = [People.from_dict(self.db, c) for c in neighbors_json]
        neighbors = PeopleGroup(neighbor_list)

        raise gen.Return(neighbors)

    def to_dict(self):

        to_dict =  {"loc" : [self.x, self.y], "type" : "Point",
                    "name": self.name}
        if self.id:
            to_dict["_id"] = ObjectId(self.id)

        return to_dict

    @classmethod
    def from_dict(cls, db, data):

        x, y = data["loc"]
        id = str(data["_id"])
        name = data["name"]

        return cls(x, y, db, id=id, name=name)

    def __str__(self):
        return unicode({"x": self.x, "y": self.y, "id": str(self.id),
                        "name": self.name})

    __unicode__ = __str__

    def _neighbors_query(self):
        return self.db.people.find({"loc":
                                    {"$near":
                                     {"$geometry":{"type": "Point",
                                                   "coordinates": [self.x, self.y]},
                                      "$maxDistance": self._distance }}})

    @gen.coroutine
    def remove(self):
        yield self.db.people.remove({"_id": ObjectId(self.id)})

class PeopleGroup(object):
    """ Group of people"""

    def __init__(self, people=[]):
        self.people = people

    def to_dicts(self):
        return [{'x': p.x, 'y': p.y} for p in self.people]

    def __iter__(self):
        return iter(self.people)

    def remove(self, key):
        self.people.remove(key)

    def add(self, people):
        self.people.append(people)

class Broadcast(object):
    """ Broadcast to all clients """

    def __init__(self, client=None):
        if client:
            self.add(client.people.name, client)

    @property
    def clients(self):
        if not hasattr(self.__class__, "_clients"):
            self.__class__._clients = {}
        return self.__class__._clients

    def add(self, name, client):
        if name in self.clients:
            raise KeyError("Unable to add %s. Client already exists!" % name)
        self.clients[name] = client

    def remove(self, name):
        self.clients.pop(name)

    @gen.coroutine
    def send(self, people, msg):
        neighbors = yield people.neighbors()

        for key in neighbors:
            logger.debug("Will send to: "+key.name)
            if key.name in self.clients:
                logger.debug("Sending to: "+key.name)
                self.clients[key.name].write_message(msg)

        logger.info(u"Message from %s: %s" % (people.name, unicode(msg)))

class WSHandler(WebSocketHandler):
    """ People messenger websocket """

    def check_origin(self, origin):
        return True

    def _send_message(self, *args):
        try:
            return self.write_message(*args)
        except:
            logger.info("Trying to use a close websocket")

    @gen.coroutine
    def open(self, name):
        print "new connection", name
        self.people = None
        self.people = yield load_people(self.settings["db"], name)
        self.broadcast = None
        if not self.people:
            self.send_error("Name already exists!")
            raise gen.Return(None)
        self.broadcast = Broadcast(self)

    @gen.coroutine
    def on_message(self, data_json):
        logger.info("Message received: " + str(data_json))

        if not self.people:
            raise gen.Return()

        data = json.loads(data_json)

        if data["type"] == "position":
            self.people.x, self.people.y = data["latitude"], data["longitude"]
            yield self.people.save()
            raise gen.Return(None)

        msg = make_message(data.get("msg", ""), self.people,
                           data.get("mentions", []))

        yield self.broadcast.send(self.people, msg)

    def on_close(self):
        print "connection closed"
        super(self.__class__, self).on_close()
        if self.broadcast:
            self.broadcast.remove(self.people.name)

class HomeHandler(RequestHandler):
    """ Returns home screen """

    def check_origin(self, origin):
        return True

    def get(self):
        self.render("html/index.html")

    @gen.coroutine
    def post(self, name):
        logger.debug("Command received " + str(self.request.body))
        data = json.loads(self.request.body)

        self.people = yield load_people(self.settings["db"], name)
        if self.people:
            self.send_error(status_code=409)
            raise gen.Return(None)

        url, x, y = data["url"], data["latitude"], data["longitude"]

        people = People(x, y, db=self.settings["db"], name=name,
                        url=url)
        people.save()
        self.write('{"status": "OK"}')


def main():

    app = Application([url(r"/ws/(\w+)", WSHandler),
                       url(r"/static/(.*)", StaticFileHandler,
                           {'path': "static"}),
                       url(r"/new/(\w+)", HomeHandler),
                       url(r"/(.+)", StaticFileHandler,
                           {'path': "html"}),
                       url(r"/", HomeHandler)])

    server = HTTPServer(app)
    parser = ArgumentParser()
    parser.add_argument("--mongo", help="Mongo hostname", default="localhost")
    parser.add_argument("--port", help="Server port", default=8888)

    args = parser.parse_args()
    server.bind(args.port)
    server.start(1)
    app.settings["db"] = MotorClient(args.mongo).db138
    IOLoop.current().start()


if __name__ ==  "__main__":
    main()
