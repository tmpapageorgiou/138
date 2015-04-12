# -*- coding:UTF-8 -*-
import json
import time
import os

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

from tornado_cors import CorsMixin

from motor import MotorClient
from motor import MotorCursor

from bson.objectid import ObjectId

from argparse import ArgumentParser

from core138 import logger


def make_message(msg, people, mentions):
    return {"from": people.name, "msg": unicode(msg), "mentions": mentions,
            "type": "message", "avatar": people.avatar,
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

    def __init__(self, db, id=None, name=None, avatar=""):
        self.x = 0
        self.y = 0
        self.db = db
        self.name = name
        self.avatar = avatar
        self.id = id
        self._distance = 1000
        self._active = False

    @gen.coroutine
    def save(self):
        self.id = yield self.db.people.save(self.to_dict())
        self.id = str(self.id)

    def set_position(self, x, y):
        self.x = x
        self.y = y
        self._active = True

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
                    "name": self.name, "active": self._active,
                    "avatar": self.avatar}
        if self.id:
            to_dict["_id"] = ObjectId(self.id)

        return to_dict

    @classmethod
    def from_dict(cls, db, data):

        x, y = data["loc"]
        id = str(data["_id"])
        name = data["name"]
        avatar = data.get("avatar", "")

        obj = cls(db, id=id, name=name, avatar=avatar)
        obj._active = data["active"]
        obj.x = x
        obj.y = y
        return obj

    def __str__(self):
        return unicode({"x": self.x, "y": self.y, "id": str(self.id),
                        "name": self.name})

    __unicode__ = __str__

    def _neighbors_query(self):
        return self.db.people.find({"loc":
                                    {"$near":
                                     {"$geometry":{"type": "Point",
                                                   "coordinates": [self.x, self.y]},
                                      "$maxDistance": self._distance }},
                                    "active": True})

    @gen.coroutine
    def remove(self):
        yield self.db.people.remove({"_id": ObjectId(self.id)})

class PeopleGroup(object):
    """ Group of people"""

    def __init__(self, people=[]):
        self.people = people

    def to_dict(self):
        return {"neightbors": [{"name": p.name, "avatar": p.avatar}
                               for p in self.people]}

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
            if key.name in self.clients:
                logger.debug("Sending to: "+key.name)
                self.clients[key.name].write_message(msg)
            else:
                logger.debug("User disconnected: "+key.name)

        logger.info(u"Message from %s: %s" % (people.name, unicode(msg)))

class WSHandler(WebSocketHandler):
    """ People messenger websocket """

    def check_origin(self, origin):
        return True

    @gen.coroutine
    def open(self, name):
        print "new connection", name
        self.people = None
        self.people = yield load_people(self.settings["db"], name)
        self.broadcast = None
        if not self.people:
            self.send_error("Name do not exists!")
            logger.error("Name does not exists! %s" % name)
            raise gen.Return(None)
        try:
            self.broadcast = Broadcast(self)
        except KeyError:
            logger.error("Second user try to connect with same name %s" % name)
            self.send_error("User already connected")

    @gen.coroutine
    def on_message(self, data_json):
        logger.info("Message received: " + unicode(data_json))
        COMMAND_HANDLER = {"message": self.message_handler,
                           "position": self.position_handler}

        if not self.people:
            raise gen.Return()

        data = json.loads(data_json)
        msg_type = data["type"].lower()
        yield COMMAND_HANDLER[msg_type](data)

    @gen.coroutine
    def on_close(self):
        print "connection closed, user: %s" % str(self.people)
        super(self.__class__, self).on_close()
        if self.people:
            yield self.people.remove()
        if self.broadcast:
            self.broadcast.remove(self.people.name)

    @gen.coroutine
    def message_handler(self, data):
        msg = make_message(data.get("msg", ""), self.people,
                           data.get("mentions", []))

        yield self.broadcast.send(self.people, msg)

    @gen.coroutine
    def position_handler(self, data):
        self.people.set_position(data["latitude"], data["longitude"])
        yield self.people.save()
        neighbors = yield self.people.neighbors()
        neighbors_msg = neighbors.to_dict()
        neighbors_msg["type"] = "neighbors"
        logger.debug("Sending neighbors: "+unicode(neighbors_msg))
        self.write_message(json.dumps(neighbors_msg))

class HomeHandler(CorsMixin, RequestHandler):
    """ Returns home screen """

    CORS_ORIGIN = '*'
    CORS_HEADERS = 'Content-Type'
    CORS_METHODS = 'POST,OPTIONS,GET'
    CORS_CREDENTIALS = True
    CORS_MAX_AGE = 21600
    CORS_EXPOSE_HEADERS = '*'

    def check_origin(self, origin):
        return True

    def get(self):
        self.render("html/index.html")

    @gen.coroutine
    def post(self, name):
        logger.debug("Creating new user: %s -- %s" % (name, str(self.request.body)))
        data = json.loads(self.request.body)

        self.people = yield load_people(self.settings["db"], name)
        if self.people:
            self.send_error(status_code=409)
            raise gen.Return(None)

        avatar = data["avatar"]

        people = People(db=self.settings["db"], name=name,
                        avatar=avatar)
        people.save()
        self.write('{"status": "OK"}')

def get_current_dir():
    return os.path.dirname(__file__)

def main():

    app = Application([url(r"/ws/(\w+)", WSHandler),
                       url(r"/static/(.*)", StaticFileHandler,
                           {'path': get_current_dir()+"/static"}),
                       url(r"/new/(\w+)", HomeHandler),
                       url(r"/(.+)", StaticFileHandler, {'path': get_current_dir()+"/html"}),
                       url(r"/", HomeHandler)], debug=False)

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
