# -*- coding:UTF-8 -*-
import json

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

from core138 import logger


def make_message(msg, mentions, people):
    return {"from": people.name, "msg": str(msg), "mentions": mentions,
            "type": "message", "avatar": people.url,
            "datetime": datetime.now()}

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
        return str({"x": self.x, "y": self.y, "id": str(self.id),
                    "name": self.name})

    def _neighbors_query(self):
        return self.db.command({ "geoSearch": "people" ,
                                 "search": { "type": "Point"},
                                 "near": [self.x, self.y],
                                 "maxDistance": 10},
                                 {"_id": {"$ne": ObjectId(self.id)}})

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
        if not self.people:
            raise Exception("TODO: handle user unkown")

    @gen.coroutine
    def on_message(self, data_json):
        COMMAND_HANDLER = {"messsage": self.message_handler,
                           "position": self.position_handler}

        if not self.people:
            raise gen.Return()

        data = json.loads(data_json)

        if data["type"] == "position":
            self.people.x, people.y = [int(p) for p in data["position"]]
            yield self.people.save()
            raise gen.Return(None)

        neighbors = yield self.people.neighbors()

        msg = make_message(self.people, msg["menstions"] )

        logger.info("Message from %s: %s " % (str(self.people), msg,
                    str(neighbors)))

    def on_close(self):
        print "connection closed"
        super(self.__class__, self).on_close()
        self.people.remove()

    def message_handler(self, msg):
        pass

    def position_handler(self):
        pass

class HomeHandler(RequestHandler):
    """ Returns home screen """

    def check_origin(self, origin):
        return True

    def get(self):
        self.render("index.html")

    @gen.coroutine
    def post(self, name):

        logger.debug("Command received " + str(self.request.body))
        init_data = json.loads(self.request.body)

        people = People(x, y, db=self.settings["db"], name=name,
                        url=init_data["url"])
        self.write('{"status": "OK"}')


def main():

    app = Application([url(r"/ws/(\w+)", WSHandler),
                       url(r"/static/(.*)", StaticFileHandler,
                           {'path': "static"}),
                       url(r"/new/(\w+)", HomeHandler),
                       url(r"/", HomeHandler)])

    server = HTTPServer(app)
    server.bind(8888)
    server.start(0)  # forks one process per cpu
    app.settings["db"] = MotorClient().db138
    IOLoop.current().start()

if __name__ ==  "__main__":
    main()
