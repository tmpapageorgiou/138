# -*- coding:UTF-8 -*-
import json
import time
import StringIO

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

from random import randint

from prototype.character import ACharacter
from prototype.character import CharacterGroup
from prototype.character import update_message

from prototype import logger


@gen.coroutine
def load_chracter(db, char_id):
    for retries in range(10):
        char_json = yield db.places.find_one({"_id": ObjectId(char_id)})
        if char_json:
            break
        print  "Load_character", char_json
    else:
        logger.error("Char id = %s not found"% char_id)
        raise KeyError("Char id = %s not found"% char_id)

    raise gen.Return(Character.deserialize(db, char_json))


class People(object):

    def __init__(self):
        pass

    @gen.coroutine
    def save(self):

        self.id = yield self.db.places.save(self.serialize())
        self.id = str(self.id)

    @gen.coroutine
    def neighbors(self):
        neighbor_query = self._neighbors_query()
        if isinstance(neighbor_query, MotorCursor):
            neighbor_query = neighbor_query.to_list(1000)
        neighbors_json = yield neighbor_query

        if "results" in neighbors_json:
            neighbors_json = neighbors_json["results"]

        neighbor_list = [Character.deserialize(self.db, c) for c in neighbors_json]
        neighbors = CharacterGroup(neighbor_list)

        raise gen.Return(neighbors)

    def serialize(self):

        to_dict =  {"pos" : { "latitude": self.x, "longitude": self.y}, "type" : "Point",
                    "name": self.name, "god_mode": self.god_mode}
        if self.id:
            to_dict["_id"] = ObjectId(self.id)

        return to_dict

    @classmethod
    def deserialize(cls, db, data):

        x = data["pos"]["latitude"]
        y = data["pos"]["longitude"]
        char_id = str(data["_id"])

        god_mode = False
        if data.get("god_mode") == True:
            god_mode = True

        return cls(x, y, db=db, char_id=char_id, god_mode=god_mode)

    def __str__(self):
        return str({"x": self.x, "y": self.y, "id": str(self.id)})

    def _neighbors_query(self):
        return self.db.command({ "geoSearch": "people" ,
                                 "search": { "type": "Point"},
                                 "near": [self.x, self.y],
                                 "maxDistance": 10},
                                 {"_id": {"$ne": ObjectId(self.id)}})

    @gen.coroutine
    def remove(self):
        yield self.db.places.remove({"_id": ObjectId(self.id)})


class WSHandler(WebSocketHandler):
    """ Charactor command websocket """

    def check_origin(self, origin):
        return True

    def _send_message(self, *args):
        try:
            return self.write_message(*args)
        except:
            logger.info("Trying to use a close websocket")

    @gen.coroutine
    def open(self, char_id):
        print "new connection", char_id
        self.char = None
        self.char = yield load_chracter(self.settings["db"], char_id)

        char_neighbors = yield self.char.neighbors()

        msg = update_message(self.char, char_neighbors)
        self.write_message(msg)

    @gen.coroutine
    def on_message(self, cmd):

        if not self.char:
            raise gen.Return()

        start_time = time.time()

        cmd = json.loads(cmd)
        self.char.command(cmd["action"])

        yield self.char.save()

        neighbors = yield self.char.neighbors()

        msg = update_message(self.char, neighbors)
        try:
            self.write_message(msg)
        except:
            return

        logger.everage("Moving char: %s " % str(self.char.id), time.time()-start_time)

    def on_close(self):
        print "connection closed"
        super(self.__class__, self).on_close()
        self.char.remove()

class HomeHandler(RequestHandler):
    """ Returns home screen """

    def check_origin(self, origin):
        return True

    @gen.coroutine
    def get(self, name=None):

        char = Character(x, y, db=self.settings["db"], god_mode=god_mode)

        yield char.save()

        self.render("index.html", char_id=str(char.id))

class CommandHandler(RequestHandler):

    def check_origin(self, origin):
        return True

    @gen.coroutine
    def get(self):
        x = randint(0, 90)
        y = randint(0, 90)

        char = Character(x, y, db=self.settings["db"])

        yield char.save()

        self.write(json.dumps({"id": char.id}))

    @gen.coroutine
    def post(self, char_id):
        print "Command received " + str(self.request.body)
        cmd = json.loads(self.request.body)


        char = yield load_chracter(self.settings["db"], char_id)
        char.command(cmd["action"])
        yield char.save()

        neighbors = yield char.neighbors()

        self.write(update_message(char, neighbors))


def main():

    app = Application([url(r"/ws/(\w+)", WSHandler),
        url(r"/static/(.*)", StaticFileHandler, {'path': "static"}),
        url(r"/", HomeHandler),
        url(r"/command/(\w+)", CommandHandler),
        url(r"/new", CommandHandler)])

    server = HTTPServer(app)
    server.bind(8888)
    server.start(0)  # forks one process per cpu
    app.settings["db"] = MotorClient().prototype
    IOLoop.current().start()

if __name__ ==  "__main__":
    main()
