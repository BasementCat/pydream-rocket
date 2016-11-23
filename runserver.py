#!/usr/bin/env python

from bottle import run

from pydream_rocket.server import HTTPServer


run(HTTPServer().app, host='0.0.0.0', port=8080, debug=True)
