import json
import traceback
from datetime import datetime, timedelta

import cherrypy
from cherrypy.process.plugins import Daemonizer
from jinja2 import Environment, FileSystemLoader
import os

import GenericOps
from DBConnectivity import Redis
from Downloader import Download

PATH = os.path.abspath(os.path.dirname(__file__))
env = Environment(loader=FileSystemLoader(''))


class Root:
    @cherrypy.expose
    def index(self):
        try:
            full_path = PATH + "/" + "tmp/" + Download(datetime.now()).file_name.format(datetime.strftime(
                datetime.now() - timedelta(1), '%d%m%y'))
            if not GenericOps.if_path_exists(full_path):
                Download(datetime.now()).download()
            template = env.get_template('index.html')
            top10 = Redis().fetch_top_10_stocks()
            return template.render(data=top10, title="Top 10 entries for " + datetime.strftime(datetime.now(), '%d/%m/%y'))
        except Exception as e:
            print(str(e))
            traceback.print_exc()
            # Can also log the errors into the database
            return json.dumps({'response': 'Some error occurred please try again!'})

    @cherrypy.expose
    def search(self, search="A", searchButton="Search"):
        try:
            full_path = PATH + "/" + "tmp/" + Download(datetime.now()).file_name.format(datetime.strftime(
                datetime.now() - timedelta(1), '%d%m%y'))
            if not GenericOps.if_path_exists(full_path):
                Download(datetime.now()).download()
            template = env.get_template('index.html')
            search_result = Redis().search_for_key(search)
            return template.render(data=search_result, title="Search results for: "+search)
        except Exception as e:
            # Can also log the errors into the database
            return json.dumps({'response': 'Some error occurred please try again!'})


if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '0.0.0.0',
                            'server.socket_port': 8080,
                            'engine.autoreload.on': False
                            })
    conf = {
        '/': {
            'tools.sessions.on': True,
            'tools.staticdir.root': os.path.abspath(os.getcwd())
        },
        '/static': {
            'tools.staticdir.on': True,
            'tools.staticdir.dir': './static'
        }
    }
    cherrypy.tree.mount(Root(), config=conf)
    if hasattr(cherrypy.engine, 'block'):
        # 3.1 syntax
        cherrypy.engine.start()
        cherrypy.engine.block()
    else:
        # 3.0 syntax
        cherrypy.server.quickstart()
        cherrypy.engine.start()

    # cherrypy.quickstart(Root(), '/', conf)