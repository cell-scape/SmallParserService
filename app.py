#! /usr/bin/env pypy3
# -*- coding: utf-8 -*-

from quart import Quart

app = Quart(__name__)


@app.route("/")
async def hello():
    return "<p>Hello, world!</p>"


app.run()
